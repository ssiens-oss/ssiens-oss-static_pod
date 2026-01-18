/**
 * Custom error types for better error handling
 * Provides specific error classes for different failure scenarios
 */

/**
 * Base error class for service errors
 */
export class ServiceError extends Error {
  constructor(
    message: string,
    public readonly serviceName: string,
    public readonly statusCode?: number,
    public readonly originalError?: Error
  ) {
    super(message);
    this.name = 'ServiceError';
  }
}

/**
 * Error when external API call fails
 */
export class APIError extends ServiceError {
  constructor(
    message: string,
    serviceName: string,
    statusCode?: number,
    public readonly responseBody?: any,
    originalError?: Error
  ) {
    super(message, serviceName, statusCode, originalError);
    this.name = 'APIError';
  }
}

/**
 * Error when authentication fails
 */
export class AuthenticationError extends ServiceError {
  constructor(message: string, serviceName: string, originalError?: Error) {
    super(message, serviceName, 401, originalError);
    this.name = 'AuthenticationError';
  }
}

/**
 * Error when rate limit is exceeded
 */
export class RateLimitError extends ServiceError {
  constructor(
    message: string,
    serviceName: string,
    public readonly retryAfter?: number,
    originalError?: Error
  ) {
    super(message, serviceName, 429, originalError);
    this.name = 'RateLimitError';
  }
}

/**
 * Error when timeout occurs
 */
export class TimeoutError extends ServiceError {
  constructor(
    message: string,
    serviceName: string,
    public readonly timeoutMs: number,
    originalError?: Error
  ) {
    super(message, serviceName, 408, originalError);
    this.name = 'TimeoutError';
  }
}

/**
 * Error when validation fails
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly field?: string,
    public readonly value?: any
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Error when configuration is invalid
 */
export class ConfigurationError extends Error {
  constructor(message: string, public readonly missingKeys?: string[]) {
    super(message);
    this.name = 'ConfigurationError';
  }
}

/**
 * Error when image processing fails
 */
export class ImageProcessingError extends ServiceError {
  constructor(
    message: string,
    public readonly imagePath?: string,
    originalError?: Error
  ) {
    super(message, 'ImageProcessing', undefined, originalError);
    this.name = 'ImageProcessingError';
  }
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: Error): boolean {
  if (error instanceof RateLimitError) return true;
  if (error instanceof TimeoutError) return true;
  if (error instanceof APIError) {
    const statusCode = error.statusCode;
    // Retry on 5xx errors and 408 (timeout)
    return (
      statusCode === 408 ||
      statusCode === 429 ||
      (statusCode !== undefined && statusCode >= 500 && statusCode < 600)
    );
  }
  return false;
}

/**
 * Extract user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unknown error occurred';
}

/**
 * Format error for logging
 */
export function formatErrorForLogging(error: unknown): Record<string, any> {
  if (error instanceof ServiceError) {
    return {
      name: error.name,
      message: error.message,
      serviceName: error.serviceName,
      statusCode: error.statusCode,
      stack: error.stack
    };
  }

  if (error instanceof Error) {
    return {
      name: error.name,
      message: error.message,
      stack: error.stack
    };
  }

  return {
    error: String(error)
  };
}
