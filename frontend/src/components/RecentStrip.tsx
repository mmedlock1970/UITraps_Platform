import React from 'react';
import { getAnalysisHistory } from '../services/analysisHistory';
import styles from './RecentStrip.module.css';

interface RecentStripProps {
  onViewAll: () => void;
}

export const RecentStrip: React.FC<RecentStripProps> = ({ onViewAll }) => {
  const count = getAnalysisHistory().length;
  if (count === 0) return null;

  return (
    <div className={styles.strip}>
      <button className={styles.link} onClick={onViewAll}>
        Past analyses ({count}) →
      </button>
    </div>
  );
};

export default RecentStrip;
