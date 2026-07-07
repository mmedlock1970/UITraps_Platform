/**
 * localStorage-based storage for past analysis reports.
 * Stores the last 10 analyses with ability to view and download.
 */

import { ReportStatistics, KbVersion } from '../api/types';

/** Serialisable snapshot of all raw form fields (no File objects). */
export interface FormSnapshot {
  figmaLink: string;
  screenName: string;
  platform: string;
  productDomain: string;
  productContext: string;
  expLevel: string;
  techSavvy: string;
  frequency: string;
  tasks: Array<{ name: string; description: string }>;
  userDesc: string;
  priorProducts: string;
  physicalEnv: string;
  lighting: string;
  gripPosition: string;
  attentionalState: string;
  extraContext: string;
  kbVersion: KbVersion;
  selectedTenets: string[];
  verbosity: 'brief' | 'standard';
  pass1Model: 'sonnet' | 'haiku';
  thoroughMode: boolean;
  mode?: 'single' | 'twopass';
  reportStyle?: 'trap' | 'issues';
  lockedInputType: 'screenshot' | 'video' | 'flow_diagram' | null;
}

export interface StoredAnalysis {
  id: string;
  timestamp: string;
  fileNames: string[];
  statistics?: ReportStatistics;
  html: string;
  markdown?: string;
  formSnapshot?: FormSnapshot;
}

const STORAGE_KEY = 'uitraps-analysis-history';
export const HISTORY_LIMIT = 5; // Reduced from 10 due to larger report sizes with embedded screenshots
const MAX_ENTRIES = HISTORY_LIMIT;

export function saveAnalysis(analysis: Omit<StoredAnalysis, 'id'>): void {
  const id = `analysis-${Date.now()}`;
  const entry: StoredAnalysis = { id, ...analysis };
  const existing = getAnalysisHistory();
  const updated = [entry, ...existing].slice(0, MAX_ENTRIES);

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    // localStorage full — progressive fallback
    console.warn('localStorage full, reducing stored analyses...');

    try {
      // Try with 3 entries
      const trimmed = updated.slice(0, 3);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch {
      try {
        // Last resort: only save this one entry
        localStorage.setItem(STORAGE_KEY, JSON.stringify([entry]));
        console.warn('localStorage critically full - keeping only latest analysis');
      } catch {
        console.error('Cannot save analysis - localStorage quota exceeded');
      }
    }
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
