/**
 * Single chat message component.
 *
 * Renders user messages as right-aligned bubbles and assistant messages
 * as left-aligned bubbles. Analysis results render as full-width cards
 * with embedded HTML report content.
 */

import React from 'react';
import DOMPurify from 'dompurify';
import { ChatMessage as ChatMessageType } from '../api/types';
import styles from './ChatMessage.module.css';

interface ChatMessageProps {
  message: ChatMessageType;
}

const SANITIZE_CONFIG = {
  ALLOWED_TAGS: [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
    'ul', 'ol', 'li', 'strong', 'em', 'a', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'section', 'img',
  ],
  ALLOWED_ATTR: ['class', 'id', 'href', 'target', 'rel', 'style', 'src', 'alt', 'title'],
};

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatMarkdown(text: string): string {
  return text
    .split('\n\n')
    .map(para => {
      let processed = para;
      processed = processed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      processed = processed.replace(/\*(.+?)\*/g, '<em>$1</em>');
      processed = processed.replace(/`(.+?)`/g, '<code>$1</code>');
      processed = processed.replace(
        /(https?:\/\/[^\s)]+)/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>',
      );
      return `<p>${processed}</p>`;
    })
    .join('');
}

export const ChatMessageComponent: React.FC<ChatMessageProps> = React.memo(({ message }) => {
  const { role, content, mode, sources, timestamp, reportHtml } = message;
  const isUser = role === 'user';

  // Analysis result message — render as a card
  if (mode === 'analysis' && reportHtml) {
    const cleanHtml = DOMPurify.sanitize(reportHtml, SANITIZE_CONFIG);

    return (
      <div className={styles.message}>
        <div className={styles.avatar}>AI</div>
        <div className={styles.analysisCard}>
          <div className={styles.analysisHeader}>
            Trap Analysis Results
          </div>
          <div
            className={styles.analysisContent}
            dangerouslySetInnerHTML={{ __html: cleanHtml }}
          />
        </div>
      </div>
    );
  }

  // Standard chat bubble
  const messageClass = `${styles.message} ${isUser ? styles.user : styles.assistant}`;

  return (
    <div className={messageClass}>
      <div className={styles.avatar}>{isUser ? 'U' : 'AI'}</div>
      <div>
        <div
          className={styles.bubble}
          dangerouslySetInnerHTML={{ __html: formatMarkdown(content) }}
        />
        {sources && sources.length > 0 && (
          <div className={styles.sources}>
            <strong>Sources: </strong>
            {sources.map((url, i) => (
              <a key={i} href={url} target="_blank" rel="noopener noreferrer">
                {new URL(url).pathname.replace(/\/$/, '').split('/').pop() || url}
              </a>
            ))}
          </div>
        )}
        <div className={styles.timestamp}>{formatTime(timestamp)}</div>
      </div>
    </div>
  );
});

ChatMessageComponent.displayName = 'ChatMessage';
