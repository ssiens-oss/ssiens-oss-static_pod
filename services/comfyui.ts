/**
 * ComfyUI Integration Service
 * Handles AI image generation via ComfyUI API
 */

import { sleep } from '../utils/delay';
import { retryWithBackoff } from '../utils/retry';
import { CircuitBreaker } from '../utils/circuitBreaker';
import {
  APIError,
  TimeoutError,
  ServiceError,
  isRetryableError
} from '../utils/errors';

interface ComfyUIConfig {
  apiUrl: string
  outputDir: string
  timeout?: number
  maxRetries?: number
  pollInterval?: number
  enableCircuitBreaker?: boolean
}

interface ComfyUIWorkflow {
  prompt: string
  workflow?: string
  seed?: number
  width?: number
  height?: number
  steps?: number
  cfg_scale?: number
}

interface GenerationResult {
  images: string[]
  promptId: string
  status: 'completed' | 'failed'
  error?: string
  duration?: number
}

interface HistoryResponse {
  [promptId: string]: {
    status?: {
      completed?: boolean
      status_str?: string
    }
    outputs?: Record<string, {
      images?: Array<{
        filename: string
        subfolder?: string
        type: string
      }>
    }>
  }
}

export class ComfyUIService {
  private config: ComfyUIConfig
  private ws: WebSocket | null = null
  private circuitBreaker?: CircuitBreaker
  private readonly maxRetries: number
  private readonly pollInterval: number

  constructor(config: ComfyUIConfig) {
    this.config = {
      timeout: 300000, // 5 minutes
      maxRetries: 3,
      pollInterval: 2000, // 2 seconds initial
      enableCircuitBreaker: true,
      ...config
    }

    this.maxRetries = this.config.maxRetries!;
    this.pollInterval = this.config.pollInterval!;

    if (this.config.enableCircuitBreaker) {
      this.circuitBreaker = new CircuitBreaker('ComfyUI', {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 60000,
        onStateChange: (state) => {
          console.log(`[ComfyUI] Circuit breaker state: ${state}`);
        }
      });
    }
  }

  /**
   * Submit a prompt to ComfyUI for image generation
   */
  async generate(workflow: ComfyUIWorkflow): Promise<GenerationResult> {
    const startTime = Date.now();

    try {
      const operation = async () => {
        // Build workflow JSON for ComfyUI
        const workflowData = this.buildWorkflow(workflow);

        // Submit to queue with retry
        const response = await this.submitPrompt(workflowData);
        const { prompt_id } = response;

        // Wait for generation to complete
        const result = await this.waitForCompletion(prompt_id);

        return {
          ...result,
          duration: Date.now() - startTime
        };
      };

      // Use circuit breaker if enabled
      if (this.circuitBreaker) {
        return await this.circuitBreaker.execute(operation);
      }

      return await operation();
    } catch (error) {
      console.error('[ComfyUI] Generation failed:', error);

      return {
        images: [],
        promptId: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: Date.now() - startTime
      };
    }
  }

  /**
   * Submit prompt to ComfyUI with retry logic
   */
  private async submitPrompt(workflowData: any): Promise<{ prompt_id: string }> {
    return retryWithBackoff(
      async () => {
        const response = await fetch(`${this.config.apiUrl}/prompt`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: workflowData,
            client_id: this.getClientId()
          })
        });

        if (!response.ok) {
          const errorBody = await response.text().catch(() => '');
          throw new APIError(
            `Failed to submit prompt: ${response.statusText}`,
            'ComfyUI',
            response.status,
            errorBody
          );
        }

        return response.json();
      },
      {
        maxRetries: this.maxRetries,
        initialDelay: 1000,
        maxDelay: 10000,
        backoffMultiplier: 2,
        onRetry: (error, attempt) => {
          console.log(`[ComfyUI] Retry attempt ${attempt} after error:`, error.message);
        }
      }
    );
  }

  /**
   * Generate multiple images in batch
   */
  async generateBatch(workflows: ComfyUIWorkflow[]): Promise<GenerationResult[]> {
    const results: GenerationResult[] = []

    for (const workflow of workflows) {
      const result = await this.generate(workflow)
      results.push(result)
    }

    return results
  }

  /**
   * Build ComfyUI workflow JSON
   */
  private buildWorkflow(workflow: ComfyUIWorkflow): any {
    const {
      prompt,
      seed = Math.floor(Math.random() * 1000000),
      width = 1024,
      height = 1024,
      steps = 20,
      cfg_scale = 7
    } = workflow

    // Basic SDXL workflow structure
    return {
      "3": {
        "inputs": {
          "seed": seed,
          "steps": steps,
          "cfg": cfg_scale,
          "sampler_name": "euler",
          "scheduler": "normal",
          "denoise": 1,
          "model": ["4", 0],
          "positive": ["6", 0],
          "negative": ["7", 0],
          "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
      },
      "4": {
        "inputs": {
          "ckpt_name": "sd_xl_base_1.0.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
      },
      "5": {
        "inputs": {
          "width": width,
          "height": height,
          "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
      },
      "6": {
        "inputs": {
          "text": prompt,
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": {
          "text": "text, watermark, low quality, worst quality",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "8": {
        "inputs": {
          "samples": ["3", 0],
          "vae": ["4", 2]
        },
        "class_type": "VAEDecode"
      },
      "9": {
        "inputs": {
          "filename_prefix": "ComfyUI",
          "images": ["8", 0]
        },
        "class_type": "SaveImage"
      }
    }
  }

  /**
   * Wait for generation to complete via polling with exponential backoff
   */
  private async waitForCompletion(promptId: string): Promise<GenerationResult> {
    const startTime = Date.now();
    let pollDelay = this.pollInterval;
    const maxPollDelay = 10000; // Max 10 seconds between polls
    let attempts = 0;

    while (Date.now() - startTime < this.config.timeout!) {
      try {
        attempts++;

        const response = await fetch(`${this.config.apiUrl}/history/${promptId}`);

        if (!response.ok) {
          throw new APIError(
            'Failed to fetch generation status',
            'ComfyUI',
            response.status
          );
        }

        const history: HistoryResponse = await response.json();
        const promptData = history[promptId];

        if (!promptData) {
          // Prompt not in history yet, continue polling
          await sleep(pollDelay);
          pollDelay = Math.min(pollDelay * 1.5, maxPollDelay);
          continue;
        }

        // Check if completed
        if (promptData.status?.completed) {
          const images = this.extractImagesFromHistory(promptData);

          console.log(`[ComfyUI] Generation completed after ${attempts} polls (${Date.now() - startTime}ms)`);

          return {
            images,
            promptId,
            status: 'completed'
          };
        }

        // Check if failed
        if (promptData.status?.status_str === 'error') {
          throw new ServiceError(
            'Generation failed in ComfyUI',
            'ComfyUI'
          );
        }

        // Still processing, wait before polling again
        await sleep(pollDelay);
        pollDelay = Math.min(pollDelay * 1.5, maxPollDelay);
      } catch (error) {
        if (error instanceof ServiceError) {
          return {
            images: [],
            promptId,
            status: 'failed',
            error: error.message
          };
        }

        console.error('[ComfyUI] Error polling status:', error);

        // Retry with backoff on transient errors
        await sleep(pollDelay);
        pollDelay = Math.min(pollDelay * 2, maxPollDelay);
      }
    }

    throw new TimeoutError(
      `Generation timeout after ${this.config.timeout}ms`,
      'ComfyUI',
      this.config.timeout!
    );
  }

  /**
   * Extract image URLs from ComfyUI history response
   */
  private extractImagesFromHistory(promptData: HistoryResponse[string]): string[] {
    const images: string[] = [];
    const outputs = promptData.outputs ?? {};

    for (const nodeId in outputs) {
      const nodeOutputs = outputs[nodeId];
      if (nodeOutputs.images) {
        for (const img of nodeOutputs.images) {
          const subfolder = img.subfolder || '';
          images.push(
            `${this.config.apiUrl}/view?filename=${img.filename}&subfolder=${subfolder}&type=${img.type}`
          );
        }
      }
    }

    return images;
  }

  /**
   * Connect to ComfyUI WebSocket for real-time updates
   */
  connectWebSocket(onProgress?: (data: any) => void): void {
    const wsUrl = this.config.apiUrl.replace('http', 'ws') + '/ws'

    this.ws = new WebSocket(wsUrl)

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (onProgress) {
        onProgress(data)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * Get or generate client ID
   */
  private getClientId(): string {
    if (typeof window !== 'undefined') {
      let clientId = localStorage.getItem('comfyui_client_id')
      if (!clientId) {
        clientId = Math.random().toString(36).substring(7)
        localStorage.setItem('comfyui_client_id', clientId)
      }
      return clientId
    }
    return 'server-' + Math.random().toString(36).substring(7)
  }

  /**
   * Helper: Sleep utility
   */

  /**
   * Check if ComfyUI is available
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.apiUrl}/system_stats`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });

      if (response.ok) {
        // Reset circuit breaker on successful health check
        if (this.circuitBreaker) {
          this.circuitBreaker.reset();
        }
        return true;
      }

      return false;
    } catch (error) {
      console.error('[ComfyUI] Health check failed:', error);
      return false;
    }
  }

  /**
   * Get queue status
   */
  async getQueueStatus(): Promise<QueueStatus | null> {
    try {
      const response = await fetch(`${this.config.apiUrl}/queue`, {
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        throw new APIError(
          'Failed to get queue status',
          'ComfyUI',
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      console.error('[ComfyUI] Error getting queue status:', error);
      return null;
    }
  }

  /**
   * Get circuit breaker metrics
   */
  getMetrics() {
    return {
      circuitBreaker: this.circuitBreaker?.getMetrics(),
      config: {
        timeout: this.config.timeout,
        maxRetries: this.maxRetries,
        pollInterval: this.pollInterval
      }
    };
  }
}

interface QueueStatus {
  queue_running?: any[];
  queue_pending?: any[];
}
