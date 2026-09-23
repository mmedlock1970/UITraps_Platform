import React from 'react';
import styles from './PastChats.module.css';

interface PastChatsProps {
  // token + apiEndpoint are used in Step 2 to fetch the saved chat list; accepted now so
  // the wiring from App is already in place.
  token?: string;
  apiEndpoint?: string;
  onStartChat?: () => void;
}

/**
 * "See past chats" — a Claude-style list of the user's saved Q&A conversations.
 * Step 1 renders the empty state; Step 2 fetches and lists saved chats (summary title,
 * click to reopen). Chats are saved per signed-in user, forward-only.
 */
export const PastChats: React.FC<PastChatsProps> = ({ onStartChat }) => {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Past chats</h2>
      <div className={styles.empty}>
        <p className={styles.emptyText}>
          Your past chats will appear here once you've asked a question.
        </p>
        {onStartChat && (
          <button type="button" className={styles.startBtn} onClick={onStartChat}>
            Ask a question
          </button>
        )}
      </div>
    </div>
  );
};

export default PastChats;
