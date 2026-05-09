import { useState, useCallback, useRef, useEffect } from 'react';
import { reportChat } from '../api/client';

export interface ReportChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface UseReportChatOptions {
  apiEndpoint: string;
  apiKey: string;
  reportMarkdown: string | null;
}

export function useReportChat({ apiEndpoint, apiKey, reportMarkdown }: UseReportChatOptions) {
  const [messages, setMessages] = useState<ReportChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Clear conversation when a new report loads
  useEffect(() => {
    setMessages([]);
    setError(null);
  }, [reportMarkdown]);

  const sendMessage = useCallback(async (message: string) => {
    if (!reportMarkdown || !message.trim() || isLoading) return;

    const userMsg: ReportChatMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    abortRef.current = new AbortController();

    try {
      const result = await reportChat({
        apiEndpoint,
        apiKey,
        message,
        reportMarkdown,
        // pass history without the message we just appended
        conversation: messages,
        signal: abortRef.current.signal,
      });

      setMessages(prev => [...prev, { role: 'assistant', content: result.response }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
    } finally {
      setIsLoading(false);
      abortRef.current = null;
    }
  }, [apiEndpoint, apiKey, reportMarkdown, messages, isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
