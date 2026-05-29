/**
 * UITraps Unified Platform - Main Application
 *
 * Single-page app with a conversation panel and unified input.
 * Routes to chat (RAG) or analysis based on user input.
 * Supports centered welcome layout, analysis progress, and full-page reports.
 */

import React, { useState, useCallback, useEffect } from 'react';
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
import { saveAnalysis, StoredAnalysis, FormSnapshot } from './services/analysisHistory';
import { ReportStatistics, UsageInfo, UnifiedAskResponse, TimeEstimate, UserContext, isFigmaEstimate, isUrlEstimate, isFileEstimate, UnifiedEstimate } from './api/types';
import { unifiedAsk } from './api/client';
import { ChatPanel } from './components/ChatPanel';
import { RecentStrip } from './components/RecentStrip';
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
  // Read URL params once — no flash, works inside an iframe
  // ?mode=analyze|chat  → locks view, hides tabs
  // ?theme=light|dark   → sets initial theme, hides toggle
  // postMessage { type: 'uitraps-theme', theme: 'light'|'dark' } → live theme updates
  const _params = new URLSearchParams(window.location.search);
  const [theme, setTheme] = useState<'light' | 'dark'>(() =>
    _params.get('theme') === 'dark' ? 'dark' : 'light'
  );
  const [externalTheme, setExternalTheme] = useState(() => _params.has('theme'));
  const [externalMode] = useState(() => _params.has('mode'));
  const [apiEndpoint] = useState(DEFAULT_API_ENDPOINT);
  const [view, setView] = useState<AppView>(() =>
    _params.get('mode') === 'chat' ? 'chat' : 'form'
  );
  const [activeReport, setActiveReport] = useState<ActiveReport | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [isRerunning, setIsRerunning] = useState(false);
  const rerunElapsed = useElapsedTime();

  // Form pre-fill — incremented key forces AnalyzerForm to remount with new initialValues
  const [prefillValues, setPrefillValues] = useState<FormSnapshot | undefined>(undefined);
  const [formKey, setFormKey] = useState(0);

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

  // Direct access (not in iframe, not localhost) — access code flow
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const isDirectAccess = window.self === window.top && !isLocalhost;
  const [accessCode, setAccessCode] = useState('');
  const [accessCodeError, setAccessCodeError] = useState('');
  const [accessCodeLoading, setAccessCodeLoading] = useState(false);

  const handleAccessCodeSubmit = useCallback(async () => {
    if (!accessCode.trim()) return;
    setAccessCodeLoading(true);
    setAccessCodeError('');
    try {
      const res = await fetch(`${DEFAULT_API_ENDPOINT}/auth/access-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: accessCode.trim() }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('uitraps-access-granted', 'true');
        setDevMode(true);
      } else if (!res.ok) {
        setAccessCodeError(`Server error (${res.status}): ${data.detail || data.error || 'Unknown error'}`);
      } else {
        setAccessCodeError('Incorrect access code. Please try again.');
      }
    } catch {
      setAccessCodeError('Could not reach the server. Please try again.');
    } finally {
      setAccessCodeLoading(false);
    }
  }, [accessCode]);

  // Listen for messages posted from the parent WordPress page:
  //   { type: 'uitraps-theme', theme: 'dark'|'light' }  → live theme update
  //   { type: 'uitraps-token', token: '<jwt>' }          → JWT auth on iframe load
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'uitraps-theme') {
        const val = event.data.theme;
        if (val === 'dark' || val === 'light') { setTheme(val); setExternalTheme(true); }
      } else if (event.data?.type === 'uitraps-token') {
        const token = event.data.token;
        if (typeof token === 'string' && token.trim()) { auth.setToken(token.trim()); }
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [auth.setToken]);

  // Report content height to parent so WordPress can resize the iframe to fit
  useEffect(() => {
    if (window.self === window.top) return; // only when embedded in an iframe
    const report = () => {
      const height = document.documentElement.scrollHeight;
      window.parent.postMessage({ type: 'uitraps-height', height }, '*');
    };
    report();
    const observer = new ResizeObserver(report);
    observer.observe(document.documentElement);
    return () => observer.disconnect();
  }, [view]);

  // Auto-authenticate from ?token= URL param (for WordPress iframe src embedding)
  useEffect(() => {
    const urlToken = new URLSearchParams(window.location.search).get('token');
    if (urlToken) {
      auth.setToken(urlToken);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [auth.setToken]);

  // Skip auth on localhost, or on direct access if the user has already entered the access code.
  const [devMode, setDevMode] = useState(() => {
    const host = window.location.hostname;
    const params = new URLSearchParams(window.location.search);
    if (host === 'localhost' || host === '127.0.0.1') return true;
    if (params.get('dev') === 'true') return true;
    if (params.get('token')) return true;
    if (window.self === window.top && localStorage.getItem('uitraps-access-granted') === 'true') return true;
    return false;
  });
  const effectiveToken = auth.token || (devMode ? 'dev-mode' : '');

  const handleAnalysisComplete = useCallback((result: UnifiedAskResponse, fileNames: string[], files?: File[], context?: UserContext, formSnapshot?: FormSnapshot) => {
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
        markdown: result.report_markdown,
        formSnapshot,
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
          originalContext: { ...prev.originalContext, ...correctedContext },
        } : prev);
        setChatOpen(false);

        saveAnalysis({
          timestamp: new Date().toISOString(),
          fileNames: activeReport.originalFiles.map(f => f.name),
          statistics: result.statistics,
          html: result.report_html,
          markdown: result.report_markdown,
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
    const { files, context, formSnapshot } = payload;

    setFormError(null);
    setFormAnalysisPhase('analyzing');
    setFormFileCount(files.length || 1);
    formElapsed.start();

    try {
      const inputFiles = files.length > 0 ? files : [];
      const imageTimeout = Math.min(180000 + (files.length || 1) * 120000, 1800000);

      const kbVersionForRequest = context?.kb_version;
      const effectiveTimeout = kbVersionForRequest === 'both'
        ? Math.min(imageTimeout * 2, 3600000)
        : imageTimeout;

      const result = await unifiedAsk({
        apiEndpoint,
        token: effectiveToken,
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
          context,
          formSnapshot
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
      markdown: analysis.markdown,
      statistics: analysis.statistics,
    });
    setView('report');
  }, []);

  const handleReuseSettings = useCallback((analysis: StoredAnalysis) => {
    if (!analysis.formSnapshot) return;
    setPrefillValues(analysis.formSnapshot);
    setFormKey(k => k + 1);
    setView('form');
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

  // Auth gate
  if (!auth.isAuthenticated && !devMode) {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <div className={styles.authPrompt}>
            <div className={styles.authTitle}>
              UI Traps <span className={styles.logoAccent}>Helper</span>
            </div>
            {isDirectAccess ? (
              <>
                <div className={styles.authSubtitle}>Enter your access code to continue.</div>
                <input
                  className={styles.tokenInput}
                  type="password"
                  placeholder="Access code"
                  value={accessCode}
                  onChange={e => setAccessCode(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleAccessCodeSubmit()}
                  autoFocus
                />
                {accessCodeError && (
                  <div className={styles.devNote} style={{ color: '#e05c1a' }}>{accessCodeError}</div>
                )}
                <button
                  className={styles.connectButton}
                  onClick={handleAccessCodeSubmit}
                  disabled={accessCodeLoading || !accessCode.trim()}
                >
                  {accessCodeLoading ? 'Verifying...' : 'Continue'}
                </button>
              </>
            ) : (
              <>
                <div className={styles.authSubtitle}>
                  Enter your JWT token to connect.
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
              </>
            )}
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
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <div className={styles.topBorderLine} />
          <div className={styles.subTabActions}>
            <button
              className={chatOpen ? styles.headerButtonActive : styles.headerButton}
              onClick={() => setChatOpen(o => !o)}
            >
              Chat about Results
            </button>
            <button className={styles.headerButton} onClick={() => setView('form')}>
              New Analysis
            </button>
            {!externalTheme && (
              <button className={`${styles.headerButton} ${styles.themeToggle}`} onClick={toggleTheme} title={theme === 'light' ? 'Dark mode' : 'Light mode'}>
                {theme === 'light'
                ? <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                : <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>}
              </button>
            )}
          </div>
          <div className={styles.reportWithChat}>
            <div className={styles.reportArea}>
              <ReportViewer
                html={activeReport.html}
                markdown={activeReport.markdown}
                statistics={activeReport.statistics}
                showStatistics={true}
                showUsageInfo={false}
                isDark={theme === 'dark'}
                htmlV1={activeReport.htmlV1}
                htmlV2={activeReport.htmlV2}
                statisticsV1={activeReport.statisticsV1}
                statisticsV2={activeReport.statisticsV2}
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
          <div className={styles.topBorderLine} />
          {!externalTheme && (
            <div className={styles.subTabActions}>
              <button className={`${styles.headerButton} ${styles.themeToggle}`} onClick={toggleTheme} title={theme === 'light' ? 'Dark mode' : 'Light mode'}>
                {theme === 'light'
                ? <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                : <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>}
              </button>
            </div>
          )}
          <PastAnalyses
            onViewReport={handleViewHistoryReport}
            onReuseSettings={handleReuseSettings}
            onClose={() => setView('form')}
          />
        </div>
      </div>
    );
  }

  // ── Estimate preview overlay ──
  if (view === 'chat' && unified.analysisPhase === 'previewing' && unified.estimate) {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <div className={styles.topBorderLine} />
          <div className={styles.subTabActions}>
            <button className={styles.headerButton} onClick={unified.cancelAnalysis}>
              Cancel
            </button>
          </div>
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
  if (view === 'chat' && unified.analysisPhase === 'analyzing') {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
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

  // ── Form + Chat views — single tree so header/tabs never unmount ──
  const isFormAnalyzing = view === 'form' && formAnalysisPhase === 'analyzing';
  const isEmpty = unified.messages.length === 0 && !unified.isLoading;

  return (
    <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        {!isFormAnalyzing && (
          <>
            {/* Tab row — hidden when parent site drives the mode */}
            {!externalMode && (
              <div className={styles.tabRow}>
                <button type="button" className={`${styles.tab} ${view === 'form' ? styles.tabActive : ''}`} onClick={() => setView('form')}>Analyze a design</button>
                <button type="button" className={`${styles.tab} ${view === 'chat' ? styles.tabActive : ''}`} onClick={() => setView('chat')}>Ask a question</button>
              </div>
            )}
            {/* Separator line when tab row is hidden */}
            {externalMode && <div className={styles.topBorderLine} />}
            {/* Sub-actions: New Session (chat), theme toggle */}
            {(view === 'chat' || !externalTheme) && (
              <div className={styles.subTabActions}>
                {view === 'chat' && (
                  <button className={styles.headerButton} onClick={() => unified.clearHistory()}>New Session</button>
                )}
                {!externalTheme && (
                  <button className={`${styles.headerButton} ${styles.themeToggle}`} onClick={toggleTheme} title={theme === 'light' ? 'Dark mode' : 'Light mode'}>
                    {theme === 'light'
                      ? <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                      : <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>}
                  </button>
                )}
              </div>
            )}
          </>
        )}

        {/* Form view — always mounted so field values survive navigation to other views */}
        <div style={{ display: view === 'form' ? 'contents' : 'none' }}>
          <>
            {isFormAnalyzing && (
              <div className={styles.overlayContainer}>
                <AnalysisProgress
                  elapsedTime={formElapsed.elapsedTime}
                  onCancel={() => { setFormAnalysisPhase('idle'); formElapsed.reset(); }}
                  inputType={formFileCount > 1 ? 'multi_image' : 'single_image'}
                  fileCount={formFileCount}
                />
              </div>
            )}
            <div style={{ display: isFormAnalyzing ? 'none' : 'flex', flexDirection: 'column', overflowY: 'auto', flex: 1, paddingTop: '24px' }}>
              <RecentStrip onViewAll={() => setView('history')} />
              {formError && (
                <div style={{ maxWidth: 900, margin: '0 auto 0', padding: '0 24px', width: '100%', boxSizing: 'border-box' }}>
                  <div style={{ background: '#fdecea', border: '1px solid #f5c6c6', color: '#c0392b', borderRadius: 8, padding: '12px 16px', fontSize: 13, marginBottom: 16 }}>
                    {formError}
                  </div>
                </div>
              )}
              <AnalyzerForm key={formKey} initialValues={prefillValues} onSubmit={handleFormSubmit} disabled={isFormAnalyzing} />
            </div>
          </>
        </div>

        {view === 'chat' && (
          isEmpty ? (
            <div className={styles.centeredLayout}>
              <div className={styles.chatPageContent}>
                <div className={styles.chatPageIntro}>
                  <h1 className={styles.chatPageTitle}>Ask me anything...</h1>
                  <p className={styles.chatPageSubtitle}>Ask anything about UI Tenets &amp; Traps, or describe an interface issue and I'll identify the relevant Traps.</p>
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
          )
        )}
      </div>
    </div>
  );
};

export default App;
