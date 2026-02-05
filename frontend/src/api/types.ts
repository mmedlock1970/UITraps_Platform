// API Request/Response Types

// Content types for analysis mode selection
export type ContentType = 'website' | 'mobile_app' | 'desktop_app' | 'game' | 'other';

export interface UserContext {
  users: string;
  tasks: string;
  format: string;
  contentType?: ContentType;
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
  max_images: number;
  max_video_frames: number;
  max_image_size_mb: number;
  max_video_size_mb: number;
  supported_image_types: string[];
  supported_video_types: string[];
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
}

export interface EstimatePreviewProps {
  estimate: EstimateResponse;
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
}

// Analyzer State

export type AnalyzerView = 'form' | 'preview' | 'loading' | 'report' | 'error';

export type InputType = 'single_image' | 'multi_image' | 'video';

export interface AnalyzerState {
  view: AnalyzerView;
  files: File[];
  inputType: InputType | null;
  users: string;
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
  // Analysis fields
  report_html?: string;
  report_markdown?: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  error?: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  userId: number | null;
  hasSubscription: boolean;
  isLoading: boolean;
  error: string | null;
}
