/**
 * Past Analyses list — shows the last 10 stored analysis reports.
 * Users can view or download each report.
 */

import React, { useState, useCallback } from 'react';
import { getAnalysisHistory, deleteAnalysis, StoredAnalysis } from '../services/analysisHistory';
import styles from './PastAnalyses.module.css';

interface PastAnalysesProps {
  onViewReport: (analysis: StoredAnalysis) => void;
  onClose: () => void;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export const PastAnalyses: React.FC<PastAnalysesProps> = ({ onViewReport, onClose }) => {
  const [analyses, setAnalyses] = useState(() => getAnalysisHistory());

  const handleDelete = useCallback((id: string) => {
    deleteAnalysis(id);
    setAnalyses(getAnalysisHistory());
  }, []);

  const handleDownload = useCallback((analysis: StoredAnalysis) => {
    const blob = new Blob([analysis.html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ui-traps-report-${new Date(analysis.timestamp).toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  if (analyses.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.empty}>
          <div className={styles.emptyTitle}>No Past Analyses</div>
          <p className={styles.emptyText}>
            Your completed analyses will appear here. Run an analysis to get started.
          </p>
          <button className={styles.backButton} onClick={onClose}>
            Back to Chat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Past Analyses</h2>
        <span className={styles.count}>{analyses.length} of 10</span>
      </div>

      <div className={styles.list}>
        {analyses.map(analysis => (
          <div key={analysis.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.cardDate}>{formatDate(analysis.timestamp)}</span>
              {analysis.fileNames.length > 0 && (
                <span className={styles.cardFiles}>
                  {analysis.fileNames.join(', ')}
                </span>
              )}
            </div>

            {analysis.statistics && (
              <div className={styles.statsRow}>
                {analysis.statistics.critical_count > 0 && (
                  <span className={`${styles.statBadge} ${styles.critical}`}>
                    {analysis.statistics.critical_count} Critical
                  </span>
                )}
                {analysis.statistics.moderate_count > 0 && (
                  <span className={`${styles.statBadge} ${styles.moderate}`}>
                    {analysis.statistics.moderate_count} Moderate
                  </span>
                )}
                {analysis.statistics.minor_count > 0 && (
                  <span className={`${styles.statBadge} ${styles.minor}`}>
                    {analysis.statistics.minor_count} Minor
                  </span>
                )}
                {analysis.statistics.positive_count > 0 && (
                  <span className={`${styles.statBadge} ${styles.positive}`}>
                    {analysis.statistics.positive_count} Positive
                  </span>
                )}
              </div>
            )}

            <div className={styles.cardActions}>
              <button
                className={styles.viewButton}
                onClick={() => onViewReport(analysis)}
              >
                View Report
              </button>
              <button
                className={styles.downloadButton}
                onClick={() => handleDownload(analysis)}
              >
                Download
              </button>
              <button
                className={styles.deleteButton}
                onClick={() => handleDelete(analysis.id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PastAnalyses;
