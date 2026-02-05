/**
 * localStorage-based storage for past analysis reports.
 * Stores the last 10 analyses with ability to view and download.
 */

import { ReportStatistics } from '../api/types';

export interface StoredAnalysis {
  id: string;
  timestamp: string;
  fileNames: string[];
  statistics?: ReportStatistics;
  html: string;
}

const STORAGE_KEY = 'uitraps-analysis-history';
const MAX_ENTRIES = 10;

export function saveAnalysis(analysis: Omit<StoredAnalysis, 'id'>): void {
  const id = `analysis-${Date.now()}`;
  const entry: StoredAnalysis = { id, ...analysis };
  const existing = getAnalysisHistory();
  const updated = [entry, ...existing].slice(0, MAX_ENTRIES);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch {
    // localStorage full — remove oldest entries and retry
    const trimmed = updated.slice(0, 5);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  }
}

export function getAnalysisHistory(): StoredAnalysis[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function getAnalysisById(id: string): StoredAnalysis | null {
  return getAnalysisHistory().find(a => a.id === id) || null;
}

export function deleteAnalysis(id: string): void {
  const updated = getAnalysisHistory().filter(a => a.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}
