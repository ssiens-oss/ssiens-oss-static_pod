/**
 * RunPod Serverless ComfyUI Integration
 * Handles AI image generation via RunPod Serverless API
 */

import { sleep } from '../utils/delay';

interface RunPodConfig {
  apiKey: string;
  endpointId: string;
  timeout?: number;
}

interface RunPodWorkflow {
  prompt: string;
  workflow?: string;
  seed?: number;
  width?: number;
  height?: number;
  steps?: number;
  cfg_scale?: number;
}

interface RunPodGenerationResult {
  images: string[];
  jobId: string;
  status: 'completed' | 'failed' | 'pending' | 'running';
  error?: string;
}

export class RunPodServerlessService {
  private config: RunPodConfig;
  private baseUrl: string;

  constructor(config: RunPodConfig) {
    this.config = {
      timeout: 600000, // 10 minutes for serverless
      ...config
    };
    this.baseUrl = `https://api.runpod.ai/v2/${this.config.endpointId}`;
  }

  /**
   * Submit a prompt to RunPod Serverless for image generation
   */
  async generate(workflow: RunPodWorkflow): Promise<RunPodGenerationResult> {
    try {
      // Build workflow JSON for ComfyUI
      const workflowData = this.buildWorkflow(workflow);

      // Submit to RunPod /run endpoint (async)
      const response = await fetch(`${this.baseUrl}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          input: {
            workflow: workflowData,
            images: [] // Optional base64 encoded images if needed
          }
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`RunPod API error (${response.status}): ${errorText}`);
      }

      const { id: jobId } = await response.json();

      // Wait for generation to complete
      const result = await this.waitForCompletion(jobId);

      return result;
    } catch (error) {
      return {
        images: [],
        jobId: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Generate using /runsync endpoint (synchronous, waits for completion)
   */
  async generateSync(workflow: RunPodWorkflow): Promise<RunPodGenerationResult> {
    try {
      const workflowData = this.buildWorkflow(workflow);

      const response = await fetch(`${this.baseUrl}/runsync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          input: {
            workflow: workflowData,
            images: []
          }
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`RunPod API error (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      if (data.status === 'COMPLETED') {
        return {
          images: data.output?.images || [],
          jobId: data.id,
          status: 'completed'
        };
      } else if (data.status === 'FAILED') {
        return {
          images: [],
          jobId: data.id,
          status: 'failed',
          error: data.error || 'Generation failed'
        };
      }

      return {
        images: [],
        jobId: data.id,
        status: 'failed',
        error: 'Unexpected status: ' + data.status
      };
    } catch (error) {
      return {
        images: [],
        jobId: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Generate multiple images in batch
   */
  async generateBatch(workflows: RunPodWorkflow[]): Promise<RunPodGenerationResult[]> {
    const results: RunPodGenerationResult[] = [];

    for (const workflow of workflows) {
      const result = await this.generate(workflow);
      results.push(result);
    }

    return results;
  }

  /**
   * Build ComfyUI workflow JSON (same format as local ComfyUI)
   */
  private buildWorkflow(workflow: RunPodWorkflow): any {
    const {
      prompt,
      seed = Math.floor(Math.random() * 1000000),
      width = 1024,
      height = 1024,
      steps = 20,
      cfg_scale = 7
    } = workflow;

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
    };
  }

  /**
   * Wait for generation to complete via polling /status endpoint
   */
  private async waitForCompletion(jobId: string): Promise<RunPodGenerationResult> {
    const startTime = Date.now();
    let attempts = 0;

    while (Date.now() - startTime < this.config.timeout!) {
      try {
        const response = await fetch(`${this.baseUrl}/status/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`
          }
        });

        if (!response.ok) {
          throw new Error(`Status check failed: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.status === 'COMPLETED') {
          // Extract images from output
          const images = data.output?.images || [];

          return {
            images,
            jobId,
            status: 'completed'
          };
        }

        if (data.status === 'FAILED') {
          return {
            images: [],
            jobId,
            status: 'failed',
            error: data.error || 'Generation failed'
          };
        }

        // Still processing (IN_QUEUE or IN_PROGRESS)
        // Exponential backoff: 2s, 4s, 6s, 8s, max 10s
        const waitTime = Math.min(2000 + (attempts * 2000), 10000);
        await sleep(waitTime);
        attempts++;

      } catch (error) {
        console.error('Error polling RunPod status:', error);
        await sleep(5000); // Wait 5s on error before retrying
      }
    }

    return {
      images: [],
      jobId,
      status: 'failed',
      error: 'Generation timeout'
    };
  }

  /**
   * Cancel a running job
   */
  async cancelJob(jobId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/cancel/${jobId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`
        }
      });

      return response.ok;
    } catch (error) {
      console.error('Error canceling job:', error);
      return false;
    }
  }

  /**
   * Check RunPod endpoint health
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`
        }
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get endpoint status
   */
  async getEndpointStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/status`, {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`
        }
      });
      return await response.json();
    } catch (error) {
      console.error('Error getting endpoint status:', error);
      return null;
    }
  }
}
