import { AnalysisResponse, UserContext, EstimateResponse, CapabilitiesResponse, ChatApiResponse, UnifiedAskResponse } from './types';

export interface AnalyzeOptions {
  apiEndpoint: string;
  apiKey: string;
  file: File;
  context: UserContext;
  timeout?: number;
  signal?: AbortSignal;
}

export interface AnalyzeMultiOptions {
  apiEndpoint: string;
  apiKey: string;
  files: File[];
  context: UserContext;
  timeout?: number;
  signal?: AbortSignal;
}

export interface AnalyzeVideoOptions {
  apiEndpoint: string;
  apiKey: string;
  video: File;
  context: UserContext;
  maxFrames?: number;
  timeout?: number;
  signal?: AbortSignal;
}

export interface EstimateOptions {
  apiEndpoint: string;
  files: File[];
  timeout?: number;
}

// Helper to combine multiple AbortSignals
function anySignal(signals: AbortSignal[]): AbortSignal {
  const controller = new AbortController();

  for (const signal of signals) {
    if (signal.aborted) {
      controller.abort(signal.reason);
      return controller.signal;
    }

    signal.addEventListener('abort', () => {
      controller.abort(signal.reason);
    }, { once: true });
  }

  return controller.signal;
}

export async function analyzeImage(options: AnalyzeOptions): Promise<AnalysisResponse> {
  const { apiEndpoint, apiKey, file, context, timeout = 120000, signal } = options;

  const formData = new FormData();
  formData.append('image', file);
  formData.append('users', context.users);
  formData.append('tasks', context.tasks);
  formData.append('format', context.format);
  formData.append('content_type', context.contentType || 'website');
  formData.append('api_key', apiKey);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const combinedSignal = signal
    ? anySignal([signal, controller.signal])
    : controller.signal;

  try {
    const response = await fetch(`${apiEndpoint}/analyze`, {
      method: 'POST',
      body: formData,
      signal: combinedSignal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}: Analysis failed`);
    }

    if (!data.success) {
      throw new Error(data.error || 'Analysis failed');
    }

    return data as AnalysisResponse;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Analysis timed out. Please try again.');
      }
      throw error;
    }

    throw new Error('Unknown error occurred');
  }
}

export async function analyzeMultiImage(options: AnalyzeMultiOptions): Promise<AnalysisResponse> {
  const { apiEndpoint, apiKey, files, context, timeout = 600000, signal } = options;

  const formData = new FormData();
  files.forEach((file) => {
    formData.append('images', file);
  });
  formData.append('users', context.users);
  formData.append('tasks', context.tasks);
  formData.append('format', context.format);
  formData.append('content_type', context.contentType || 'website');
  formData.append('api_key', apiKey);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const combinedSignal = signal
    ? anySignal([signal, controller.signal])
    : controller.signal;

  try {
    const response = await fetch(`${apiEndpoint}/analyze-multi`, {
      method: 'POST',
      body: formData,
      signal: combinedSignal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}: Analysis failed`);
    }

    if (!data.success) {
      throw new Error(data.error || 'Analysis failed');
    }

    return data as AnalysisResponse;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Analysis timed out. Please try again.');
      }
      throw error;
    }

    throw new Error('Unknown error occurred');
  }
}

export async function analyzeVideo(options: AnalyzeVideoOptions): Promise<AnalysisResponse> {
  const { apiEndpoint, apiKey, video, context, maxFrames = 15, timeout = 900000, signal } = options;

  const formData = new FormData();
  formData.append('video', video);
  formData.append('users', context.users);
  formData.append('tasks', context.tasks);
  formData.append('format', context.format);
  formData.append('content_type', context.contentType || 'website');
  formData.append('api_key', apiKey);
  formData.append('max_frames', maxFrames.toString());

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const combinedSignal = signal
    ? anySignal([signal, controller.signal])
    : controller.signal;

  try {
    const response = await fetch(`${apiEndpoint}/analyze-video`, {
      method: 'POST',
      body: formData,
      signal: combinedSignal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}: Video analysis failed`);
    }

    if (!data.success) {
      throw new Error(data.error || 'Video analysis failed');
    }

    return data as AnalysisResponse;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Video analysis timed out. Please try again.');
      }
      throw error;
    }

    throw new Error('Unknown error occurred');
  }
}

export async function getEstimate(options: EstimateOptions): Promise<EstimateResponse> {
  const { apiEndpoint, files, timeout = 30000 } = options;

  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${apiEndpoint}/estimate`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || data.detail || `HTTP ${response.status}: Estimation failed`);
    }

    return data as EstimateResponse;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Estimation timed out');
      }
      throw error;
    }

    throw new Error('Unknown error occurred');
  }
}

export async function getCapabilities(apiEndpoint: string): Promise<CapabilitiesResponse> {
  const response = await fetch(`${apiEndpoint}/capabilities`);

  if (!response.ok) {
    throw new Error('Failed to fetch capabilities');
  }

  return response.json();
}

export async function checkUsage(apiEndpoint: string, apiKey: string): Promise<{
  used_this_month: number;
  limit: number;
  remaining: number;
}> {
  const response = await fetch(`${apiEndpoint}/usage?api_key=${encodeURIComponent(apiKey)}`);

  if (!response.ok) {
    throw new Error('Failed to fetch usage information');
  }

  return response.json();
}

export async function checkHealth(apiEndpoint: string): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${apiEndpoint}/health`);

  if (!response.ok) {
    throw new Error('API is not healthy');
  }

  return response.json();
}


// ===========================================================
// Chat & Unified Platform API
// ===========================================================

export interface ChatOptions {
  apiEndpoint: string;
  token: string;
  message: string;
  conversationHistory?: Array<{ role: string; content: string }>;
  signal?: AbortSignal;
  timeout?: number;
}

export async function sendChatMessage(options: ChatOptions): Promise<ChatApiResponse> {
  const { apiEndpoint, token, message, conversationHistory = [], signal, timeout = 60000 } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const combinedSignal = signal
    ? anySignal([signal, controller.signal])
    : controller.signal;

  try {
    const response = await fetch(`${apiEndpoint}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message, conversationHistory }),
      signal: combinedSignal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    return data as ChatApiResponse;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. Please try again.');
      }
      throw error;
    }

    throw new Error('Unknown error occurred');
  }
}

export interface UnifiedAskOptions {
  apiEndpoint: string;
  token: string;
  message?: string;
  files?: File[];
  context?: UserContext;
  conversationHistory?: string;
  signal?: AbortSignal;
  timeout?: number;
}

export async function unifiedAsk(options: UnifiedAskOptions): Promise<UnifiedAskResponse> {
  const { apiEndpoint, token, message, files = [], context,
          conversationHistory, signal, timeout = 120000 } = options;

  const formData = new FormData();
  if (message) formData.append('message', message);
  files.forEach(f => formData.append('files', f));
  if (context) {
    formData.append('users', context.users);
    formData.append('tasks', context.tasks);
    formData.append('format', context.format);
    formData.append('content_type', context.contentType || 'website');
  }
  if (conversationHistory) formData.append('conversation_history', conversationHistory);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const combinedSignal = signal
    ? anySignal([signal, controller.signal])
    : controller.signal;

  try {
    const response = await fetch(`${apiEndpoint}/api/ask`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
      signal: combinedSignal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    return data as UnifiedAskResponse;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. Please try again.');
      }
      throw error;
    }

    throw new Error('Unknown error occurred');
  }
}
