/**
 * Unified input component with text area, file drop zone, and context settings.
 *
 * - Type a question → chat mode
 * - Drop/attach files + fill context → analysis mode
 * - Drop files + type question → hybrid mode
 */

import React, { useRef, useState, useCallback, useEffect } from 'react';
import { ContentType } from '../api/types';
import styles from './UnifiedInput.module.css';

type DetectedMode = 'chat' | 'analysis' | 'hybrid' | 'idle' | 'figma' | 'url' | 'pdf' | 'video';

interface UnifiedInputProps {
  inputText: string;
  onInputTextChange: (text: string) => void;
  files: File[];
  onFilesChange: (files: File[]) => void;
  users: string;
  onUsersChange: (v: string) => void;
  tasks: string;
  onTasksChange: (v: string) => void;
  format: string;
  onFormatChange: (v: string) => void;
  contentType: ContentType;
  onContentTypeChange: (v: ContentType) => void;
  contextExpanded: boolean;
  onContextExpandedChange?: (v: boolean) => void;
  detectedMode: DetectedMode;
  isLoading: boolean;
  onSubmit: () => void;
  centered?: boolean;
  placeholder?: string;
}

// Accepted file types for analysis
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/jpg'];
const ACCEPTED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/webm'];
const ACCEPTED_DOCUMENT_TYPES = ['application/pdf'];
const ACCEPTED_TYPES = [...ACCEPTED_IMAGE_TYPES, ...ACCEPTED_VIDEO_TYPES, ...ACCEPTED_DOCUMENT_TYPES];

// Helper to categorize file type
function getFileCategory(file: File): 'image' | 'video' | 'pdf' | 'unknown' {
  if (ACCEPTED_IMAGE_TYPES.includes(file.type)) return 'image';
  if (ACCEPTED_VIDEO_TYPES.includes(file.type)) return 'video';
  if (ACCEPTED_DOCUMENT_TYPES.includes(file.type) || file.name.toLowerCase().endsWith('.pdf')) return 'pdf';
  return 'unknown';
}

// Get file icon based on type
function getFileIcon(file: File): string {
  const category = getFileCategory(file);
  switch (category) {
    case 'video': return '🎬';
    case 'pdf': return '📄';
    default: return '📷';
  }
}

export const UnifiedInput: React.FC<UnifiedInputProps> = ({
  inputText,
  onInputTextChange,
  files,
  onFilesChange,
  users,
  onUsersChange,
  tasks,
  onTasksChange,
  format,
  onFormatChange,
  contentType,
  onContentTypeChange,
  contextExpanded,
  // onContextExpandedChange is available for future use
  detectedMode,
  isLoading,
  onSubmit,
  centered = false,
  placeholder,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Auto-focus the textarea when component mounts
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && detectedMode !== 'idle') {
        onSubmit();
      }
    }
  }, [isLoading, detectedMode, onSubmit]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = Array.from(e.dataTransfer.files).filter(
      f => ACCEPTED_TYPES.includes(f.type) || f.name.toLowerCase().endsWith('.pdf'),
    );
    if (dropped.length > 0) {
      onFilesChange([...files, ...dropped].slice(0, 10));
    }
  }, [files, onFilesChange]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []).filter(
      f => ACCEPTED_TYPES.includes(f.type) || f.name.toLowerCase().endsWith('.pdf'),
    );
    if (selected.length > 0) {
      onFilesChange([...files, ...selected].slice(0, 10));
    }
    e.target.value = '';
  }, [files, onFilesChange]);

  const removeFile = useCallback((index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  }, [files, onFilesChange]);

  // Auto-resize textarea
  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onInputTextChange(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  }, [onInputTextChange]);

  return (
    <div className={`${styles.container} ${centered ? styles.centered : ''}`}>
      {/* File previews */}
      {files.length > 0 && (
        <div className={styles.filePreviews}>
          {files.map((f, i) => (
            <div key={i} className={styles.fileChip}>
              <span className={styles.fileIcon}>{getFileIcon(f)}</span>
              {f.name.length > 20 ? f.name.slice(0, 17) + '...' : f.name}
              <span className={styles.fileChipRemove} onClick={() => removeFile(i)}>
                ×
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Main input row */}
      <div className={styles.inputRow}>
        <div className={styles.textareaWrapper}>
          <button
            className={styles.addButton}
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            data-tooltip="Upload images or videos"
            type="button"
          >
            +
          </button>
          <textarea
            ref={textareaRef}
            className={`${styles.textarea} ${isDragging ? styles.dragging : ''}`}
            placeholder={
              placeholder !== undefined
                ? placeholder
                : files.length > 0
                  ? 'Add context for analysis, or ask a question about these files...'
                  : 'Ask about UI traps, or drop images/video/PDF for analysis...'
            }
            value={inputText}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            disabled={isLoading}
            rows={1}
          />
        </div>

        <button
          className={styles.sendButton}
          onClick={onSubmit}
          disabled={isLoading || detectedMode === 'idle'}
          title="Send"
        >
          {isLoading ? '...' : '→'}
        </button>
      </div>


      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className={styles.hiddenInput}
        accept=".png,.jpg,.jpeg,.mp4,.mov,.webm,.pdf"
        multiple
        onChange={handleFileSelect}
      />

      {/* Context settings panel */}
      {contextExpanded && (
        <div className={styles.contextPanel}>
          <div className={styles.contextTitle}>Analysis Context</div>
          <div className={styles.contextGrid}>
            <div className={styles.contextField}>
              <label className={styles.contextLabel}>Who are the users?</label>
              <textarea
                className={styles.contextInput}
                value={users}
                onChange={e => onUsersChange(e.target.value)}
                placeholder="e.g., First-time visitors, ages 25-45"
                rows={2}
              />
            </div>
            <div className={styles.contextField}>
              <label className={styles.contextLabel}>What are they trying to do?</label>
              <textarea
                className={styles.contextInput}
                value={tasks}
                onChange={e => onTasksChange(e.target.value)}
                placeholder="e.g., Sign up for an account"
                rows={2}
              />
            </div>
            <div className={styles.contextField}>
              <label className={styles.contextLabel}>What format is this?</label>
              <textarea
                className={styles.contextInput}
                value={format}
                onChange={e => onFormatChange(e.target.value)}
                placeholder="e.g., Mobile app screenshot"
                rows={2}
              />
            </div>
            <div className={styles.contextField}>
              <label className={styles.contextLabel}>Content type</label>
              <select
                className={styles.contextInput}
                value={contentType}
                onChange={e => onContentTypeChange(e.target.value as ContentType)}
              >
                <option value="website">Website</option>
                <option value="mobile_app">Mobile App</option>
                <option value="desktop_app">Desktop App</option>
                <option value="game">Game</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
