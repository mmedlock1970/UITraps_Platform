// API Request/Response Types

// Content types for analysis mode selection
// Basic content types (backwards compatible)
export type ContentType = 'website' | 'mobile_app' | 'desktop_app' | 'game' | 'other';

// Extended platform types for more specific analysis guidance
export type PlatformType =
  | 'web'
  | 'ios_native'
  | 'android_native'
  | 'desktop_windows'
  | 'desktop_macos'
  | 'desktop_linux'
  | 'mobile_app'
  | 'desktop_app'
  | 'game'
  | 'pdf_document'
  | 'other';

// Platform options for UI dropdown
export interface PlatformOption {
  value: PlatformType;
  label: string;
  description: string;
  acceptsVideo: boolean;
  acceptsImages: boolean;
  acceptsPdf: boolean;
}

export const PLATFORM_OPTIONS: PlatformOption[] = [
  {
    value: 'web',
    label: 'Web Application',
    description: 'Website or web app',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: false,
  },
  {
    value: 'ios_native',
    label: 'iOS App',
    description: 'iPhone or iPad app (Apple HIG)',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: false,
  },
  {
    value: 'android_native',
    label: 'Android App',
    description: 'Android app (Material Design)',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: false,
  },
  {
    value: 'desktop_windows',
    label: 'Windows App',
    description: 'Windows desktop application',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: false,
  },
  {
    value: 'desktop_macos',
    label: 'macOS App',
    description: 'Mac desktop application',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: false,
  },
  {
    value: 'game',
    label: 'Video Game',
    description: 'Game UI (menus, HUD, settings)',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: false,
  },
  {
    value: 'pdf_document',
    label: 'PDF Document',
    description: 'PDF, form, or document interface',
    acceptsVideo: false,
    acceptsImages: true,
    acceptsPdf: true,
  },
  {
    value: 'other',
    label: 'Other',
    description: 'Other interface type',
    acceptsVideo: true,
    acceptsImages: true,
    acceptsPdf: true,
  },
];

// Map ContentType to PlatformType for backwards compatibility
export function contentTypeToPlatform(contentType: ContentType): PlatformType {
  const mapping: Record<ContentType, PlatformType> = {
    website: 'web',
    mobile_app: 'mobile_app',
    desktop_app: 'desktop_app',
    game: 'game',
    other: 'other',
  };
  return mapping[contentType] || 'other';
}

export type KbVersion = 'v1' | 'v2' | 'v2.1' | 'both';

export interface UserContext {
  users: string;
  expertise?: string;
  tasks: string;
  task_list?: Array<{ name: string; description: string }>;
  format: string;
  design_name?: string;
  contentType?: ContentType;
  extra_context?: string;
  product_context?: string;
  physical_env?: string;
  lighting?: string;
  grip_position?: string;
  attentional_state?: string;
  kb_version?: KbVersion;
  tenet_filter?: string[];
  verbosity?: 'brief' | 'standard';
  pass1_model?: 'sonnet' | 'haiku';
  thorough_mode?: boolean;
  input_type?: 'screenshot' | 'video' | 'flow_diagram';
  flow_mode?: 'screen' | 'flow';
  figma_url?: string;
}

export interface ReportStatistics {
  total_issues: number;
  critical_count: number;
  moderate_count: number;
  minor_count: number;
  positive_count: number;
  traps_not_found_count: number;
  summary_length: number;
}

export interface UsageInfo {
  used_this_month: number;
  limit: number;
  remaining: number;
}

export interface AnalysisResponse {
  success: boolean;
  report_html?: string;
  report_markdown?: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  error?: string;
  analysis_type?: 'single_image' | 'multi_image' | 'video';
  frame_count?: number;
}

export interface TimeEstimate {
  min_seconds: number;
  max_seconds: number;
  min_formatted: string;
  max_formatted: string;
}

export interface CostEstimate {
  min_credits: number;
  max_credits: number;
  min_dollars: number;
  max_dollars: number;
}

export interface EstimateResponse {
  success: boolean;
  input_type: 'single_image' | 'multi_image' | 'video';
  file_count: number;
  total_size_mb: number;
  estimated_frames?: number;
  video_duration_seconds?: number;
  time_estimate: TimeEstimate;
  cost_estimate: CostEstimate;
  ffmpeg_available: boolean;
}

export interface CapabilitiesResponse {
  video_analysis: boolean;
  figma_analysis: boolean;
  url_analysis: boolean;
  pdf_analysis: boolean;
  max_images: number;
  max_video_frames: number;
  max_pdf_pages: number;
  max_crawl_pages: number;
  max_image_size_mb: number;
  max_video_size_mb: number;
  max_pdf_size_mb: number;
  supported_image_types: string[];
  supported_video_types: string[];
  supported_document_types: string[];
}

// PDF Analysis Types
export interface PdfEstimateResponse {
  success: boolean;
  file_name: string;
  page_count: number;
  pages_to_analyze: number;
  pdf_info: {
    title: string;
    author: string;
  };
  time_estimate: {
    min_seconds: number;
    max_seconds: number;
    description: string;
  };
  cost_estimate: {
    credits: number;
    description: string;
  };
  pymupdf_available: boolean;
}

// Figma Analysis Types
export interface FigmaEstimateResponse {
  success: boolean;
  file_name: string;
  frame_count: number;
  has_prototype_flows: boolean;
  flow_count: number;
  time_estimate: {
    min_seconds: number;
    max_seconds: number;
    description: string;
  };
  cost_estimate: {
    credits: number;
    description: string;
  };
  figma_available: boolean;
}

export interface SiteAnalysisResponse {
  success: boolean;
  report_html?: string;
  report_markdown?: string;
  statistics?: ReportStatistics;
  site_summary?: {
    overall_assessment: string;
    critical_count: number;
    moderate_count: number;
    minor_count: number;
    total_issues: number;
  };
  pages_analyzed: number;
  analysis_type: 'figma' | 'url';
  error?: string;
}

// URL Analysis Types
export interface UrlEstimateResponse {
  success: boolean;
  url: string;
  estimated_pages: number;
  time_estimate: {
    min_seconds: number;
    max_seconds: number;
    description: string;
  };
  cost_estimate: {
    credits: number;
    description: string;
  };
  playwright_available: boolean;
}

export interface Issue {
  trap_name: string;
  tenet: string;
  location: string;
  problem: string;
  recommendation: string;
  confidence: 'high' | 'medium' | 'low';
}

export interface PotentialIssue {
  trap_name: string;
  tenet: string;
  location: string;
  observation: string;
  why_uncertain: string;
  confidence: 'low';
}

export interface AnalysisResult {
  summary: string[];
  critical_issues: Issue[];
  moderate_issues: Issue[];
  minor_issues: Issue[];
  positive_observations: string[];
  potential_issues: PotentialIssue[];
  traps_checked_not_found: string[];
}

// Component Props Types

export interface UITrapsAnalyzerProps {
  /** Backend API URL (e.g., "https://api.uitraps.com") */
  apiEndpoint: string;
  /** User's API key for authentication */
  apiKey: string;
  /** Color theme */
  theme?: 'light' | 'dark';
  /** Additional CSS class for the container */
  className?: string;
  /** Inline styles for the container */
  style?: React.CSSProperties;
  /** Show remaining API quota */
  showUsageInfo?: boolean;
  /** Show statistics after analysis */
  showStatistics?: boolean;
  /** Pre-fill the users field */
  initialUsers?: string;
  /** Pre-fill the tasks field */
  initialTasks?: string;
  /** Pre-fill the format field */
  initialFormat?: string;
  /** Callback when analysis starts */
  onAnalysisStart?: () => void;
  /** Callback when analysis completes successfully */
  onAnalysisComplete?: (result: AnalysisResponse) => void;
  /** Callback when analysis fails */
  onAnalysisError?: (error: Error) => void;
  /** Request timeout in milliseconds (default: 120000) */
  timeout?: number;
}

export interface FileUploadProps {
  files: File[];
  onFilesSelect: (files: File[]) => void;
  error?: string;
  disabled?: boolean;
  maxFiles?: number;
  acceptVideo?: boolean;
}

export interface ContextInputsProps {
  users: string;
  tasks: string;
  format: string;
  contentType: ContentType;
  onUsersChange: (value: string) => void;
  onTasksChange: (value: string) => void;
  onFormatChange: (value: string) => void;
  onContentTypeChange: (value: ContentType) => void;
  errors?: {
    users?: string;
    tasks?: string;
    format?: string;
  };
  disabled?: boolean;
}

export interface AnalysisProgressProps {
  elapsedTime: number;
  onCancel?: () => void;
  inputType?: InputType;
  fileCount?: number;
  estimatedTime?: TimeEstimate;
  isComplete?: boolean;
}

/** Union type for all estimate responses */
export type UnifiedEstimate = EstimateResponse | FigmaEstimateResponse | UrlEstimateResponse | PdfEstimateResponse;

/** Type guards for estimates */
export function isFigmaEstimate(estimate: UnifiedEstimate): estimate is FigmaEstimateResponse {
  return 'file_name' in estimate && 'frame_count' in estimate && !('page_count' in estimate);
}

export function isUrlEstimate(estimate: UnifiedEstimate): estimate is UrlEstimateResponse {
  return 'url' in estimate && 'estimated_pages' in estimate;
}

export function isFileEstimate(estimate: UnifiedEstimate): estimate is EstimateResponse {
  return 'input_type' in estimate && 'file_count' in estimate;
}

export function isPdfEstimate(estimate: UnifiedEstimate): estimate is PdfEstimateResponse {
  return 'page_count' in estimate && 'pages_to_analyze' in estimate;
}

export interface EstimatePreviewProps {
  estimate: UnifiedEstimate;
  onConfirm: () => void;
  onBack: () => void;
  isLoading?: boolean;
}

export interface ReportViewerProps {
  html: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  showStatistics?: boolean;
  showUsageInfo?: boolean;
  onNewAnalysis: () => void;
  isDark?: boolean;
  // Dual-report (compare mode) — when both are present a toggle is shown
  htmlV1?: string;
  htmlV2?: string;
  statisticsV1?: ReportStatistics;
  statisticsV2?: ReportStatistics;
}

// Analyzer State

export type AnalyzerView = 'form' | 'preview' | 'loading' | 'report' | 'error';

export type InputType = 'single_image' | 'multi_image' | 'video' | 'figma' | 'url' | 'pdf';

export interface AnalyzerState {
  view: AnalyzerView;
  files: File[];
  inputType: InputType | null;
  users: string;
  expertise: string;
  tasks: string;
  format: string;
  contentType: ContentType;
  isSubmitting: boolean;
  isEstimating: boolean;
  estimate: EstimateResponse | null;
  elapsedTime: number;
  reportHtml: string | null;
  reportMarkdown: string | null;
  statistics: ReportStatistics | null;
  usage: UsageInfo | null;
  error: string | null;
  // Legacy support
  file: File | null;
}

export type AnalyzerAction =
  | { type: 'SET_FILES'; payload: File[] }
  | { type: 'SET_FILE'; payload: File | null }
  | { type: 'SET_USERS'; payload: string }
  | { type: 'SET_EXPERTISE'; payload: string }
  | { type: 'SET_TASKS'; payload: string }
  | { type: 'SET_FORMAT'; payload: string }
  | { type: 'SET_CONTENT_TYPE'; payload: ContentType }
  | { type: 'START_ESTIMATION' }
  | { type: 'ESTIMATION_SUCCESS'; payload: EstimateResponse }
  | { type: 'ESTIMATION_ERROR'; payload: string }
  | { type: 'CONFIRM_ANALYSIS' }
  | { type: 'START_ANALYSIS' }
  | { type: 'UPDATE_ELAPSED_TIME'; payload: number }
  | { type: 'ANALYSIS_SUCCESS'; payload: AnalysisResponse }
  | { type: 'ANALYSIS_ERROR'; payload: string }
  | { type: 'BACK_TO_FORM' }
  | { type: 'RESET' };


// ===========================================================
// Chat & Unified Platform Types
// ===========================================================

export type MessageMode = 'analysis' | 'chat' | 'hybrid';

export interface OptionsWidgetChoice {
  id: string;
  label: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  mode: MessageMode;
  sources?: string[];
  timestamp: Date;
  /** If this message contains an analysis report */
  reportHtml?: string;
  statistics?: ReportStatistics;
  /** If this message contains an options widget */
  widgetType?: 'options';
  widgetChoices?: OptionsWidgetChoice[];
  /** Whether widget choices have been used (disables buttons after selection) */
  widgetUsed?: boolean;
}

export interface ChatApiResponse {
  response: string;
  sources: string[];
  usage?: { inputTokens: number; outputTokens: number };
  mode: string;
}

export interface UnifiedAskResponse {
  success: boolean;
  mode: MessageMode;
  // Chat fields
  response?: string;
  sources?: string[];
  // Analysis fields (single version)
  report_html?: string;
  report_markdown?: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  error?: string;
  kb_version?: KbVersion;
  // Dual analysis fields (kb_version="both")
  report_html_v1?: string;
  report_html_v2?: string;
  statistics_v1?: ReportStatistics;
  statistics_v2?: ReportStatistics;
}

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  userId: number | null;
  hasSubscription: boolean;
  isLoading: boolean;
  error: string | null;
}
