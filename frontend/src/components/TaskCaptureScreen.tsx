/**
 * Task Capture Screen
 *
 * Allows users to capture a task step-by-step by pasting or
 * dropping screenshots. Each screenshot becomes a numbered step.
 * On completion, hands off to the existing estimate/analyze pipeline.
 */

import React, { useCallback, useRef, useState, useEffect } from 'react';
import styles from './TaskCaptureScreen.module.css';

export interface CapturedStep {
  id: string;
  stepNumber: number;
  imageData: string;   // base64 data URL
  fileName: string;
  fileSizeKb: number;
}

interface TaskCaptureScreenProps {
  taskName: string;
  onTaskNameChange: (name: string) => void;
  steps: CapturedStep[];
  onAddStep: (step: CapturedStep) => void;
  onDeleteStep: (id: string) => void;
  onReorderSteps: (steps: CapturedStep[]) => void;
  onFinish: () => void;
  onCancel: () => void;
  /** Estimated cost based on current screenshot count */
  runningCostEstimate?: string;
}

const MAX_SCREENSHOTS = 15;
const WARN_THRESHOLD = 10;
const TARGET_SIZE_KB = 1500; // Compress to ~1.5MB max

/** Compress an image file to reduce upload size */
async function compressImage(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      const canvas = document.createElement('canvas');
      let { width, height } = img;

      // Scale down if very large
      const MAX_DIM = 1920;
      if (width > MAX_DIM || height > MAX_DIM) {
        const scale = Math.min(MAX_DIM / width, MAX_DIM / height);
        width = Math.round(width * scale);
        height = Math.round(height * scale);
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, width, height);

      // Try quality 0.85 first, reduce if still too large
      let quality = 0.85;
      let dataUrl = canvas.toDataURL('image/jpeg', quality);

      // Rough size check (base64 is ~4/3 of binary size)
      const approxKb = (dataUrl.length * 0.75) / 1024;
      if (approxKb > TARGET_SIZE_KB) {
        quality = Math.min(0.85, TARGET_SIZE_KB / approxKb * 0.85);
        dataUrl = canvas.toDataURL('image/jpeg', Math.max(0.5, quality));
      }

      resolve(dataUrl);
    };
    img.onerror = reject;
    img.src = url;
  });
}

/** Get OS-specific screenshot instruction */
function getOSInstructions(): string {
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes('mac')) return 'Press Cmd+Shift+4, then Cmd+V to paste here';
  if (ua.includes('win')) return 'Press Win+Shift+S, then Ctrl+V to paste here';
  return 'Take a screenshot, then Ctrl+V to paste here';
}

let stepIdCounter = 0;
function generateStepId(): string {
  return `step-${Date.now()}-${++stepIdCounter}`;
}

export const TaskCaptureScreen: React.FC<TaskCaptureScreenProps> = ({
  taskName,
  onTaskNameChange,
  steps,
  onAddStep,
  onDeleteStep,
  onReorderSteps,
  onFinish,
  onCancel,
  runningCostEstimate,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskNameLocked, setTaskNameLocked] = useState(!!taskName);
  const [fullViewStep, setFullViewStep] = useState<CapturedStep | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dragOverId, setDragOverId] = useState<string | null>(null);
  const taskInputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  const osInstructions = getOSInstructions();
  const atLimit = steps.length >= MAX_SCREENSHOTS;
  const nearLimit = steps.length >= WARN_THRESHOLD && !atLimit;

  // Focus task name input on mount if no task name yet
  useEffect(() => {
    if (!taskName) taskInputRef.current?.focus();
  }, [taskName]);

  const processImageFile = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError(`"${file.name}" is not an image file. Please paste a screenshot.`);
      return;
    }
    if (steps.length >= MAX_SCREENSHOTS) {
      setError(`Maximum ${MAX_SCREENSHOTS} screenshots per task reached.`);
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const imageData = await compressImage(file);
      const approxKb = Math.round((imageData.length * 0.75) / 1024);

      const step: CapturedStep = {
        id: generateStepId(),
        stepNumber: steps.length + 1,
        imageData,
        fileName: file.name || `screenshot-${steps.length + 1}.jpg`,
        fileSizeKb: approxKb,
      };
      onAddStep(step);
    } catch {
      setError('Failed to process that image. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  }, [steps.length, onAddStep]);

  const processFiles = useCallback(async (files: FileList | File[]) => {
    const fileArr = Array.from(files);
    const imageFiles = fileArr.filter(f => f.type.startsWith('image/'));
    const skipped = fileArr.filter(f => !f.type.startsWith('image/'));

    if (skipped.length > 0) {
      setError(`Skipped ${skipped.length} non-image file(s): ${skipped.map(f => f.name).join(', ')}`);
    }

    for (const file of imageFiles) {
      if (steps.length >= MAX_SCREENSHOTS) break;
      await processImageFile(file);
    }
  }, [processImageFile, steps.length]);

  // Paste handler (Ctrl+V)
  useEffect(() => {
    const handlePaste = async (e: ClipboardEvent) => {
      if (atLimit) return;
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith('image/')) {
          const file = items[i].getAsFile();
          if (file) {
            e.preventDefault();
            await processImageFile(file);
            return;
          }
        }
      }
    };

    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, [processImageFile, atLimit]);

  // Drag handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      await processFiles(e.dataTransfer.files);
    }
  }, [processFiles]);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFiles(e.target.files);
      e.target.value = '';
    }
  }, [processFiles]);

  // Drag-to-reorder handlers
  const handleStepDragStart = (id: string) => setDraggedId(id);
  const handleStepDragOver = (e: React.DragEvent, id: string) => {
    e.preventDefault();
    setDragOverId(id);
  };
  const handleStepDrop = (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (!draggedId || draggedId === targetId) {
      setDraggedId(null);
      setDragOverId(null);
      return;
    }
    const newOrder = [...steps];
    const fromIdx = newOrder.findIndex(s => s.id === draggedId);
    const toIdx = newOrder.findIndex(s => s.id === targetId);
    const [moved] = newOrder.splice(fromIdx, 1);
    newOrder.splice(toIdx, 0, moved);
    const renumbered = newOrder.map((s, i) => ({ ...s, stepNumber: i + 1 }));
    onReorderSteps(renumbered);
    setDraggedId(null);
    setDragOverId(null);
  };
  const handleStepDragEnd = () => {
    setDraggedId(null);
    setDragOverId(null);
  };

  const handleDeleteClick = (id: string) => setDeleteConfirm(id);
  const handleDeleteConfirm = (id: string) => {
    onDeleteStep(id);
    setDeleteConfirm(null);
  };

  const handleStartCapture = () => {
    if (!taskName.trim()) {
      taskInputRef.current?.focus();
      return;
    }
    setTaskNameLocked(true);
  };

  return (
    <div className={styles.screen}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTitle}>Task Capture</span>
          {steps.length > 0 && (
            <span className={styles.stepCount}>{steps.length} / {MAX_SCREENSHOTS}</span>
          )}
        </div>
        <button className={styles.cancelBtn} onClick={onCancel}>Cancel</button>
      </div>

      {/* Task Name */}
      <div className={styles.taskSection}>
        {!taskNameLocked ? (
          <div className={styles.taskSetup}>
            <label className={styles.taskLabel}>What task are you capturing?</label>
            <div className={styles.taskInputRow}>
              <input
                ref={taskInputRef}
                className={styles.taskInput}
                type="text"
                value={taskName}
                onChange={e => onTaskNameChange(e.target.value)}
                placeholder="e.g., Sign up for an account"
                onKeyDown={e => e.key === 'Enter' && handleStartCapture()}
              />
              <button
                className={styles.startBtn}
                onClick={handleStartCapture}
                disabled={!taskName.trim()}
              >
                Start Capturing
              </button>
            </div>
          </div>
        ) : (
          <div className={styles.taskBadge}>
            <span className={styles.taskBadgeLabel}>Task:</span>
            <span className={styles.taskBadgeName}>{taskName}</span>
          </div>
        )}
      </div>

      {taskNameLocked && (
        <>
          {/* Warnings */}
          {nearLimit && (
            <div className={styles.warning}>
              That's a long flow ({steps.length} steps). Are all these part of the same task?
              Splitting into smaller tasks gives more focused results.
            </div>
          )}
          {atLimit && (
            <div className={styles.limitReached}>
              Maximum {MAX_SCREENSHOTS} screenshots reached. Finish this task or delete some steps.
            </div>
          )}

          {/* Step Timeline */}
          {steps.length > 0 && (
            <div className={styles.timeline}>
              {steps.map(step => (
                <div
                  key={step.id}
                  className={`${styles.stepCard} ${dragOverId === step.id ? styles.dragOver : ''} ${draggedId === step.id ? styles.dragging : ''}`}
                  draggable
                  onDragStart={() => handleStepDragStart(step.id)}
                  onDragOver={e => handleStepDragOver(e, step.id)}
                  onDrop={e => handleStepDrop(e, step.id)}
                  onDragEnd={handleStepDragEnd}
                >
                  <div className={styles.stepNumber}>Step {step.stepNumber}</div>
                  <img
                    className={styles.stepThumbnail}
                    src={step.imageData}
                    alt={`Step ${step.stepNumber}`}
                    onClick={() => setFullViewStep(step)}
                    title="Click to view full size"
                  />
                  <div className={styles.stepMenu}>
                    {deleteConfirm === step.id ? (
                      <div className={styles.deleteConfirm}>
                        <span>Delete?</span>
                        <button onClick={() => handleDeleteConfirm(step.id)}>Yes</button>
                        <button onClick={() => setDeleteConfirm(null)}>No</button>
                      </div>
                    ) : (
                      <button
                        className={styles.deleteBtn}
                        onClick={() => handleDeleteClick(step.id)}
                        title="Delete step"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Drop Zone */}
          {!atLimit && (
            <div
              ref={dropZoneRef}
              className={`${styles.dropZone} ${isDragOver ? styles.dragActive : ''} ${isProcessing ? styles.processing : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              {isProcessing ? (
                <span className={styles.processingText}>Processing screenshot...</span>
              ) : steps.length === 0 ? (
                <>
                  <div className={styles.dropInstruction}>{osInstructions}</div>
                  <div className={styles.dropSub}>or drag and drop a screenshot, or click to select a file</div>
                </>
              ) : (
                <div className={styles.dropInstruction}>
                  Paste next screenshot ({osInstructions.split(',')[0]}) or drag here
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                style={{ display: 'none' }}
                onChange={handleFileSelect}
              />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className={styles.errorMsg}>
              {error}
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}

          {/* Running Cost + Finish */}
          {steps.length > 0 && (
            <div className={styles.footer}>
              {runningCostEstimate && (
                <span className={styles.costEstimate}>{runningCostEstimate}</span>
              )}
              <button
                className={styles.finishBtn}
                onClick={onFinish}
                disabled={steps.length === 0}
              >
                Finish Task →
              </button>
            </div>
          )}
        </>
      )}

      {/* Full size modal */}
      {fullViewStep && (
        <div className={styles.modal} onClick={() => setFullViewStep(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <span>Step {fullViewStep.stepNumber}</span>
              <button onClick={() => setFullViewStep(null)}>✕ Close</button>
            </div>
            <img
              className={styles.modalImage}
              src={fullViewStep.imageData}
              alt={`Step ${fullViewStep.stepNumber} full size`}
            />
          </div>
        </div>
      )}
    </div>
  );
};
