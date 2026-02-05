import React, { useState, useCallback, useMemo } from 'react';
import { FileUpload } from './FileUpload';
import { ContextInputs } from './ContextInputs';
import { LimitationsNotice } from './LimitationsNotice';
import { ContentType } from '../api/types';
import styles from './AnalyzerForm.module.css';

interface AnalyzerFormProps {
  files: File[];
  users: string;
  tasks: string;
  format: string;
  contentType: ContentType;
  onFilesChange: (files: File[]) => void;
  onUsersChange: (value: string) => void;
  onTasksChange: (value: string) => void;
  onFormatChange: (value: string) => void;
  onContentTypeChange: (value: ContentType) => void;
  onSubmit: () => void;
  disabled?: boolean;
  isEstimating?: boolean;
}

const MIN_CONTEXT_LENGTH = 10;

export const AnalyzerForm: React.FC<AnalyzerFormProps> = ({
  files,
  users,
  tasks,
  format,
  contentType,
  onFilesChange,
  onUsersChange,
  onTasksChange,
  onFormatChange,
  onContentTypeChange,
  onSubmit,
  disabled = false,
  isEstimating = false,
}) => {
  const [errors, setErrors] = useState<{
    files?: string;
    users?: string;
    tasks?: string;
    format?: string;
  }>({});

  const validate = useCallback((): boolean => {
    const newErrors: typeof errors = {};

    if (files.length === 0) {
      newErrors.files = 'Please upload at least one screenshot or video';
    }

    if (users.trim().length < MIN_CONTEXT_LENGTH) {
      newErrors.users = `Please enter at least ${MIN_CONTEXT_LENGTH} characters`;
    }

    if (tasks.trim().length < MIN_CONTEXT_LENGTH) {
      newErrors.tasks = `Please enter at least ${MIN_CONTEXT_LENGTH} characters`;
    }

    if (format.trim().length < MIN_CONTEXT_LENGTH) {
      newErrors.format = `Please enter at least ${MIN_CONTEXT_LENGTH} characters`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [files, users, tasks, format]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit();
    }
  }, [validate, onSubmit]);

  const isFormValid = files.length > 0 &&
    users.trim().length >= MIN_CONTEXT_LENGTH &&
    tasks.trim().length >= MIN_CONTEXT_LENGTH &&
    format.trim().length >= MIN_CONTEXT_LENGTH;

  // Check if any file is a video
  const isVideo = useMemo(() => {
    return files.some(f => ['video/mp4', 'video/quicktime', 'video/webm'].includes(f.type));
  }, [files]);

  // Determine button text based on file count
  const getButtonText = () => {
    if (isEstimating) return 'Calculating...';
    if (files.length === 0) return 'Analyze Design';
    if (files.length === 1) {
      const isVideo = ['video/mp4', 'video/quicktime', 'video/webm'].includes(files[0].type);
      return isVideo ? 'Analyze Video' : 'Analyze Design';
    }
    return `Analyze ${files.length} Screenshots`;
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>1. Upload Design</h3>
        <FileUpload
          files={files}
          onFilesSelect={onFilesChange}
          error={errors.files}
          disabled={disabled || isEstimating}
          acceptVideo={true}
          maxFiles={10}
        />
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>2. Provide Context</h3>
        <ContextInputs
          users={users}
          tasks={tasks}
          format={format}
          contentType={contentType}
          onUsersChange={onUsersChange}
          onTasksChange={onTasksChange}
          onFormatChange={onFormatChange}
          onContentTypeChange={onContentTypeChange}
          errors={errors}
          disabled={disabled || isEstimating}
        />
      </div>

      {/* Show limitations notice for video or game content */}
      <LimitationsNotice
        contentType={contentType}
        isVideo={isVideo}
        show={isVideo || contentType === 'game'}
      />

      <button
        type="submit"
        className={styles.submitButton}
        disabled={disabled || isEstimating || !isFormValid}
      >
        {isEstimating ? (
          <span className={styles.spinner} />
        ) : (
          <svg className={styles.buttonIcon} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        )}
        {getButtonText()}
      </button>

      <p className={styles.disclaimer}>
        {files.length > 1 || (files.length === 1 && ['video/mp4', 'video/quicktime', 'video/webm'].includes(files[0]?.type))
          ? 'You will see time and cost estimates before analysis starts.'
          : 'Analysis typically takes 30-60 seconds. Please keep this window open.'}
      </p>
    </form>
  );
};

export default AnalyzerForm;
