/**
 * Authentication hook for JWT token management.
 *
 * Supports two modes:
 * - 'standalone': Token provided directly as a prop (for dev/testing)
 * - 'wordpress': Token fetched from WordPress AJAX endpoint
 */

import { useState, useEffect, useCallback } from 'react';
import { AuthState } from '../api/types';

interface UseAuthOptions {
  mode: 'standalone' | 'wordpress';
  /** JWT token (standalone mode) */
  token?: string;
  /** WordPress AJAX URL (wordpress mode) */
  ajaxUrl?: string;
  /** WordPress nonce (wordpress mode) */
  nonce?: string;
}

export function useAuth(options: UseAuthOptions): AuthState & {
  refreshToken: () => Promise<void>;
  setToken: (token: string) => void;
} {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    token: null,
    userId: null,
    hasSubscription: false,
    isLoading: options.mode === 'wordpress',
    error: null,
  });

  // Standalone mode: use provided token directly
  useEffect(() => {
    if (options.mode === 'standalone' && options.token) {
      try {
        // Decode JWT payload (no verification - that's server-side)
        const parts = options.token.split('.');
        if (parts.length === 3) {
          const payload = JSON.parse(atob(parts[1]));
          setState({
            isAuthenticated: true,
            token: options.token,
            userId: payload.userId || null,
            hasSubscription: payload.hasActiveSubscription || false,
            isLoading: false,
            error: null,
          });
        }
      } catch {
        setState(prev => ({
          ...prev,
          isAuthenticated: true,
          token: options.token!,
          isLoading: false,
        }));
      }
    }
  }, [options.mode, options.token]);

  // WordPress mode: fetch token from AJAX endpoint
  const fetchWordPressToken = useCallback(async () => {
    if (options.mode !== 'wordpress' || !options.ajaxUrl) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(options.ajaxUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          action: 'traps_ai_get_token',
          nonce: options.nonce || '',
        }),
      });

      const data = await response.json();

      if (data.success && data.data?.token) {
        const payload = JSON.parse(atob(data.data.token.split('.')[1]));
        setState({
          isAuthenticated: true,
          token: data.data.token,
          userId: payload.userId || null,
          hasSubscription: payload.hasActiveSubscription || false,
          isLoading: false,
          error: null,
        });
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: data.data?.message || 'Authentication failed',
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Authentication failed',
      }));
    }
  }, [options.mode, options.ajaxUrl, options.nonce]);

  useEffect(() => {
    if (options.mode === 'wordpress') {
      fetchWordPressToken();
    }
  }, [fetchWordPressToken]);

  const setToken = useCallback((token: string) => {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        setState({
          isAuthenticated: true,
          token,
          userId: payload.userId || null,
          hasSubscription: payload.hasActiveSubscription || false,
          isLoading: false,
          error: null,
        });
      }
    } catch {
      setState(prev => ({
        ...prev,
        isAuthenticated: true,
        token,
        isLoading: false,
      }));
    }
  }, []);

  return {
    ...state,
    refreshToken: fetchWordPressToken,
    setToken,
  };
}
