import React, { useCallback, useEffect, useRef } from 'react';
import { ReportViewerProps } from '../api/types';
import styles from './ReportViewer.module.css';

const DARK_MODE_CSS = `
  /* ── Base ── */
  body, html { background: #1a1a2e !important; color: #e2e8f0 !important; }
  body > div, .ui-traps-report, .container, .report-container {
    background: #1a1a2e !important;
  }

  /* ── All text ── */
  h1, h2, h3, h4, h5, h6 { color: #e2e8f0 !important; }
  p, li, label, strong, b, small { color: #e2e8f0 !important; }

  /* ── Sections ── */
  .context-section, .summary-section, .user-issues-section,
  .issues-section, .positives-section, .checked-section {
    background: #1a1a2e !important;
    color: #e2e8f0 !important;
  }
  .context-section, .summary-section {
    background: #16213e !important;
    border-color: #2d3748 !important;
  }

  /* ── Issue / trap cards ── */
  .issue-card {
    background: #16213e !important;
    border-color: #2d3748 !important;
    color: #e2e8f0 !important;
  }
  /* Preserve severity left-border accent colors */
  .issue-card.critical  { border-left-color: #fc8181 !important; }
  .issue-card.moderate  { border-left-color: #f6ad55 !important; }
  .issue-card.minor     { border-left-color: #63b3ed !important; }

  /* ── General issue cards ── */
  .user-issue-card {
    background: #16213e !important;
    border-color: #2d3748 !important;
    color: #e2e8f0 !important;
    box-shadow: none !important;
  }
  .user-issue-card.impact-high   { border-left-color: #fc8181 !important; }
  .user-issue-card.impact-medium { border-left-color: #f6ad55 !important; }
  .user-issue-card.impact-low    { border-left-color: #63b3ed !important; }
  .user-issue-title { color: #e2e8f0 !important; }
  .user-issues-intro { color: #a0aec0 !important; }

  /* ── Impact badges ── */
  .impact-badge.high   { background: rgba(252,129,129,0.15) !important; color: #fc8181 !important; }
  .impact-badge.medium { background: rgba(246,173,85,0.15)  !important; color: #f6ad55 !important; }
  .impact-badge.low    { background: rgba(99,179,237,0.15)  !important; color: #63b3ed !important; }

  /* ── Severity badges in trap cards ── */
  .sev-critical { background: #c53030 !important; }
  .sev-moderate { background: #c05621 !important; }
  .sev-minor    { background: #2b6cb0 !important; }

  /* ── Contributing trap pills ── */
  .trap-pill, .contributing-traps span {
    background: #0f3460 !important;
    color: #90cdf4 !important;
    border-color: #2b6cb0 !important;
  }
  .traps-label { color: #a0aec0 !important; }

  /* ── Meta / muted text ── */
  .task-context, .timestamp { color: #a0aec0 !important; }
  em, i { color: #a0aec0 !important; }

  /* ── Summary ── */
  .findings-overview {
    background: #16213e !important;
    color: #a0aec0 !important;
    border-color: #2d3748 !important;
  }
  .summary-section ul { border-left-color: #4a90d9 !important; }

  /* ── Chat context badge ── */
  .chat-context-badge {
    background: #1e3a5f !important;
    color: #63b3ed !important;
    border-color: #2b6cb0 !important;
  }

  /* ── Tables (generic) ── */
  table { background: #16213e !important; border-color: #2d3748 !important; }
  tr { background: #1a1a2e !important; }
  tr:nth-child(even) { background: #16213e !important; }
  th { background: #0f3460 !important; color: #e2e8f0 !important; border-color: #2d3748 !important; }
  td { color: #e2e8f0 !important; border-color: #2d3748 !important; }

  /* ── Trap Coverage Matrix ── */
  .trap-matrix-table .tenet-cell {
    background: #0f3460 !important;
    color: #90cdf4 !important;
    border-right-color: #2d3748 !important;
  }
  .trap-matrix-table .trap-name { color: #e2e8f0 !important; }
  .trap-matrix-table tr.has-issues td.trap-name { color: #e2e8f0 !important; }
  .trap-matrix-table .count.total { color: #e2e8f0 !important; border-left-color: #2d3748 !important; }
  .trap-matrix-table thead th { background: #0d2137 !important; }

  /* ── Traps not found / untestable ── */
  .traps-not-found h3 { color: #e2e8f0 !important; }
  .untestable-list li { border-bottom-color: #2d3748 !important; color: #a0aec0 !important; }
  .untestable-list .trap-label { color: #e2e8f0 !important; }
  .untestable-note { color: #718096 !important; }

  /* ── Positive observations ── */
  .positive-item { color: #68d391 !important; }

  /* ── Misc ── */
  a { color: #63b3ed !important; }
  hr { border-color: #2d3748 !important; }
  code, pre { background: #0f3460 !important; color: #e2e8f0 !important; }
`;

export const ReportViewer: React.FC<ReportViewerProps> = ({
  html,
  statistics,
  usage,
  showStatistics = true,
  showUsageInfo = false,
  onNewAnalysis,
  isDark = false,
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const applyDarkMode = useCallback((doc: Document, dark: boolean) => {
    const existing = doc.getElementById('__dark-mode-override__');
    if (dark && !existing) {
      const style = doc.createElement('style');
      style.id = '__dark-mode-override__';
      style.textContent = DARK_MODE_CSS;
      doc.head.appendChild(style);
    } else if (!dark && existing) {
      existing.remove();
    }
  }, []);

  // Auto-resize iframe to match its content height, and apply dark mode on load
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const onLoad = () => {
      try {
        const doc = iframe.contentDocument;
        if (doc && doc.body) {
          iframe.style.height = doc.body.scrollHeight + 40 + 'px';
          applyDarkMode(doc, isDark);
        }
      } catch {
        // cross-origin safety guard
      }
    };

    iframe.addEventListener('load', onLoad);
    if (iframe.contentDocument?.readyState === 'complete') {
      onLoad();
    }
    return () => iframe.removeEventListener('load', onLoad);
  }, [html, isDark, applyDarkMode]);

  // Toggle dark mode without reloading the iframe
  useEffect(() => {
    const doc = iframeRef.current?.contentDocument;
    if (doc?.readyState === 'complete') {
      applyDarkMode(doc, isDark);
    }
  }, [isDark, applyDarkMode]);

  const handleDownload = useCallback(() => {
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ui-traps-report-${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [html]);

  return (
    <div className={styles.container}>
      {/* Statistics Summary */}
      {showStatistics && statistics && (
        <div className={styles.statsGrid}>
          <div className={`${styles.statCard} ${styles.critical}`}>
            <span className={styles.statValue}>{statistics.critical_count}</span>
            <span className={styles.statLabel}>High Severity</span>
          </div>
          <div className={`${styles.statCard} ${styles.moderate}`}>
            <span className={styles.statValue}>{statistics.moderate_count}</span>
            <span className={styles.statLabel}>Moderate Severity</span>
          </div>
          <div className={`${styles.statCard} ${styles.minor}`}>
            <span className={styles.statValue}>{statistics.minor_count}</span>
            <span className={styles.statLabel}>Low Severity</span>
          </div>
          <div className={`${styles.statCard} ${styles.positive}`}>
            <span className={styles.statValue}>{statistics.positive_count}</span>
            <span className={styles.statLabel}>Positives</span>
          </div>
        </div>
      )}

      {/* Usage Info */}
      {showUsageInfo && usage && (
        <div className={styles.usageInfo}>
          <span>
            {usage.remaining} of {usage.limit} analyses remaining this month
          </span>
        </div>
      )}

      {/* Report Content — rendered in an iframe so embedded CSS applies correctly */}
      <iframe
        ref={iframeRef}
        className={styles.reportFrame}
        srcDoc={html}
        title="Analysis Report"
        sandbox="allow-same-origin"
        style={{ width: '100%', border: 'none', minHeight: '400px' }}
      />

      {/* Actions */}
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.primaryButton}
          onClick={onNewAnalysis}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 4v16m8-8H4"/>
          </svg>
          New Analysis
        </button>

        <button
          type="button"
          className={styles.secondaryButton}
          onClick={handleDownload}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
          </svg>
          Download Report
        </button>
      </div>
    </div>
  );
};

export default ReportViewer;
