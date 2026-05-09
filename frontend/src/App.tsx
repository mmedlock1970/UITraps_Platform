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
import { useElapsedTime } from './hooks/useElapsedTime';
import { ConversationPanel } from './components/ConversationPanel';
import { UnifiedInput } from './components/UnifiedInput';
import { EstimatePreview } from './components/EstimatePreview';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ReportViewer } from './components/ReportViewer';
import { PastAnalyses } from './components/PastAnalyses';
import { TaskCaptureScreen, CapturedStep } from './components/TaskCaptureScreen';
import { saveAnalysis, getAnalysisHistory, StoredAnalysis } from './services/analysisHistory';
import { ReportStatistics, UsageInfo, UnifiedAskResponse, TimeEstimate, ContentType, isFigmaEstimate, isUrlEstimate, isFileEstimate, UnifiedEstimate } from './api/types';
import { unifiedAsk } from './api/client';
import { ChatPanel } from './components/ChatPanel';
import './styles/variables.css';
import styles from './App.module.css';
import cardsImage from './assets/cards.png';

/** Estimate running cost based on screenshot count (rough calculation) */
function estimateRunningCost(count: number): string {
  if (count === 0) return '';
  const cost = (count * 0.03).toFixed(2);
  const mins = count <= 5 ? '~1 min' : count <= 10 ? '~2 min' : '~3-4 min';
  return `${count} screenshot${count > 1 ? 's' : ''} — est. $${cost}, ${mins}`;
}

// Default API endpoint for development
const DEFAULT_API_ENDPOINT = 'http://localhost:8000';

/** Helper to normalize time estimates from different sources */
function normalizeTimeEstimate(estimate: UnifiedEstimate | null): TimeEstimate | undefined {
  if (!estimate) return undefined;

  if (isFileEstimate(estimate)) {
    return estimate.time_estimate;
  }

  if (isFigmaEstimate(estimate) || isUrlEstimate(estimate)) {
    const { min_seconds, max_seconds, description } = estimate.time_estimate;
    return {
      min_seconds,
      max_seconds,
      min_formatted: description.split('-')[0]?.trim() || `${Math.round(min_seconds / 60)} min`,
      max_formatted: description.split('-')[1]?.trim() || `${Math.round(max_seconds / 60)} min`,
    };
  }

  return undefined;
}

type AppView = 'chat' | 'report' | 'history' | 'task-capture';

interface ActiveReport {
  html: string;
  markdown?: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  originalFiles?: File[];
  originalContext?: { users: string; tasks: string; format: string; contentType: ContentType };
}

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [apiEndpoint] = useState(DEFAULT_API_ENDPOINT);
  const [view, setView] = useState<AppView>('chat');
  const [activeReport, setActiveReport] = useState<ActiveReport | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [isRerunning, setIsRerunning] = useState(false);
  const rerunElapsed = useElapsedTime();

  // Task capture state
  const [taskName, setTaskName] = useState('');
  const [capturedSteps, setCapturedSteps] = useState<CapturedStep[]>([]);

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

  const handleAnalysisComplete = useCallback((result: UnifiedAskResponse, fileNames: string[], files?: File[], context?: { users: string; tasks: string; format: string; contentType: ContentType }) => {
    if (result.report_html) {
      const report: ActiveReport = {
        html: result.report_html,
        markdown: result.report_markdown,
        statistics: result.statistics,
        usage: result.usage,
        originalFiles: files,
        originalContext: context,
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

  const handleRerunAnalysis = useCallback(async (chatMessages: Array<{ role: string; content: string }>) => {
    if (!activeReport?.originalFiles?.length || !activeReport?.originalContext) return;

    const chatContext = chatMessages
      .map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`)
      .join('\n\n');

    setIsRerunning(true);
    rerunElapsed.start();

    try {
      const { users, tasks, format, contentType } = activeReport.originalContext;
      const imageTimeout = Math.min(180000 + activeReport.originalFiles.length * 120000, 1800000);

      const result = await unifiedAsk({
        apiEndpoint,
        token: effectiveToken,
        files: activeReport.originalFiles,
        context: { users, tasks, format, contentType, expertise: '' },
        chatContext,
        timeout: imageTimeout,
      });

      rerunElapsed.stop();

      if (result.report_html) {
        setActiveReport(prev => prev ? {
          ...prev,
          html: result.report_html!,
          markdown: result.report_markdown,
          statistics: result.statistics,
        } : prev);

        saveAnalysis({
          timestamp: new Date().toISOString(),
          fileNames: activeReport.originalFiles.map(f => f.name),
          statistics: result.statistics,
          html: result.report_html,
        });
      }
    } catch (err) {
      rerunElapsed.stop();
      console.error('Re-run analysis failed:', err);
    } finally {
      setIsRerunning(false);
      rerunElapsed.reset();
    }
  }, [activeReport, apiEndpoint, effectiveToken, rerunElapsed]);

  const handleStartTaskCapture = useCallback((initialTaskName: string) => {
    setTaskName(initialTaskName);
    setCapturedSteps([]);
    setView('task-capture');
  }, []);

  const unified = useUnifiedInput({
    apiEndpoint,
    token: effectiveToken,
    onAnalysisComplete: handleAnalysisComplete,
    onStartTaskCapture: handleStartTaskCapture,
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

  // Task capture handlers
  const handleAddStep = useCallback((step: CapturedStep) => {
    setCapturedSteps(prev => [...prev, step]);
  }, []);

  const handleDeleteStep = useCallback((id: string) => {
    setCapturedSteps(prev => {
      const filtered = prev.filter(s => s.id !== id);
      return filtered.map((s, i) => ({ ...s, stepNumber: i + 1 }));
    });
  }, []);

  const handleReorderSteps = useCallback((steps: CapturedStep[]) => {
    setCapturedSteps(steps);
  }, []);

  const handleFinishTask = useCallback(async () => {
    if (capturedSteps.length === 0) return;

    // Convert base64 data URLs back to File objects for the analysis pipeline
    const files = await Promise.all(capturedSteps.map(async (step, i) => {
      const res = await fetch(step.imageData);
      const blob = await res.blob();
      return new File([blob], `step-${i + 1}.jpg`, { type: 'image/jpeg' });
    }));

    // Pre-fill the task as context, inject files into unified input, then return to chat
    unified.setTasks(taskName);
    unified.setFiles(files);
    setView('chat');
    unified.notifyTaskCaptureComplete(capturedSteps.length);
  }, [capturedSteps, taskName, unified]);

  const handleCancelTaskCapture = useCallback(() => {
    setCapturedSteps([]);
    setTaskName('');
    setView('chat');
  }, []);

  // Auth gate: show token input if not authenticated
  if (!auth.isAuthenticated && !devMode) {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <div className={styles.authPrompt}>
          <div className={styles.authTitle}>
            UI Traps <span className={styles.logoAccent}>Helper</span>
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
      </div>
    );
  }

  // ── Task capture view ──
  if (view === 'task-capture') {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <TaskCaptureScreen
            taskName={taskName}
            onTaskNameChange={setTaskName}
            steps={capturedSteps}
            onAddStep={handleAddStep}
            onDeleteStep={handleDeleteStep}
            onReorderSteps={handleReorderSteps}
            onFinish={handleFinishTask}
            onCancel={handleCancelTaskCapture}
            runningCostEstimate={estimateRunningCost(capturedSteps.length)}
          />
        </div>
      </div>
    );
  }

  // ── Report view ──
  if (view === 'report' && activeReport) {
    if (isRerunning) {
      return (
        <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
          <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
            <header className={styles.header}>
              <div className={styles.logo}>
                UI Traps <span className={styles.logoAccent}>Helper</span>
              </div>
            </header>
            <div className={styles.overlayContainer}>
              <AnalysisProgress
                elapsedTime={rerunElapsed.elapsedTime}
                onCancel={() => { setIsRerunning(false); rerunElapsed.reset(); }}
                inputType="multi_image"
                fileCount={activeReport.originalFiles?.length ?? 1}
              />
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme} style={{ height: '100vh', overflow: 'hidden' }}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme} style={{ height: '100vh', overflow: 'hidden' }}>
          <header className={styles.header}>
            <div className={styles.logo}>
              UI Traps <span className={styles.logoAccent}>Helper</span>
            </div>
            <div className={styles.headerActions}>
              <button
                className={chatOpen ? styles.headerButtonActive : styles.headerButton}
                onClick={() => setChatOpen(o => !o)}
              >
                Chat about Results
              </button>
              <button className={styles.headerButton} onClick={() => setView('chat')}>
                Back to Chat
              </button>
              <button className={styles.headerButton} onClick={toggleTheme}>
                {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
              </button>
            </div>
          </header>
          <div className={styles.reportWithChat}>
            <div className={styles.reportArea}>
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
            {chatOpen && (
              <ChatPanel
                apiEndpoint={apiEndpoint}
                apiKey={effectiveToken}
                reportMarkdown={activeReport.markdown || null}
                canRerun={!!activeReport.originalFiles?.length && !!activeReport.originalContext}
                onRerunAnalysis={handleRerunAnalysis}
              />
            )}
          </div>
        </div>
      </div>
    );
  }

  // ── History view ──
  if (view === 'history') {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <header className={styles.header}>
            <div className={styles.logo}>
              UI Traps <span className={styles.logoAccent}>Helper</span>
            </div>
            <div className={styles.headerActions}>
              <button className={styles.headerButton} onClick={() => setView('chat')}>
                Back to Chat
              </button>
              <button className={styles.headerButton} onClick={toggleTheme}>
                {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
              </button>
            </div>
          </header>
          <PastAnalyses
            onViewReport={handleViewHistoryReport}
            onClose={() => setView('chat')}
          />
        </div>
      </div>
    );
  }

  // ── Estimate preview overlay ──
  if (unified.analysisPhase === 'previewing' && unified.estimate) {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <header className={styles.header}>
            <div className={styles.logo}>
              UI Traps <span className={styles.logoAccent}>Helper</span>
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
      </div>
    );
  }

  // ── Analysis in progress ──
  if (unified.analysisPhase === 'analyzing') {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <header className={styles.header}>
            <div className={styles.logo}>
              UI Traps <span className={styles.logoAccent}>Helper</span>
            </div>
          </header>
          <div className={styles.overlayContainer}>
            <AnalysisProgress
              elapsedTime={unified.elapsedTime}
              onCancel={unified.cancelAnalysis}
              inputType={unified.detectedUrl ? (unified.detectedMode === 'figma' ? 'figma' : 'url') : (unified.files.length > 1 ? 'multi_image' : 'single_image')}
              fileCount={unified.files.length}
              estimatedTime={normalizeTimeEstimate(unified.estimate)}
            />
          </div>
        </div>
      </div>
    );
  }

  // ── Main chat view ──
  const isEmpty = unified.messages.length === 0 && !unified.isLoading;

  return (
    <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>
            UI Traps <span className={styles.logoAccent}>Helper</span>
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
              {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
            </button>
          </div>
        </header>

        {isEmpty ? (
          <div className={styles.centeredLayout}>
            <img
              src={cardsImage}
              alt="UI Tenets & Traps Cards"
              className={styles.welcomeImage}
            />
            <div className={styles.welcomeTitle}>
              UI Traps <span className={styles.logoAccent}>Helper</span>
            </div>
            <div className={styles.welcomeSubtitle}>
              <ul>
                <li>Ask any question about UI Tenets & Traps</li>
                <li>Describe an interface issue, it will identify Traps for you</li>
                <li>Analyze screenshots, Figma designs, or websites</li>
                <li>Get detailed reports with findings and recommendations</li>
              </ul>
            </div>
            <UnifiedInput
              centered
              placeholder=""
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
              onWidgetChoice={unified.handleWidgetChoice}
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
    </div>
  );
};

export default App;
