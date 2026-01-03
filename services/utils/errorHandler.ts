/**
 * Error Handling Utilities
 * Provides retry logic, exponential backoff, and error categorization
 */

export interface RetryOptions {
  maxRetries?: number
  initialDelay?: number
  maxDelay?: number
  backoffMultiplier?: number
  retryableErrors?: string[]
  onRetry?: (error: Error, attempt: number) => void
}

export class RetryableError extends Error {
  constructor(message: string, public readonly statusCode?: number) {
    super(message)
    this.name = 'RetryableError'
  }
}

export class NonRetryableError extends Error {
  constructor(message: string, public readonly statusCode?: number) {
    super(message)
    this.name = 'NonRetryableError'
  }
}

export class RateLimitError extends RetryableError {
  constructor(message: string, public readonly retryAfter?: number) {
    super(message, 429)
    this.name = 'RateLimitError'
  }
}

/**
 * Sleep utility
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Calculate exponential backoff delay
 */
export function calculateBackoff(
  attempt: number,
  initialDelay: number = 1000,
  maxDelay: number = 30000,
  multiplier: number = 2
): number {
  const delay = initialDelay * Math.pow(multiplier, attempt)
  const jitter = Math.random() * 0.3 * delay // Add 0-30% jitter
  return Math.min(delay + jitter, maxDelay)
}

/**
 * Determine if error is retryable
 */
export function isRetryableError(error: Error | any): boolean {
  // Already categorized
  if (error instanceof NonRetryableError) {
    return false
  }

  if (error instanceof RetryableError) {
    return true
  }

  // Network errors
  if (error.code === 'ECONNRESET' ||
      error.code === 'ETIMEDOUT' ||
      error.code === 'ENOTFOUND' ||
      error.code === 'ECONNREFUSED') {
    return true
  }

  // HTTP status codes
  if (error.statusCode || error.status) {
    const status = error.statusCode || error.status

    // Retry on server errors and rate limits
    if (status === 429 || status === 503 || status === 502 || status === 504) {
      return true
    }

    // Don't retry client errors (except 429)
    if (status >= 400 && status < 500) {
      return false
    }

    // Retry server errors
    if (status >= 500) {
      return true
    }
  }

  // Default: retry
  return true
}

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    onRetry
  } = options

  let lastError: Error | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      // Don't retry if not retryable
      if (!isRetryableError(error)) {
        throw error
      }

      // Don't retry if this was the last attempt
      if (attempt === maxRetries) {
        break
      }

      // Calculate delay
      let delay = calculateBackoff(attempt, initialDelay, maxDelay, backoffMultiplier)

      // Handle rate limits
      if (error instanceof RateLimitError && error.retryAfter) {
        delay = error.retryAfter * 1000
      }

      // Call retry callback
      if (onRetry) {
        onRetry(lastError, attempt + 1)
      }

      // Wait before retrying
      await sleep(delay)
    }
  }

  throw lastError || new Error('Retry failed with unknown error')
}

/**
 * Wrap a fetch call with retry logic
 */
export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retryOptions: RetryOptions = {}
): Promise<Response> {
  return retryWithBackoff(async () => {
    const response = await fetch(url, options)

    // Handle rate limiting
    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60')
      throw new RateLimitError(
        `Rate limit exceeded for ${url}`,
        retryAfter
      )
    }

    // Handle server errors
    if (response.status >= 500) {
      throw new RetryableError(
        `Server error: ${response.statusText}`,
        response.status
      )
    }

    // Handle client errors (non-retryable)
    if (response.status >= 400 && response.status < 500) {
      const errorBody = await response.text().catch(() => 'Unknown error')
      throw new NonRetryableError(
        `Client error: ${response.statusText} - ${errorBody}`,
        response.status
      )
    }

    return response
  }, retryOptions)
}

/**
 * Error logger with context
 */
export class ErrorLogger {
  private context: Record<string, any>

  constructor(context: Record<string, any> = {}) {
    this.context = context
  }

  log(error: Error, additionalContext?: Record<string, any>): void {
    const errorInfo = {
      timestamp: new Date().toISOString(),
      name: error.name,
      message: error.message,
      stack: error.stack,
      context: { ...this.context, ...additionalContext }
    }

    console.error('[ERROR]', JSON.stringify(errorInfo, null, 2))
  }

  warn(message: string, context?: Record<string, any>): void {
    console.warn('[WARN]', message, { ...this.context, ...context })
  }

  info(message: string, context?: Record<string, any>): void {
    console.info('[INFO]', message, { ...this.context, ...context })
  }
}

/**
 * Circuit breaker pattern for fault tolerance
 */
export class CircuitBreaker {
  private failures: number = 0
  private lastFailureTime: number = 0
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED'

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000,
    private resetTimeout: number = 30000
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      const now = Date.now()
      if (now - this.lastFailureTime >= this.resetTimeout) {
        this.state = 'HALF_OPEN'
      } else {
        throw new Error('Circuit breaker is OPEN')
      }
    }

    try {
      const result = await fn()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess(): void {
    this.failures = 0
    this.state = 'CLOSED'
  }

  private onFailure(): void {
    this.failures++
    this.lastFailureTime = Date.now()

    if (this.failures >= this.threshold) {
      this.state = 'OPEN'
    }
  }

  getState(): string {
    return this.state
  }

  reset(): void {
    this.failures = 0
    this.state = 'CLOSED'
  }
}

/**
 * Batch error handler for processing multiple items
 */
export class BatchErrorHandler {
  private errors: Array<{ item: any; error: Error }> = []
  private successes: any[] = []

  recordSuccess(item: any): void {
    this.successes.push(item)
  }

  recordError(item: any, error: Error): void {
    this.errors.push({ item, error })
  }

  hasErrors(): boolean {
    return this.errors.length > 0
  }

  getErrors(): Array<{ item: any; error: Error }> {
    return this.errors
  }

  getSuccesses(): any[] {
    return this.successes
  }

  getSummary(): {
    total: number
    successful: number
    failed: number
    successRate: number
  } {
    const total = this.successes.length + this.errors.length
    return {
      total,
      successful: this.successes.length,
      failed: this.errors.length,
      successRate: total > 0 ? (this.successes.length / total) * 100 : 0
    }
  }

  printSummary(): void {
    const summary = this.getSummary()
    console.log('=== Batch Processing Summary ===')
    console.log(`Total: ${summary.total}`)
    console.log(`Successful: ${summary.successful}`)
    console.log(`Failed: ${summary.failed}`)
    console.log(`Success Rate: ${summary.successRate.toFixed(2)}%`)

    if (this.errors.length > 0) {
      console.log('\nErrors:')
      this.errors.forEach(({ item, error }, index) => {
        console.log(`${index + 1}. ${error.message}`)
        console.log(`   Item:`, item)
      })
    }
  }
}

/**
 * Timeout wrapper
 */
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage: string = 'Operation timed out'
): Promise<T> {
  let timeoutHandle: NodeJS.Timeout

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutHandle = setTimeout(() => {
      reject(new Error(errorMessage))
    }, timeoutMs)
  })

  try {
    const result = await Promise.race([promise, timeoutPromise])
    clearTimeout(timeoutHandle!)
    return result
  } catch (error) {
    clearTimeout(timeoutHandle!)
    throw error
  }
}
