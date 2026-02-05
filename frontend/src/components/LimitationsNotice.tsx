import React from 'react';
import styles from './LimitationsNotice.module.css';
import { ContentType } from '../api/types';

interface LimitationsNoticeProps {
  contentType: ContentType;
  isVideo: boolean;
  show?: boolean;
}

export const LimitationsNotice: React.FC<LimitationsNoticeProps> = ({
  contentType,
  isVideo,
  show = true,
}) => {
  if (!show) return null;

  // Show notice for games or videos
  const showGameNotice = contentType === 'game';
  const showVideoNotice = isVideo;

  if (!showGameNotice && !showVideoNotice) return null;

  return (
    <div className={styles.container}>
      {showVideoNotice && (
        <div className={styles.notice}>
          <div className={styles.icon}>📹</div>
          <div className={styles.content}>
            <h4 className={styles.title}>Video Analysis Limitations</h4>
            <p className={styles.description}>
              This analyzer works by extracting static frames from your video. It cannot detect:
            </p>
            <ul className={styles.list}>
              <li>Animations, transitions, or motion effects</li>
              <li>Interaction feedback (hover states, click responses)</li>
              <li>Loading sequence timing or progress</li>
              <li>Audio cues or sound feedback</li>
            </ul>
            <p className={styles.note}>
              We automatically filter out loading screens and blank frames, but some may still appear in the analysis.
            </p>
          </div>
        </div>
      )}

      {showGameNotice && (
        <div className={`${styles.notice} ${styles.warning}`}>
          <div className={styles.icon}>🎮</div>
          <div className={styles.content}>
            <h4 className={styles.title}>Game Analysis - Limited Scope</h4>
            <p className={styles.description}>
              This analyzer is optimized for traditional UI, not gameplay. Analysis is limited to:
            </p>
            <ul className={styles.list}>
              <li>Menus and settings screens</li>
              <li>HUD elements and overlays</li>
              <li>Tutorial and help systems</li>
              <li>Inventory and status screens</li>
            </ul>
            <p className={styles.note}>
              Gameplay mechanics, real-time interactions, and immersive elements cannot be evaluated.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LimitationsNotice;
