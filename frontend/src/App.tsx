/**
 * UITraps Unified Platform - Main Application
 *
 * Single-page app with a conversation panel and unified input.
 * Routes to chat (RAG) or analysis based on user input.
 * Supports centered welcome layout, analysis progress, and full-page reports.
 */

import React, { useState, useCallback } from 'react';
import { useAuth } from './hooks/useAuth';
import { useUnifiedInput } from './hooks/useUnifiedInput';
import { ConversationPanel } from './components/ConversationPanel';
import { UnifiedInput } from './components/UnifiedInput';
import { EstimatePreview } from './components/EstimatePreview';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ReportViewer } from './components/ReportViewer';
import { PastAnalyses } from './components/PastAnalyses';
import { saveAnalysis, getAnalysisHistory, StoredAnalysis } from './services/analysisHistory';
import { ReportStatistics, UsageInfo, UnifiedAskResponse } from './api/types';
import './styles/variables.css';
import styles from './App.module.css';

// Default API endpoint for development
const DEFAULT_API_ENDPOINT = 'http://localhost:8000';

type AppView = 'chat' | 'report' | 'history';

interface ActiveReport {
  html: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
}

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [apiEndpoint] = useState(DEFAULT_API_ENDPOINT);
  const [view, setView] = useState<AppView>('chat');
  const [activeReport, setActiveReport] = useState<ActiveReport | null>(null);

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

  const handleAnalysisComplete = useCallback((result: UnifiedAskResponse, fileNames: string[]) => {
    if (result.report_html) {
      const report: ActiveReport = {
        html: result.report_html,
        statistics: result.statistics,
        usage: result.usage,
      };
      setActiveReport(report);
      setView('report');

      // Save to history
      saveAnalysis({
        timestamp: new Date().toISOString(),
        fileNames,
        statistics: result.statistics,
        html: result.report_html,
      });
    }
  }, []);

  const unified = useUnifiedInput({
    apiEndpoint,
    token: effectiveToken,
    onAnalysisComplete: handleAnalysisComplete,
  });

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  const handleViewHistoryReport = useCallback((analysis: StoredAnalysis) => {
    setActiveReport({
      html: analysis.html,
      statistics: analysis.statistics,
    });
    setView('report');
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

  // ── Report view ──
  if (view === 'report' && activeReport) {
    return (
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>
            UI<span className={styles.logoAccent}>Traps</span>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.headerButton} onClick={() => setView('chat')}>
              Back to Chat
            </button>
            <button className={styles.headerButton} onClick={toggleTheme}>
              {theme === 'light' ? 'Dark' : 'Light'}
            </button>
          </div>
        </header>
        <div className={styles.reportContainer}>
          <ReportViewer
            html={activeReport.html}
            statistics={activeReport.statistics}
            showStatistics={true}
            showUsageInfo={false}
            onNewAnalysis={() => {
              setView('chat');
              setActiveReport(null);
            }}
          />
        </div>
      </div>
    );
  }

  // ── History view ──
  if (view === 'history') {
    return (
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>
            UI<span className={styles.logoAccent}>Traps</span>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.headerButton} onClick={() => setView('chat')}>
              Back to Chat
            </button>
            <button className={styles.headerButton} onClick={toggleTheme}>
              {theme === 'light' ? 'Dark' : 'Light'}
            </button>
          </div>
        </header>
        <PastAnalyses
          onViewReport={handleViewHistoryReport}
          onClose={() => setView('chat')}
        />
      </div>
    );
  }

  // ── Estimate preview overlay ──
  if (unified.analysisPhase === 'previewing' && unified.estimate) {
    return (
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>
            UI<span className={styles.logoAccent}>Traps</span>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.headerButton} onClick={unified.cancelAnalysis}>
              Cancel
            </button>
          </div>
        </header>
        <div className={styles.overlayContainer}>
          <EstimatePreview
            estimate={unified.estimate}
            onConfirm={unified.confirmAnalysis}
            onBack={unified.cancelAnalysis}
          />
        </div>
      </div>
    );
  }

  // ── Analysis in progress ──
  if (unified.analysisPhase === 'analyzing') {
    return (
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>
            UI<span className={styles.logoAccent}>Traps</span>
          </div>
        </header>
        <div className={styles.overlayContainer}>
          <AnalysisProgress
            elapsedTime={unified.elapsedTime}
            onCancel={unified.cancelAnalysis}
            inputType={unified.files.length > 1 ? 'multi_image' : 'single_image'}
            fileCount={unified.files.length}
            estimatedTime={unified.estimate?.time_estimate}
          />
        </div>
      </div>
    );
  }

  // ── Main chat view ──
  const isEmpty = unified.messages.length === 0 && !unified.isLoading;

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
          {getAnalysisHistory().length > 0 && (
            <button className={styles.headerButton} onClick={() => setView('history')}>
              Past Analyses
            </button>
          )}
          <button className={styles.headerButton} onClick={toggleTheme}>
            {theme === 'light' ? 'Dark' : 'Light'}
          </button>
        </div>
      </header>

      {isEmpty ? (
        <div className={styles.centeredLayout}>
          <div className={styles.welcomeTitle}>
            UI<span className={styles.logoAccent}>Traps</span> Assistant
          </div>
          <div className={styles.welcomeSubtitle}>
            Ask about UI design traps and best practices,
            or drop screenshots for a full trap analysis.
          </div>
          <UnifiedInput
            centered
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
      ) : (
        <>
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
        </>
      )}
    </div>
  );
};

export default App;
