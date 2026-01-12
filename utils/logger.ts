/**
 * Logger Utility
 * Centralized logging with different levels
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

class Logger {
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = import.meta.env.MODE === 'development';
  }

  /**
   * Debug logs (only in development)
   */
  debug(...args: any[]): void {
    if (this.isDevelopment) {
      console.log('%c[DEBUG]', 'color: #8b5cf6; font-weight: bold', ...args);
    }
  }

  /**
   * Info logs (always shown)
   */
  info(...args: any[]): void {
    console.log('%c[INFO]', 'color: #3b82f6; font-weight: bold', ...args);
  }

  /**
   * Warning logs (always shown)
   */
  warn(...args: any[]): void {
    console.warn('%c[WARN]', 'color: #f59e0b; font-weight: bold', ...args);
  }

  /**
   * Error logs (always shown)
   */
  error(...args: any[]): void {
    console.error('%c[ERROR]', 'color: #ef4444; font-weight: bold', ...args);
    // In production, you could send this to an error tracking service
    // this.sendToErrorTrackingService(args);
  }

  /**
   * Group logs (useful for debugging complex flows)
   */
  group(label: string, collapsed: boolean = false): void {
    if (collapsed) {
      console.groupCollapsed(label);
    } else {
      console.group(label);
    }
  }

  /**
   * End log group
   */
  groupEnd(): void {
    console.groupEnd();
  }
}

// Export singleton instance
export const logger = new Logger();
