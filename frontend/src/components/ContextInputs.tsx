import React from 'react';
import { ContextInputsProps, ContentType } from '../api/types';
import styles from './ContextInputs.module.css';

const CONTENT_TYPE_OPTIONS: { value: ContentType; label: string; description: string }[] = [
  { value: 'website', label: 'Website', description: 'Web pages, web apps, SaaS products' },
  { value: 'mobile_app', label: 'Mobile App', description: 'iOS/Android applications' },
  { value: 'desktop_app', label: 'Desktop App', description: 'Windows/macOS/Linux applications' },
  { value: 'game', label: 'Video Game', description: 'Games (limited analysis - menus/HUD only)' },
  { value: 'other', label: 'Other', description: 'Other UI types' },
];

export const ContextInputs: React.FC<ContextInputsProps> = ({
  users,
  tasks,
  format,
  contentType,
  onUsersChange,
  onTasksChange,
  onFormatChange,
  onContentTypeChange,
  errors = {},
  disabled = false,
}) => {
  return (
    <div className={styles.container}>
      {/* Content Type Selection - First for context */}
      <div className={styles.field}>
        <label htmlFor="uitraps-content-type" className={styles.label}>
          What type of content is this?
          <span className={styles.required}>*</span>
        </label>
        <select
          id="uitraps-content-type"
          className={styles.select}
          value={contentType}
          onChange={(e) => onContentTypeChange(e.target.value as ContentType)}
          disabled={disabled}
        >
          {CONTENT_TYPE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label} - {option.description}
            </option>
          ))}
        </select>
        {contentType === 'game' && (
          <div className={styles.warningBox}>
            <strong>⚠️ Game Analysis Limitations:</strong>
            <p>This analyzer is optimized for traditional UI. For games, analysis is limited to:</p>
            <ul>
              <li>Menus and settings screens</li>
              <li>HUD elements and overlays</li>
              <li>Tutorial and help systems</li>
              <li>Inventory and status screens</li>
            </ul>
            <p>Gameplay, animations, and real-time interactions cannot be evaluated from static frames.</p>
          </div>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor="uitraps-users" className={styles.label}>
          Who are the users?
          <span className={styles.required}>*</span>
        </label>
        <textarea
          id="uitraps-users"
          className={`${styles.textarea} ${errors.users ? styles.error : ''}`}
          value={users}
          onChange={(e) => onUsersChange(e.target.value)}
          placeholder="e.g., First-time visitors, ages 25-45, looking to purchase products online"
          disabled={disabled}
          rows={3}
        />
        {errors.users && (
          <p className={styles.errorMessage}>{errors.users}</p>
        )}
        <p className={styles.hint}>Describe your target users and their characteristics</p>
      </div>

      <div className={styles.field}>
        <label htmlFor="uitraps-tasks" className={styles.label}>
          What are they trying to do?
          <span className={styles.required}>*</span>
        </label>
        <textarea
          id="uitraps-tasks"
          className={`${styles.textarea} ${errors.tasks ? styles.error : ''}`}
          value={tasks}
          onChange={(e) => onTasksChange(e.target.value)}
          placeholder="e.g., Find a specific product, add it to cart, and complete checkout"
          disabled={disabled}
          rows={3}
        />
        {errors.tasks && (
          <p className={styles.errorMessage}>{errors.tasks}</p>
        )}
        <p className={styles.hint}>Describe the primary tasks users want to accomplish</p>
      </div>

      <div className={styles.field}>
        <label htmlFor="uitraps-format" className={styles.label}>
          What format is this?
          <span className={styles.required}>*</span>
        </label>
        <input
          id="uitraps-format"
          type="text"
          className={`${styles.input} ${errors.format ? styles.error : ''}`}
          value={format}
          onChange={(e) => onFormatChange(e.target.value)}
          placeholder="e.g., Mobile app screenshot, Desktop website, Figma mockup"
          disabled={disabled}
        />
        {errors.format && (
          <p className={styles.errorMessage}>{errors.format}</p>
        )}
        <p className={styles.hint}>Specify the type of design being analyzed</p>
      </div>
    </div>
  );
};

export default ContextInputs;
