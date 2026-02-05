import React, { useCallback, useRef, useState } from 'react';
import { FileUploadProps } from '../api/types';
import styles from './FileUpload.module.css';

const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_VIDEO_SIZE = 100 * 1024 * 1024; // 100MB
const IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/jpg'];
const VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/webm'];

export const FileUpload: React.FC<FileUploadProps> = ({
  files,
  onFilesSelect,
  error,
  disabled = false,
  maxFiles = 10,
  acceptVideo = true,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const acceptedTypes = acceptVideo
    ? [...IMAGE_TYPES, ...VIDEO_TYPES]
    : IMAGE_TYPES;

  const isVideo = (file: File) => VIDEO_TYPES.includes(file.type);
  const isImage = (file: File) => IMAGE_TYPES.includes(file.type);

  const validateFiles = useCallback((fileList: File[]): string | null => {
    if (fileList.length === 0) {
      return 'Please select at least one file';
    }

    if (fileList.length > maxFiles) {
      return `Maximum ${maxFiles} files allowed`;
    }

    // Check for mixed types
    const hasVideos = fileList.some(isVideo);
    const hasImages = fileList.some(isImage);

    if (hasVideos && hasImages) {
      return 'Cannot mix images and videos. Please upload one type.';
    }

    if (hasVideos && fileList.length > 1) {
      return 'Only one video file allowed at a time';
    }

    for (const file of fileList) {
      if (!acceptedTypes.includes(file.type)) {
        const types = acceptVideo ? 'PNG, JPEG, MP4, MOV, or WebM' : 'PNG or JPEG';
        return `Unsupported file type: ${file.name}. Please upload ${types}`;
      }

      const maxSize = isVideo(file) ? MAX_VIDEO_SIZE : MAX_IMAGE_SIZE;
      const maxSizeMB = maxSize / (1024 * 1024);

      if (file.size > maxSize) {
        return `${file.name} is too large. Maximum size is ${maxSizeMB}MB`;
      }
    }

    return null;
  }, [acceptedTypes, acceptVideo, maxFiles]);

  const handleFiles = useCallback((newFiles: File[]) => {
    const validationError = validateFiles(newFiles);
    if (validationError) {
      setLocalError(validationError);
      onFilesSelect([]);
    } else {
      setLocalError(null);
      onFilesSelect(newFiles);
    }
  }, [validateFiles, onFilesSelect]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  }, [disabled, handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleClick = useCallback(() => {
    if (!disabled) {
      inputRef.current?.click();
    }
  }, [disabled]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (selectedFiles.length > 0) {
      handleFiles(selectedFiles);
    }
  }, [handleFiles]);

  const handleRemove = useCallback((e: React.MouseEvent, index?: number) => {
    e.stopPropagation();
    setLocalError(null);

    if (index !== undefined) {
      // Remove specific file
      const newFiles = files.filter((_, i) => i !== index);
      onFilesSelect(newFiles);
    } else {
      // Remove all
      onFilesSelect([]);
    }

    if (inputRef.current) {
      inputRef.current.value = '';
    }
  }, [files, onFilesSelect]);

  const displayError = error || localError;

  // Determine input type for display
  const hasVideo = files.some(isVideo);
  const fileCount = files.length;
  const totalSize = files.reduce((sum, f) => sum + f.size, 0);

  // Build accept string
  const acceptString = acceptVideo
    ? 'image/png,image/jpeg,image/jpg,video/mp4,video/quicktime,video/webm'
    : 'image/png,image/jpeg,image/jpg';

  return (
    <div className={styles.container}>
      <div
        className={`${styles.dropzone} ${isDragging ? styles.dragging : ''} ${files.length > 0 ? styles.hasFile : ''} ${disabled ? styles.disabled : ''} ${displayError ? styles.error : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload files"
      >
        <input
          ref={inputRef}
          type="file"
          accept={acceptString}
          onChange={handleInputChange}
          className={styles.input}
          disabled={disabled}
          aria-hidden="true"
          multiple={!hasVideo}
        />

        {files.length > 0 ? (
          <div className={styles.preview}>
            {/* Show thumbnail(s) */}
            <div className={styles.thumbnails}>
              {files.slice(0, 4).map((file, index) => (
                <div key={index} className={styles.thumbnailWrapper}>
                  {isImage(file) ? (
                    <img
                      src={URL.createObjectURL(file)}
                      alt={`Preview ${index + 1}`}
                      className={styles.previewImage}
                    />
                  ) : (
                    <div className={styles.videoPlaceholder}>
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <polygon points="5 3 19 12 5 21 5 3"/>
                      </svg>
                    </div>
                  )}
                  {files.length > 1 && (
                    <button
                      type="button"
                      className={styles.thumbnailRemove}
                      onClick={(e) => handleRemove(e, index)}
                      aria-label={`Remove ${file.name}`}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
              {files.length > 4 && (
                <div className={styles.moreFiles}>
                  +{files.length - 4} more
                </div>
              )}
            </div>

            {/* File info summary */}
            <div className={styles.fileInfo}>
              <span className={styles.fileName}>
                {hasVideo ? (
                  <>Video: {files[0].name}</>
                ) : fileCount === 1 ? (
                  files[0].name
                ) : (
                  <>{fileCount} screenshots selected</>
                )}
              </span>
              <span className={styles.fileSize}>
                {(totalSize / 1024 / 1024).toFixed(2)} MB total
              </span>
            </div>

            {/* Clear all button */}
            <button
              type="button"
              className={styles.removeButton}
              onClick={(e) => handleRemove(e)}
              aria-label="Remove all files"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 8.586L15.293 3.293a1 1 0 111.414 1.414L11.414 10l5.293 5.293a1 1 0 01-1.414 1.414L10 11.414l-5.293 5.293a1 1 0 01-1.414-1.414L8.586 10 3.293 4.707a1 1 0 011.414-1.414L10 8.586z"/>
              </svg>
            </button>
          </div>
        ) : (
          <div className={styles.placeholder}>
            <svg className={styles.icon} width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <p className={styles.text}>
              <span className={styles.highlight}>Click to upload</span> or drag and drop
            </p>
            <p className={styles.hint}>
              {acceptVideo ? (
                <>
                  Screenshots (PNG, JPEG) or Video (MP4, MOV, WebM)
                  <br />
                  <span className={styles.subHint}>
                    Upload 1-{maxFiles} screenshots, or 1 video (max 100MB)
                  </span>
                </>
              ) : (
                <>PNG or JPEG (max 10MB)</>
              )}
            </p>
          </div>
        )}
      </div>

      {displayError && (
        <p className={styles.errorMessage}>{displayError}</p>
      )}
    </div>
  );
};

export default FileUpload;
