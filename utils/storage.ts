/**
 * Local storage utilities for persisting app state
 */

const STORAGE_PREFIX = 'staticwaves_pod_';

export const StorageKeys = {
  SETTINGS: `${STORAGE_PREFIX}settings`,
  EDITOR_STATE: `${STORAGE_PREFIX}editor_state`,
  RECENT_DROPS: `${STORAGE_PREFIX}recent_drops`,
  QUEUE_HISTORY: `${STORAGE_PREFIX}queue_history`,
  DESIGN_HISTORY: `${STORAGE_PREFIX}design_history`,
} as const;

/**
 * Save data to local storage
 */
export const saveToStorage = <T>(key: string, data: T): void => {
  try {
    const serialized = JSON.stringify(data);
    localStorage.setItem(key, serialized);
  } catch (error) {
    console.error(`Failed to save to storage (${key}):`, error);
  }
};

/**
 * Load data from local storage
 */
export const loadFromStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    if (item === null) {
      return defaultValue;
    }
    return JSON.parse(item) as T;
  } catch (error) {
    console.error(`Failed to load from storage (${key}):`, error);
    return defaultValue;
  }
};

/**
 * Remove data from local storage
 */
export const removeFromStorage = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Failed to remove from storage (${key}):`, error);
  }
};

/**
 * Clear all app data from storage
 */
export const clearAllStorage = (): void => {
  try {
    Object.values(StorageKeys).forEach((key) => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.error('Failed to clear storage:', error);
  }
};

/**
 * Check if storage is available
 */
export const isStorageAvailable = (): boolean => {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
};

/**
 * Get storage size in bytes
 */
export const getStorageSize = (): number => {
  let total = 0;
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }
  return total;
};

/**
 * Get storage size in human-readable format
 */
export const getStorageSizeFormatted = (): string => {
  const bytes = getStorageSize();
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};
