/**
 * Configuration Service
 * Centralizes environment variable access
 */

export const config = {
  comfyui: {
    apiUrl: import.meta.env.VITE_COMFYUI_API_URL || 'http://localhost:8188',
    outputDir: '/workspace/ComfyUI/output',
    timeout: 300000, // 5 minutes
  },
  runpod: {
    podId: import.meta.env.VITE_RUNPOD_POD_ID || '',
  },
  anthropic: {
    apiKey: import.meta.env.VITE_ANTHROPIC_API_KEY || '',
  }
}

export function getComfyUIUrl(): string {
  return config.comfyui.apiUrl
}

export function isRunPod(): boolean {
  return !!config.runpod.podId
}
