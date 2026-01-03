/**
 * ComfyUI Integration Service
 * Handles AI image generation via ComfyUI API
 */

interface ComfyUIConfig {
  apiUrl: string
  outputDir: string
  timeout?: number
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
}

export class ComfyUIService {
  private config: ComfyUIConfig
  private ws: WebSocket | null = null

  constructor(config: ComfyUIConfig) {
    this.config = {
      timeout: 300000, // 5 minutes
      ...config
    }
  }

  /**
   * Submit a prompt to ComfyUI for image generation
   */
  async generate(workflow: ComfyUIWorkflow): Promise<GenerationResult> {
    try {
      // Build workflow JSON for ComfyUI
      const workflowData = this.buildWorkflow(workflow)

      // Submit to queue
      const response = await fetch(`${this.config.apiUrl}/prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: workflowData,
          client_id: this.getClientId()
        })
      })

      if (!response.ok) {
        throw new Error(`ComfyUI API error: ${response.statusText}`)
      }

      const { prompt_id } = await response.json()

      // Wait for generation to complete
      const result = await this.waitForCompletion(prompt_id)

      return result
    } catch (error) {
      return {
        images: [],
        promptId: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
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
          "ckpt_name": "v1-5-pruned-emaonly.safetensors"
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
   * Wait for generation to complete via polling
   */
  private async waitForCompletion(promptId: string): Promise<GenerationResult> {
    const startTime = Date.now()

    while (Date.now() - startTime < this.config.timeout!) {
      try {
        const response = await fetch(`${this.config.apiUrl}/history/${promptId}`)
        const history = await response.json()

        if (history[promptId]?.status?.completed) {
          // Extract output images
          const outputs = history[promptId].outputs
          const images: string[] = []

          for (const nodeId in outputs) {
            if (outputs[nodeId].images) {
              for (const img of outputs[nodeId].images) {
                images.push(`${this.config.apiUrl}/view?filename=${img.filename}&subfolder=${img.subfolder || ''}&type=${img.type}`)
              }
            }
          }

          return {
            images,
            promptId,
            status: 'completed'
          }
        }

        // Check if failed
        if (history[promptId]?.status?.status_str === 'error') {
          return {
            images: [],
            promptId,
            status: 'failed',
            error: 'Generation failed in ComfyUI'
          }
        }

        // Wait before polling again
        await this.sleep(2000)
      } catch (error) {
        console.error('Error polling ComfyUI:', error)
        await this.sleep(2000)
      }
    }

    return {
      images: [],
      promptId,
      status: 'failed',
      error: 'Generation timeout'
    }
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
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * Check if ComfyUI is available
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.apiUrl}/system_stats`, {
        method: 'GET'
      })
      return response.ok
    } catch {
      return false
    }
  }

  /**
   * Get queue status
   */
  async getQueueStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.config.apiUrl}/queue`)
      return await response.json()
    } catch (error) {
      console.error('Error getting queue status:', error)
      return null
    }
  }
}
