/**
 * Unified input orchestrator hook.
 *
 * Composes useChat and useAnalyzer to provide a single submit() function
 * that auto-routes based on what the user provides:
 * - Text only → chat
 * - Files + context → analysis
 * - Files + question → hybrid
 */

import { useState, useCallback, useMemo } from 'react';
import { ChatMessage, ContentType, UserContext } from '../api/types';
import { useChat } from './useChat';
import { unifiedAsk } from '../api/client';

interface UseUnifiedInputOptions {
  apiEndpoint: string;
  token: string;
}

type DetectedMode = 'chat' | 'analysis' | 'hybrid' | 'idle';

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
  if (hasFiles && !hasText && !hasContext) return 'analysis'; // Will prompt for context
  return 'chat';
}

export function useUnifiedInput(options: UseUnifiedInputOptions): UseUnifiedInputReturn {
  const { apiEndpoint, token } = options;

  // Input state
  const [inputText, setInputText] = useState('');
  const [files, setFiles] = useState<File[]>([]);

  // Context fields
  const [users, setUsers] = useState('');
  const [tasks, setTasks] = useState('');
  const [format, setFormat] = useState('');
  const [contentType, setContentType] = useState<ContentType>('website');
  const [contextExpanded, setContextExpanded] = useState(false);

  // Loading state for unified requests
  const [isUnifiedLoading, setIsUnifiedLoading] = useState(false);

  // Chat hook for pure chat messages
  const chat = useChat({ apiEndpoint, token });

  // Mode detection
  const detectedMode = useMemo(
    () => detectMode(inputText, files, users, tasks, format),
    [inputText, files, users, tasks, format],
  );

  const submit = useCallback(async () => {
    if (detectedMode === 'idle' || !token) return;

    if (detectedMode === 'chat') {
      // Pure chat — delegate to useChat
      const text = inputText.trim();
      setInputText('');
      await chat.sendMessage(text);
      return;
    }

    // Analysis or hybrid — use unified endpoint
    setIsUnifiedLoading(true);

    // Add a placeholder user message into the conversation via chat hook
    chat.addAnalysisMessage('', undefined); // placeholder, we'll replace with real results

    const context: UserContext | undefined = (users && tasks && format) ? {
      users,
      tasks,
      format,
      contentType,
    } : undefined;

    const conversationHistory = chat.messages
      .filter(m => m.role === 'user' || (m.role === 'assistant' && !m.reportHtml))
      .slice(-10)
      .map(m => ({ role: m.role, content: m.content }));

    try {
      const result = await unifiedAsk({
        apiEndpoint,
        token,
        message: inputText.trim() || undefined,
        files,
        context,
        conversationHistory: JSON.stringify(conversationHistory),
      });

      // Clear inputs after successful submission
      setInputText('');
      setFiles([]);

      if (result.mode === 'analysis' || result.mode === 'hybrid') {
        // Remove placeholder and add real messages
        if (result.report_html) {
          chat.addAnalysisMessage(
            result.report_html,
            result.statistics as Record<string, unknown> | undefined,
          );
        }
        if (result.response) {
          // Hybrid: also got a chat response
          // Already handled by addAnalysisMessage for report,
          // add chat response separately
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Request failed';
      // Show error in conversation
      chat.addAnalysisMessage(`<p>Error: ${msg}</p>`, undefined);
    } finally {
      setIsUnifiedLoading(false);
    }
  }, [detectedMode, inputText, files, users, tasks, format, contentType, token, apiEndpoint, chat]);

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
    messages: chat.messages,
    isLoading: chat.isLoading || isUnifiedLoading,
    error: chat.error,
    submit,
    clearHistory: chat.clearHistory,
  };
}
