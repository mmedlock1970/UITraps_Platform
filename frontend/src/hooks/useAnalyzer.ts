import { useReducer, useCallback, useRef } from 'react';
import { analyzeImage, analyzeMultiImage, analyzeVideo, getEstimate } from '../api/client';
import {
  AnalyzerState,
  AnalyzerAction,
  AnalysisResponse,
  UserContext,
  InputType,
  ContentType,
} from '../api/types';

const VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/webm'];

const initialState: AnalyzerState = {
  view: 'form',
  files: [],
  file: null,
  inputType: null,
  users: '',
  expertise: '',
  tasks: '',
  format: '',
  contentType: 'website',
  isSubmitting: false,
  isEstimating: false,
  estimate: null,
  elapsedTime: 0,
  reportHtml: null,
  reportMarkdown: null,
  statistics: null,
  usage: null,
  error: null,
};

function detectInputType(files: File[]): InputType | null {
  if (files.length === 0) return null;

  const hasVideo = files.some(f => VIDEO_TYPES.includes(f.type));
  if (hasVideo) return 'video';
  if (files.length === 1) return 'single_image';
  return 'multi_image';
}

function analyzerReducer(state: AnalyzerState, action: AnalyzerAction): AnalyzerState {
  switch (action.type) {
    case 'SET_FILES':
      return {
        ...state,
        files: action.payload,
        file: action.payload[0] || null,
        inputType: detectInputType(action.payload),
      };
    case 'SET_FILE':
      return {
        ...state,
        file: action.payload,
        files: action.payload ? [action.payload] : [],
        inputType: action.payload ? 'single_image' : null,
      };
    case 'SET_USERS':
      return { ...state, users: action.payload };
    case 'SET_EXPERTISE':
      return { ...state, expertise: action.payload };
    case 'SET_TASKS':
      return { ...state, tasks: action.payload };
    case 'SET_FORMAT':
      return { ...state, format: action.payload };
    case 'SET_CONTENT_TYPE':
      return { ...state, contentType: action.payload };
    case 'START_ESTIMATION':
      return {
        ...state,
        isEstimating: true,
        error: null,
      };
    case 'ESTIMATION_SUCCESS':
      return {
        ...state,
        isEstimating: false,
        estimate: action.payload,
        view: 'preview',
        error: null,
      };
    case 'ESTIMATION_ERROR':
      return {
        ...state,
        isEstimating: false,
        error: action.payload,
      };
    case 'CONFIRM_ANALYSIS':
    case 'START_ANALYSIS':
      return {
        ...state,
        view: 'loading',
        isSubmitting: true,
        elapsedTime: 0,
        error: null,
      };
    case 'UPDATE_ELAPSED_TIME':
      return { ...state, elapsedTime: action.payload };
    case 'ANALYSIS_SUCCESS':
      return {
        ...state,
        view: 'report',
        isSubmitting: false,
        reportHtml: action.payload.report_html || null,
        reportMarkdown: action.payload.report_markdown || null,
        statistics: action.payload.statistics || null,
        usage: action.payload.usage || null,
        error: null,
      };
    case 'ANALYSIS_ERROR':
      return {
        ...state,
        view: 'error',
        isSubmitting: false,
        error: action.payload,
      };
    case 'BACK_TO_FORM':
      return {
        ...state,
        view: 'form',
        estimate: null,
        isEstimating: false,
        isSubmitting: false,
        error: null,
      };
    case 'RESET':
      return {
        ...initialState,
        users: state.users,
        tasks: state.tasks,
        format: state.format,
        contentType: state.contentType,
      };
    default:
      return state;
  }
}

export interface UseAnalyzerOptions {
  apiEndpoint: string;
  apiKey: string;
  timeout?: number;
  initialUsers?: string;
  initialTasks?: string;
  initialFormat?: string;
  onAnalysisStart?: () => void;
  onAnalysisComplete?: (result: AnalysisResponse) => void;
  onAnalysisError?: (error: Error) => void;
}

export interface UseAnalyzerReturn {
  state: AnalyzerState;
  setFiles: (files: File[]) => void;
  setFile: (file: File | null) => void;
  setUsers: (value: string) => void;
  setExpertise: (value: string) => void;
  setTasks: (value: string) => void;
  setFormat: (value: string) => void;
  setContentType: (value: ContentType) => void;
  requestEstimate: () => Promise<void>;
  confirmAnalysis: () => Promise<void>;
  submitAnalysis: () => Promise<void>;
  backToForm: () => void;
  reset: () => void;
  cancelAnalysis: () => void;
}

export function useAnalyzer(options: UseAnalyzerOptions): UseAnalyzerReturn {
  const {
    apiEndpoint,
    apiKey,
    timeout = 120000,
    initialUsers = '',
    initialTasks = '',
    initialFormat = '',
    onAnalysisStart,
    onAnalysisComplete,
    onAnalysisError,
  } = options;

  const [state, dispatch] = useReducer(analyzerReducer, {
    ...initialState,
    users: initialUsers,
    tasks: initialTasks,
    format: initialFormat,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const setFiles = useCallback((files: File[]) => {
    dispatch({ type: 'SET_FILES', payload: files });
  }, []);

  const setFile = useCallback((file: File | null) => {
    dispatch({ type: 'SET_FILE', payload: file });
  }, []);

  const setUsers = useCallback((value: string) => {
    dispatch({ type: 'SET_USERS', payload: value });
  }, []);

  const setExpertise = useCallback((value: string) => {
    dispatch({ type: 'SET_EXPERTISE', payload: value });
  }, []);

  const setTasks = useCallback((value: string) => {
    dispatch({ type: 'SET_TASKS', payload: value });
  }, []);

  const setFormat = useCallback((value: string) => {
    dispatch({ type: 'SET_FORMAT', payload: value });
  }, []);

  const setContentType = useCallback((value: ContentType) => {
    dispatch({ type: 'SET_CONTENT_TYPE', payload: value });
  }, []);

  const requestEstimate = useCallback(async () => {
    if (state.files.length === 0) {
      dispatch({ type: 'ESTIMATION_ERROR', payload: 'No files selected' });
      return;
    }

    dispatch({ type: 'START_ESTIMATION' });

    try {
      const estimate = await getEstimate({
        apiEndpoint,
        files: state.files,
      });
      dispatch({ type: 'ESTIMATION_SUCCESS', payload: estimate });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Estimation failed';
      dispatch({ type: 'ESTIMATION_ERROR', payload: errorMessage });
    }
  }, [state.files, apiEndpoint]);

  const runAnalysis = useCallback(async () => {
    if (state.files.length === 0) {
      dispatch({ type: 'ANALYSIS_ERROR', payload: 'No files selected' });
      return;
    }

    const context: UserContext = {
      users: state.users,
      expertise: state.expertise,
      tasks: state.tasks,
      format: state.format,
      contentType: state.contentType,
    };

    abortControllerRef.current = new AbortController();

    dispatch({ type: 'START_ANALYSIS' });
    onAnalysisStart?.();

    try {
      let result: AnalysisResponse;

      // Choose endpoint based on input type
      if (state.inputType === 'video') {
        result = await analyzeVideo({
          apiEndpoint,
          apiKey,
          video: state.files[0],
          context,
          timeout: 900000, // 15 minutes for video
          signal: abortControllerRef.current.signal,
        });
      } else if (state.inputType === 'multi_image') {
        result = await analyzeMultiImage({
          apiEndpoint,
          apiKey,
          files: state.files,
          context,
          timeout: state.files.length * 120000, // 2 min per image
          signal: abortControllerRef.current.signal,
        });
      } else {
        result = await analyzeImage({
          apiEndpoint,
          apiKey,
          file: state.files[0],
          context,
          timeout,
          signal: abortControllerRef.current.signal,
        });
      }

      dispatch({ type: 'ANALYSIS_SUCCESS', payload: result });
      onAnalysisComplete?.(result);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed';

      if (error instanceof Error && error.name === 'AbortError') {
        dispatch({ type: 'RESET' });
        return;
      }

      dispatch({ type: 'ANALYSIS_ERROR', payload: errorMessage });
      onAnalysisError?.(error instanceof Error ? error : new Error(errorMessage));
    } finally {
      abortControllerRef.current = null;
    }
  }, [
    state.files,
    state.inputType,
    state.users,
    state.tasks,
    state.format,
    state.contentType,
    apiEndpoint,
    apiKey,
    timeout,
    onAnalysisStart,
    onAnalysisComplete,
    onAnalysisError,
  ]);

  const confirmAnalysis = useCallback(async () => {
    await runAnalysis();
  }, [runAnalysis]);

  const submitAnalysis = useCallback(async () => {
    // For single images, go directly to analysis
    // For multi-file/video, show estimate first
    if (state.inputType === 'single_image') {
      await runAnalysis();
    } else {
      await requestEstimate();
    }
  }, [state.inputType, runAnalysis, requestEstimate]);

  const backToForm = useCallback(() => {
    dispatch({ type: 'BACK_TO_FORM' });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  const cancelAnalysis = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    dispatch({ type: 'RESET' });
  }, []);

  return {
    state,
    setFiles,
    setFile,
    setUsers,
    setExpertise,
    setTasks,
    setFormat,
    setContentType,
    requestEstimate,
    confirmAnalysis,
    submitAnalysis,
    backToForm,
    reset,
    cancelAnalysis,
  };
}

export default useAnalyzer;
