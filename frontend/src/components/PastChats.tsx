import React, { useEffect, useState } from 'react';
import styles from './PastChats.module.css';
import { listChats, SavedChatSummary } from '../api/chatApi';

interface PastChatsProps {
  token?: string;
  apiEndpoint?: string;
  onOpenChat?: (sessionId: string) => void;
}

/**
 * "See past chats" — a Claude-style list of the signed-in user's saved Q&A conversations.
 * Each item shows a brief summary title; clicking one re-opens that conversation to continue it.
 */
export const PastChats: React.FC<PastChatsProps> = ({ token, apiEndpoint, onOpenChat }) => {
  const [chats, setChats] = useState<SavedChatSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!token || !apiEndpoint) {
        setLoading(false);
        return;
      }
      const list = await listChats({ apiEndpoint, token });
      if (!cancelled) {
        setChats(list);
        setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, apiEndpoint]);

  return (
    <div className={styles.container}>
      {loading ? (
        <p className={styles.emptyText}>Loading…</p>
      ) : chats.length === 0 ? (
        <div className={styles.empty}>
          <p className={styles.emptyText}>
            Your past chats will appear here once you've asked a question.
          </p>
        </div>
      ) : (
        <ul className={styles.list}>
          {chats.map((c) => (
            <li key={c.session_id}>
              <button
                type="button"
                className={styles.item}
                onClick={() => onOpenChat?.(c.session_id)}
              >
                {c.title || 'Untitled chat'}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PastChats;
