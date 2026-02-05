/**
 * Chat hook for RAG conversation management.
 *
 * Manages conversation history, sends messages via API,
 * and maintains the message list state.
 */

import { useState, useCallback, useRef } from 'react';
import { ChatMessage, MessageMode } from '../api/types';
import { sendChatMessage } from '../api/client';

interface UseChatOptions {
  apiEndpoint: string;
  token: string;
  /** Max messages to keep in conversation history sent to API (default: 10) */
  maxHistory?: number;
}

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  addAnalysisMessage: (reportHtml: string, statistics?: Record<string, unknown>) => void;
  clearHistory: () => void;
}

let messageIdCounter = 0;
function generateId(): string {
  return `msg-${Date.now()}-${++messageIdCounter}`;
}

export function useChat(options: UseChatOptions): UseChatReturn {
  const { apiEndpoint, token, maxHistory = 10 } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || !token) return;

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: message,
      mode: 'chat',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Build conversation history for API (last N messages)
    const history = messages
      .filter(m => m.role === 'user' || (m.role === 'assistant' && !m.reportHtml))
      .slice(-maxHistory)
      .map(m => ({ role: m.role, content: m.content }));

    // Abort any in-flight request
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      const response = await sendChatMessage({
        apiEndpoint,
        token,
        message,
        conversationHistory: history,
        signal: abortRef.current.signal,
      });

      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.response,
        mode: (response.mode as MessageMode) || 'chat',
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);

      // Add error as assistant message so it's visible in chat
      const errorMsg: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}`,
        mode: 'chat',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint, token, messages, maxHistory]);

  const addAnalysisMessage = useCallback((
    reportHtml: string,
    statistics?: Record<string, unknown>,
  ) => {
    const analysisMsg: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: 'Analysis complete. Here are the results:',
      mode: 'analysis',
      reportHtml,
      statistics: statistics as ChatMessage['statistics'],
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, analysisMsg]);
  }, []);

  const clearHistory = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    addAnalysisMessage,
    clearHistory,
  };
}
