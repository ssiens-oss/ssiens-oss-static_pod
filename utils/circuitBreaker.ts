/**
 * Circuit Breaker pattern implementation
 * Prevents cascading failures by failing fast when a service is down
 */

import { ServiceError } from './errors';

export enum CircuitState {
  CLOSED = 'CLOSED',     // Normal operation
  OPEN = 'OPEN',         // Blocking requests
  HALF_OPEN = 'HALF_OPEN' // Testing if service recovered
}

export interface CircuitBreakerOptions {
  failureThreshold?: number;      // Number of failures before opening
  successThreshold?: number;       // Number of successes to close from half-open
  timeout?: number;                // Time to wait before half-open (ms)
  resetTimeout?: number;           // Time to reset failure count (ms)
  onStateChange?: (state: CircuitState) => void;
}

export class CircuitBreakerError extends ServiceError {
  constructor(serviceName: string) {
    super(
      `Circuit breaker is OPEN for ${serviceName}. Service temporarily unavailable.`,
      serviceName,
      503
    );
    this.name = 'CircuitBreakerError';
  }
}

/**
 * Circuit Breaker implementation
 */
export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime?: number;
  private nextAttemptTime?: number;

  private readonly failureThreshold: number;
  private readonly successThreshold: number;
  private readonly timeout: number;
  private readonly resetTimeout: number;
  private readonly onStateChange?: (state: CircuitState) => void;

  constructor(
    private readonly name: string,
    options: CircuitBreakerOptions = {}
  ) {
    this.failureThreshold = options.failureThreshold ?? 5;
    this.successThreshold = options.successThreshold ?? 2;
    this.timeout = options.timeout ?? 60000; // 1 minute
    this.resetTimeout = options.resetTimeout ?? 300000; // 5 minutes
    this.onStateChange = options.onStateChange;
  }

  /**
   * Execute operation through circuit breaker
   */
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    // Check if circuit is open
    if (this.state === CircuitState.OPEN) {
      if (Date.now() < this.nextAttemptTime!) {
        throw new CircuitBreakerError(this.name);
      }
      // Try half-open
      this.setState(CircuitState.HALF_OPEN);
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * Handle successful operation
   */
  private onSuccess(): void {
    this.failureCount = 0;

    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;

      if (this.successCount >= this.successThreshold) {
        this.setState(CircuitState.CLOSED);
        this.successCount = 0;
      }
    }
  }

  /**
   * Handle failed operation
   */
  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    this.successCount = 0;

    if (this.state === CircuitState.HALF_OPEN) {
      this.setState(CircuitState.OPEN);
      this.nextAttemptTime = Date.now() + this.timeout;
    } else if (this.failureCount >= this.failureThreshold) {
      this.setState(CircuitState.OPEN);
      this.nextAttemptTime = Date.now() + this.timeout;
    }

    // Auto-reset failure count after resetTimeout
    setTimeout(() => {
      if (this.state === CircuitState.CLOSED) {
        this.failureCount = 0;
      }
    }, this.resetTimeout);
  }

  /**
   * Change circuit state
   */
  private setState(newState: CircuitState): void {
    if (this.state !== newState) {
      this.state = newState;
      console.log(`[CircuitBreaker:${this.name}] State changed to ${newState}`);
      if (this.onStateChange) {
        this.onStateChange(newState);
      }
    }
  }

  /**
   * Get current state
   */
  getState(): CircuitState {
    return this.state;
  }

  /**
   * Get metrics
   */
  getMetrics() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime,
      nextAttemptTime: this.nextAttemptTime
    };
  }

  /**
   * Manually reset circuit breaker
   */
  reset(): void {
    this.state = CircuitState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = undefined;
    this.nextAttemptTime = undefined;
  }
}

/**
 * Circuit Breaker Manager for multiple services
 */
export class CircuitBreakerManager {
  private breakers = new Map<string, CircuitBreaker>();

  /**
   * Get or create circuit breaker for service
   */
  getBreaker(
    serviceName: string,
    options?: CircuitBreakerOptions
  ): CircuitBreaker {
    if (!this.breakers.has(serviceName)) {
      this.breakers.set(serviceName, new CircuitBreaker(serviceName, options));
    }
    return this.breakers.get(serviceName)!;
  }

  /**
   * Get all breakers
   */
  getAllBreakers(): Map<string, CircuitBreaker> {
    return this.breakers;
  }

  /**
   * Get health status of all services
   */
  getHealthStatus(): Record<string, any> {
    const status: Record<string, any> = {};

    this.breakers.forEach((breaker, name) => {
      const metrics = breaker.getMetrics();
      status[name] = {
        state: metrics.state,
        healthy: metrics.state !== CircuitState.OPEN,
        failureCount: metrics.failureCount,
        lastFailure: metrics.lastFailureTime
          ? new Date(metrics.lastFailureTime).toISOString()
          : null
      };
    });

    return status;
  }

  /**
   * Reset all circuit breakers
   */
  resetAll(): void {
    this.breakers.forEach(breaker => breaker.reset());
  }
}
