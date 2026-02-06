import React from 'react';
import { EstimatePreviewProps, isFigmaEstimate, isUrlEstimate, isFileEstimate } from '../api/types';
import styles from './EstimatePreview.module.css';

export const EstimatePreview: React.FC<EstimatePreviewProps> = ({
  estimate,
  onConfirm,
  onBack,
  isLoading = false,
}) => {
  const getInputTypeLabel = () => {
    if (isFigmaEstimate(estimate)) {
      return estimate.file_name || 'Figma File';
    }
    if (isUrlEstimate(estimate)) {
      try {
        return new URL(estimate.url).hostname;
      } catch {
        return 'Website';
      }
    }
    if (isFileEstimate(estimate)) {
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
    }
    return 'Files';
  };

  const getInputTypeIcon = () => {
    if (isFigmaEstimate(estimate)) {
      // Figma icon
      return (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M5 5.5A3.5 3.5 0 018.5 2H12v7H8.5A3.5 3.5 0 015 5.5z"/>
          <path d="M12 2h3.5a3.5 3.5 0 110 7H12V2z"/>
          <path d="M12 12.5a3.5 3.5 0 117 0 3.5 3.5 0 11-7 0z"/>
          <path d="M5 19.5A3.5 3.5 0 018.5 16H12v3.5a3.5 3.5 0 11-7 0z"/>
          <path d="M5 12.5A3.5 3.5 0 018.5 9H12v7H8.5A3.5 3.5 0 015 12.5z"/>
        </svg>
      );
    }
    if (isUrlEstimate(estimate)) {
      // Globe icon for website
      return (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
        </svg>
      );
    }
    if (isFileEstimate(estimate) && estimate.input_type === 'video') {
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

  const getTimeEstimate = () => {
    if (isFigmaEstimate(estimate) || isUrlEstimate(estimate)) {
      return estimate.time_estimate.description;
    }
    if (isFileEstimate(estimate)) {
      return `${estimate.time_estimate.min_formatted} - ${estimate.time_estimate.max_formatted}`;
    }
    return 'Unknown';
  };

  const getCostEstimate = () => {
    if (isFigmaEstimate(estimate) || isUrlEstimate(estimate)) {
      return estimate.cost_estimate.description;
    }
    if (isFileEstimate(estimate)) {
      const { min_credits, max_credits } = estimate.cost_estimate;
      return min_credits === max_credits
        ? `${min_credits} credit${min_credits !== 1 ? 's' : ''}`
        : `${min_credits}-${max_credits} credits`;
    }
    return 'Unknown';
  };

  const getCostDollars = () => {
    if (isFileEstimate(estimate)) {
      return `($${estimate.cost_estimate.min_dollars.toFixed(2)} - $${estimate.cost_estimate.max_dollars.toFixed(2)})`;
    }
    return null;
  };

  const getSubtitle = () => {
    if (isFigmaEstimate(estimate)) {
      return `${estimate.frame_count} frames${estimate.has_prototype_flows ? ` + ${estimate.flow_count} flows` : ''}`;
    }
    if (isUrlEstimate(estimate)) {
      return `Up to ${estimate.estimated_pages} pages`;
    }
    return getInputTypeLabel();
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.icon}>
          {getInputTypeIcon()}
        </div>
        <h3 className={styles.title}>Ready to Analyze</h3>
        <p className={styles.subtitle}>{getSubtitle()}</p>
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
              {getTimeEstimate()}
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
              {getCostEstimate()}
            </span>
            {getCostDollars() && (
              <span className={styles.estimateDollars}>
                {getCostDollars()}
              </span>
            )}
          </div>
        </div>

        {/* Video-specific info */}
        {isFileEstimate(estimate) && estimate.input_type === 'video' && estimate.estimated_frames && (
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

        {/* Figma prototype flows info */}
        {isFigmaEstimate(estimate) && estimate.has_prototype_flows && (
          <div className={styles.estimateCard}>
            <div className={styles.estimateIcon}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
            </div>
            <div className={styles.estimateContent}>
              <span className={styles.estimateLabel}>Prototype Flows</span>
              <span className={styles.estimateValue}>
                {estimate.flow_count} navigation flows detected
              </span>
            </div>
          </div>
        )}

        {/* FFmpeg warning for video */}
        {isFileEstimate(estimate) && estimate.input_type === 'video' && !estimate.ffmpeg_available && (
          <div className={styles.warning}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>Video analysis may not be available on this server.</span>
          </div>
        )}

        {/* Figma availability warning */}
        {isFigmaEstimate(estimate) && !estimate.figma_available && (
          <div className={styles.warning}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>Figma analysis may not be available. Check FIGMA_TOKEN configuration.</span>
          </div>
        )}

        {/* Playwright availability warning */}
        {isUrlEstimate(estimate) && !estimate.playwright_available && (
          <div className={styles.warning}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>Website crawling may not be available. Playwright not installed.</span>
          </div>
        )}
      </div>

      {/* File size info - only for file estimates */}
      {isFileEstimate(estimate) && (
        <p className={styles.sizeInfo}>
          Total size: {estimate.total_size_mb.toFixed(2)} MB
        </p>
      )}

      {/* URL display for URL estimates */}
      {isUrlEstimate(estimate) && (
        <p className={styles.sizeInfo}>
          {estimate.url}
        </p>
      )}

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
