/**
 * RunPod Service
 * Manages RunPod pod interactions and file syncing
 */

export interface RunPodConfig {
  apiKey: string
  podId: string
  baseUrl?: string
}

export interface PodStatus {
  id: string
  status: 'running' | 'stopped' | 'starting' | 'stopping'
  gpuType: string
  cpuCores: number
  memoryGB: number
  diskGB: number
}

export interface FileInfo {
  path: string
  name: string
  size: number
  lastModified: string
  url: string
}

export class RunPodService {
  private config: RunPodConfig
  private baseUrl: string

  constructor(config: RunPodConfig) {
    this.config = config
    this.baseUrl = config.baseUrl || 'https://api.runpod.io/v2'
  }

  /**
   * Get pod status
   */
  async getPodStatus(): Promise<PodStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/${this.config.podId}/status`, {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get pod status: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error getting pod status:', error)
      throw error
    }
  }

  /**
   * List files in pod directory
   */
  async listFiles(directory: string = '/workspace/ComfyUI/output'): Promise<FileInfo[]> {
    try {
      // Note: This is a placeholder implementation
      // In production, you would use RunPod's actual API or SSH/SFTP to list files

      console.log(`Listing files in ${directory} on pod ${this.config.podId}`)

      // Example response structure
      const files: FileInfo[] = []

      return files
    } catch (error) {
      console.error('Error listing files:', error)
      throw error
    }
  }

  /**
   * Download file from pod
   */
  async downloadFile(remotePath: string): Promise<Buffer> {
    try {
      // Note: In production, this would download via RunPod API, HTTP endpoint, or SFTP
      // For now, this is a placeholder

      console.log(`Downloading ${remotePath} from pod ${this.config.podId}`)

      // In a real implementation:
      // 1. Use RunPod's HTTP endpoint to access files
      // 2. Or use SSH/SFTP to download files
      // 3. Or use RunPod's API to get file URLs

      // Example: If RunPod exposes files via HTTP
      // const fileUrl = `https://${this.config.podId}.runpod.io/files${remotePath}`
      // const response = await fetch(fileUrl)
      // return Buffer.from(await response.arrayBuffer())

      throw new Error('Download file not implemented - configure RunPod file access')
    } catch (error) {
      console.error('Error downloading file:', error)
      throw error
    }
  }

  /**
   * Sync ComfyUI output directory to local storage
   */
  async syncComfyUIOutput(
    outputDir: string = '/workspace/ComfyUI/output',
    localDir: string
  ): Promise<string[]> {
    try {
      console.log(`Syncing ComfyUI output from ${outputDir} to ${localDir}`)

      const files = await this.listFiles(outputDir)
      const downloadedFiles: string[] = []

      for (const file of files) {
        try {
          const buffer = await this.downloadFile(file.path)

          // Save to local directory
          const fs = await import('fs')
          const path = await import('path')

          const localPath = path.join(localDir, file.name)
          await fs.promises.writeFile(localPath, buffer)

          downloadedFiles.push(localPath)
          console.log(`Downloaded: ${file.name}`)
        } catch (error) {
          console.error(`Failed to download ${file.name}:`, error)
        }
      }

      return downloadedFiles
    } catch (error) {
      console.error('Error syncing ComfyUI output:', error)
      throw error
    }
  }

  /**
   * Execute command on pod
   */
  async executeCommand(command: string): Promise<string> {
    try {
      // Note: This would require SSH or RunPod's exec API
      console.log(`Executing command on pod: ${command}`)

      throw new Error('Execute command not implemented - configure RunPod SSH access')
    } catch (error) {
      console.error('Error executing command:', error)
      throw error
    }
  }

  /**
   * Upload file to pod
   */
  async uploadFile(localPath: string, remotePath: string): Promise<void> {
    try {
      console.log(`Uploading ${localPath} to ${remotePath} on pod ${this.config.podId}`)

      // In production, implement file upload via:
      // 1. RunPod's upload API
      // 2. SSH/SFTP
      // 3. HTTP POST to pod's endpoint

      throw new Error('Upload file not implemented - configure RunPod file upload')
    } catch (error) {
      console.error('Error uploading file:', error)
      throw error
    }
  }

  /**
   * Get ComfyUI status on pod
   */
  async getComfyUIStatus(): Promise<{
    running: boolean
    port: number
    url: string
  }> {
    try {
      // Check if ComfyUI is running on the pod
      const podStatus = await this.getPodStatus()

      // Assuming ComfyUI runs on port 8188
      const port = 8188
      const url = `https://${this.config.podId}.runpod.io:${port}`

      return {
        running: podStatus.status === 'running',
        port,
        url
      }
    } catch (error) {
      console.error('Error getting ComfyUI status:', error)
      throw error
    }
  }

  /**
   * Wait for pod to be ready
   */
  async waitForReady(timeoutMs: number = 60000): Promise<void> {
    const startTime = Date.now()

    while (Date.now() - startTime < timeoutMs) {
      try {
        const status = await this.getPodStatus()
        if (status.status === 'running') {
          console.log('Pod is ready')
          return
        }
      } catch (error) {
        // Ignore errors while waiting
      }

      // Wait 5 seconds before checking again
      await new Promise(resolve => setTimeout(resolve, 5000))
    }

    throw new Error('Pod did not become ready within timeout')
  }
}
