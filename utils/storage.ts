import { EngineConfig, QueueItem, LogEntry } from '../types';

/**
 * LocalStorage utilities for persisting POD Studio data
 */

const STORAGE_KEYS = {
  CONFIG: 'pod_studio_config',
  QUEUE: 'pod_studio_queue',
  LOGS: 'pod_studio_logs'
} as const;

// ==================== CONFIG PERSISTENCE ====================

export const saveConfig = (config: EngineConfig): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.CONFIG, JSON.stringify(config));
  } catch (error) {
    console.error('Failed to save config:', error);
  }
};

export const loadConfig = (): EngineConfig | null => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.CONFIG);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Failed to load config:', error);
    return null;
  }
};

// ==================== QUEUE PERSISTENCE ====================

export const saveQueue = (queue: QueueItem[]): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.QUEUE, JSON.stringify(queue));
  } catch (error) {
    console.error('Failed to save queue:', error);
  }
};

export const loadQueue = (): QueueItem[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.QUEUE);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to load queue:', error);
    return [];
  }
};

// ==================== LOGS PERSISTENCE ====================

export const saveLogs = (logs: LogEntry[]): void => {
  try {
    // Only save last 100 logs to avoid storage limits
    const recentLogs = logs.slice(-100);
    localStorage.setItem(STORAGE_KEYS.LOGS, JSON.stringify(recentLogs));
  } catch (error) {
    console.error('Failed to save logs:', error);
  }
};

export const loadLogs = (): LogEntry[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.LOGS);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to load logs:', error);
    return [];
  }
};

// ==================== CLEAR STORAGE ====================

export const clearAllStorage = (): void => {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.error('Failed to clear storage:', error);
  }
};
