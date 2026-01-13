import { LogEntry, LogType } from '../types';

/**
 * Factory class for creating log entries with consistent formatting
 */
export class LogFactory {
  /**
   * Create a new log entry
   * @param message - The log message
   * @param type - The log type (defaults to INFO)
   * @returns A properly formatted LogEntry
   */
  static create(message: string, type: LogType = LogType.INFO): LogEntry {
    return {
      id: this.generateId(),
      timestamp: this.getCurrentTime(),
      message,
      type
    };
  }

  /**
   * Generate a unique ID for the log entry
   */
  private static generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  /**
   * Get current time formatted as HH:MM:SS
   */
  private static getCurrentTime(): string {
    return new Date().toLocaleTimeString('en-US', { hour12: false });
  }
}
