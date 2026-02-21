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
import { ChatMessage, ContentType, UserContext, EstimateResponse, UnifiedAskResponse, FigmaEstimateResponse, UrlEstimateResponse, PdfEstimateResponse, OptionsWidgetChoice } from '../api/types';
import { useChat } from './useChat';
import { useElapsedTime } from './useElapsedTime';
import { unifiedAsk, getEstimate, getFigmaEstimate, analyzeFigma, getPdfEstimate, analyzePdf } from '../api/client';

// NOTE: getUrlEstimate and analyzeUrl are intentionally not imported.
// Web crawler is disabled — URL inputs redirect to task capture flow instead.

interface UseUnifiedInputOptions {
  apiEndpoint: string;
  token: string;
  onAnalysisComplete?: (result: UnifiedAskResponse, fileNames: string[]) => void;
  onStartTaskCapture?: (taskName: string) => void;
}

type DetectedMode = 'chat' | 'analysis' | 'hybrid' | 'idle' | 'figma' | 'url' | 'pdf' | 'video';

/** File type detection helpers */
const VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/webm'];
const PDF_TYPE = 'application/pdf';

function isPdfFile(file: File): boolean {
  return file.type === PDF_TYPE || file.name.toLowerCase().endsWith('.pdf');
}

function isVideoFile(file: File): boolean {
  return VIDEO_TYPES.includes(file.type);
}

function detectFileType(files: File[]): 'pdf' | 'video' | 'image' | 'mixed' | null {
  if (files.length === 0) return null;

  const hasPdf = files.some(isPdfFile);
  const hasVideo = files.some(isVideoFile);
  const hasImage = files.some(f => !isPdfFile(f) && !isVideoFile(f));

  // PDF takes precedence (only one PDF allowed)
  if (hasPdf && files.length === 1) return 'pdf';
  // Video takes precedence
  if (hasVideo && files.length === 1) return 'video';
  // All images
  if (hasImage && !hasPdf && !hasVideo) return 'image';
  // Mixed types
  return 'mixed';
}

/** URL detection helpers */
const FIGMA_URL_PATTERN = /https?:\/\/(www\.)?figma\.com\/(file|design|proto)\/[a-zA-Z0-9]+[^\s]*/i;
// Match URLs with http(s):// protocol
const WEBSITE_URL_PATTERN_EXTRACT = /https?:\/\/[^\s]+/i;
// Match domain names without protocol (e.g., "amazon.com", "www.google.com")
// Requires at least one dot and valid domain structure
const DOMAIN_PATTERN = /\b(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+(?:\/[^\s]*)?\b/i;

function detectUrlType(url: string): 'figma' | 'url' | null {
  if (!url) return null;
  // Normalize URL by adding protocol if missing
  const normalizedUrl = url.match(/^https?:\/\//i) ? url : `https://${url}`;
  if (FIGMA_URL_PATTERN.test(normalizedUrl)) return 'figma';
  // Any URL (with or without protocol) that's not Figma is a website
  if (WEBSITE_URL_PATTERN_EXTRACT.test(normalizedUrl) || DOMAIN_PATTERN.test(url)) return 'url';
  return null;
}

function extractUrl(text: string): string | null {
  const trimmed = text.trim();

  // Check for Figma URL first (can be anywhere in text)
  const figmaMatch = trimmed.match(FIGMA_URL_PATTERN);
  if (figmaMatch) return figmaMatch[0];

  // Check for URLs with protocol
  const urlMatch = trimmed.match(WEBSITE_URL_PATTERN_EXTRACT);
  if (urlMatch) {
    // Clean up any trailing punctuation that might have been captured
    let url = urlMatch[0];
    url = url.replace(/[.,;:!?)>\]]+$/, '');
    return url;
  }

  // Check for domain names without protocol
  const domainMatch = trimmed.match(DOMAIN_PATTERN);
  if (domainMatch) {
    let domain = domainMatch[0];
    domain = domain.replace(/[.,;:!?)>\]]+$/, '');
    // Prepend https:// for domain-only matches
    return `https://${domain}`;
  }

  return null;
}

/**
 * Extract task description from text that contains a URL
 * Returns the text with the URL removed and cleaned up
 */
function extractTaskFromUrlText(text: string, detectedUrl: string): string {
  let task = text;

  // Remove the detected URL (with or without protocol)
  // Use case-insensitive replacement
  const urlWithoutProtocol = detectedUrl.replace(/^https?:\/\//i, '');
  const urlPattern = new RegExp(urlWithoutProtocol.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
  task = task.replace(urlPattern, '').trim();

  // Also try removing the full URL with protocol if it appears
  const fullUrlPattern = new RegExp(detectedUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
  task = task.replace(fullUrlPattern, '').trim();

  // Remove common command-like prefixes
  task = task.replace(/^(test|analyze|check|review|evaluate)\s+/i, '').trim();

  // Remove "with this task" or similar phrases at the beginning
  task = task.replace(/^with\s+this\s+task[:\s]*/i, '').trim();

  return task;
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

/** Unified estimate that works for files, Figma, URL, or PDF */
type UnifiedEstimate = EstimateResponse | FigmaEstimateResponse | UrlEstimateResponse | PdfEstimateResponse;

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
  handleWidgetChoice: (messageId: string, choiceId: string) => void;
  notifyTaskCaptureComplete: (screenshotCount: number) => void;
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

  // File-based analysis modes
  if (hasFiles) {
    const fileType = detectFileType(files);
    if (fileType === 'pdf') return 'pdf';
    if (fileType === 'video') return 'video';
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

/** Intent patterns that trigger the options widget instead of plain chat */
const ANALYSIS_INTENT_PATTERNS = [
  /\banalyze\b/i,
  /\banalysis\b/i,
  /\bcheck\s+(my|this|the)\b/i,
  /\breview\s+(my|this|the)\b/i,
  /\bevaluate\b/i,
  /\btest\s+(my|this|the)\b/i,
  /\bstart\s+(a\s+)?new\s+analysis\b/i,
  /\bi\s+have\s+a\s+design\b/i,
  /\bi\s+want\s+to\s+(analyze|check|review|test)\b/i,
];

const CAPABILITY_PATTERNS = [
  /\bwhat\s+can\s+you\s+do\b/i,
  /\bhow\s+does\s+this\s+work\b/i,
  /\bwhat\s+is\s+this\b/i,
  /\bhelp\s*me?\b/i,
  /\bget\s+started\b/i,
];

const PAST_ANALYSES_PATTERNS = [
  /\bpast\s+anal/i,
  /\bprevious\s+anal/i,
  /\bmy\s+anal/i,
  /\bhistory\b/i,
  /\bsee\s+my\b/i,
];

const OPTIONS_WIDGET_CHOICES: OptionsWidgetChoice[] = [
  { id: 'describe_task', label: 'Describe the task here' },
  { id: 'drop_screenshots', label: 'Drop screenshots you have already taken' },
  { id: 'step_capture', label: 'Help me capture step by step screenshots of the task' },
  { id: 'just_chat', label: 'Other (just chat)' },
];

const URL_WIDGET_CHOICES: OptionsWidgetChoice[] = [
  { id: 'drop_screenshots', label: 'Drop screenshots you have already taken' },
  { id: 'step_capture', label: 'Capture step by step screenshots of the task (I will help you)' },
  { id: 'just_chat', label: 'Other (just chat)' },
];

export function useUnifiedInput(options: UseUnifiedInputOptions): UseUnifiedInputReturn {
  const { apiEndpoint, token, onAnalysisComplete, onStartTaskCapture } = options;

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
  const [deviceType, setDeviceType] = useState<string | null>(null);
  const [contextExpanded, setContextExpanded] = useState(false);

  // Conversational context gathering
  const [contextGatheringPhase, setContextGatheringPhase] = useState<ContextGatheringPhase>('idle');
  const [pendingQuestion, setPendingQuestion] = useState('');

  // Analysis pipeline
  const [analysisPhase, setAnalysisPhase] = useState<AnalysisPhase>('idle');
  const [estimate, setEstimate] = useState<UnifiedEstimate | null>(null);
  const [pendingUrl, setPendingUrl] = useState<string | null>(null);
  const [pendingUrlTask, setPendingUrlTask] = useState<string>('');
  const [isUrlContextFlow, setIsUrlContextFlow] = useState(false);
  const elapsed = useElapsedTime();

  // Loading state for unified requests
  const [isUnifiedLoading, setIsUnifiedLoading] = useState(false);

  // Flag: context was gathered before task capture, so skip re-asking after capture completes
  const [contextGatheredForCapture, setContextGatheredForCapture] = useState(false);

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

      // Handle URL-based analysis — only for Figma; files take priority over website pendingUrl
      if (pendingUrl && files.length === 0 && detectUrlType(pendingUrl) === 'figma') {
        const urlType = 'figma';

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
          // Website URL analysis is disabled — this branch should not be reached
          // (URL inputs are intercepted in submit() before reaching runAnalysis)
          throw new Error('Website URL analysis is not available. Please use task-based screenshot capture instead.');
        }

        chat.addSystemPrompt(`Analysis completed for ${analysisName}. View the full report above.`);
      } else if (files.length === 1 && isPdfFile(files[0])) {
        // PDF analysis
        const pdfFile = files[0];
        const result = await analyzePdf({
          apiEndpoint,
          apiKey: token,
          file: pdfFile,
          context,
          maxPages: 20,
        });

        elapsed.stop();
        setAnalysisPhase('complete');

        if (result.success && onAnalysisComplete) {
          onAnalysisComplete({
            success: true,
            mode: 'analysis',
            report_html: result.report_html,
            statistics: result.statistics,
          }, [pdfFile.name]);
        }
        chat.addSystemPrompt(`Analysis completed for ${pdfFile.name}. View the full report above.`);
      } else {
        // File-based analysis (images or video)
        const conversationHistory = chat.messages
          .filter(m => m.role === 'user' || (m.role === 'assistant' && !m.reportHtml))
          .slice(-10)
          .map(m => ({ role: m.role, content: m.content }));

        // Scale timeout with file count: 3 min base + 60s per file, max 15 min
        const imageTimeout = Math.min(180000 + files.length * 60000, 900000);

        const result = await unifiedAsk({
          apiEndpoint,
          token,
          message: pendingQuestion || undefined,
          files,
          context,
          conversationHistory: JSON.stringify(conversationHistory),
          timeout: imageTimeout,
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
  }, [users, expertise, tasks, format, contentType, deviceType, files, pendingQuestion, pendingUrl, apiEndpoint, token, chat, elapsed, onAnalysisComplete]);

  /** User confirms the estimate → start analysis */
  const confirmAnalysis = useCallback(async () => {
    await runAnalysis();
  }, [runAnalysis]);

  /** User picks a choice from the options widget */
  const handleWidgetChoice = useCallback((messageId: string, choiceId: string) => {
    chat.markWidgetUsed(messageId);

    switch (choiceId) {
      case 'describe_task':
        setContextGatheredForCapture(false);  // Clear flag - not using task capture
        chat.addSystemPrompt(
          'Go ahead — describe the UI issue or task flow and I\'ll identify any UI traps for you.'
        );
        break;

      case 'drop_screenshots':
        // Keep contextGatheredForCapture - user is dropping screenshots, context still applies
        chat.addSystemPrompt(
          'Drop your screenshots into the input area below (or click to select files). ' +
          'If you have multiple screenshots, I\'ll ask if they\'re in order.'
        );
        break;

      case 'step_capture':
        // Keep contextGatheredForCapture - this is the task capture flow
        chat.addSystemPrompt(
          pendingUrlTask
            ? `Got it — opening step-by-step capture for: **${pendingUrlTask}**`
            : 'Starting step-by-step capture. What task are you capturing? *(e.g., "Sign up for an account", "Complete a purchase")*'
        );
        onStartTaskCapture?.(pendingUrlTask);
        break;

      case 'just_chat':
        setContextGatheredForCapture(false);  // Clear flag - not using task capture
        chat.addSystemPrompt('Sure — what would you like to know?');
        break;
    }
  }, [chat, onStartTaskCapture, pendingUrlTask]);

  /** User cancels from estimate preview or progress */
  const cancelAnalysis = useCallback(() => {
    elapsed.reset();
    setAnalysisPhase('idle');
    setEstimate(null);
    setIsUnifiedLoading(false);
    setContextGatheredForCapture(false);  // Clear the flag on cancel
  }, [elapsed]);

  /** Start the estimation step (called after context is complete) */
  /** Called when task capture finishes — clears pendingUrl and asks for any last context */
  const notifyTaskCaptureComplete = useCallback((screenshotCount: number) => {
    setPendingUrl(null);
    chat.addSystemPrompt(
      `Got it — **${screenshotCount} screenshot${screenshotCount > 1 ? 's' : ''}** captured. ` +
      'Is there anything else you\'d like me to know before running the analysis? ' +
      '*(Or just hit send to proceed.)*'
    );
  }, [chat]);

  const startEstimation = useCallback(async (urlToAnalyze?: string) => {
    setAnalysisPhase('estimating');
    setIsUnifiedLoading(true);

    try {
      let est: UnifiedEstimate;

      if (urlToAnalyze) {
        // Only Figma URLs reach estimation — website URLs are intercepted earlier
        est = await getFigmaEstimate({ apiEndpoint, figmaUrl: urlToAnalyze });
        setPendingUrl(urlToAnalyze);
      } else if (files.length === 1 && isPdfFile(files[0])) {
        // PDF estimate
        est = await getPdfEstimate({ apiEndpoint, file: files[0] });
      } else if (files.length > 10) {
        // Estimate API caps at 10 files — calculate locally for larger sets
        const count = files.length;
        const minS = count * 20;
        const maxS = count * 35;
        est = {
          success: true,
          input_type: 'multi_image',
          file_count: count,
          total_size_mb: 0,
          time_estimate: {
            min_seconds: minS,
            max_seconds: maxS,
            min_formatted: `${Math.round(minS / 60)} min`,
            max_formatted: `${Math.round(maxS / 60)} min`,
          },
          cost_estimate: {
            min_credits: count,
            max_credits: count,
            min_dollars: parseFloat((count * 0.03).toFixed(2)),
            max_dollars: parseFloat((count * 0.05).toFixed(2)),
          },
          ffmpeg_available: false,
        };
      } else {
        // File-based estimate (images or video)
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
        // Only Figma URLs reach this path — fallback to Figma estimate
        setPendingUrl(urlToAnalyze);
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
      } else if (files.length === 1 && isPdfFile(files[0])) {
        // PDF fallback estimate
        setEstimate({
          success: true,
          file_name: files[0].name,
          page_count: 10,
          pages_to_analyze: 10,
          pdf_info: { title: '', author: '' },
          time_estimate: { min_seconds: 150, max_seconds: 300, description: '2-5 minutes' },
          cost_estimate: { credits: 10, description: '~10 credits' },
          pymupdf_available: true,
        });
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
  }, [apiEndpoint, files, deviceType, chat]);

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

        // Skip asking for tasks if they were already provided (e.g., from URL input)
        if (tasks && tasks.trim().length >= 10) {
          setContextGatheringPhase('asking_format');
          chat.addSystemPrompt(
            'Thanks. Finally, **what format is this design?**\n\n' +
            '*(e.g., "Mobile app screenshot", "Desktop website", "Tablet app")*'
          );
          return;
        }

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
          setDeviceType('mobile');
        } else if (lowerAnswer.includes('tablet') || lowerAnswer.includes('ipad')) {
          setContentType('website');
          setDeviceType('tablet');
        } else if (lowerAnswer.includes('desktop') || lowerAnswer.includes('windows') || lowerAnswer.includes('mac')) {
          setContentType('desktop_app');
          setDeviceType('desktop');
        } else if (lowerAnswer.includes('game')) {
          setContentType('game');
        } else if (lowerAnswer.includes('web') || lowerAnswer.includes('site')) {
          setContentType('website');
          setDeviceType('desktop'); // Default web to desktop
        }

        // URL context flow: show capture options widget instead of starting estimation
        if (isUrlContextFlow) {
          setIsUrlContextFlow(false);
          setContextGatheredForCapture(true);  // Mark that context is ready for task capture
          const hostname = pendingUrl ? new URL(pendingUrl).hostname : 'that site';
          chat.addOptionsWidget(
            `All set! Now, how would you like to capture screenshots of **${hostname}**?`,
            URL_WIDGET_CHOICES
          );
          return;
        }

        chat.addSystemPrompt(
          'All set! Let me estimate how long this analysis will take...'
        );

        // Context is now complete — proceed to estimation
        // Pass pendingUrl if this was a Figma analysis
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

      // Past analyses intent
      if (PAST_ANALYSES_PATTERNS.some(p => p.test(text))) {
        chat.addUserMessage(text, 'chat');
        chat.addSystemPrompt("Your past analyses are saved — click **Past Analyses** in the menu to view them.");
        return;
      }

      // Capability / help intent
      if (CAPABILITY_PATTERNS.some(p => p.test(text))) {
        chat.addUserMessage(text, 'chat');
        chat.addOptionsWidget(
          "I can help you with UI analysis in a few ways:",
          OPTIONS_WIDGET_CHOICES
        );
        return;
      }

      // Analysis intent with no files or URL
      if (ANALYSIS_INTENT_PATTERNS.some(p => p.test(text))) {
        chat.addUserMessage(text, 'chat');
        chat.addOptionsWidget(
          "How would you like to analyze your UI?",
          OPTIONS_WIDGET_CHOICES
        );
        return;
      }

      // Default: plain RAG chat
      await chat.sendMessage(text);
      return;
    }

    // ── PDF or Video analysis modes ──
    if (detectedMode === 'pdf' || detectedMode === 'video') {
      const fileType = detectedMode === 'pdf' ? 'PDF document' : 'video';
      const fileNames = files.map(f => f.name).join(', ');

      // Show user message in chat
      chat.addUserMessage(`Analyze this ${fileType}: ${fileNames}`, 'analysis');
      setInputText('');

      // Check if we already have full context
      if (hasFullContext(users, expertise, tasks, format)) {
        chat.addSystemPrompt(`Starting ${fileType} analysis...`);
        await startEstimation();
        return;
      }

      // Context is missing — start conversational gathering
      setContextGatheringPhase('asking_users');
      chat.addSystemPrompt(
        `I'll analyze this **${fileType}** for UI traps! First, I need a bit of context.\n\n` +
        '**Who are the intended users** of this interface?\n\n' +
        '*(e.g., "Adults ages 25-45 looking to stream movies", "Enterprise software developers")*'
      );
      return;
    }

    // ── Figma mode ──
    if (detectedMode === 'figma') {
      const url = detectedUrl!;
      setPendingUrl(url);
      const taskDescription = extractTaskFromUrlText(inputText, url);
      if (taskDescription && taskDescription.length >= 10) setTasks(taskDescription);

      const userMessage = taskDescription
        ? `Analyze this Figma design: ${url}\n\nTask: ${taskDescription}`
        : `Analyze this Figma design: ${url}`;
      chat.addUserMessage(userMessage, 'analysis');
      setInputText('');

      if (hasFullContext(users, expertise, tasks || taskDescription, format)) {
        chat.addSystemPrompt('Starting Figma analysis...');
        await startEstimation(url);
        return;
      }

      setContextGatheringPhase('asking_users');
      chat.addSystemPrompt(
        `I'll analyze this **Figma design** for UI traps! First, I need a bit of context.\n\n` +
        '**Who are the intended users** of this interface?\n\n' +
        '*(e.g., "Adults ages 25-45 looking to stream movies", "Enterprise software developers")*'
      );
      return;
    }

    // ── URL mode — web crawler disabled, gather context then offer capture options ──
    if (detectedMode === 'url') {
      const url = detectedUrl!;
      const hostname = new URL(url).hostname;
      const taskText = extractTaskFromUrlText(inputText, url);
      setPendingUrlTask(taskText);
      setPendingUrl(url);
      if (taskText && taskText.length >= 10) setTasks(taskText);
      chat.addUserMessage(inputText.trim(), 'chat');
      setInputText('');

      // Use the task text we just extracted (not the stale state value) for the check
      const effectiveTasks = (taskText && taskText.length >= 10) ? taskText : tasks;

      // If all context already provided, go straight to the capture options widget
      if (hasFullContext(users, expertise, effectiveTasks, format)) {
        chat.addOptionsWidget(
          `I can't automatically crawl **${hostname}** — most sites block automated access.\n\nHow would you like to capture screenshots of this flow?`,
          URL_WIDGET_CHOICES
        );
        return;
      }

      // Otherwise gather missing context first, then show the widget
      setIsUrlContextFlow(true);
      const intro = `I can't automatically crawl **${hostname}** — most sites block automated access, so I'll need you to capture screenshots. First, a few quick questions.\n\n`;

      if (users.trim().length < 10) {
        setContextGatheringPhase('asking_users');
        chat.addSystemPrompt(
          intro +
          '**Who are the intended users** of this interface?\n\n' +
          '*(e.g., "Adults ages 25-45 who own pets", "Enterprise software developers")*'
        );
      } else if (expertise.trim().length < 5) {
        setContextGatheringPhase('asking_expertise');
        chat.addSystemPrompt(
          intro +
          '**What level of expertise** will these users have?\n\n' +
          '*(e.g., "First-time users", "Intermediate users", "Power users")*'
        );
      } else if (effectiveTasks.trim().length < 10) {
        setContextGatheringPhase('asking_tasks');
        chat.addSystemPrompt(
          intro +
          '**What tasks are these users trying to accomplish?**\n\n' +
          '*(e.g., "Find and buy cat food", "Sign up for an account")*'
        );
      } else {
        setContextGatheringPhase('asking_format');
        chat.addSystemPrompt(
          intro +
          '**What type of device** will users be on?\n\n' +
          '*(e.g., "Desktop website", "Mobile browser", "Tablet")*'
        );
      }
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

    // Check if we already have full context OR context was gathered for task capture
    if (hasFullContext(users, expertise, tasks, format) || contextGatheredForCapture) {
      // Context is ready — go straight to estimation
      setContextGatheredForCapture(false);  // Clear the flag
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
    users, expertise, tasks, format, chat, startEstimation, isUrlContextFlow, contextGatheredForCapture,
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
    handleWidgetChoice,
    notifyTaskCaptureComplete,
  };
}
