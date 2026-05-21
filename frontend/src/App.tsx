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
import { AnalyzerForm, FormSubmitPayload } from './components/AnalyzerForm';
import { ConversationPanel } from './components/ConversationPanel';
import { UnifiedInput } from './components/UnifiedInput';
import { EstimatePreview } from './components/EstimatePreview';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ReportViewer } from './components/ReportViewer';
import { PastAnalyses } from './components/PastAnalyses';
import { TaskCaptureScreen, CapturedStep } from './components/TaskCaptureScreen';
import { saveAnalysis, getAnalysisHistory, StoredAnalysis } from './services/analysisHistory';
import { ReportStatistics, UsageInfo, UnifiedAskResponse, TimeEstimate, UserContext, isFigmaEstimate, isUrlEstimate, isFileEstimate, UnifiedEstimate } from './api/types';
import { unifiedAsk } from './api/client';
import { ChatPanel } from './components/ChatPanel';
import './styles/variables.css';
import styles from './App.module.css';

/** Estimate running cost based on screenshot count (rough calculation) */
function estimateRunningCost(count: number): string {
  if (count === 0) return '';
  const cost = (count * 0.03).toFixed(2);
  const mins = count <= 5 ? '~1 min' : count <= 10 ? '~2 min' : '~3-4 min';
  return `${count} screenshot${count > 1 ? 's' : ''} — est. $${cost}, ${mins}`;
}

// Default API endpoint — reads from env var in production, falls back to localhost for dev
const DEFAULT_API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000';

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

// User group terms we can detect and extract from correction messages
const USER_GROUP_TERMS = [
  'adults', 'adult', 'kids', 'children', 'child', 'seniors', 'elderly',
  'teens', 'teenagers', 'professionals', 'employees', 'students', 'customers',
  'users', 'beginners', 'experts', 'parents', 'patients', 'developers',
  'designers', 'managers', 'executives', 'shoppers', 'subscribers',
];

const CORRECTION_SIGNALS = [
  'meant', 'should have', 'actually', 'oops', 'wrong', 'mistake',
  'correction', 'not ', 'instead', 'scratch that', 'sorry', 'my bad',
];

/**
 * Scans user chat messages for context corrections (e.g. "meant adults not kids")
 * and returns an updated context with the corrected values.
 */
function extractContextCorrections(
  messages: Array<{ role: string; content: string }>,
  original: UserContext
): UserContext {
  const corrected = { ...original };

  for (const msg of messages) {
    if (msg.role !== 'user') continue;
    const lower = msg.content.toLowerCase();

    const isCorrection = CORRECTION_SIGNALS.some(s => lower.includes(s));
    if (!isCorrection) continue;

    // Find all user-group terms mentioned in this message
    const found = USER_GROUP_TERMS.filter(t => lower.includes(t));
    if (found.length === 0) continue;

    const originalLower = corrected.users.toLowerCase();

    // Any term NOT matching the original is a candidate correction.
    // Pick the one that appears earliest (before the "not X" part).
    let bestTerm: string | null = null;
    let bestPos = Infinity;

    for (const term of found) {
      if (originalLower.includes(term)) continue; // this is the old value, skip
      const pos = lower.indexOf(term);
      if (pos !== -1 && pos < bestPos) {
        bestTerm = term;
        bestPos = pos;
      }
    }

    if (bestTerm) {
      corrected.users = bestTerm.charAt(0).toUpperCase() + bestTerm.slice(1);
    }
  }

  return corrected;
}

type AppView = 'form' | 'chat' | 'report' | 'history' | 'task-capture';

interface ActiveReport {
  html: string;
  markdown?: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  originalFiles?: File[];
  originalContext?: UserContext;
  // Dual-report compare mode
  htmlV1?: string;
  htmlV2?: string;
  statisticsV1?: ReportStatistics;
  statisticsV2?: ReportStatistics;
}

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [apiEndpoint] = useState(DEFAULT_API_ENDPOINT);
  const [view, setView] = useState<AppView>('form');
  const [activeReport, setActiveReport] = useState<ActiveReport | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [isRerunning, setIsRerunning] = useState(false);
  const rerunElapsed = useElapsedTime();

  // Form-specific analysis state
  const [formAnalysisPhase, setFormAnalysisPhase] = useState<'idle' | 'analyzing'>('idle');
  const [formFileCount, setFormFileCount] = useState(0);
  const [formError, setFormError] = useState<string | null>(null);
  const formElapsed = useElapsedTime();

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

  // Skip auth in dev mode — default true for local dev (localhost), false in production
  const [devMode, setDevMode] = useState(() =>
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  );
  const effectiveToken = auth.token || (devMode ? 'dev-mode' : '');

  const handleAnalysisComplete = useCallback((result: UnifiedAskResponse, fileNames: string[], files?: File[], context?: UserContext) => {
    // Dual-report (compare mode) — report_html_v1 and report_html_v2 are both present
    const isDualReport = !!(result.report_html_v1 && result.report_html_v2);
    if (isDualReport || result.report_html) {
      const report: ActiveReport = {
        html: result.report_html ?? result.report_html_v2 ?? '',
        markdown: result.report_markdown,
        statistics: isDualReport ? result.statistics_v2 : result.statistics,
        usage: result.usage,
        originalFiles: files,
        originalContext: context,
        htmlV1: result.report_html_v1,
        htmlV2: result.report_html_v2,
        statisticsV1: result.statistics_v1,
        statisticsV2: result.statistics_v2,
      };
      setActiveReport(report);
      setView('report');
      setChatOpen(false);

      // Save to history
      saveAnalysis({
        timestamp: new Date().toISOString(),
        fileNames,
        statistics: isDualReport ? result.statistics_v2 : result.statistics,
        html: (result.report_html ?? result.report_html_v2) || '',
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
      const correctedContext = extractContextCorrections(chatMessages, activeReport.originalContext);
      const imageTimeout = Math.min(180000 + activeReport.originalFiles.length * 120000, 1800000);

      const result = await unifiedAsk({
        apiEndpoint,
        token: effectiveToken,
        files: activeReport.originalFiles,
        context: {
          ...activeReport.originalContext,
          ...correctedContext,
        },
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
          originalContext: correctedContext,
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

  const handleFormSubmit = useCallback(async (payload: FormSubmitPayload) => {
    const { files, url, context } = payload;

    setFormError(null);
    setFormAnalysisPhase('analyzing');
    setFormFileCount(files.length || 1);
    formElapsed.start();

    try {
      const inputFiles = files.length > 0 ? files : [];
      const inputMessage = url && files.length === 0 ? url : undefined;
      const imageTimeout = Math.min(180000 + (files.length || 1) * 120000, 1800000);

      const kbVersionForRequest = context?.kb_version;
      const effectiveTimeout = kbVersionForRequest === 'both'
        ? Math.min(imageTimeout * 2, 3600000)
        : imageTimeout;

      const result = await unifiedAsk({
        apiEndpoint,
        token: effectiveToken,
        message: inputMessage,
        files: inputFiles,
        context,
        kbVersion: kbVersionForRequest,
        timeout: effectiveTimeout,
      });

      formElapsed.stop();

      if (result.report_html || (result.report_html_v1 && result.report_html_v2)) {
        handleAnalysisComplete(
          result,
          files.map(f => f.name),
          files,
          context
        );
      } else if (result.error) {
        setFormError(result.error);
      } else {
        setFormError('Analysis did not return a report. Please try again.');
      }
    } catch (err) {
      formElapsed.stop();
      setFormError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setFormAnalysisPhase('idle');
      formElapsed.reset();
    }
  }, [apiEndpoint, effectiveToken, formElapsed, handleAnalysisComplete]);

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
              <button className={styles.headerButton} onClick={() => setView('form')}>
                New Analysis
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
                isDark={theme === 'dark'}
                htmlV1={activeReport.htmlV1}
                htmlV2={activeReport.htmlV2}
                statisticsV1={activeReport.statisticsV1}
                statisticsV2={activeReport.statisticsV2}
                onNewAnalysis={() => {
                  setView('form');
                  setActiveReport(null);
                }}
              />
            </div>
            <div style={{ display: chatOpen ? undefined : 'none' }}>
              <ChatPanel
                apiEndpoint={apiEndpoint}
                apiKey={effectiveToken}
                reportMarkdown={activeReport.markdown || null}
                canRerun={!!activeReport.originalFiles?.length && !!activeReport.originalContext}
                onRerunAnalysis={handleRerunAnalysis}
              />
            </div>
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
              <button className={styles.headerButton} onClick={() => setView('form')}>
                Back
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

  // ── Form view (default + analysis in progress) ──
  // AnalyzerForm is always mounted here so its local state survives the analyzing phase.
  if (view === 'form') {
    const isAnalyzing = formAnalysisPhase === 'analyzing';
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <header className={styles.header}>
            <div className={styles.logo}>UI Traps <span className={styles.logoAccent}>Helper</span></div>
            {!isAnalyzing && (
              <div className={styles.headerActions}>
                {getAnalysisHistory().length > 0 && (
                  <button className={styles.headerButton} onClick={() => setView('history')}>Past Analyses</button>
                )}
                <button className={styles.headerButton} onClick={toggleTheme}>
                  {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
                </button>
              </div>
            )}
          </header>

          {!isAnalyzing && (
            <div className={styles.tabRow}>
              <button type="button" className={`${styles.tab} ${styles.tabActive}`}>Analyze a design</button>
              <button type="button" className={styles.tab} onClick={() => setView('chat')}>Ask general questions</button>
            </div>
          )}

          {/* Progress overlay — visible during analysis */}
          {isAnalyzing && (
            <div className={styles.overlayContainer}>
              <AnalysisProgress
                elapsedTime={formElapsed.elapsedTime}
                onCancel={() => { setFormAnalysisPhase('idle'); formElapsed.reset(); }}
                inputType={formFileCount > 1 ? 'multi_image' : 'single_image'}
                fileCount={formFileCount}
              />
            </div>
          )}

          {/* Form — always mounted (hidden during analysis) so field values are preserved */}
          <div style={{ display: isAnalyzing ? 'none' : 'flex', flexDirection: 'column', overflowY: 'auto', flex: 1, paddingTop: '24px' }}>
            {formError && (
              <div style={{ maxWidth: 900, margin: '0 auto 0', padding: '0 24px', width: '100%', boxSizing: 'border-box' }}>
                <div style={{ background: '#fdecea', border: '1px solid #f5c6c6', color: '#c0392b', borderRadius: 8, padding: '12px 16px', fontSize: 13, marginBottom: 16 }}>
                  {formError}
                </div>
              </div>
            )}
            <AnalyzerForm onSubmit={handleFormSubmit} disabled={isAnalyzing} />
          </div>
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

        <div className={styles.tabRow}>
          <button type="button" className={styles.tab} onClick={() => setView('form')}>Analyze a design</button>
          <button type="button" className={`${styles.tab} ${styles.tabActive}`}>Ask general questions</button>
        </div>

        {isEmpty ? (
          <div className={styles.centeredLayout}>
            <div className={styles.chatPageIntro}>
              <h1 className={styles.chatPageTitle}>Ask me anything...</h1>
              <div className={styles.chatPageSubtitle}>
                <ul>
                  <li>Ask any question about UI Tenets &amp; Traps</li>
                  <li>Describe an interface issue, it will identify Traps for you</li>
                </ul>
              </div>
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
