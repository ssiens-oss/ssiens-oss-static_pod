/**
 * Simple in-memory cache with TTL support
 * Useful for caching API responses and reducing external calls
 */

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  maxSize?: number; // Maximum number of entries
}

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

/**
 * Simple LRU cache with TTL
 */
export class Cache<K = string, V = any> {
  private cache = new Map<K, CacheEntry<V>>();
  private readonly ttl: number;
  private readonly maxSize: number;

  constructor(options: CacheOptions = {}) {
    this.ttl = options.ttl ?? 300000; // Default 5 minutes
    this.maxSize = options.maxSize ?? 1000;
  }

  /**
   * Get value from cache
   */
  get(key: K): V | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      return undefined;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return undefined;
    }

    return entry.value;
  }

  /**
   * Set value in cache
   */
  set(key: K, value: V, ttl?: number): void {
    // Enforce max size (simple LRU: remove oldest)
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    const expiresAt = Date.now() + (ttl ?? this.ttl);
    this.cache.set(key, { value, expiresAt });
  }

  /**
   * Check if key exists and is not expired
   */
  has(key: K): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Delete key from cache
   */
  delete(key: K): boolean {
    return this.cache.delete(key);
  }

  /**
   * Clear all entries
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache size
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      ttl: this.ttl
    };
  }

  /**
   * Get or set pattern (fetch if not cached)
   */
  async getOrSet(
    key: K,
    fetcher: () => Promise<V>,
    ttl?: number
  ): Promise<V> {
    const cached = this.get(key);
    if (cached !== undefined) {
      return cached;
    }

    const value = await fetcher();
    this.set(key, value, ttl);
    return value;
  }

  /**
   * Clean expired entries
   */
  cleanup(): void {
    const now = Date.now();
    const keysToDelete: K[] = [];

    this.cache.forEach((entry, key) => {
      if (now > entry.expiresAt) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }

  /**
   * Start automatic cleanup interval
   */
  startAutoCleanup(intervalMs: number = 60000): () => void {
    const interval = setInterval(() => this.cleanup(), intervalMs);
    return () => clearInterval(interval);
  }
}

/**
 * Async cache wrapper for functions
 */
export function memoize<Args extends any[], Result>(
  fn: (...args: Args) => Promise<Result>,
  options: CacheOptions & {
    keyGenerator?: (...args: Args) => string;
  } = {}
): (...args: Args) => Promise<Result> {
  const cache = new Cache<string, Result>(options);
  const keyGenerator =
    options.keyGenerator ?? ((...args: Args) => JSON.stringify(args));

  return async (...args: Args): Promise<Result> => {
    const key = keyGenerator(...args);
    return cache.getOrSet(key, () => fn(...args));
  };
}
