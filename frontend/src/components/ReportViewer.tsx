import React, { useMemo, useCallback } from 'react';
import DOMPurify from 'dompurify';
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
  // Sanitize HTML to prevent XSS while allowing images for frame display
  const sanitizedHtml = useMemo(() => {
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: [
        'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'strong', 'em', 'b', 'i', 'a',
        'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot',
        'br', 'hr', 'blockquote', 'pre', 'code',
        'section', 'article', 'header', 'footer', 'main',
        'img', // Allow images for frame thumbnails and gallery
      ],
      ALLOWED_ATTR: [
        'class', 'id', 'href', 'target', 'rel', 'style',
        'src', 'alt', 'title', 'width', 'height', // Image attributes
      ],
    });
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
            <span className={styles.statLabel}>Critical</span>
          </div>
          <div className={`${styles.statCard} ${styles.moderate}`}>
            <span className={styles.statValue}>{statistics.moderate_count}</span>
            <span className={styles.statLabel}>Moderate</span>
          </div>
          <div className={`${styles.statCard} ${styles.minor}`}>
            <span className={styles.statValue}>{statistics.minor_count}</span>
            <span className={styles.statLabel}>Minor</span>
          </div>
          <div className={`${styles.statCard} ${styles.positive}`}>
            <span className={styles.statValue}>{statistics.positive_count}</span>
            <span className={styles.statLabel}>Positive</span>
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

      {/* Report Content */}
      <div
        className={styles.reportContent}
        dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
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
