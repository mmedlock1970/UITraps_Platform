// Reads the signed-in user's analysis usage for the upper-right counter.
// Fail-soft: returns null on any error so the UI simply hides the counter.

export interface UserUsage {
  subscription_status: string;
  monthly_limit: number;
  monthly_used: number;
  monthly_remaining: number;
  bonus_tokens: number;
}

export async function getUserUsage(opts: {
  apiEndpoint: string;
  token: string;
}): Promise<UserUsage | null> {
  try {
    const res = await fetch(`${opts.apiEndpoint}/api/user/usage`, {
      headers: { Authorization: `Bearer ${opts.token}` },
      cache: 'no-store',  // always read the live count, never a cached response
    });
    if (!res.ok) return null;
    const data = await res.json();
    if (!data || data.success === false) return null;
    return data as UserUsage;
  } catch {
    return null;
  }
}
