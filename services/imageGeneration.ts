/**
 * Image Generation Service Factory
 * Automatically selects between Local ComfyUI and RunPod Serverless based on environment
 */

import { ComfyUIService } from './comfyui';
import { RunPodServerlessService } from './runpod';

interface ImageGenConfig {
  prompt: string;
  seed?: number;
  width?: number;
  height?: number;
  steps?: number;
  cfg_scale?: number;
}

interface ImageGenResult {
  images: string[];
  jobId: string;
  status: 'completed' | 'failed' | 'pending' | 'running';
  error?: string;
}

/**
 * Unified Image Generation Service
 * Automatically uses RunPod Serverless if configured, otherwise falls back to local ComfyUI
 */
export class ImageGenerationService {
  private service: ComfyUIService | RunPodServerlessService;
  private serviceType: 'local' | 'runpod';

  constructor() {
    // Check for RunPod configuration
    const runpodApiKey = import.meta.env.VITE_RUNPOD_API_KEY || process.env.RUNPOD_API_KEY;
    const runpodEndpointId = import.meta.env.VITE_RUNPOD_ENDPOINT_ID || process.env.RUNPOD_ENDPOINT_ID;

    if (runpodApiKey && runpodEndpointId) {
      // Use RunPod Serverless
      console.log('[ImageGen] Using RunPod Serverless:', runpodEndpointId);
      this.service = new RunPodServerlessService({
        apiKey: runpodApiKey,
        endpointId: runpodEndpointId,
        timeout: 600000 // 10 minutes
      });
      this.serviceType = 'runpod';
    } else {
      // Fall back to local ComfyUI
      const comfyuiUrl = import.meta.env.VITE_COMFYUI_API_URL ||
                         process.env.COMFYUI_API_URL ||
                         'http://localhost:8188';
      const outputDir = import.meta.env.VITE_COMFYUI_OUTPUT_DIR ||
                        process.env.COMFYUI_OUTPUT_DIR ||
                        '/data/comfyui/output';

      console.log('[ImageGen] Using Local ComfyUI:', comfyuiUrl);
      this.service = new ComfyUIService({
        apiUrl: comfyuiUrl,
        outputDir: outputDir,
        timeout: 300000 // 5 minutes
      });
      this.serviceType = 'local';
    }
  }

  /**
   * Generate a single image
   */
  async generate(config: ImageGenConfig): Promise<ImageGenResult> {
    if (this.serviceType === 'runpod') {
      const runpodService = this.service as RunPodServerlessService;
      return await runpodService.generate({
        prompt: config.prompt,
        seed: config.seed,
        width: config.width,
        height: config.height,
        steps: config.steps,
        cfg_scale: config.cfg_scale
      });
    } else {
      const comfyService = this.service as ComfyUIService;
      const result = await comfyService.generate({
        prompt: config.prompt,
        seed: config.seed,
        width: config.width,
        height: config.height,
        steps: config.steps,
        cfg_scale: config.cfg_scale
      });

      return {
        images: result.images,
        jobId: result.promptId,
        status: result.status,
        error: result.error
      };
    }
  }

  /**
   * Generate multiple images in batch
   */
  async generateBatch(configs: ImageGenConfig[]): Promise<ImageGenResult[]> {
    const results: ImageGenResult[] = [];

    for (const config of configs) {
      const result = await this.generate(config);
      results.push(result);
    }

    return results;
  }

  /**
   * Health check for the active service
   */
  async healthCheck(): Promise<boolean> {
    return await this.service.healthCheck();
  }

  /**
   * Get service type
   */
  getServiceType(): 'local' | 'runpod' {
    return this.serviceType;
  }

  /**
   * Get queue status (local ComfyUI only)
   */
  async getQueueStatus(): Promise<any> {
    if (this.serviceType === 'local') {
      const comfyService = this.service as ComfyUIService;
      return await comfyService.getQueueStatus();
    }
    return null;
  }

  /**
   * Connect to WebSocket for real-time updates (local ComfyUI only)
   */
  connectWebSocket(onProgress?: (data: any) => void): void {
    if (this.serviceType === 'local') {
      const comfyService = this.service as ComfyUIService;
      comfyService.connectWebSocket(onProgress);
    } else {
      console.warn('[ImageGen] WebSocket not supported for RunPod Serverless');
    }
  }

  /**
   * Disconnect WebSocket (local ComfyUI only)
   */
  disconnectWebSocket(): void {
    if (this.serviceType === 'local') {
      const comfyService = this.service as ComfyUIService;
      comfyService.disconnectWebSocket();
    }
  }
}

// Export singleton instance
export const imageGenService = new ImageGenerationService();
