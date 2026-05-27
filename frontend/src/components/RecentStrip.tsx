import React from 'react';
import { getAnalysisHistory, StoredAnalysis } from '../services/analysisHistory';
import styles from './RecentStrip.module.css';

interface RecentStripProps {
  onViewReport: (analysis: StoredAnalysis) => void;
  onViewAll: () => void;
}

function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export const RecentStrip: React.FC<RecentStripProps> = ({ onViewReport, onViewAll }) => {
  const analyses = getAnalysisHistory();
  if (analyses.length === 0) return null;

  const visible = analyses.slice(0, 3);

  return (
    <div className={styles.strip}>
      <span className={styles.label}>Recent</span>
      <div className={styles.chips}>
        {visible.map(a => (
          <button key={a.id} className={styles.chip} onClick={() => onViewReport(a)}>
            <span className={styles.date}>{shortDate(a.timestamp)}</span>
            {a.statistics && (
              <span className={styles.counts}>
                {a.statistics.critical_count > 0 && (
                  <span className={styles.crit}>{a.statistics.critical_count}C</span>
                )}
                {a.statistics.moderate_count > 0 && (
                  <span className={styles.mod}>{a.statistics.moderate_count}M</span>
                )}
                {a.statistics.minor_count > 0 && (
                  <span className={styles.min}>{a.statistics.minor_count}m</span>
                )}
              </span>
            )}
          </button>
        ))}
      </div>
      <button className={styles.viewAll} onClick={onViewAll}>
        View all ({analyses.length}) →
      </button>
    </div>
  );
};

export default RecentStrip;
