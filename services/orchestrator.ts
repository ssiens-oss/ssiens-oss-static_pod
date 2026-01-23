/**
 * Pipeline Orchestrator
 * Coordinates the entire POD automation workflow
 */

import { PromptData, SavedImageData, ProductResult } from '../types';
import { ComfyUIService } from './comfyui';
import { ClaudePromptingService } from './claudePrompting';
import { StorageService } from './storage';
import { PrintifyService } from './printify';
import { ShopifyService } from './shopify';
import { TikTokShopService } from './platforms/tiktok';
import { EtsyService } from './platforms/etsy';
import { InstagramService } from './platforms/instagram';
import { FacebookShopService } from './platforms/facebook';
import { CircuitBreakerManager } from '../utils/circuitBreaker';
import { getErrorMessage, formatErrorForLogging } from '../utils/errors';

interface OrchestratorConfig {
  comfyui: {
    apiUrl: string
    outputDir: string
  }
  claude: {
    apiKey: string
  }
  storage: {
    type: 'local' | 's3' | 'gcs'
    basePath: string
  }
  printify?: {
    apiKey: string
    shopId: string
  }
  shopify?: {
    storeUrl: string
    accessToken: string
  }
  tiktok?: {
    appKey: string
    appSecret: string
    shopId: string
    accessToken: string
  }
  etsy?: {
    apiKey: string
    shopId: string
    accessToken: string
  }
  instagram?: {
    accessToken: string
    businessAccountId: string
  }
  facebook?: {
    pageId: string
    accessToken: string
    catalogId: string
  }
  options?: {
    enabledPlatforms?: string[]
    autoPublish?: boolean
    tshirtPrice?: number
    hoodiePrice?: number
  }
}

interface PipelineRequest {
  prompt?: string
  theme?: string
  style?: string
  niche?: string
  productTypes: ('tshirt' | 'hoodie')[]
  count?: number
  autoPublish?: boolean
}

interface PipelineResult {
  success: boolean
  generatedImages: Array<{
    id: string
    url: string
    prompt: string
  }>
  products: Array<{
    platform: string
    productId: string
    url: string
    type: 'tshirt' | 'hoodie'
  }>
  errors: string[]
  platformErrors?: Array<{
    platform: string
    error: string
    imageId?: string
  }>
  totalTime: number
}

export class Orchestrator {
  private comfyui: ComfyUIService
  private claude: ClaudePromptingService
  private storage: StorageService
  private printify?: PrintifyService
  private shopify?: ShopifyService
  private tiktok?: TikTokShopService
  private etsy?: EtsyService
  private instagram?: InstagramService
  private facebook?: FacebookShopService
  private config: OrchestratorConfig
  private logCallback?: (message: string, type: string) => void
  private circuitBreakerManager: CircuitBreakerManager
  private stats = {
    totalRuns: 0,
    successfulRuns: 0,
    failedRuns: 0,
    totalImages: 0,
    totalProducts: 0,
    totalErrors: 0
  }

  constructor(config: OrchestratorConfig) {
    this.config = config
    this.circuitBreakerManager = new CircuitBreakerManager()

    // Initialize core services
    this.comfyui = new ComfyUIService(config.comfyui)
    this.claude = new ClaudePromptingService(config.claude)
    this.storage = new StorageService(config.storage)

    // Initialize platform services
    if (config.printify) {
      this.printify = new PrintifyService(config.printify)
    }
    if (config.shopify) {
      this.shopify = new ShopifyService(config.shopify)
    }
    if (config.tiktok) {
      this.tiktok = new TikTokShopService(config.tiktok)
    }
    if (config.etsy) {
      this.etsy = new EtsyService(config.etsy)
    }
    if (config.instagram) {
      this.instagram = new InstagramService(config.instagram)
    }
    if (config.facebook) {
      this.facebook = new FacebookShopService(config.facebook)
    }

    this.log('✅ Orchestrator initialized', 'SUCCESS')
  }

  /**
   * Set logging callback
   */
  setLogger(callback: (message: string, type: string) => void): void {
    this.logCallback = callback
  }

  /**
   * Log message
   */
  private log(message: string, type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' = 'INFO'): void {
    console.log(`[${type}] ${message}`)
    if (this.logCallback) {
      this.logCallback(message, type)
    }
  }

  /**
   * Run complete pipeline
   */
  async run(request: PipelineRequest): Promise<PipelineResult> {
    const startTime = Date.now()
    this.stats.totalRuns++

    const result: PipelineResult = {
      success: false,
      generatedImages: [],
      products: [],
      errors: [],
      platformErrors: [],
      totalTime: 0
    }

    try {
      this.log('🚀 Starting POD automation pipeline...', 'INFO')

      // Step 1: Generate prompts using Claude
      this.log('📝 Generating creative prompts with Claude...', 'INFO')
      const prompts = await this.generatePrompts(request)
      this.log(`✓ Generated ${prompts.length} creative prompts`, 'SUCCESS')

      // Step 2: Generate images with ComfyUI (can be parallelized)
      this.log('🎨 Generating AI images with ComfyUI...', 'INFO')
      const images = await this.generateImagesParallel(prompts)
      const successfulImages = images.filter(img => img !== null) as string[]

      if (successfulImages.length === 0) {
        throw new Error('Failed to generate any images')
      }

      this.log(`✓ Generated ${successfulImages.length}/${prompts.length} images`, 'SUCCESS')
      this.stats.totalImages += successfulImages.length

      // Step 3: Save images to storage
      this.log('💾 Saving images to storage...', 'INFO')
      const savedImages = await this.saveImages(successfulImages, prompts)
      result.generatedImages = savedImages.map((img, i) => ({
        id: img.id,
        url: img.url,
        prompt: prompts[i]?.prompt || 'Unknown'
      }))
      this.log(`✓ Saved ${savedImages.length} images`, 'SUCCESS')

      // Step 4: Create products on enabled platforms (parallelize per image)
      this.log('📦 Creating products on platforms...', 'INFO')
      const productCreationPromises = savedImages.flatMap((savedImage, index) => {
        const promptData = prompts[index]
        return request.productTypes.map(productType =>
          this.createProductsSafe(
            savedImage,
            promptData,
            productType,
            request.autoPublish ?? this.config.options?.autoPublish ?? true
          )
        )
      })

      const productResults = await Promise.allSettled(productCreationPromises)

      productResults.forEach((productResult, index) => {
        if (productResult.status === 'fulfilled') {
          result.products.push(...productResult.value)
        } else {
          const errorMsg = getErrorMessage(productResult.reason)
          this.log(`⚠️  Product creation failed: ${errorMsg}`, 'WARNING')
          result.errors.push(errorMsg)
          this.stats.totalErrors++
        }
      })

      this.stats.totalProducts += result.products.length

      result.success = result.products.length > 0
      result.totalTime = Date.now() - startTime

      if (result.success) {
        this.stats.successfulRuns++
        this.log(
          `✅ Pipeline complete! Created ${result.products.length} products in ${(result.totalTime / 1000).toFixed(2)}s`,
          'SUCCESS'
        )
      } else {
        this.stats.failedRuns++
        this.log(
          `⚠️  Pipeline completed with errors. No products created. Time: ${(result.totalTime / 1000).toFixed(2)}s`,
          'WARNING'
        )
      }

      return result
    } catch (error) {
      this.stats.failedRuns++
      this.stats.totalErrors++

      const errorMsg = getErrorMessage(error)
      this.log(`❌ Pipeline failed: ${errorMsg}`, 'ERROR')
      console.error('[Orchestrator] Pipeline error:', formatErrorForLogging(error))

      result.errors.push(errorMsg)
      result.totalTime = Date.now() - startTime
      return result
    }
  }

  /**
   * Generate prompts using Claude
   */
  private async generatePrompts(request: PipelineRequest): Promise<PromptData[]> {
    if (request.prompt) {
      // Use provided prompt
      return [{
        prompt: request.prompt,
        title: 'Custom Design',
        tags: ['custom', 'ai-art'],
        description: 'Unique AI-generated design'
      }]
    }

    // Generate prompts with Claude
    return this.claude.generatePrompts({
      theme: request.theme,
      style: request.style,
      niche: request.niche,
      count: request.count || 1,
      productType: request.productTypes[0]
    })
  }

  /**
   * Generate images with ComfyUI (sequential)
   */
  private async generateImages(prompts: PromptData[]): Promise<string[]> {
    const allImages: string[] = []

    for (const promptData of prompts) {
      this.log(`Generating image for: ${promptData.title}`, 'INFO')

      const result = await this.comfyui.generate({
        prompt: promptData.prompt,
        width: 1024,
        height: 1024,
        steps: 20
      })

      if (result.status === 'completed' && result.images.length > 0) {
        allImages.push(...result.images)
      } else {
        throw new Error(`Failed to generate image: ${result.error}`)
      }
    }

    return allImages
  }

  /**
   * Generate images with ComfyUI in parallel (with rate limiting)
   */
  private async generateImagesParallel(prompts: PromptData[]): Promise<(string | null)[]> {
    const maxConcurrent = 3 // Limit concurrent generations to avoid overwhelming ComfyUI

    const generateWithTimeout = async (promptData: PromptData): Promise<string | null> => {
      try {
        this.log(`Generating image for: ${promptData.title}`, 'INFO')

        const result = await this.comfyui.generate({
          prompt: promptData.prompt,
          width: 1024,
          height: 1024,
          steps: 20
        })

        if (result.status === 'completed' && result.images.length > 0) {
          return result.images[0]
        } else {
          this.log(`⚠️  Failed to generate image: ${result.error}`, 'WARNING')
          return null
        }
      } catch (error) {
        this.log(`⚠️  Error generating image: ${getErrorMessage(error)}`, 'WARNING')
        return null
      }
    }

    // Process in batches to avoid overwhelming the system
    const results: (string | null)[] = []
    for (let i = 0; i < prompts.length; i += maxConcurrent) {
      const batch = prompts.slice(i, i + maxConcurrent)
      const batchResults = await Promise.all(batch.map(generateWithTimeout))
      results.push(...batchResults)
    }

    return results
  }

  /**
   * Save images to storage
   */
  private async saveImages(imageUrls: string[], prompts: PromptData[]): Promise<SavedImageData[]> {
    const saved = []

    for (let i = 0; i < imageUrls.length; i++) {
      const imageUrl = imageUrls[i]
      const prompt = prompts[i]

      const savedImage = await this.storage.saveImage(imageUrl, {
        prompt: prompt.prompt,
        title: prompt.title,
        tags: prompt.tags,
        description: prompt.description
      })

      saved.push(savedImage)
    }

    return saved
  }

  /**
   * Create products on all enabled platforms (with error handling)
   */
  private async createProductsSafe(
    image: SavedImageData,
    promptData: PromptData,
    productType: 'tshirt' | 'hoodie',
    autoPublish: boolean
  ): Promise<ProductResult[]> {
    try {
      return await this.createProducts(image, promptData, productType, autoPublish)
    } catch (error) {
      this.log(`Failed to create products: ${getErrorMessage(error)}`, 'ERROR')
      console.error('[Orchestrator] Product creation error:', formatErrorForLogging(error))
      return []
    }
  }

  /**
   * Create products on all enabled platforms
   */
  private async createProducts(
    image: SavedImageData,
    promptData: PromptData,
    productType: 'tshirt' | 'hoodie',
    autoPublish: boolean
  ): Promise<ProductResult[]> {
    const products: ProductResult[] = []
    const enabledPlatforms = this.config.options?.enabledPlatforms || ['printify', 'shopify']

    const price = productType === 'tshirt'
      ? this.config.options?.tshirtPrice || 19.99
      : this.config.options?.hoodiePrice || 34.99

    // Create array of platform creation promises for parallel execution
    const platformPromises: Promise<ProductResult | null>[] = []

    // Printify
    if (enabledPlatforms.includes('printify') && this.printify) {
      platformPromises.push(
        (async () => {
          try {
            const method = productType === 'tshirt' ? 'createTShirt' : 'createHoodie'
            const product = await this.printify![method](
              image.url,
              promptData.title,
              promptData.description,
              { price, tags: promptData.tags }
            )

            if (autoPublish && product.id) {
              await this.printify!.publishProduct(product.id)
            }

            return {
              platform: 'printify',
              productId: product.id,
              url: product.printifyUrl,
              type: productType
            }
          } catch (error) {
            const errorMsg = getErrorMessage(error)
            this.log(`⚠️  Printify error for "${promptData.title}": ${errorMsg}`, 'WARNING')
            this.stats.totalErrors++
            return null
          }
        })()
      )
    }

    // Shopify
    if (enabledPlatforms.includes('shopify') && this.shopify) {
      platformPromises.push(
        (async () => {
          try {
            const product = await this.shopify!.createFromPrintify(
              promptData.title,
              promptData.description,
              image.url,
              price,
              promptData.tags,
              productType === 'tshirt' ? 'T-Shirt' : 'Hoodie'
            )

            return {
              platform: 'shopify',
              productId: product.id,
              url: product.storeUrl,
              type: productType
            }
          } catch (error) {
            const errorMsg = getErrorMessage(error)
            this.log(`⚠️  Shopify error for "${promptData.title}": ${errorMsg}`, 'WARNING')
            this.stats.totalErrors++
            return null
          }
        })()
      )
    }

    // TikTok, Etsy, Instagram, Facebook - similar pattern
    // Note: These platforms can also be parallelized but may need rate limiting
    if (enabledPlatforms.includes('tiktok') && this.tiktok) {
      platformPromises.push(
        (async () => {
          try {
            const productId = await this.tiktok!.createFromPOD(
              promptData.title,
              promptData.description,
              image.url,
              price,
              productType
            )

            if (productId) {
              return {
                platform: 'tiktok',
                productId,
                url: `https://seller.tiktok.com/product/${productId}`,
                type: productType
              }
            }
            return null
          } catch (error) {
            const errorMsg = getErrorMessage(error)
            this.log(`⚠️  TikTok error for "${promptData.title}": ${errorMsg}`, 'WARNING')
            this.stats.totalErrors++
            return null
          }
        })()
      )
    }

    if (enabledPlatforms.includes('etsy') && this.etsy) {
      platformPromises.push(
        (async () => {
          try {
            const listingId = await this.etsy!.createFromPOD(
              promptData.title,
              promptData.description,
              image.url,
              price,
              promptData.tags,
              productType
            )

            if (listingId && autoPublish) {
              await this.etsy!.publishListing(listingId)
            }

            if (listingId) {
              return {
                platform: 'etsy',
                productId: listingId,
                url: `https://www.etsy.com/listing/${listingId}`,
                type: productType
              }
            }
            return null
          } catch (error) {
            const errorMsg = getErrorMessage(error)
            this.log(`⚠️  Etsy error for "${promptData.title}": ${errorMsg}`, 'WARNING')
            this.stats.totalErrors++
            return null
          }
        })()
      )
    }

    if (enabledPlatforms.includes('instagram') && this.instagram) {
      platformPromises.push(
        (async () => {
          try {
            const productId = await this.instagram!.createFromPOD(
              this.config.instagram!.businessAccountId,
              promptData.title,
              promptData.description,
              image.url,
              price,
              `https://yourstore.com/products/${promptData.title.toLowerCase().replace(/\s+/g, '-')}`
            )

            if (productId) {
              return {
                platform: 'instagram',
                productId,
                url: `https://www.instagram.com/`,
                type: productType
              }
            }
            return null
          } catch (error) {
            const errorMsg = getErrorMessage(error)
            this.log(`⚠️  Instagram error for "${promptData.title}": ${errorMsg}`, 'WARNING')
            this.stats.totalErrors++
            return null
          }
        })()
      )
    }

    if (enabledPlatforms.includes('facebook') && this.facebook) {
      platformPromises.push(
        (async () => {
          try {
            const productId = await this.facebook!.createFromPOD(
              promptData.title,
              promptData.description,
              image.url,
              price,
              `https://yourstore.com/products/${promptData.title.toLowerCase().replace(/\s+/g, '-')}`
            )

            if (productId) {
              return {
                platform: 'facebook',
                productId,
                url: `https://www.facebook.com/commerce/products/${productId}`,
                type: productType
              }
            }
            return null
          } catch (error) {
            const errorMsg = getErrorMessage(error)
            this.log(`⚠️  Facebook error for "${promptData.title}": ${errorMsg}`, 'WARNING')
            this.stats.totalErrors++
            return null
          }
        })()
      )
    }

    // Wait for all platform creations to complete
    const results = await Promise.allSettled(platformPromises)

    results.forEach(result => {
      if (result.status === 'fulfilled' && result.value) {
        products.push(result.value)
      }
    })

    return products
  }

  /**
   * Get pipeline statistics and health
   */
  async getStats(): Promise<Record<string, any>> {
    const storageStats = this.storage.getStats()
    const comfyuiHealthy = await this.comfyui.healthCheck()

    return {
      pipeline: {
        totalRuns: this.stats.totalRuns,
        successfulRuns: this.stats.successfulRuns,
        failedRuns: this.stats.failedRuns,
        successRate: this.stats.totalRuns > 0
          ? ((this.stats.successfulRuns / this.stats.totalRuns) * 100).toFixed(2) + '%'
          : '0%',
        totalImages: this.stats.totalImages,
        totalProducts: this.stats.totalProducts,
        totalErrors: this.stats.totalErrors,
        averageProductsPerRun: this.stats.successfulRuns > 0
          ? (this.stats.totalProducts / this.stats.successfulRuns).toFixed(2)
          : '0'
      },
      storage: storageStats,
      services: {
        comfyui: {
          enabled: true,
          healthy: comfyuiHealthy,
          metrics: this.comfyui.getMetrics()
        },
        printify: {
          enabled: !!this.printify,
          metrics: this.printify?.getMetrics()
        },
        shopify: { enabled: !!this.shopify },
        tiktok: { enabled: !!this.tiktok },
        etsy: { enabled: !!this.etsy },
        instagram: { enabled: !!this.instagram },
        facebook: { enabled: !!this.facebook }
      },
      circuitBreakers: this.circuitBreakerManager.getHealthStatus(),
      enabledPlatforms: this.config.options?.enabledPlatforms || ['printify', 'shopify']
    }
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      totalRuns: 0,
      successfulRuns: 0,
      failedRuns: 0,
      totalImages: 0,
      totalProducts: 0,
      totalErrors: 0
    }
    this.circuitBreakerManager.resetAll()
    this.log('📊 Statistics reset', 'INFO')
  }

  /**
   * Get orchestrator health status
   */
  async getHealth(): Promise<{ healthy: boolean; issues: string[] }> {
    const issues: string[] = []

    // Check ComfyUI
    const comfyuiHealthy = await this.comfyui.healthCheck()
    if (!comfyuiHealthy) {
      issues.push('ComfyUI is not responding')
    }

    // Check circuit breakers
    const circuitBreakerHealth = this.circuitBreakerManager.getHealthStatus()
    Object.entries(circuitBreakerHealth).forEach(([service, status]) => {
      if (!status.healthy) {
        issues.push(`${service} circuit breaker is OPEN`)
      }
    })

    // Check enabled platforms
    const enabledPlatforms = this.config.options?.enabledPlatforms || []
    if (enabledPlatforms.length === 0) {
      issues.push('No platforms enabled for product creation')
    }

    return {
      healthy: issues.length === 0,
      issues
    }
  }
}
