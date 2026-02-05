/**
 * Unified input orchestrator hook.
 *
 * Composes useChat to provide a single submit() function
 * that auto-routes based on what the user provides:
 * - Text only → chat
 * - Files + context → analysis (with estimate preview + progress)
 * - Files without context → conversational context gathering first
 */

import { useState, useCallback, useMemo } from 'react';
import { ChatMessage, ContentType, UserContext, EstimateResponse, UnifiedAskResponse } from '../api/types';
import { useChat } from './useChat';
import { useElapsedTime } from './useElapsedTime';
import { unifiedAsk, getEstimate } from '../api/client';

interface UseUnifiedInputOptions {
  apiEndpoint: string;
  token: string;
  onAnalysisComplete?: (result: UnifiedAskResponse, fileNames: string[]) => void;
}

type DetectedMode = 'chat' | 'analysis' | 'hybrid' | 'idle';

/** Phases for conversational context gathering */
type ContextGatheringPhase =
  | 'idle'
  | 'asking_users'
  | 'asking_tasks'
  | 'asking_format'
  | 'complete';

/** Phases for the analysis pipeline */
type AnalysisPhase =
  | 'idle'
  | 'estimating'
  | 'previewing'
  | 'analyzing'
  | 'complete';

interface UseUnifiedInputReturn {
  // Input state
  inputText: string;
  setInputText: (text: string) => void;
  files: File[];
  setFiles: (files: File[]) => void;

  // Context fields (for analysis mode)
  users: string;
  setUsers: (v: string) => void;
  tasks: string;
  setTasks: (v: string) => void;
  format: string;
  setFormat: (v: string) => void;
  contentType: ContentType;
  setContentType: (v: ContentType) => void;
  contextExpanded: boolean;
  setContextExpanded: (v: boolean) => void;

  // Mode detection
  detectedMode: DetectedMode;

  // Context gathering
  contextGatheringPhase: ContextGatheringPhase;

  // Analysis pipeline
  analysisPhase: AnalysisPhase;
  estimate: EstimateResponse | null;
  elapsedTime: number;
  confirmAnalysis: () => Promise<void>;
  cancelAnalysis: () => void;

  // Conversation
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;

  // Actions
  submit: () => Promise<void>;
  clearHistory: () => void;
}

function detectMode(
  inputText: string,
  files: File[],
  users: string,
  tasks: string,
  format: string,
): DetectedMode {
  const hasText = inputText.trim().length > 0;
  const hasFiles = files.length > 0;
  const hasContext = (
    users.trim().length >= 10 &&
    tasks.trim().length >= 10 &&
    format.trim().length >= 10
  );

  if (!hasText && !hasFiles) return 'idle';
  if (hasFiles && hasContext) return 'analysis';
  if (hasFiles && hasText && !hasContext) return 'hybrid';
  if (hasFiles && !hasText && !hasContext) return 'analysis';
  return 'chat';
}

function hasFullContext(users: string, tasks: string, format: string): boolean {
  return (
    users.trim().length >= 10 &&
    tasks.trim().length >= 10 &&
    format.trim().length >= 10
  );
}

export function useUnifiedInput(options: UseUnifiedInputOptions): UseUnifiedInputReturn {
  const { apiEndpoint, token, onAnalysisComplete } = options;

  // Input state
  const [inputText, setInputText] = useState('');
  const [files, setFiles] = useState<File[]>([]);

  // Context fields
  const [users, setUsers] = useState('');
  const [tasks, setTasks] = useState('');
  const [format, setFormat] = useState('');
  const [contentType, setContentType] = useState<ContentType>('website');
  const [contextExpanded, setContextExpanded] = useState(false);

  // Conversational context gathering
  const [contextGatheringPhase, setContextGatheringPhase] = useState<ContextGatheringPhase>('idle');
  const [pendingQuestion, setPendingQuestion] = useState('');

  // Analysis pipeline
  const [analysisPhase, setAnalysisPhase] = useState<AnalysisPhase>('idle');
  const [estimate, setEstimate] = useState<EstimateResponse | null>(null);
  const elapsed = useElapsedTime();

  // Loading state for unified requests
  const [isUnifiedLoading, setIsUnifiedLoading] = useState(false);

  // Chat hook for pure chat messages
  const chat = useChat({ apiEndpoint, token });

  // Mode detection
  const detectedMode = useMemo(
    () => detectMode(inputText, files, users, tasks, format),
    [inputText, files, users, tasks, format],
  );

  /** Run the actual analysis API call (called after estimate confirmation) */
  const runAnalysis = useCallback(async () => {
    setAnalysisPhase('analyzing');
    elapsed.start();
    setIsUnifiedLoading(true);

    const context: UserContext = {
      users,
      tasks,
      format,
      contentType,
    };

    const conversationHistory = chat.messages
      .filter(m => m.role === 'user' || (m.role === 'assistant' && !m.reportHtml))
      .slice(-10)
      .map(m => ({ role: m.role, content: m.content }));

    try {
      const result = await unifiedAsk({
        apiEndpoint,
        token,
        message: pendingQuestion || undefined,
        files,
        context,
        conversationHistory: JSON.stringify(conversationHistory),
      });

      elapsed.stop();
      setAnalysisPhase('complete');

      // Notify parent (App) so it can switch to report view
      const fileNames = files.map(f => f.name);
      if ((result.mode === 'analysis' || result.mode === 'hybrid') && onAnalysisComplete) {
        onAnalysisComplete(result, fileNames);
      }
      chat.addSystemPrompt(`Analysis completed for ${fileNames.join(', ')}. View the full report above.`);

      // Clear inputs
      setInputText('');
      setFiles([]);
      setPendingQuestion('');
      setAnalysisPhase('idle');
      setEstimate(null);
    } catch (err) {
      elapsed.stop();
      const msg = err instanceof Error ? err.message : 'Request failed';
      chat.addSystemPrompt(`Analysis failed: ${msg}`);
      setAnalysisPhase('idle');
      setEstimate(null);
    } finally {
      setIsUnifiedLoading(false);
    }
  }, [users, tasks, format, contentType, files, pendingQuestion, apiEndpoint, token, chat, elapsed, onAnalysisComplete]);

  /** User confirms the estimate → start analysis */
  const confirmAnalysis = useCallback(async () => {
    await runAnalysis();
  }, [runAnalysis]);

  /** User cancels from estimate preview or progress */
  const cancelAnalysis = useCallback(() => {
    elapsed.reset();
    setAnalysisPhase('idle');
    setEstimate(null);
    setIsUnifiedLoading(false);
  }, [elapsed]);

  /** Start the estimation step (called after context is complete) */
  const startEstimation = useCallback(async () => {
    setAnalysisPhase('estimating');
    setIsUnifiedLoading(true);

    try {
      const est = await getEstimate({ apiEndpoint, files });
      setEstimate(est);
      setAnalysisPhase('previewing');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      chat.addSystemPrompt(
        `Could not get estimate: ${msg}. ` +
        'Please click **Start Analysis** below to proceed without an estimate.'
      );
      // Create a fallback estimate so the user can still proceed
      setEstimate({
        success: true,
        input_type: files.length > 1 ? 'multi_image' : 'single_image',
        file_count: files.length,
        total_size_mb: 0,
        time_estimate: {
          min_seconds: 30,
          max_seconds: 120,
          min_formatted: '30 seconds',
          max_formatted: '2 minutes',
        },
        cost_estimate: { min_credits: 1, max_credits: 1, min_dollars: 0.1, max_dollars: 0.3 },
        ffmpeg_available: false,
      });
      setAnalysisPhase('previewing');
    } finally {
      setIsUnifiedLoading(false);
    }
  }, [apiEndpoint, files, chat]);

  const submit = useCallback(async () => {
    if (!token) return;

    // ── Handle conversational context gathering ──
    if (contextGatheringPhase !== 'idle') {
      const answer = inputText.trim();
      if (!answer) return;

      // Show user's answer in chat
      chat.addUserMessage(answer, 'analysis');
      setInputText('');

      if (contextGatheringPhase === 'asking_users') {
        setUsers(answer);
        setContextGatheringPhase('asking_tasks');
        chat.addSystemPrompt(
          'Got it. Now, **what tasks are these users trying to accomplish?**\n\n' +
          '*(e.g., "Find and play a movie", "Sign up for an account", "Complete a purchase")*'
        );
        return;
      }

      if (contextGatheringPhase === 'asking_tasks') {
        setTasks(answer);
        setContextGatheringPhase('asking_format');
        chat.addSystemPrompt(
          'Thanks. Finally, **what format is this design?**\n\n' +
          '*(e.g., "Mobile app screenshot", "Desktop website", "Tablet app")*'
        );
        return;
      }

      if (contextGatheringPhase === 'asking_format') {
        setFormat(answer);
        setContextGatheringPhase('idle');

        // Auto-detect content type from format answer
        const lowerAnswer = answer.toLowerCase();
        if (lowerAnswer.includes('mobile') || lowerAnswer.includes('ios') || lowerAnswer.includes('android')) {
          setContentType('mobile_app');
        } else if (lowerAnswer.includes('desktop') || lowerAnswer.includes('windows') || lowerAnswer.includes('mac')) {
          setContentType('desktop_app');
        } else if (lowerAnswer.includes('game')) {
          setContentType('game');
        } else if (lowerAnswer.includes('web') || lowerAnswer.includes('site')) {
          setContentType('website');
        }

        chat.addSystemPrompt(
          'All set! Let me estimate how long this analysis will take...'
        );

        // Context is now complete — proceed to estimation
        await startEstimation();
        return;
      }

      return;
    }

    if (detectedMode === 'idle') return;

    // ── Pure chat mode ──
    if (detectedMode === 'chat') {
      const text = inputText.trim();
      setInputText('');
      await chat.sendMessage(text);
      return;
    }

    // ── Analysis or hybrid — files are present ──
    const fileNames = files.map(f => f.name).join(', ');
    const userText = inputText.trim();
    const userContent = userText
      ? `${userText}\n\n*Attached: ${fileNames}*`
      : `*Attached for analysis: ${fileNames}*`;

    // Show user message in chat
    chat.addUserMessage(userContent, 'analysis');

    // Store the question for later use in the API call
    setPendingQuestion(userText);
    setInputText('');

    // Check if we already have full context
    if (hasFullContext(users, tasks, format)) {
      // Context is ready — go straight to estimation
      await startEstimation();
      return;
    }

    // Context is missing — start conversational gathering
    setContextGatheringPhase('asking_users');
    chat.addSystemPrompt(
      "I'd be happy to analyze this for UI traps! First, I need a bit of context.\n\n" +
      '**Who are the intended users** of this interface?\n\n' +
      '*(e.g., "Adults ages 25-45 looking to stream movies", "Enterprise software developers")*'
    );
  }, [
    token, contextGatheringPhase, detectedMode, inputText, files,
    users, tasks, format, chat, startEstimation,
  ]);

  return {
    inputText,
    setInputText,
    files,
    setFiles,
    users,
    setUsers,
    tasks,
    setTasks,
    format,
    setFormat,
    contentType,
    setContentType,
    contextExpanded,
    setContextExpanded,
    detectedMode,
    contextGatheringPhase,
    analysisPhase,
    estimate,
    elapsedTime: elapsed.elapsedTime,
    confirmAnalysis,
    cancelAnalysis,
    messages: chat.messages,
    isLoading: chat.isLoading || isUnifiedLoading,
    error: chat.error,
    submit,
    clearHistory: chat.clearHistory,
  };
}
