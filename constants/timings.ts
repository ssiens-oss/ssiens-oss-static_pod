/**
 * Timing Constants
 * Centralized timing values for consistency
 */

export const TIMEOUTS = {
  /** Connection health check interval: 30 seconds */
  CONNECTION_CHECK_INTERVAL: 30_000,

  /** ComfyUI polling interval: 2 seconds */
  POLLING_INTERVAL: 2_000,

  /** ComfyUI generation timeout: 5 minutes */
  GENERATION_TIMEOUT: 300_000,

  /** Default API request timeout: 30 seconds */
  API_REQUEST_TIMEOUT: 30_000,

  /** Short delay for UI animations: 600ms */
  SHORT_DELAY: 600,

  /** Medium delay: 800ms */
  MEDIUM_DELAY: 800,

  /** Long delay: 1 second */
  LONG_DELAY: 1_000,
} as const;

export const RETRY_CONFIG = {
  /** Default number of retries for failed requests */
  DEFAULT_RETRIES: 3,

  /** Base delay for exponential backoff: 1 second */
  BASE_RETRY_DELAY: 1_000,

  /** Maximum retry delay: 16 seconds */
  MAX_RETRY_DELAY: 16_000,
} as const;
