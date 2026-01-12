/**
 * Storage Service
 * Handles auto-saving of generated images to local/cloud storage
 *
 * ⚠️ BACKEND ONLY - This service uses Node.js APIs (fs, path, crypto)
 * This will NOT work in browser environments. Only use this in:
 * - Node.js backend servers
 * - Electron apps
 * - Server-side rendering contexts
 *
 * For browser-based storage, use Web APIs like IndexedDB or localStorage
 */

import * as fs from 'fs'
import * as path from 'path'
import * as crypto from 'crypto'

interface StorageConfig {
  type: 'local' | 's3' | 'gcs'
  basePath: string
  s3Config?: {
    bucket: string
    region: string
    accessKeyId: string
    secretAccessKey: string
  }
  gcsConfig?: {
    bucket: string
    projectId: string
    keyFilename: string
  }
}

interface SavedImage {
  id: string
  filename: string
  path: string
  url: string
  hash: string
  size: number
  timestamp: Date
  metadata?: any
}

export class StorageService {
  private config: StorageConfig
  private imageIndex: Map<string, SavedImage> = new Map()

  constructor(config: StorageConfig) {
    this.config = config
    this.ensureDirectory()
  }

  /**
   * Save image from URL or Buffer
   */
  async saveImage(
    source: string | Buffer,
    metadata?: any
  ): Promise<SavedImage> {
    let imageBuffer: Buffer

    // Get image data
    if (typeof source === 'string') {
      imageBuffer = await this.fetchImage(source)
    } else {
      imageBuffer = source
    }

    // Generate hash to detect duplicates
    const hash = this.generateHash(imageBuffer)

    // Check if already exists
    const existing = Array.from(this.imageIndex.values()).find(
      img => img.hash === hash
    )
    if (existing) {
      console.log('Duplicate image detected, returning existing:', existing.id)
      return existing
    }

    // Generate filename
    const id = this.generateId()
    const ext = this.detectExtension(imageBuffer)
    const filename = `${id}.${ext}`

    // Save based on storage type
    let savedImage: SavedImage

    switch (this.config.type) {
      case 'local':
        savedImage = await this.saveLocal(filename, imageBuffer, hash, metadata)
        break
      case 's3':
        savedImage = await this.saveToS3(filename, imageBuffer, hash, metadata)
        break
      case 'gcs':
        savedImage = await this.saveToGCS(filename, imageBuffer, hash, metadata)
        break
      default:
        throw new Error(`Unsupported storage type: ${this.config.type}`)
    }

    // Add to index
    this.imageIndex.set(id, savedImage)

    // Save metadata
    await this.saveMetadata(id, savedImage)

    return savedImage
  }

  /**
   * Save multiple images in batch
   */
  async saveBatch(sources: Array<string | Buffer>, metadata?: any[]): Promise<SavedImage[]> {
    const results: SavedImage[] = []

    for (let i = 0; i < sources.length; i++) {
      const source = sources[i]
      const meta = metadata?.[i] || {}
      const saved = await this.saveImage(source, meta)
      results.push(saved)
    }

    return results
  }

  /**
   * Save to local filesystem
   */
  private async saveLocal(
    filename: string,
    buffer: Buffer,
    hash: string,
    metadata?: any
  ): Promise<SavedImage> {
    const filepath = path.join(this.config.basePath, filename)

    // Write file
    await fs.promises.writeFile(filepath, buffer)

    const id = filename.split('.')[0]

    return {
      id,
      filename,
      path: filepath,
      url: `file://${filepath}`,
      hash,
      size: buffer.length,
      timestamp: new Date(),
      metadata
    }
  }

  /**
   * Save to AWS S3 (placeholder - requires aws-sdk)
   */
  private async saveToS3(
    filename: string,
    buffer: Buffer,
    hash: string,
    metadata?: any
  ): Promise<SavedImage> {
    // Note: In production, use AWS SDK
    // import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'

    console.warn('S3 storage not fully implemented - saving locally instead')
    return this.saveLocal(filename, buffer, hash, metadata)
  }

  /**
   * Save to Google Cloud Storage (placeholder - requires @google-cloud/storage)
   */
  private async saveToGCS(
    filename: string,
    buffer: Buffer,
    hash: string,
    metadata?: any
  ): Promise<SavedImage> {
    // Note: In production, use Google Cloud Storage SDK
    // import { Storage } from '@google-cloud/storage'

    console.warn('GCS storage not fully implemented - saving locally instead')
    return this.saveLocal(filename, buffer, hash, metadata)
  }

  /**
   * Fetch image from URL
   */
  private async fetchImage(url: string): Promise<Buffer> {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.statusText}`)
    }
    const arrayBuffer = await response.arrayBuffer()
    return Buffer.from(arrayBuffer)
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `img_${Date.now()}_${Math.random().toString(36).substring(7)}`
  }

  /**
   * Generate hash for duplicate detection
   */
  private generateHash(buffer: Buffer): string {
    return crypto.createHash('sha256').update(buffer).digest('hex')
  }

  /**
   * Detect image file extension
   */
  private detectExtension(buffer: Buffer): string {
    // Check magic numbers
    if (buffer[0] === 0xFF && buffer[1] === 0xD8) return 'jpg'
    if (buffer[0] === 0x89 && buffer[1] === 0x50) return 'png'
    if (buffer[0] === 0x47 && buffer[1] === 0x49) return 'gif'
    if (buffer[0] === 0x52 && buffer[1] === 0x49) return 'webp'

    // Default to png
    return 'png'
  }

  /**
   * Ensure storage directory exists
   */
  private ensureDirectory(): void {
    if (this.config.type === 'local') {
      if (!fs.existsSync(this.config.basePath)) {
        fs.mkdirSync(this.config.basePath, { recursive: true })
      }
    }
  }

  /**
   * Save metadata to JSON
   */
  private async saveMetadata(id: string, image: SavedImage): Promise<void> {
    const metadataPath = path.join(
      this.config.basePath,
      `${id}.metadata.json`
    )

    await fs.promises.writeFile(
      metadataPath,
      JSON.stringify(image, null, 2)
    )
  }

  /**
   * Get image by ID
   */
  async getImage(id: string): Promise<SavedImage | null> {
    return this.imageIndex.get(id) || null
  }

  /**
   * List all saved images
   */
  async listImages(filter?: { startDate?: Date; endDate?: Date }): Promise<SavedImage[]> {
    let images = Array.from(this.imageIndex.values())

    if (filter?.startDate) {
      images = images.filter(img => img.timestamp >= filter.startDate!)
    }

    if (filter?.endDate) {
      images = images.filter(img => img.timestamp <= filter.endDate!)
    }

    return images.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }

  /**
   * Delete image by ID
   */
  async deleteImage(id: string): Promise<boolean> {
    const image = this.imageIndex.get(id)
    if (!image) return false

    if (this.config.type === 'local') {
      try {
        await fs.promises.unlink(image.path)
        await fs.promises.unlink(image.path.replace(/\.\w+$/, '.metadata.json'))
      } catch (error) {
        console.error('Error deleting image:', error)
        return false
      }
    }

    this.imageIndex.delete(id)
    return true
  }

  /**
   * Get storage statistics
   */
  getStats(): {
    totalImages: number
    totalSize: number
    oldestImage: Date | null
    newestImage: Date | null
  } {
    const images = Array.from(this.imageIndex.values())

    return {
      totalImages: images.length,
      totalSize: images.reduce((sum, img) => sum + img.size, 0),
      oldestImage: images.length > 0
        ? new Date(Math.min(...images.map(img => img.timestamp.getTime())))
        : null,
      newestImage: images.length > 0
        ? new Date(Math.max(...images.map(img => img.timestamp.getTime())))
        : null
    }
  }
}
