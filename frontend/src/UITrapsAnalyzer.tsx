import React, { useEffect } from 'react';
import { UITrapsAnalyzerProps } from './api/types';
import { useAnalyzer } from './hooks/useAnalyzer';
import { useElapsedTime } from './hooks/useElapsedTime';
import { AnalyzerForm } from './components/AnalyzerForm';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ReportViewer } from './components/ReportViewer';
import { EstimatePreview } from './components/EstimatePreview';
import './styles/variables.css';
import styles from './UITrapsAnalyzer.module.css';

export const UITrapsAnalyzer: React.FC<UITrapsAnalyzerProps> = ({
  apiEndpoint,
  apiKey,
  theme = 'light',
  className,
  style,
  showUsageInfo = false,
  showStatistics = true,
  initialUsers = '',
  initialTasks = '',
  initialFormat = '',
  onAnalysisStart,
  onAnalysisComplete,
  onAnalysisError,
  timeout = 120000,
}) => {
  const {
    state,
    setFiles,
    setUsers,
    setTasks,
    setFormat,
    setContentType,
    submitAnalysis,
    confirmAnalysis,
    backToForm,
    reset,
    cancelAnalysis,
  } = useAnalyzer({
    apiEndpoint,
    apiKey,
    timeout,
    initialUsers,
    initialTasks,
    initialFormat,
    onAnalysisStart,
    onAnalysisComplete,
    onAnalysisError,
  });

  const { elapsedTime, start: startTimer, stop: stopTimer, reset: resetTimer } = useElapsedTime();

  // Start/stop timer based on analysis state
  useEffect(() => {
    if (state.view === 'loading') {
      startTimer();
    } else {
      stopTimer();
    }
  }, [state.view, startTimer, stopTimer]);

  const handleNewAnalysis = () => {
    resetTimer();
    reset();
  };

  const handleCancel = () => {
    resetTimer();
    cancelAnalysis();
  };

  const handleBack = () => {
    backToForm();
  };

  const handleConfirm = async () => {
    await confirmAnalysis();
  };

  return (
    <div
      className={`uitraps-analyzer ${styles.container} ${className || ''}`}
      data-theme={theme}
      style={style}
    >
      <header className={styles.header}>
        <img
          src="/Cards.png"
          alt="UI Tenets & Traps Cards"
          className={styles.headerImage}
        />
        <h2 className={styles.title}>UI Trap Analyzer</h2>
        <p className={styles.subtitle}>
          Analyze your design for usability issues using the UI Tenets & Traps framework
        </p>
      </header>

      <main className={styles.main}>
        {state.view === 'form' && (
          <AnalyzerForm
            files={state.files}
            users={state.users}
            tasks={state.tasks}
            format={state.format}
            contentType={state.contentType}
            onFilesChange={setFiles}
            onUsersChange={setUsers}
            onTasksChange={setTasks}
            onFormatChange={setFormat}
            onContentTypeChange={setContentType}
            onSubmit={submitAnalysis}
            disabled={state.isSubmitting}
            isEstimating={state.isEstimating}
          />
        )}

        {state.view === 'preview' && state.estimate && (
          <EstimatePreview
            estimate={state.estimate}
            onConfirm={handleConfirm}
            onBack={handleBack}
            isLoading={state.isSubmitting}
          />
        )}

        {state.view === 'loading' && (
          <AnalysisProgress
            elapsedTime={elapsedTime}
            onCancel={handleCancel}
            inputType={state.inputType || undefined}
            fileCount={state.files.length}
            estimatedTime={state.estimate?.time_estimate}
          />
        )}

        {state.view === 'report' && state.reportHtml && (
          <ReportViewer
            html={state.reportHtml}
            statistics={state.statistics || undefined}
            usage={state.usage || undefined}
            showStatistics={showStatistics}
            showUsageInfo={showUsageInfo}
            onNewAnalysis={handleNewAnalysis}
          />
        )}

        {state.view === 'error' && (
          <div className={styles.error}>
            <div className={styles.errorIcon}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h3 className={styles.errorTitle}>Analysis Failed</h3>
            <p className={styles.errorMessage}>{state.error}</p>
            <button
              type="button"
              className={styles.retryButton}
              onClick={handleNewAnalysis}
            >
              Try Again
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default UITrapsAnalyzer;
