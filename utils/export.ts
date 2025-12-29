import { QueueItem, LogEntry } from '../types';

/**
 * Export utilities for downloading POD Studio data
 */

// ==================== CSV EXPORT ====================

/**
 * Converts queue items to CSV format
 */
export const queueToCSV = (queue: QueueItem[]): string => {
  const headers = ['Name', 'Status', 'ID'];
  const rows = queue.map(item => [
    `"${item.name}"`,
    item.status,
    item.id
  ]);

  return [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');
};

/**
 * Converts logs to CSV format
 */
export const logsToCSV = (logs: LogEntry[]): string => {
  const headers = ['Timestamp', 'Type', 'Message', 'ID'];
  const rows = logs.map(log => [
    log.timestamp,
    log.type,
    `"${log.message.replace(/"/g, '""')}"`, // Escape quotes
    log.id
  ]);

  return [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');
};

// ==================== JSON EXPORT ====================

/**
 * Converts queue to formatted JSON
 */
export const queueToJSON = (queue: QueueItem[]): string => {
  return JSON.stringify(queue, null, 2);
};

/**
 * Converts logs to formatted JSON
 */
export const logsToJSON = (logs: LogEntry[]): string => {
  return JSON.stringify(logs, null, 2);
};

// ==================== DOWNLOAD HELPER ====================

/**
 * Triggers a download of content as a file
 */
export const downloadFile = (content: string, filename: string, mimeType: string = 'text/plain'): void => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();

  // Cleanup
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// ==================== CONVENIENCE EXPORTS ====================

/**
 * Export queue as CSV file
 */
export const exportQueueAsCSV = (queue: QueueItem[]): void => {
  const csv = queueToCSV(queue);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  downloadFile(csv, `pod-queue-${timestamp}.csv`, 'text/csv');
};

/**
 * Export queue as JSON file
 */
export const exportQueueAsJSON = (queue: QueueItem[]): void => {
  const json = queueToJSON(queue);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  downloadFile(json, `pod-queue-${timestamp}.json`, 'application/json');
};

/**
 * Export logs as CSV file
 */
export const exportLogsAsCSV = (logs: LogEntry[]): void => {
  const csv = logsToCSV(logs);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  downloadFile(csv, `pod-logs-${timestamp}.csv`, 'text/csv');
};

/**
 * Export logs as JSON file
 */
export const exportLogsAsJSON = (logs: LogEntry[]): void => {
  const json = logsToJSON(logs);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  downloadFile(json, `pod-logs-${timestamp}.json`, 'application/json');
};
