/**
 * Small badge showing the detected input mode.
 * Updates in real-time as user types or attaches files.
 */

import React from 'react';
import styles from './ModeIndicator.module.css';

interface ModeIndicatorProps {
  mode: 'chat' | 'analysis' | 'hybrid' | 'idle';
}

const MODE_LABELS: Record<string, string> = {
  chat: 'Chat',
  analysis: 'Analysis',
  hybrid: 'Hybrid',
  idle: 'Ready',
};

export const ModeIndicator: React.FC<ModeIndicatorProps> = ({ mode }) => {
  return (
    <span className={`${styles.indicator} ${styles[mode]}`}>
      {MODE_LABELS[mode]}
    </span>
  );
};
