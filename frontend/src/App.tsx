/**
 * UITraps Unified Platform - Main Application
 *
 * Single-page app with a conversation panel and unified input.
 * Routes to chat (RAG) or analysis based on user input.
 * Supports centered welcome layout, analysis progress, and full-page reports.
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
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
import { PastChats } from './components/PastChats';
import { saveChat, getChat } from './api/chatApi';
import { TaskCaptureScreen, CapturedStep } from './components/TaskCaptureScreen';
import { saveAnalysis, StoredAnalysis, FormSnapshot } from './services/analysisHistory';
import { ChatMessage, ReportStatistics, UsageInfo, UnifiedAskResponse, TimeEstimate, UserContext, isFigmaEstimate, isUrlEstimate, isFileEstimate, UnifiedEstimate } from './api/types';
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

type AppView = 'form' | 'chat' | 'report' | 'history' | 'task-capture' | 'pastchats';

// Which tabs a given ?mode= shows. Multi-tab modes (>1 tab) render a restricted tab row;
// any other ?mode= value (chat / history / analyze / …) locks to one view with no tabs.
// No ?mode= at all → the full three-tab default.
//   analyzer → "Trap Analyzer"    : Analyze a design + See past analyses
//   ask      → "Ask me anything"  : Ask a question   + See past chats
const TAB_MODES: Record<string, AppView[]> = {
  // "Trap Analyzer" page — accept the natural spellings so the WordPress iframe / shortcut
  // URL just works whether it says analyzer, analyze, or analysis.
  analyzer: ['form', 'history'],
  analyze: ['form', 'history'],
  analysis: ['form', 'history'],
  // "Ask me anything" page
  ask: ['chat', 'pastchats'],
};
const TAB_LABELS: Record<string, string> = {
  form: 'Analyze a design',
  history: 'See past analyses',
  chat: 'Ask a question',
  pastchats: 'See past chats',
};

interface ActiveReport {
  html: string;
  markdown?: string;
  statistics?: ReportStatistics;
  usage?: UsageInfo;
  originalFiles?: File[];
  originalContext?: UserContext;
}

export const App: React.FC = () => {
  // Read URL params once — no flash, works inside an iframe
  // ?mode=analyze|chat  → locks view, hides tabs
  // ?theme=light|dark   → sets initial theme, hides toggle
  // postMessage { type: 'uitraps-theme', theme: 'light'|'dark' } → live theme updates
  const _params = new URLSearchParams(window.location.search);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const p = _params.get('theme');
    if (p === 'dark') return 'dark';
    if (p === 'light') return 'light';
    // Default to light on open when no explicit theme is provided. A ?theme= URL param or a
    // postMessage({type:'uitraps-theme'}) still overrides (e.g. the WordPress host forcing dark).
    return 'light';
  });
  const _mode = _params.get('mode');
  // The tabs to show for this mode: a multi-tab mode from TAB_MODES; the full three tabs when
  // no mode is given; or none (single locked view) for any other explicit mode value.
  const [tabs] = useState<AppView[]>(() => {
    if (_mode && TAB_MODES[_mode]) return TAB_MODES[_mode];
    if (!_mode) return ['form', 'history', 'chat'];
    return [];
  });
  const showTabs = tabs.length > 1;
  const [apiEndpoint] = useState(DEFAULT_API_ENDPOINT);
  const [view, setView] = useState<AppView>(() => {
    if (_mode && TAB_MODES[_mode]) return TAB_MODES[_mode][0];
    if (_mode === 'chat') return 'chat';
    if (_mode === 'history') return 'history';
    if (_mode === 'pastchats') return 'pastchats';
    return 'form';
  });
  const [activeReport, setActiveReport] = useState<ActiveReport | null>(null);
  // Whether the shown report was opened from See past analyses (vs. a fresh analysis) — drives
  // which tab stays active and the back button (Back to all vs Back to analyzer).
  const [reportFromHistory, setReportFromHistory] = useState(false);
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
        if (val === 'dark' || val === 'light') { setTheme(val); }
      } else if (event.data?.type === 'uitraps-token') {
        const token = event.data.token;
        const isDevParam = new URLSearchParams(window.location.search).get('dev') === 'true';
        if (!isDevParam && typeof token === 'string' && token.trim()) { auth.setToken(token.trim()); }
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [auth.setToken]);

  // Signal to the parent WordPress page that the iframe is mounted and listening.
  // WordPress should respond with { type: 'uitraps-theme', theme: 'dark'|'light' }
  // to set the theme reliably (avoids the race where the message arrives before this listener).
  useEffect(() => {
    if (window.self !== window.top) {
      window.parent.postMessage({ type: 'uitraps-ready' }, '*');
    }
  }, []);

  // When embedded in an iframe, the global CSS (html[data-embed]) sets height:auto /
  // overflow:visible on the wrappers, so document.documentElement.scrollHeight correctly
  // measures the full content height rather than just the current iframe height.
  const isEmbedded = window.self !== window.top;
  const lastSentHeightRef = useRef(0);

  useEffect(() => {
    if (isEmbedded) document.documentElement.setAttribute('data-embed', 'true');
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const sendHeightToParent = useCallback(() => {
    if (!isEmbedded) return;
    // getBoundingClientRect().height gives the true rendered height of the element
    // regardless of overflow settings — unlike scrollHeight which is clamped when
    // overflow:visible removes scroll contexts.
    const platform = document.querySelector('.uitraps-platform');
    const height = platform
      ? Math.ceil(platform.getBoundingClientRect().height)
      : document.documentElement.scrollHeight;
    if (height > 100 && height !== lastSentHeightRef.current) {
      lastSentHeightRef.current = height;
      window.parent.postMessage({ type: 'uitraps-height', height }, '*');
    }
  }, []); // isEmbedded is a stable constant — never changes after mount

  // Re-run when view changes; poll every 500ms for 20s to catch lazy-loading content
  useEffect(() => {
    if (window.self === window.top) return;
    lastSentHeightRef.current = 0; // reset so the new view always sends
    sendHeightToParent();
    let ticks = 0;
    const interval = setInterval(() => {
      sendHeightToParent();
      if (++ticks >= 40) clearInterval(interval);
    }, 500);
    return () => clearInterval(interval);
  }, [view, sendHeightToParent]);

  // Precise trigger: inner report iframe just finished loading and was resized
  const handleReportContentLoaded = useCallback(() => {
    requestAnimationFrame(() => requestAnimationFrame(sendHeightToParent));
  }, [sendHeightToParent]);

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
      setReportFromHistory(false);
      setView('report');
      setChatOpen(false);

      // Save to history
      saveAnalysis({
        timestamp: new Date().toISOString(),
        fileNames,
        statistics: result.statistics,
        html: result.report_html,
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
    // Tell the parent page to scroll the iframe into view after the height message has
    // been sent and applied — delay ensures the reflow from iframe shrinking is done first.
    if (isEmbedded) setTimeout(() => window.parent.postMessage({ type: 'uitraps-scroll-top' }, '*'), 800);
    setFormFileCount(files.length || 1);
    formElapsed.start();

    try {
      const inputFiles = files.length > 0 ? files : [];
      const imageTimeout = Math.min(180000 + (files.length || 1) * 120000, 1800000);

      const result = await unifiedAsk({
        apiEndpoint,
        token: effectiveToken,
        files: inputFiles,
        context,
        kbVersion: context?.kb_version,
        timeout: imageTimeout,
      });

      formElapsed.stop();

      if (result.report_html) {
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

  // Persist the current conversation after each completed exchange, so it shows under
  // "See past chats". Fire-and-forget; skipped without a real signed-in token.
  useEffect(() => {
    const msgs = unified.messages;
    if (!effectiveToken || effectiveToken === 'dev-mode') return;
    if (unified.isLoading || msgs.length === 0) return;
    if (msgs[msgs.length - 1].role !== 'assistant') return;
    void saveChat({ apiEndpoint, token: effectiveToken, sessionId: unified.sessionId, messages: msgs });
  }, [unified.messages, unified.isLoading, unified.sessionId, effectiveToken, apiEndpoint]);

  // Re-open a saved chat and continue it (under its original session id).
  const handleOpenChat = useCallback(async (sessionId: string) => {
    if (!effectiveToken) return;
    const data = await getChat({ apiEndpoint, token: effectiveToken, sessionId });
    if (!data) return;
    const raw = (data.messages || []) as unknown as ChatMessage[];
    const msgs = raw.map((m) => ({ ...m, timestamp: new Date(m.timestamp as unknown as string) }));
    unified.loadConversation(msgs, data.session_id);
    setView('chat');
  }, [apiEndpoint, effectiveToken, unified]);

  const handleViewHistoryReport = useCallback((analysis: StoredAnalysis) => {
    setActiveReport({
      html: analysis.html,
      markdown: analysis.markdown,
      statistics: analysis.statistics,
    });
    setReportFromHistory(true);
    setChatOpen(false);
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
  // Re-run in progress overlays the whole view. The finished report itself now renders
  // inside the tabbed layout below (under the "Analyze a design" tab).
  if (view === 'report' && activeReport && isRerunning) {
    return (
      <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
        <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
          <div className={styles.overlayContainer} style={isEmbedded ? { minHeight: '500px' } : undefined}>
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

  // ── History view ──
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
          <div className={styles.overlayContainer} style={isEmbedded ? { minHeight: '500px' } : undefined}>
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
          <div className={styles.overlayContainer} style={isEmbedded ? { minHeight: '500px' } : undefined}>
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

  // A viewed report belongs to the "Analyze a design" tab, so it stays highlighted while the
  // report shows. Clicking that tab returns to the current report (or the form if none).
  const activeTab: AppView = view === 'report' ? (reportFromHistory ? 'history' : 'form') : view;

  return (
    <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        {/* Tab row — always visible (even while an analysis is running) so the mode's two tabs
            stay present. A single-view mode (or none) renders no tabs, just a separator line. */}
        {showTabs && (
          <div className={styles.tabRow}>
            {tabs.map((t) => (
              <button
                key={t}
                type="button"
                className={`${styles.tab} ${activeTab === t ? styles.tabActive : ''}`}
                onClick={() => { if (view === 'report' && t === activeTab) return; setView(t); }}
              >
                {TAB_LABELS[t]}
              </button>
            ))}
          </div>
        )}
        {/* Separator line when there is no tab row */}
        {!showTabs && <div className={styles.topBorderLine} />}
        {/* Sub-action rows — hidden while an analysis is running */}
        {!isFormAnalyzing && (
          <>
            {view === 'chat' && !isEmpty && (
              <div className={styles.subTabActions}>
                <button className={styles.reportBtn} onClick={() => unified.clearHistory()}>New Session</button>
              </div>
            )}
            {view === 'report' && (
              <div className={styles.reportActions}>
                {reportFromHistory ? (
                  <button className={styles.reportBtn} onClick={() => setView('history')}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 19V5M5 12l7-7 7 7" />
                    </svg>
                    Back to all
                  </button>
                ) : (
                  <button className={styles.reportBtn} onClick={() => { setActiveReport(null); setView('form'); }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 19V5M5 12l7-7 7 7" />
                    </svg>
                    Back to analyzer
                  </button>
                )}
                <button
                  className={chatOpen ? styles.reportBtnActive : styles.reportBtn}
                  onClick={() => setChatOpen(o => !o)}
                >
                  Chat about results
                </button>
              </div>
            )}
          </>
        )}

        {/* Form view — always mounted so field values survive navigation to other views */}
        <div style={{ display: view === 'form' ? 'contents' : 'none' }}>
          <>
            {isFormAnalyzing && (
              <div className={styles.overlayContainer} style={isEmbedded ? { minHeight: '500px' } : undefined}>
                <AnalysisProgress
                  elapsedTime={formElapsed.elapsedTime}
                  onCancel={() => { setFormAnalysisPhase('idle'); formElapsed.reset(); }}
                  inputType={formFileCount > 1 ? 'multi_image' : 'single_image'}
                  fileCount={formFileCount}
                />
              </div>
            )}
            <div style={{ display: isFormAnalyzing ? 'none' : 'flex', flexDirection: 'column', ...(isEmbedded ? { overflow: 'visible' } : { overflowY: 'auto', flex: 1 }), paddingTop: '24px' }}>
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
        {view === 'history' && (
          <div style={{ display: 'flex', flexDirection: 'column', ...(isEmbedded ? { overflow: 'visible' } : { overflowY: 'auto', flex: 1 }) }}>
            <PastAnalyses
              onViewReport={handleViewHistoryReport}
              onReuseSettings={handleReuseSettings}
              onClose={() => setView('form')}
              token={effectiveToken || undefined}
              apiEndpoint={apiEndpoint}
            />
          </div>
        )}
        {view === 'pastchats' && (
          <div style={{ display: 'flex', flexDirection: 'column', ...(isEmbedded ? { overflow: 'visible' } : { overflowY: 'auto', flex: 1 }) }}>
            <PastChats
              token={effectiveToken || undefined}
              apiEndpoint={apiEndpoint}
              onStartChat={() => setView('chat')}
              onOpenChat={handleOpenChat}
            />
          </div>
        )}
        {view === 'report' && activeReport && (
          <div className={styles.reportWithChat} style={isEmbedded ? { overflow: 'visible', height: 'auto' } : undefined}>
            <div className={styles.reportArea} style={isEmbedded ? { overflowY: 'visible' } : undefined}>
              <ReportViewer
                html={activeReport.html}
                markdown={activeReport.markdown}
                statistics={activeReport.statistics}
                showStatistics={true}
                showUsageInfo={false}
                isDark={theme === 'dark'}
                onContentLoaded={handleReportContentLoaded}
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
        )}
      </div>
    </div>
  );
};

export default App;
