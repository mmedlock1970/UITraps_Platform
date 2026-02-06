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
import { ChatMessage, ContentType, UserContext, EstimateResponse, UnifiedAskResponse, FigmaEstimateResponse, UrlEstimateResponse } from '../api/types';
import { useChat } from './useChat';
import { useElapsedTime } from './useElapsedTime';
import { unifiedAsk, getEstimate, getFigmaEstimate, getUrlEstimate, analyzeFigma, analyzeUrl } from '../api/client';

interface UseUnifiedInputOptions {
  apiEndpoint: string;
  token: string;
  onAnalysisComplete?: (result: UnifiedAskResponse, fileNames: string[]) => void;
}

type DetectedMode = 'chat' | 'analysis' | 'hybrid' | 'idle' | 'figma' | 'url';

/** URL detection helpers */
const FIGMA_URL_PATTERN = /https?:\/\/(www\.)?figma\.com\/(file|design|proto)\/[a-zA-Z0-9]+/i;
const WEBSITE_URL_PATTERN = /^https?:\/\/[^\s]+$/i;

function detectUrlType(text: string): 'figma' | 'url' | null {
  const trimmed = text.trim();
  if (FIGMA_URL_PATTERN.test(trimmed)) return 'figma';
  if (WEBSITE_URL_PATTERN.test(trimmed) && !trimmed.includes(' ')) return 'url';
  return null;
}

function extractUrl(text: string): string | null {
  const trimmed = text.trim();
  // Check for Figma URL first
  const figmaMatch = trimmed.match(FIGMA_URL_PATTERN);
  if (figmaMatch) return figmaMatch[0];
  // Check for any URL
  const urlMatch = trimmed.match(WEBSITE_URL_PATTERN);
  if (urlMatch) return urlMatch[0];
  return null;
}

/** Phases for conversational context gathering */
type ContextGatheringPhase =
  | 'idle'
  | 'asking_users'
  | 'asking_expertise'
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

/** Unified estimate that works for files, Figma, or URL */
type UnifiedEstimate = EstimateResponse | FigmaEstimateResponse | UrlEstimateResponse;

interface UseUnifiedInputReturn {
  // Input state
  inputText: string;
  setInputText: (text: string) => void;
  files: File[];
  setFiles: (files: File[]) => void;

  // URL detection
  detectedUrl: string | null;

  // Context fields (for analysis mode)
  users: string;
  setUsers: (v: string) => void;
  expertise: string;
  setExpertise: (v: string) => void;
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
  estimate: UnifiedEstimate | null;
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
  expertise: string,
  tasks: string,
  format: string,
  detectedUrl: string | null,
): DetectedMode {
  const hasText = inputText.trim().length > 0;
  const hasFiles = files.length > 0;
  const hasContext = (
    users.trim().length >= 10 &&
    expertise.trim().length >= 5 &&
    tasks.trim().length >= 10 &&
    format.trim().length >= 10
  );

  // URL-based analysis modes
  if (detectedUrl) {
    const urlType = detectUrlType(detectedUrl);
    if (urlType === 'figma') return 'figma';
    if (urlType === 'url') return 'url';
  }

  if (!hasText && !hasFiles) return 'idle';
  if (hasFiles && hasContext) return 'analysis';
  if (hasFiles && hasText && !hasContext) return 'hybrid';
  if (hasFiles && !hasText && !hasContext) return 'analysis';
  return 'chat';
}

function hasFullContext(users: string, expertise: string, tasks: string, format: string): boolean {
  return (
    users.trim().length >= 10 &&
    expertise.trim().length >= 5 &&
    tasks.trim().length >= 10 &&
    format.trim().length >= 10
  );
}

export function useUnifiedInput(options: UseUnifiedInputOptions): UseUnifiedInputReturn {
  const { apiEndpoint, token, onAnalysisComplete } = options;

  // Input state
  const [inputText, setInputText] = useState('');
  const [files, setFiles] = useState<File[]>([]);

  // URL detection (derived from inputText)
  const detectedUrl = useMemo(() => extractUrl(inputText), [inputText]);

  // Context fields
  const [users, setUsers] = useState('');
  const [expertise, setExpertise] = useState('');
  const [tasks, setTasks] = useState('');
  const [format, setFormat] = useState('');
  const [contentType, setContentType] = useState<ContentType>('website');
  const [contextExpanded, setContextExpanded] = useState(false);

  // Conversational context gathering
  const [contextGatheringPhase, setContextGatheringPhase] = useState<ContextGatheringPhase>('idle');
  const [pendingQuestion, setPendingQuestion] = useState('');

  // Analysis pipeline
  const [analysisPhase, setAnalysisPhase] = useState<AnalysisPhase>('idle');
  const [estimate, setEstimate] = useState<UnifiedEstimate | null>(null);
  const [pendingUrl, setPendingUrl] = useState<string | null>(null);
  const elapsed = useElapsedTime();

  // Loading state for unified requests
  const [isUnifiedLoading, setIsUnifiedLoading] = useState(false);

  // Chat hook for pure chat messages
  const chat = useChat({ apiEndpoint, token });

  // Mode detection
  const detectedMode = useMemo(
    () => detectMode(inputText, files, users, expertise, tasks, format, detectedUrl),
    [inputText, files, users, expertise, tasks, format, detectedUrl],
  );

  /** Run the actual analysis API call (called after estimate confirmation) */
  const runAnalysis = useCallback(async () => {
    setAnalysisPhase('analyzing');
    elapsed.start();
    setIsUnifiedLoading(true);

    const context: UserContext = {
      users,
      expertise,
      tasks,
      format,
      contentType,
    };

    try {
      let analysisName: string;

      // Handle URL-based analysis (Figma or website)
      if (pendingUrl) {
        const urlType = detectUrlType(pendingUrl);

        if (urlType === 'figma') {
          analysisName = `Figma file`;
          const result = await analyzeFigma({
            apiEndpoint,
            apiKey: token,
            figmaUrl: pendingUrl,
            context,
            maxFrames: 10,
          });

          elapsed.stop();
          setAnalysisPhase('complete');

          if (result.success && onAnalysisComplete) {
            onAnalysisComplete({
              success: true,
              mode: 'analysis',
              report_html: result.report_html,
              statistics: result.statistics,
            }, [analysisName]);
          }
        } else {
          // Website URL analysis
          analysisName = new URL(pendingUrl).hostname;
          const result = await analyzeUrl({
            apiEndpoint,
            apiKey: token,
            url: pendingUrl,
            context,
            maxPages: 10,
          });

          elapsed.stop();
          setAnalysisPhase('complete');

          if (result.success && onAnalysisComplete) {
            onAnalysisComplete({
              success: true,
              mode: 'analysis',
              report_html: result.report_html,
              statistics: result.statistics,
            }, [analysisName]);
          }
        }

        chat.addSystemPrompt(`Analysis completed for ${analysisName}. View the full report above.`);
      } else {
        // File-based analysis
        const conversationHistory = chat.messages
          .filter(m => m.role === 'user' || (m.role === 'assistant' && !m.reportHtml))
          .slice(-10)
          .map(m => ({ role: m.role, content: m.content }));

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
      }

      // Clear inputs
      setInputText('');
      setFiles([]);
      setPendingQuestion('');
      setPendingUrl(null);
      setAnalysisPhase('idle');
      setEstimate(null);
    } catch (err) {
      elapsed.stop();
      const msg = err instanceof Error ? err.message : 'Request failed';
      chat.addSystemPrompt(`Analysis failed: ${msg}`);
      setAnalysisPhase('idle');
      setEstimate(null);
      setPendingUrl(null);
    } finally {
      setIsUnifiedLoading(false);
    }
  }, [users, expertise, tasks, format, contentType, files, pendingQuestion, pendingUrl, apiEndpoint, token, chat, elapsed, onAnalysisComplete]);

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
  const startEstimation = useCallback(async (urlToAnalyze?: string) => {
    setAnalysisPhase('estimating');
    setIsUnifiedLoading(true);

    try {
      let est: UnifiedEstimate;

      if (urlToAnalyze) {
        // URL-based estimate
        const urlType = detectUrlType(urlToAnalyze);
        if (urlType === 'figma') {
          est = await getFigmaEstimate({ apiEndpoint, figmaUrl: urlToAnalyze });
        } else {
          est = await getUrlEstimate({ apiEndpoint, url: urlToAnalyze, maxPages: 10 });
        }
        setPendingUrl(urlToAnalyze);
      } else {
        // File-based estimate
        est = await getEstimate({ apiEndpoint, files });
      }

      setEstimate(est);
      setAnalysisPhase('previewing');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      chat.addSystemPrompt(
        `Could not get estimate: ${msg}. ` +
        'Please click **Start Analysis** below to proceed without an estimate.'
      );
      // Create a fallback estimate so the user can still proceed
      if (urlToAnalyze) {
        const urlType = detectUrlType(urlToAnalyze);
        setPendingUrl(urlToAnalyze);
        if (urlType === 'figma') {
          setEstimate({
            success: true,
            file_name: 'Figma file',
            frame_count: 5,
            has_prototype_flows: false,
            flow_count: 0,
            time_estimate: { min_seconds: 120, max_seconds: 300, description: '2-5 minutes' },
            cost_estimate: { credits: 5, description: '~5 credits' },
            figma_available: true,
          });
        } else {
          setEstimate({
            success: true,
            url: urlToAnalyze,
            estimated_pages: 5,
            time_estimate: { min_seconds: 200, max_seconds: 400, description: '3-7 minutes' },
            cost_estimate: { credits: 5, description: '~5 credits' },
            playwright_available: true,
          });
        }
      } else {
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
      }
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
        // Validate minimum length (10 chars required by backend)
        if (answer.trim().length < 10) {
          chat.addSystemPrompt(
            'That response is a bit too short. Please provide more detail (at least 10 characters) about who the users are.\n\n' +
            '*(e.g., "Adults ages 25-45 looking to stream movies", "Enterprise software developers")*'
          );
          return;
        }
        setUsers(answer);
        setContextGatheringPhase('asking_expertise');
        chat.addSystemPrompt(
          'Got it. **What level of expertise will these users have** with this product?\n\n' +
          '*(e.g., "First-time users unfamiliar with the domain", "Intermediate users with some experience", "Power users with years of experience")*'
        );
        return;
      }

      if (contextGatheringPhase === 'asking_expertise') {
        // Validate minimum length (5 chars required)
        if (answer.trim().length < 5) {
          chat.addSystemPrompt(
            'Please provide a bit more detail about the users\' expertise level (at least 5 characters).\n\n' +
            '*(e.g., "First-time users", "Intermediate", "Power users")*'
          );
          return;
        }
        setExpertise(answer);
        setContextGatheringPhase('asking_tasks');
        chat.addSystemPrompt(
          'Thanks. Now, **what tasks are these users trying to accomplish?**\n\n' +
          '*(e.g., "Find and play a movie", "Sign up for an account", "Complete a purchase")*'
        );
        return;
      }

      if (contextGatheringPhase === 'asking_tasks') {
        // Validate minimum length (10 chars required by backend)
        if (answer.trim().length < 10) {
          chat.addSystemPrompt(
            'That response is a bit too short. Please provide more detail (at least 10 characters) about the tasks.\n\n' +
            '*(e.g., "Find and play a movie", "Sign up for an account and complete a purchase")*'
          );
          return;
        }
        setTasks(answer);
        setContextGatheringPhase('asking_format');
        chat.addSystemPrompt(
          'Thanks. Finally, **what format is this design?**\n\n' +
          '*(e.g., "Mobile app screenshot", "Desktop website", "Tablet app")*'
        );
        return;
      }

      if (contextGatheringPhase === 'asking_format') {
        // Validate minimum length (10 chars required by backend)
        if (answer.trim().length < 10) {
          chat.addSystemPrompt(
            'Please provide more detail about the format (at least 10 characters).\n\n' +
            '*(e.g., "Mobile app screenshot", "Desktop website layout", "Tablet application UI")*'
          );
          return;
        }
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
        // Pass pendingUrl if this was a URL analysis
        await startEstimation(pendingUrl || undefined);
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

    // ── Figma or URL analysis modes ──
    if (detectedMode === 'figma' || detectedMode === 'url') {
      const url = detectedUrl!;
      const urlLabel = detectedMode === 'figma'
        ? 'Figma file'
        : new URL(url).hostname;

      // Store URL for later use after context gathering
      setPendingUrl(url);

      // Show user message in chat
      chat.addUserMessage(`Analyze this ${detectedMode === 'figma' ? 'Figma design' : 'website'}: ${url}`, 'analysis');
      setInputText('');

      // Check if we already have full context
      if (hasFullContext(users, expertise, tasks, format)) {
        chat.addSystemPrompt(`Starting analysis of ${urlLabel}...`);
        await startEstimation(url);
        return;
      }

      // Context is missing — start conversational gathering
      setContextGatheringPhase('asking_users');
      chat.addSystemPrompt(
        `I'll analyze **${urlLabel}** for UI traps! First, I need a bit of context.\n\n` +
        '**Who are the intended users** of this interface?\n\n' +
        '*(e.g., "Adults ages 25-45 looking to stream movies", "Enterprise software developers")*'
      );
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
    if (hasFullContext(users, expertise, tasks, format)) {
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
    token, contextGatheringPhase, detectedMode, inputText, files, detectedUrl, pendingUrl,
    users, expertise, tasks, format, chat, startEstimation,
  ]);

  return {
    inputText,
    setInputText,
    files,
    setFiles,
    detectedUrl,
    users,
    setUsers,
    expertise,
    setExpertise,
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
