import React, { useCallback, useEffect, useRef, useState, KeyboardEvent } from 'react';
import { useReportChat } from '../hooks/useReportChat';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  apiEndpoint: string;
  apiKey: string;
  reportMarkdown: string | null;
  canRerun?: boolean;
  onRerunAnalysis?: (messages: Array<{ role: string; content: string }>) => void;
}


export const ChatPanel: React.FC<ChatPanelProps> = ({ apiEndpoint, apiKey, reportMarkdown, canRerun, onRerunAnalysis }) => {
  const { messages, isLoading, error, sendMessage } = useReportChat({
    apiEndpoint,
    apiKey,
    reportMarkdown,
  });

  const [input, setInput] = useState('');
  const [copied, setCopied] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const atBottomRef = useRef(true);

  const handleMessagesScroll = useCallback(() => {
    const el = messagesRef.current;
    if (!el) return;
    atBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  }, []);

  const handleCopy = useCallback(() => {
    if (messages.length === 0) return;
    const text = messages
      .map(m => `${m.role === 'user' ? 'You' : 'Assistant'}: ${m.content}`)
      .join('\n\n');
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [messages]);

  // Auto-scroll only when the user is already at the bottom
  useEffect(() => {
    if (atBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }, [input]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const msg = input.trim();
    if (!msg || isLoading) return;
    setInput('');
    atBottomRef.current = true;
    await sendMessage(msg);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <svg className={styles.headerIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span className={styles.headerTitle}>Discuss Results</span>
        <button
          type="button"
          className={styles.copyButton}
          onClick={handleCopy}
          disabled={messages.length === 0}
          title="Copy conversation"
        >
          {copied ? (
            <>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Copied!
            </>
          ) : (
            <>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              Copy
            </>
          )}
        </button>
        {canRerun && onRerunAnalysis && (
          <button
            type="button"
            className={styles.rerunButton}
            onClick={() => onRerunAnalysis(messages)}
            disabled={isLoading}
            title="Re-run the analysis using insights from this conversation"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            Re-run Analysis
          </button>
        )}
      </div>

      <div className={styles.messages} ref={messagesRef} onScroll={handleMessagesScroll}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <p>Ask a question about any finding, or re-run analysis after providing any needed clarifications.</p>
            <p className={styles.hint}>Examples: "Why was this flagged as a MEMORY CHALLENGE?" or "That modal is intentional — users requested it."</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.assistantMessage}`}>
            <div className={styles.messageContent}>{msg.content}</div>
          </div>
        ))}

        {isLoading && (
          <div className={`${styles.message} ${styles.assistantMessage}`}>
            <div className={styles.typingDots}>
              <span /><span /><span />
            </div>
          </div>
        )}

        {error && (
          <div className={styles.errorBubble}>{error}</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className={styles.inputArea} onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          className={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question… (Enter to send)"
          rows={1}
          disabled={isLoading || !reportMarkdown}
        />
        <button
          type="submit"
          className={styles.sendButton}
          disabled={isLoading || !input.trim() || !reportMarkdown}
          aria-label="Send"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
