/**
 * ID Generation Utilities
 * Centralized ID generation for consistency across the app
 */

/**
 * Generates a unique ID
 * @param prefix - Optional prefix for the ID
 * @returns string - Unique identifier
 *
 * @example
 * generateId() // => "1kf8j2lk9j"
 * generateId('log') // => "log_1kf8j2lk9j"
 * generateId('img') // => "img_1kf8j2lk9j"
 */
export function generateId(prefix?: string): string {
  // Use crypto.randomUUID if available (modern browsers + Node.js)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    const uuid = crypto.randomUUID();
    return prefix ? `${prefix}_${uuid}` : uuid;
  }

  // Fallback: Combine timestamp + random for uniqueness
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 11);
  const id = `${timestamp}${randomPart}`;

  return prefix ? `${prefix}_${id}` : id;
}

/**
 * Generates a short ID (for logs, temporary items)
 * @param prefix - Optional prefix
 * @returns string - Short unique identifier
 */
export function generateShortId(prefix?: string): string {
  const randomPart = Math.random().toString(36).substring(2, 9);
  return prefix ? `${prefix}_${randomPart}` : randomPart;
}
