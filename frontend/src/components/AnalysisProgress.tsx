import React, { useMemo } from 'react';
import { AnalysisProgressProps, InputType, TimeEstimate } from '../api/types';
import { formatElapsedTime } from '../hooks/useElapsedTime';
import styles from './AnalysisProgress.module.css';

interface Phase {
  label: string;
  duration: number;
}

// Phases for single image analysis
const SINGLE_IMAGE_PHASES: Phase[] = [
  { label: 'Uploading image...', duration: 3 },
  { label: 'Processing screenshot...', duration: 5 },
  { label: 'Analyzing UI patterns...', duration: 20 },
  { label: 'Identifying potential traps...', duration: 15 },
  { label: 'Generating report...', duration: 10 },
  { label: 'Finalizing...', duration: 7 },
];

// Phases for multi-image analysis
const MULTI_IMAGE_PHASES: Phase[] = [
  { label: 'Uploading images...', duration: 5 },
  { label: 'Processing screenshots...', duration: 10 },
  { label: 'Analyzing UI patterns across screens...', duration: 40 },
  { label: 'Detecting cross-page traps...', duration: 30 },
  { label: 'Aggregating findings...', duration: 20 },
  { label: 'Generating comprehensive report...', duration: 15 },
  { label: 'Finalizing...', duration: 10 },
];

// Phases for video analysis
const VIDEO_PHASES: Phase[] = [
  { label: 'Uploading video...', duration: 10 },
  { label: 'Extracting key frames...', duration: 20 },
  { label: 'Processing frames...', duration: 30 },
  { label: 'Analyzing interaction patterns...', duration: 60 },
  { label: 'Detecting motion-dependent traps...', duration: 45 },
  { label: 'Aggregating findings across timeline...', duration: 30 },
  { label: 'Generating comprehensive report...', duration: 20 },
  { label: 'Finalizing...', duration: 15 },
];

function getPhases(inputType?: InputType): Phase[] {
  switch (inputType) {
    case 'video':
      return VIDEO_PHASES;
    case 'multi_image':
      return MULTI_IMAGE_PHASES;
    default:
      return SINGLE_IMAGE_PHASES;
  }
}

function getCurrentPhase(elapsedTime: number, phases: Phase[]): Phase {
  let accumulated = 0;

  for (const phase of phases) {
    accumulated += phase.duration;
    if (elapsedTime < accumulated) {
      return phase;
    }
  }

  return phases[phases.length - 1];
}

function calculateProgress(elapsedTime: number, estimatedTime?: TimeEstimate): number {
  // Use estimated max time if available, otherwise use a default
  const maxTime = estimatedTime?.max_seconds || 60;
  const progress = (elapsedTime / maxTime) * 100;
  // Cap at 95% until complete
  return Math.min(progress, 95);
}

function getInputTypeLabel(inputType?: InputType, fileCount?: number): string {
  switch (inputType) {
    case 'video':
      return 'Video Recording';
    case 'multi_image':
      return `${fileCount || 'Multiple'} Screenshots`;
    default:
      return 'Screenshot';
  }
}

function getHelpText(inputType?: InputType, estimatedTime?: TimeEstimate): string {
  if (estimatedTime) {
    return `Estimated time: ${estimatedTime.min_formatted} - ${estimatedTime.max_formatted}. Please keep this window open.`;
  }

  switch (inputType) {
    case 'video':
      return 'Video analysis typically takes 3-15 minutes depending on length. Please keep this window open.';
    case 'multi_image':
      return 'Multi-screenshot analysis typically takes 1-5 minutes. Please keep this window open.';
    default:
      return 'This typically takes 30-60 seconds. Please keep this window open.';
  }
}

function getExtendedWaitThreshold(inputType?: InputType): number {
  switch (inputType) {
    case 'video':
      return 600; // 10 minutes
    case 'multi_image':
      return 300; // 5 minutes
    default:
      return 90; // 1.5 minutes
  }
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  elapsedTime,
  onCancel,
  inputType,
  fileCount,
  estimatedTime,
}) => {
  const phases = useMemo(() => getPhases(inputType), [inputType]);
  const currentPhase = useMemo(() => getCurrentPhase(elapsedTime, phases), [elapsedTime, phases]);
  const progress = useMemo(() => calculateProgress(elapsedTime, estimatedTime), [elapsedTime, estimatedTime]);
  const inputLabel = useMemo(() => getInputTypeLabel(inputType, fileCount), [inputType, fileCount]);
  const helpText = useMemo(() => getHelpText(inputType, estimatedTime), [inputType, estimatedTime]);
  const extendedWaitThreshold = useMemo(() => getExtendedWaitThreshold(inputType), [inputType]);

  const isExtendedWait = elapsedTime > extendedWaitThreshold;

  return (
    <div className={styles.container}>
      <div className={styles.iconContainer}>
        <svg className={styles.spinner} viewBox="0 0 50 50">
          <circle
            className={styles.spinnerPath}
            cx="25"
            cy="25"
            r="20"
            fill="none"
            strokeWidth="4"
          />
        </svg>
      </div>

      <h3 className={styles.title}>Analyzing Your Design</h3>

      {inputType && inputType !== 'single_image' && (
        <p className={styles.inputType}>
          {inputLabel}
        </p>
      )}

      <p className={styles.elapsed}>
        {formatElapsedTime(elapsedTime)} elapsed
      </p>

      <div className={styles.progressBar}>
        <div
          className={styles.progressFill}
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className={styles.phaseLabel}>{currentPhase.label}</p>

      <p className={styles.helpText}>
        {helpText}
      </p>

      {isExtendedWait && (
        <p className={styles.extendedWait}>
          Taking longer than usual. Complex designs may require additional processing time.
        </p>
      )}

      {onCancel && (
        <button
          type="button"
          className={styles.cancelButton}
          onClick={onCancel}
        >
          Cancel
        </button>
      )}
    </div>
  );
};

export default AnalysisProgress;
