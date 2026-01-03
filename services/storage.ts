/**
 * Storage Service
 * Handles auto-saving of generated images to local/cloud storage
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
   * Save to AWS S3
   */
  private async saveToS3(
    filename: string,
    buffer: Buffer,
    hash: string,
    metadata?: any
  ): Promise<SavedImage> {
    if (!this.config.s3Config) {
      throw new Error('S3 configuration is missing')
    }

    try {
      // Use fetch to upload to S3 (presigned URL or direct)
      // For production, you would use @aws-sdk/client-s3
      const { bucket, region, accessKeyId, secretAccessKey } = this.config.s3Config
      const key = `designs/${filename}`

      // Generate presigned URL or use SDK
      // This is a simplified implementation - in production use AWS SDK
      const s3Url = `https://${bucket}.s3.${region}.amazonaws.com/${key}`

      // For now, create a PUT request with AWS signature
      // In production: import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'
      const response = await this.uploadToS3WithSDK(
        bucket,
        key,
        buffer,
        region,
        accessKeyId,
        secretAccessKey
      )

      const id = filename.split('.')[0]

      return {
        id,
        filename,
        path: key,
        url: s3Url,
        hash,
        size: buffer.length,
        timestamp: new Date(),
        metadata
      }
    } catch (error) {
      console.error('S3 upload failed, falling back to local storage:', error)
      return this.saveLocal(filename, buffer, hash, metadata)
    }
  }

  /**
   * Upload to S3 using SDK-like approach
   * NOTE: In production, install @aws-sdk/client-s3 and use proper SDK
   */
  private async uploadToS3WithSDK(
    bucket: string,
    key: string,
    buffer: Buffer,
    region: string,
    accessKeyId: string,
    secretAccessKey: string
  ): Promise<boolean> {
    // This is a placeholder for actual S3 SDK implementation
    // To implement properly:
    // 1. Install: npm install @aws-sdk/client-s3
    // 2. Import: import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'
    // 3. Use SDK methods

    console.warn('Using S3 SDK placeholder - install @aws-sdk/client-s3 for production')

    // Simulated SDK call structure (for reference):
    /*
    const s3Client = new S3Client({
      region,
      credentials: {
        accessKeyId,
        secretAccessKey
      }
    })

    const command = new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: buffer,
      ContentType: 'image/png'
    })

    await s3Client.send(command)
    */

    return true
  }

  /**
   * Save to Google Cloud Storage
   */
  private async saveToGCS(
    filename: string,
    buffer: Buffer,
    hash: string,
    metadata?: any
  ): Promise<SavedImage> {
    if (!this.config.gcsConfig) {
      throw new Error('GCS configuration is missing')
    }

    try {
      const { bucket, projectId, keyFilename } = this.config.gcsConfig
      const objectName = `designs/${filename}`

      // Upload to GCS
      // For production: import { Storage } from '@google-cloud/storage'
      await this.uploadToGCSWithSDK(
        bucket,
        objectName,
        buffer,
        projectId,
        keyFilename
      )

      const gcsUrl = `https://storage.googleapis.com/${bucket}/${objectName}`
      const id = filename.split('.')[0]

      return {
        id,
        filename,
        path: objectName,
        url: gcsUrl,
        hash,
        size: buffer.length,
        timestamp: new Date(),
        metadata
      }
    } catch (error) {
      console.error('GCS upload failed, falling back to local storage:', error)
      return this.saveLocal(filename, buffer, hash, metadata)
    }
  }

  /**
   * Upload to GCS using SDK-like approach
   * NOTE: In production, install @google-cloud/storage and use proper SDK
   */
  private async uploadToGCSWithSDK(
    bucketName: string,
    objectName: string,
    buffer: Buffer,
    projectId: string,
    keyFilename: string
  ): Promise<boolean> {
    // This is a placeholder for actual GCS SDK implementation
    // To implement properly:
    // 1. Install: npm install @google-cloud/storage
    // 2. Import: import { Storage } from '@google-cloud/storage'
    // 3. Use SDK methods

    console.warn('Using GCS SDK placeholder - install @google-cloud/storage for production')

    // Simulated SDK call structure (for reference):
    /*
    const storage = new Storage({
      projectId,
      keyFilename
    })

    const bucket = storage.bucket(bucketName)
    const file = bucket.file(objectName)

    await file.save(buffer, {
      contentType: 'image/png',
      metadata: {
        cacheControl: 'public, max-age=31536000'
      }
    })
    */

    return true
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
