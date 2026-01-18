/**
 * Retry utility with exponential backoff
 * Provides robust retry logic for async operations
 */

import { sleep } from './delay';

export interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
  retryableErrors?: Array<new (...args: any[]) => Error>;
  onRetry?: (error: Error, attempt: number) => void;
}

export class RetryError extends Error {
  constructor(
    message: string,
    public readonly attempts: number,
    public readonly lastError: Error
  ) {
    super(message);
    this.name = 'RetryError';
  }
}

/**
 * Retry an async operation with exponential backoff
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    retryableErrors = [],
    onRetry
  } = options;

  let lastError: Error;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Check if error is retryable
      if (retryableErrors.length > 0) {
        const isRetryable = retryableErrors.some(
          ErrorClass => lastError instanceof ErrorClass
        );
        if (!isRetryable) {
          throw lastError;
        }
      }

      // Don't retry on last attempt
      if (attempt === maxRetries) {
        break;
      }

      // Call onRetry callback
      if (onRetry) {
        onRetry(lastError, attempt + 1);
      }

      // Wait before retrying
      await sleep(delay);

      // Increase delay with exponential backoff
      delay = Math.min(delay * backoffMultiplier, maxDelay);
    }
  }

  throw new RetryError(
    `Operation failed after ${maxRetries + 1} attempts`,
    maxRetries + 1,
    lastError!
  );
}

/**
 * Retry with custom condition
 */
export async function retryUntil<T>(
  operation: () => Promise<T>,
  condition: (result: T) => boolean,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    onRetry
  } = options;

  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const result = await operation();

      if (condition(result)) {
        return result;
      }

      if (attempt === maxRetries) {
        throw new Error('Condition not met after maximum retries');
      }

      if (onRetry) {
        onRetry(new Error('Condition not met'), attempt + 1);
      }

      await sleep(delay);
      delay = Math.min(delay * backoffMultiplier, maxDelay);
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }

      const errorObj = error instanceof Error ? error : new Error(String(error));
      if (onRetry) {
        onRetry(errorObj, attempt + 1);
      }

      await sleep(delay);
      delay = Math.min(delay * backoffMultiplier, maxDelay);
    }
  }

  throw new Error('Operation failed: max retries exceeded');
}
