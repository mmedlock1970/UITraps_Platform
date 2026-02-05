/**
 * UITraps Unified Platform - Main Application
 *
 * Single-page app with a conversation panel and unified input.
 * Routes to chat (RAG) or analysis based on user input.
 */

import React, { useState, useCallback } from 'react';
import { useAuth } from './hooks/useAuth';
import { useUnifiedInput } from './hooks/useUnifiedInput';
import { ConversationPanel } from './components/ConversationPanel';
import { UnifiedInput } from './components/UnifiedInput';
import './styles/variables.css';
import styles from './App.module.css';

// Default API endpoint for development
const DEFAULT_API_ENDPOINT = 'http://localhost:8000';

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [apiEndpoint] = useState(DEFAULT_API_ENDPOINT);

  const auth = useAuth({ mode: 'standalone' });

  // Dev mode: allow entering a token manually
  const [tokenInput, setTokenInput] = useState('');

  const handleConnect = useCallback(() => {
    if (tokenInput.trim()) {
      auth.setToken(tokenInput.trim());
    }
  }, [tokenInput, auth]);

  // Skip auth in dev mode — allow usage without token
  const [devMode, setDevMode] = useState(false);
  const effectiveToken = auth.token || (devMode ? 'dev-mode' : '');

  const unified = useUnifiedInput({
    apiEndpoint,
    token: effectiveToken,
  });

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  // Auth gate: show token input if not authenticated
  if (!auth.isAuthenticated && !devMode) {
    return (
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <div className={styles.authPrompt}>
          <div className={styles.authTitle}>
            UI<span className={styles.logoAccent}>Traps</span> Platform
          </div>
          <div className={styles.authSubtitle}>
            Enter your JWT token to connect, or use dev mode for local testing.
          </div>
          <input
            className={styles.tokenInput}
            type="text"
            placeholder="Paste JWT token here..."
            value={tokenInput}
            onChange={e => setTokenInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleConnect()}
          />
          <button className={styles.connectButton} onClick={handleConnect}>
            Connect
          </button>
          <button
            className={styles.headerButton}
            onClick={() => setDevMode(true)}
          >
            Use Dev Mode (no auth)
          </button>
          <div className={styles.devNote}>
            In production, the WordPress plugin provides the JWT token automatically.
            Dev mode lets you test the chat UI without authentication.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
      <header className={styles.header}>
        <div className={styles.logo}>
          UI<span className={styles.logoAccent}>Traps</span>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.headerButton} onClick={() => unified.clearHistory()}>
            New Session
          </button>
          <button className={styles.headerButton} onClick={toggleTheme}>
            {theme === 'light' ? 'Dark' : 'Light'}
          </button>
        </div>
      </header>

      <ConversationPanel
        messages={unified.messages}
        isLoading={unified.isLoading}
      />

      <UnifiedInput
        inputText={unified.inputText}
        onInputTextChange={unified.setInputText}
        files={unified.files}
        onFilesChange={unified.setFiles}
        users={unified.users}
        onUsersChange={unified.setUsers}
        tasks={unified.tasks}
        onTasksChange={unified.setTasks}
        format={unified.format}
        onFormatChange={unified.setFormat}
        contentType={unified.contentType}
        onContentTypeChange={unified.setContentType}
        contextExpanded={unified.contextExpanded}
        onContextExpandedChange={unified.setContextExpanded}
        detectedMode={unified.detectedMode}
        isLoading={unified.isLoading}
        onSubmit={unified.submit}
      />
    </div>
  );
};

export default App;
