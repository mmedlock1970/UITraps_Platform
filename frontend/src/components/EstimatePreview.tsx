import React from 'react';
import { EstimatePreviewProps } from '../api/types';
import styles from './EstimatePreview.module.css';

export const EstimatePreview: React.FC<EstimatePreviewProps> = ({
  estimate,
  onConfirm,
  onBack,
  isLoading = false,
}) => {
  const getInputTypeLabel = () => {
    switch (estimate.input_type) {
      case 'single_image':
        return '1 Screenshot';
      case 'multi_image':
        return `${estimate.file_count} Screenshots`;
      case 'video':
        return 'Video Recording';
      default:
        return 'Files';
    }
  };

  const getInputTypeIcon = () => {
    if (estimate.input_type === 'video') {
      return (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
      );
    }
    return (
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
    );
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.icon}>
          {getInputTypeIcon()}
        </div>
        <h3 className={styles.title}>Ready to Analyze</h3>
        <p className={styles.subtitle}>{getInputTypeLabel()}</p>
      </div>

      <div className={styles.estimates}>
        {/* Time Estimate */}
        <div className={styles.estimateCard}>
          <div className={styles.estimateIcon}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div className={styles.estimateContent}>
            <span className={styles.estimateLabel}>Estimated Time</span>
            <span className={styles.estimateValue}>
              {estimate.time_estimate.min_formatted} - {estimate.time_estimate.max_formatted}
            </span>
          </div>
        </div>

        {/* Cost Estimate */}
        <div className={styles.estimateCard}>
          <div className={styles.estimateIcon}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v12M9 9h6M9 15h6"/>
            </svg>
          </div>
          <div className={styles.estimateContent}>
            <span className={styles.estimateLabel}>Cost</span>
            <span className={styles.estimateValue}>
              {estimate.cost_estimate.min_credits === estimate.cost_estimate.max_credits
                ? `${estimate.cost_estimate.min_credits} credit${estimate.cost_estimate.min_credits !== 1 ? 's' : ''}`
                : `${estimate.cost_estimate.min_credits}-${estimate.cost_estimate.max_credits} credits`
              }
            </span>
            <span className={styles.estimateDollars}>
              (${estimate.cost_estimate.min_dollars.toFixed(2)} - ${estimate.cost_estimate.max_dollars.toFixed(2)})
            </span>
          </div>
        </div>

        {/* Video-specific info */}
        {estimate.input_type === 'video' && estimate.estimated_frames && (
          <div className={styles.estimateCard}>
            <div className={styles.estimateIcon}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/>
                <line x1="7" y1="2" x2="7" y2="22"/>
                <line x1="17" y1="2" x2="17" y2="22"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <line x1="2" y1="7" x2="7" y2="7"/>
                <line x1="2" y1="17" x2="7" y2="17"/>
                <line x1="17" y1="7" x2="22" y2="7"/>
                <line x1="17" y1="17" x2="22" y2="17"/>
              </svg>
            </div>
            <div className={styles.estimateContent}>
              <span className={styles.estimateLabel}>Frames to Analyze</span>
              <span className={styles.estimateValue}>
                ~{estimate.estimated_frames} frames
              </span>
              {estimate.video_duration_seconds && (
                <span className={styles.estimateDollars}>
                  from {Math.round(estimate.video_duration_seconds)}s video
                </span>
              )}
            </div>
          </div>
        )}

        {/* FFmpeg warning for video */}
        {estimate.input_type === 'video' && !estimate.ffmpeg_available && (
          <div className={styles.warning}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>Video analysis may not be available on this server.</span>
          </div>
        )}
      </div>

      {/* File size info */}
      <p className={styles.sizeInfo}>
        Total size: {estimate.total_size_mb.toFixed(2)} MB
      </p>

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.backButton}
          onClick={onBack}
          disabled={isLoading}
        >
          Back
        </button>
        <button
          type="button"
          className={styles.confirmButton}
          onClick={onConfirm}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className={styles.spinner} />
              Starting...
            </>
          ) : (
            'Start Analysis'
          )}
        </button>
      </div>
    </div>
  );
};

export default EstimatePreview;
