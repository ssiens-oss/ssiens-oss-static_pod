import { LogEntry, LogType } from '../types';

/**
 * Shared POD Utility Functions
 * Contains common utilities used across the POD application
 */

// ==================== ID GENERATION ====================
/**
 * Generates a unique random ID
 * @returns A random alphanumeric string
 */
export const generateId = (): string =>
  Math.random().toString(36).substr(2, 9);

// ==================== TIMESTAMP ====================
/**
 * Gets current time as a formatted string
 * @returns Time string in HH:MM:SS format (24-hour)
 */
export const timestamp = (): string =>
  new Date().toLocaleTimeString('en-US', { hour12: false });

// ==================== ASYNC UTILITIES ====================
/**
 * Sleep utility for async delays
 * @param ms Milliseconds to sleep
 * @returns Promise that resolves after the specified time
 */
export const sleep = (ms: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, ms));

// ==================== LOG CREATION ====================
/**
 * Creates a new log entry with timestamp and ID
 * @param message Log message content
 * @param type Log type (INFO, SUCCESS, WARNING, ERROR)
 * @returns Complete LogEntry object
 */
export const createLogEntry = (
  message: string,
  type: LogType = LogType.INFO
): LogEntry => ({
  id: generateId(),
  timestamp: timestamp(),
  message,
  type
});

// ==================== BATCH PROCESSING ====================
/**
 * Parses a comma-separated batch list into an array of drop names
 * @param batchList Comma-separated string of drop names
 * @returns Array of trimmed, non-empty drop names
 */
export const parseBatchList = (batchList: string): string[] =>
  batchList.split(',').map(d => d.trim()).filter(Boolean);

// ==================== PROGRESS CALCULATION ====================
/**
 * Calculates total progress for batch operations
 * @param batchIndex Current batch index (0-based)
 * @param totalBatches Total number of batches
 * @param stepProgress Progress within current step (0-100)
 * @returns Total progress percentage (0-100)
 */
export const calculateBatchProgress = (
  batchIndex: number,
  totalBatches: number,
  stepProgress: number
): number => {
  const baseProgress = (batchIndex / totalBatches) * 100;
  const currentStepProgress = (stepProgress / 100) * (100 / totalBatches);
  return baseProgress + currentStepProgress;
};
