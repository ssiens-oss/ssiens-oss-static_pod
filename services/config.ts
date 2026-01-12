/**
 * Configuration Service
 * Centralizes environment variable access
 */

/**
 * Client-side configuration
 * SECURITY: Only non-sensitive config should be here
 * API keys must be used server-side only
 */
export const config = {
  comfyui: {
    apiUrl: import.meta.env.VITE_COMFYUI_API_URL || 'http://localhost:8188',
    outputDir: '/workspace/ComfyUI/output',
    timeout: 300000, // 5 minutes
  },
  runpod: {
    podId: import.meta.env.VITE_RUNPOD_POD_ID || '',
    isRunPod: !!import.meta.env.VITE_RUNPOD_POD_ID,
  },
} as const;
