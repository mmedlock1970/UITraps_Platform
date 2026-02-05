// Main component export
export { UITrapsAnalyzer, default } from './UITrapsAnalyzer';

// Component exports for advanced usage
export { FileUpload } from './components/FileUpload';
export { ContextInputs } from './components/ContextInputs';
export { AnalyzerForm } from './components/AnalyzerForm';
export { AnalysisProgress } from './components/AnalysisProgress';
export { ReportViewer } from './components/ReportViewer';

// Hook exports
export { useAnalyzer } from './hooks/useAnalyzer';
export { useElapsedTime, formatElapsedTime } from './hooks/useElapsedTime';

// API client exports
export { analyzeImage, checkUsage, checkHealth } from './api/client';

// Type exports
export type {
  UITrapsAnalyzerProps,
  FileUploadProps,
  ContextInputsProps,
  AnalysisProgressProps,
  ReportViewerProps,
  AnalysisResponse,
  ReportStatistics,
  UsageInfo,
  UserContext,
  Issue,
  PotentialIssue,
  AnalysisResult,
  AnalyzerState,
  AnalyzerView,
} from './api/types';

export type { UseAnalyzerOptions, UseAnalyzerReturn } from './hooks/useAnalyzer';
export type { UseElapsedTimeReturn } from './hooks/useElapsedTime';
