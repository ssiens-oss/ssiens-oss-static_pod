/**
 * Utility function to delay execution
 * @param ms - Milliseconds to delay
 * @returns Promise that resolves after the specified delay
 */
export const sleep = (ms: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, ms));
