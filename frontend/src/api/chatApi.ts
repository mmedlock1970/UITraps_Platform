// Saved-chat API for "See past chats". JWT-authed with the same token the chat uses.
// All calls fail soft (never throw) so chat/history UX is never blocked by a save issue.

export interface SavedChatSummary {
  session_id: string;
  title: string;
}

export interface SavedChatDetail {
  session_id: string;
  title: string;
  messages: unknown[];
}

export async function saveChat(opts: {
  apiEndpoint: string;
  token: string;
  sessionId: string;
  messages: unknown[];
}): Promise<{ ok: boolean; title?: string }> {
  try {
    const res = await fetch(`${opts.apiEndpoint}/api/chats`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${opts.token}` },
      body: JSON.stringify({ session_id: opts.sessionId, messages: opts.messages }),
    });
    if (!res.ok) return { ok: false };
    return await res.json();
  } catch {
    return { ok: false };
  }
}

export async function listChats(opts: {
  apiEndpoint: string;
  token: string;
}): Promise<SavedChatSummary[]> {
  try {
    const res = await fetch(`${opts.apiEndpoint}/api/chats`, {
      headers: { Authorization: `Bearer ${opts.token}` },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data.chats) ? data.chats : [];
  } catch {
    return [];
  }
}

export async function getChat(opts: {
  apiEndpoint: string;
  token: string;
  sessionId: string;
}): Promise<SavedChatDetail | null> {
  try {
    const res = await fetch(`${opts.apiEndpoint}/api/chats/${encodeURIComponent(opts.sessionId)}`, {
      headers: { Authorization: `Bearer ${opts.token}` },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}
