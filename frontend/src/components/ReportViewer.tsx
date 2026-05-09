import React, { useCallback, useEffect, useRef } from 'react';
import { ReportViewerProps } from '../api/types';
import styles from './ReportViewer.module.css';

export const ReportViewer: React.FC<ReportViewerProps> = ({
  html,
  statistics,
  usage,
  showStatistics = true,
  showUsageInfo = false,
  onNewAnalysis,
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Auto-resize iframe to match its content height
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const resize = () => {
      try {
        const doc = iframe.contentDocument;
        if (doc && doc.body) {
          iframe.style.height = doc.body.scrollHeight + 40 + 'px';
        }
      } catch {
        // cross-origin safety guard
      }
    };

    iframe.addEventListener('load', resize);
    // Also resize if already loaded (srcdoc can load synchronously)
    if (iframe.contentDocument?.readyState === 'complete') {
      resize();
    }
    return () => iframe.removeEventListener('load', resize);
  }, [html]);

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
