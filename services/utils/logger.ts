/**
 * Structured Logging System
 * Professional logging with levels, context, and formatting
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  CRITICAL = 4
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  context?: Record<string, any>
  error?: {
    name: string
    message: string
    stack?: string
  }
}

export interface LoggerOptions {
  level?: LogLevel
  context?: Record<string, any>
  enableConsole?: boolean
  enableFile?: boolean
  filePath?: string
  enableCallback?: boolean
  callback?: (entry: LogEntry) => void
}

export class Logger {
  private level: LogLevel
  private context: Record<string, any>
  private enableConsole: boolean
  private enableCallback: boolean
  private callback?: (entry: LogEntry) => void
  private history: LogEntry[] = []
  private maxHistorySize: number = 1000

  constructor(options: LoggerOptions = {}) {
    this.level = options.level ?? LogLevel.INFO
    this.context = options.context ?? {}
    this.enableConsole = options.enableConsole ?? true
    this.enableCallback = options.enableCallback ?? false
    this.callback = options.callback
  }

  /**
   * Set log level
   */
  setLevel(level: LogLevel): void {
    this.level = level
  }

  /**
   * Set global context
   */
  setContext(context: Record<string, any>): void {
    this.context = { ...this.context, ...context }
  }

  /**
   * Clear context
   */
  clearContext(): void {
    this.context = {}
  }

  /**
   * Set callback for log entries
   */
  setCallback(callback: (entry: LogEntry) => void): void {
    this.callback = callback
    this.enableCallback = true
  }

  /**
   * Debug log
   */
  debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context)
  }

  /**
   * Info log
   */
  info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context)
  }

  /**
   * Warning log
   */
  warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context)
  }

  /**
   * Error log
   */
  error(message: string, error?: Error, context?: Record<string, any>): void {
    const errorContext = error ? {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    } : {}

    this.log(LogLevel.ERROR, message, { ...context, ...errorContext })
  }

  /**
   * Critical log
   */
  critical(message: string, error?: Error, context?: Record<string, any>): void {
    const errorContext = error ? {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    } : {}

    this.log(LogLevel.CRITICAL, message, { ...context, ...errorContext })
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, context?: Record<string, any>): void {
    if (level < this.level) {
      return
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: LogLevel[level],
      message,
      context: { ...this.context, ...context }
    }

    // Add to history
    this.addToHistory(entry)

    // Console output
    if (this.enableConsole) {
      this.logToConsole(entry, level)
    }

    // Callback
    if (this.enableCallback && this.callback) {
      this.callback(entry)
    }
  }

  /**
   * Log to console with colors
   */
  private logToConsole(entry: LogEntry, level: LogLevel): void {
    const { timestamp, message, context } = entry
    const prefix = this.getLogPrefix(level)
    const color = this.getLogColor(level)

    if (typeof process !== 'undefined' && process.stdout?.isTTY) {
      // Colored output for terminals
      console.log(`${color}${prefix}${this.resetColor()} ${timestamp} - ${message}`)
    } else {
      // Plain output for non-TTY
      console.log(`${prefix} ${timestamp} - ${message}`)
    }

    if (context && Object.keys(context).length > 0) {
      console.log('  Context:', JSON.stringify(context, null, 2))
    }
  }

  /**
   * Get log prefix based on level
   */
  private getLogPrefix(level: LogLevel): string {
    const prefixes: Record<number, string> = {
      [LogLevel.DEBUG]: '[DEBUG]',
      [LogLevel.INFO]: '[INFO] ',
      [LogLevel.WARN]: '[WARN] ',
      [LogLevel.ERROR]: '[ERROR]',
      [LogLevel.CRITICAL]: '[CRIT] '
    }
    return prefixes[level] || '[LOG]  '
  }

  /**
   * Get ANSI color code for log level
   */
  private getLogColor(level: LogLevel): string {
    const colors: Record<number, string> = {
      [LogLevel.DEBUG]: '\x1b[36m',    // Cyan
      [LogLevel.INFO]: '\x1b[32m',     // Green
      [LogLevel.WARN]: '\x1b[33m',     // Yellow
      [LogLevel.ERROR]: '\x1b[31m',    // Red
      [LogLevel.CRITICAL]: '\x1b[35m'  // Magenta
    }
    return colors[level] || ''
  }

  /**
   * Reset color
   */
  private resetColor(): string {
    return '\x1b[0m'
  }

  /**
   * Add entry to history
   */
  private addToHistory(entry: LogEntry): void {
    this.history.push(entry)

    // Maintain max history size
    if (this.history.length > this.maxHistorySize) {
      this.history.shift()
    }
  }

  /**
   * Get log history
   */
  getHistory(level?: LogLevel): LogEntry[] {
    if (level !== undefined) {
      return this.history.filter(entry => {
        const entryLevel = LogLevel[entry.level as keyof typeof LogLevel]
        return entryLevel >= level
      })
    }
    return [...this.history]
  }

  /**
   * Clear log history
   */
  clearHistory(): void {
    this.history = []
  }

  /**
   * Get log statistics
   */
  getStats(): Record<string, number> {
    const stats: Record<string, number> = {
      DEBUG: 0,
      INFO: 0,
      WARN: 0,
      ERROR: 0,
      CRITICAL: 0
    }

    for (const entry of this.history) {
      stats[entry.level] = (stats[entry.level] || 0) + 1
    }

    return stats
  }

  /**
   * Export logs as JSON
   */
  exportJSON(): string {
    return JSON.stringify(this.history, null, 2)
  }

  /**
   * Export logs as text
   */
  exportText(): string {
    return this.history
      .map(entry => {
        const ctx = entry.context && Object.keys(entry.context).length > 0
          ? ` | ${JSON.stringify(entry.context)}`
          : ''
        return `[${entry.timestamp}] ${entry.level} - ${entry.message}${ctx}`
      })
      .join('\n')
  }
}

/**
 * Create child logger with additional context
 */
export function createChildLogger(parent: Logger, context: Record<string, any>): Logger {
  const child = new Logger({
    level: parent['level'],
    context: { ...parent['context'], ...context },
    enableConsole: parent['enableConsole'],
    enableCallback: parent['enableCallback'],
    callback: parent['callback']
  })
  return child
}

/**
 * Global logger instance
 */
let globalLogger: Logger | null = null

/**
 * Initialize global logger
 */
export function initLogger(options?: LoggerOptions): Logger {
  globalLogger = new Logger(options)
  return globalLogger
}

/**
 * Get global logger
 */
export function getLogger(): Logger {
  if (!globalLogger) {
    globalLogger = new Logger()
  }
  return globalLogger
}

/**
 * Convenience functions for global logger
 */
export function debug(message: string, context?: Record<string, any>): void {
  getLogger().debug(message, context)
}

export function info(message: string, context?: Record<string, any>): void {
  getLogger().info(message, context)
}

export function warn(message: string, context?: Record<string, any>): void {
  getLogger().warn(message, context)
}

export function error(message: string, err?: Error, context?: Record<string, any>): void {
  getLogger().error(message, err, context)
}

export function critical(message: string, err?: Error, context?: Record<string, any>): void {
  getLogger().critical(message, err, context)
}

/**
 * Performance logger for timing operations
 */
export class PerformanceLogger {
  private logger: Logger
  private startTimes: Map<string, number> = new Map()

  constructor(logger?: Logger) {
    this.logger = logger || getLogger()
  }

  /**
   * Start timing an operation
   */
  start(operation: string): void {
    this.startTimes.set(operation, Date.now())
    this.logger.debug(`Started: ${operation}`)
  }

  /**
   * End timing an operation
   */
  end(operation: string, context?: Record<string, any>): number {
    const startTime = this.startTimes.get(operation)
    if (!startTime) {
      this.logger.warn(`No start time found for operation: ${operation}`)
      return 0
    }

    const duration = Date.now() - startTime
    this.startTimes.delete(operation)

    this.logger.info(`Completed: ${operation}`, {
      ...context,
      duration: `${duration}ms`
    })

    return duration
  }

  /**
   * Measure async operation
   */
  async measure<T>(
    operation: string,
    fn: () => Promise<T>,
    context?: Record<string, any>
  ): Promise<T> {
    this.start(operation)
    try {
      const result = await fn()
      this.end(operation, context)
      return result
    } catch (error) {
      this.end(operation, { ...context, error: true })
      throw error
    }
  }
}
