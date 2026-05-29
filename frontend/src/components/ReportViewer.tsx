import React, { useCallback, useEffect, useRef, useState } from 'react';
import { ReportViewerProps } from '../api/types';
import styles from './ReportViewer.module.css';

const DARK_MODE_CSS = `
  /* ── Base ── */
  body, html { background: #1a1a2e !important; color: #e2e8f0 !important; font-family: 'Inter', system-ui, -apple-system, sans-serif !important; }
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

  /* ── Frame info / issue frames inside cards ── */
  .issue-card .frame-info, .issue-frames {
    background: #0f3460 !important;
    color: #a0aec0 !important;
    border-color: #2d3748 !important;
  }

  /* ── General issue cards ── */
  .user-issue-card {
    background: #16213e !important;
    border-color: #2d3748 !important;
    color: #e2e8f0 !important;
    box-shadow: none !important;
  }
  .user-issue-title { color: #e2e8f0 !important; }
  .user-issues-intro { color: #a0aec0 !important; }

  /* ── Impact badges ── */
  .impact-badge.high   { background: rgba(252,129,129,0.15) !important; color: #fc8181 !important; }
  .impact-badge.medium { background: rgba(246,173,85,0.15)  !important; color: #f6ad55 !important; }
  .impact-badge.low    { background: rgba(99,179,237,0.15)  !important; color: #63b3ed !important; }

  /* ── Severity dots (colored circles) ── */
  .sev-dot.sev-critical { background: #fc8181 !important; }
  .sev-dot.sev-moderate { background: #f6ad55 !important; }
  .sev-dot.sev-minor    { background: #63b3ed !important; }

  /* ── Severity text labels in meta row ── */
  .meta-severity.sev-critical { color: #fc8181 !important; }
  .meta-severity.sev-moderate { color: #f6ad55 !important; }
  .meta-severity.sev-minor    { color: #63b3ed !important; }

  /* ── Contributing trap pills ── */
  .trap-pill, .contributing-traps span {
    background: #0f3460 !important;
    color: #90cdf4 !important;
    border-color: #2b6cb0 !important;
  }
  .traps-label { color: #a0aec0 !important; }

  /* ── Meta / muted text ── */
  .task-context, .timestamp { color: #a0aec0 !important; }
  .meta-label, .meta-confidence, .meta-tenet { color: #a0aec0 !important; }
  em, i { color: #a0aec0 !important; }

  /* ── Summary ── */
  .findings-overview {
    background: #16213e !important;
    color: #a0aec0 !important;
    border-color: #2d3748 !important;
  }
  .summary-section ul { border-left-color: #4a90d9 !important; background: #0f3460 !important; }

  /* ── Scorecard ── */
  .scorecard-title { color: #718096 !important; }
  .scorecard-label { background: #16213e !important; color: #a0aec0 !important; border-color: #2d3748 !important; }
  .scorecard-table thead th { background: #0d2137 !important; border-color: #2d3748 !important; }
  .scorecard-table thead th:first-child { color: #a0aec0 !important; }
  .scorecard-th-high     { color: #fc8181 !important; }
  .scorecard-th-moderate { color: #f6ad55 !important; }
  .scorecard-th-low      { color: #63b3ed !important; }
  .scorecard-th-positive { color: #68d391 !important; }
  .scorecard-val-high     { background: rgba(252,129,129,0.12) !important; color: #fc8181 !important; }
  .scorecard-val-moderate { background: rgba(246,173,85,0.12)  !important; color: #f6ad55 !important; }
  .scorecard-val-low      { background: rgba(99,179,237,0.12)  !important; color: #63b3ed !important; }
  .scorecard-val-positive { background: rgba(104,211,145,0.12) !important; color: #68d391 !important; }
  .scorecard-val-potential{ background: rgba(160,174,192,0.12) !important; color: #a0aec0 !important; }
  .scorecard-col { border-color: #2d3748 !important; }
  .scorecard-empty { color: #4a5568 !important; }

  /* ── Finding region screenshots ── */
  .issue-region-figure { background: #0f1a2e !important; border-color: #2d3748 !important; }
  .issue-region-caption { color: #718096 !important; }

  /* ── Evaluation Details / users table ── */
  .context-section { background: #16213e !important; border-color: #2d3748 !important; }
  .context-body { color: #e2e8f0 !important; }
  .context-body p, .context-body strong { color: #e2e8f0 !important; }
  .context-body ul li { color: #e2e8f0 !important; }
  .users-detail-label strong { color: #e2e8f0 !important; }
  .users-table td { border-color: #2d3748 !important; }
  .users-table .ut-label { background: #0f3460 !important; color: #718096 !important; }
  .users-table .ut-value { background: #16213e !important; color: #e2e8f0 !important; }

  /* ── Chat context badge / frame ── */
  .chat-context-badge {
    background: #1e3a5f !important;
    color: #63b3ed !important;
    border-color: #2b6cb0 !important;
  }
  .chat-context-frame {
    background: #1e3a5f !important;
    border-color: #2b6cb0 !important;
    color: #90cdf4 !important;
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

  /* ── Confidence group headers ── */
  .confidence-group-header { color: #718096 !important; border-bottom-color: #2d3748 !important; }

  /* ── Positive observations ── */
  .positive-card {
    background: #16213e !important;
    border-color: #2d3748 !important;
    border-left-color: #48bb78 !important;
    box-shadow: none !important;
  }
  .positive-item { color: #68d391 !important; }

  /* ── Potential issues section ── */
  .potential-issues-section {
    background: #16213e !important;
    border-color: #2d3748 !important;
  }

  /* ── Traps not found / untestable ── */
  .traps-not-found {
    background: #16213e !important;
    border-color: #2d3748 !important;
  }
  .traps-not-found h3 { color: #e2e8f0 !important; }
  .untestable-list li { border-bottom-color: #2d3748 !important; color: #a0aec0 !important; }
  .untestable-list .trap-label { color: #e2e8f0 !important; }
  .untestable-note { color: #718096 !important; }

  /* ── Confidentiality notice ── */
  .confidentiality-notice {
    background: #16213e !important;
    border-color: #2d3748 !important;
  }
  .confidentiality-notice h3 { color: #f6ad55 !important; }
  .confidentiality-notice p, .confidentiality-notice li { color: #a0aec0 !important; }

  /* ── Misc ── */
  a { color: #63b3ed !important; }
  hr { border-color: #2d3748 !important; }
  code, pre { background: #0f3460 !important; color: #e2e8f0 !important; }
`;

export const ReportViewer: React.FC<ReportViewerProps> = ({
  html,
  markdown,
  usage,
  showUsageInfo = false,
  isDark = false,
  htmlV1,
  htmlV2,
}) => {
  const isDualReport = !!(htmlV1 && htmlV2);
  const [activeVersion, setActiveVersion] = useState<'v1' | 'v2'>('v2');

  const activeHtml = isDualReport
    ? (activeVersion === 'v1' ? htmlV1! : htmlV2!)
    : html;

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
  }, [activeHtml, isDark, applyDarkMode]);

  // Toggle dark mode without reloading the iframe
  useEffect(() => {
    const doc = iframeRef.current?.contentDocument;
    if (doc?.readyState === 'complete') {
      applyDarkMode(doc, isDark);
    }
  }, [isDark, applyDarkMode]);

  const handleDownloadPdf = useCallback(() => {
    iframeRef.current?.contentWindow?.print();
  }, []);

  const handleDownloadMarkdown = useCallback(() => {
    if (!markdown) return;
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ui-traps-report-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [markdown]);

  return (
    <div className={styles.container}>
      {/* Dual-report version toggle */}
      {isDualReport && (
        <div className={styles.versionToggle}>
          <span className={styles.versionToggleLabel}>Knowledge base:</span>
          <div className={styles.versionToggleGroup}>
            <button
              type="button"
              className={`${styles.versionToggleBtn} ${activeVersion === 'v2' ? styles.versionToggleBtnActive : ''}`}
              onClick={() => setActiveVersion('v2')}
            >
              V2 (current)
            </button>
            <button
              type="button"
              className={`${styles.versionToggleBtn} ${activeVersion === 'v1' ? styles.versionToggleBtnActive : ''}`}
              onClick={() => setActiveVersion('v1')}
            >
              V1 (previous)
            </button>
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
        srcDoc={activeHtml}
        title="Analysis Report"
        sandbox="allow-same-origin allow-scripts allow-modals"
        style={{ width: '100%', border: 'none', minHeight: '400px' }}
      />

      {/* Actions */}
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.secondaryButton}
          onClick={handleDownloadPdf}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
          </svg>
          Download as PDF
        </button>

        <button
          type="button"
          className={styles.secondaryButton}
          onClick={handleDownloadMarkdown}
          disabled={!markdown}
          title={!markdown ? 'Markdown not available for this report' : undefined}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
          </svg>
          Download as Markup
        </button>
      </div>
    </div>
  );
};

export default ReportViewer;
