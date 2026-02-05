/**
 * Scrollable conversation panel that displays all chat messages.
 * Auto-scrolls to bottom on new messages.
 */

import React, { useRef, useEffect } from 'react';
import { ChatMessage } from '../api/types';
import { ChatMessageComponent } from './ChatMessage';
import styles from './ConversationPanel.module.css';

interface ConversationPanelProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export const ConversationPanel: React.FC<ConversationPanelProps> = ({ messages, isLoading }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className={styles.panel}>
        <div className={styles.empty}>
          <div className={styles.emptyTitle}>UITraps Assistant</div>
          <div className={styles.emptySubtitle}>
            Ask a question about UI design traps and best practices,
            or drag and drop screenshots for a full trap analysis.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.panel}>
      {messages.map(msg => (
        <ChatMessageComponent key={msg.id} message={msg} />
      ))}

      {isLoading && (
        <div className={styles.typingIndicator}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 'var(--uitraps-font-size-sm)',
            background: 'var(--uitraps-bg-secondary)',
            color: 'var(--uitraps-text-secondary)',
            border: '1px solid var(--uitraps-border)',
            flexShrink: 0,
          }}>AI</div>
          <div className={styles.typingDots}>
            <span /><span /><span />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
