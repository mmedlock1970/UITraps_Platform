/**
 * Past Analyses list — shows stored analysis reports.
 * When a token + apiEndpoint are provided, fetches from the server (cross-session).
 * Falls back to localStorage when not authenticated.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { getAnalysisHistory, deleteAnalysis, StoredAnalysis, HISTORY_LIMIT } from '../services/analysisHistory';
import styles from './PastAnalyses.module.css';

interface ServerReport {
  id: number;
  timestamp: string;
  analysis_type: string;
  design_name?: string;
  file_name?: string;
  statistics?: {
    critical_count?: number;
    moderate_count?: number;
    minor_count?: number;
    positive_count?: number;
  };
}

interface PastAnalysesProps {
  onViewReport: (analysis: StoredAnalysis) => void;
  onReuseSettings?: (analysis: StoredAnalysis) => void;
  onClose: () => void;
  token?: string;
  apiEndpoint?: string;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
  }) + ' · ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function getDisplayName(analysis: StoredAnalysis): string {
  const screenName = analysis.formSnapshot?.screenName?.trim();
  if (screenName) return screenName;
  const firstName = analysis.fileNames[0];
  if (firstName) return firstName.replace(/\.[^.]+$/, '');
  return 'Untitled analysis';
}

function serverReportDisplayName(r: ServerReport): string {
  if (r.design_name) return r.design_name;
  if (r.file_name) return r.file_name.replace(/\.[^.]+$/, '');
  return 'Untitled analysis';
}

export const PastAnalyses: React.FC<PastAnalysesProps> = ({
  onViewReport, onReuseSettings, onClose, token, apiEndpoint,
}) => {
  const useServer = !!(token && apiEndpoint);

  // Local analyses always available
  const [localAnalyses, setLocalAnalyses] = useState(() => getAnalysisHistory());

  // Server-side state
  const [serverReports, setServerReports] = useState<ServerReport[]>([]);
  const [serverLoading, setServerLoading] = useState(false);
  const [serverError, setServerError] = useState('');
  const [loadingReportId, setLoadingReportId] = useState<number | null>(null);

  useEffect(() => {
    if (!useServer) return;
    setServerLoading(true);
    fetch(`${apiEndpoint}/reports`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => {
        if (data.success) setServerReports(data.reports);
        else setServerError('Could not load reports from server.');
      })
      .catch(() => setServerError('Could not reach server.'))
      .finally(() => setServerLoading(false));
  }, [useServer, token, apiEndpoint]);

  const handleViewServer = useCallback(async (report: ServerReport) => {
    if (!apiEndpoint || !token) return;
    setLoadingReportId(report.id);
    try {
      const res = await fetch(`${apiEndpoint}/reports/${report.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!data.success) throw new Error('Failed to load report');
      const r = data.report;
      // Convert to StoredAnalysis shape for the existing viewer
      const synthetic: StoredAnalysis = {
        id: `server-${r.id}`,
        timestamp: r.timestamp,
        html: r.html,
        markdown: r.markdown,
        statistics: r.statistics,
        fileNames: r.file_name ? [r.file_name] : [],
        formSnapshot: r.design_name ? { screenName: r.design_name } as any : undefined,
      };
      onViewReport(synthetic);
    } catch {
      setServerError('Failed to load report.');
    } finally {
      setLoadingReportId(null);
    }
  }, [apiEndpoint, token, onViewReport]);

  const handleDeleteLocal = useCallback((id: string) => {
    deleteAnalysis(id);
    setLocalAnalyses(getAnalysisHistory());
  }, []);

  const handleDownloadLocal = useCallback((analysis: StoredAnalysis) => {
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

  // Server view
  if (useServer) {
    return (
      <div className={styles.container}>
        <button className={styles.backNav} onClick={onClose}>← Back</button>
        <div className={styles.header}>
          <h2 className={styles.title}>Past Analyses</h2>
        </div>

        {serverLoading && <p style={{ padding: '16px', color: 'var(--uitraps-text-secondary)' }}>Loading…</p>}
        {serverError && <p style={{ padding: '16px', color: 'var(--uitraps-error)' }}>{serverError}</p>}

        {!serverLoading && !serverError && serverReports.length === 0 && (
          <div className={styles.empty}>
            <div className={styles.emptyTitle}>No Past Analyses</div>
            <p className={styles.emptyText}>Your completed analyses will appear here.</p>
          </div>
        )}

        <div className={styles.list}>
          {serverReports.map(r => (
            <div key={r.id} className={styles.card}>
              <div className={styles.cardName}>{serverReportDisplayName(r)}</div>
              <div className={styles.cardDate}>{formatDate(r.timestamp)}</div>
              {r.statistics && (
                <div className={styles.statsRow}>
                  {(r.statistics.critical_count ?? 0) > 0 && (
                    <span className={`${styles.statBadge} ${styles.critical}`}>{r.statistics.critical_count} Critical</span>
                  )}
                  {(r.statistics.moderate_count ?? 0) > 0 && (
                    <span className={`${styles.statBadge} ${styles.moderate}`}>{r.statistics.moderate_count} Moderate</span>
                  )}
                  {(r.statistics.minor_count ?? 0) > 0 && (
                    <span className={`${styles.statBadge} ${styles.minor}`}>{r.statistics.minor_count} Minor</span>
                  )}
                  {(r.statistics.positive_count ?? 0) > 0 && (
                    <span className={`${styles.statBadge} ${styles.positive}`}>{r.statistics.positive_count} Positive</span>
                  )}
                </div>
              )}
              <div className={styles.cardActions}>
                <button
                  className={styles.viewButton}
                  onClick={() => handleViewServer(r)}
                  disabled={loadingReportId === r.id}
                >
                  {loadingReportId === r.id ? 'Loading…' : 'View Report'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Local (localStorage) view
  if (localAnalyses.length === 0) {
    return (
      <div className={styles.container}>
        <button className={styles.backNav} onClick={onClose}>← Back</button>
        <div className={styles.empty}>
          <div className={styles.emptyTitle}>No Past Analyses</div>
          <p className={styles.emptyText}>
            Your completed analyses will appear here. Run an analysis to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <button className={styles.backNav} onClick={onClose}>← Back</button>
      <div className={styles.header}>
        <h2 className={styles.title}>Past Analyses</h2>
        <span className={styles.count}>{localAnalyses.length} of {HISTORY_LIMIT}</span>
      </div>

      <div className={styles.list}>
        {localAnalyses.map(analysis => (
          <div key={analysis.id} className={styles.card}>
            <div className={styles.cardName}>{getDisplayName(analysis)}</div>
            <div className={styles.cardDate}>{formatDate(analysis.timestamp)}</div>

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
              <button className={styles.viewButton} onClick={() => onViewReport(analysis)}>
                View Report
              </button>
              {onReuseSettings && analysis.formSnapshot && (
                <button className={styles.downloadButton} onClick={() => onReuseSettings(analysis)}>
                  Re-use settings
                </button>
              )}
              <button className={styles.downloadButton} onClick={() => handleDownloadLocal(analysis)}>
                Download
              </button>
              <button className={styles.deleteButton} onClick={() => handleDeleteLocal(analysis.id)}>
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
