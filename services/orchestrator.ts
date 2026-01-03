/**
 * Pipeline Orchestrator
 * Coordinates the entire POD automation workflow
 */

import { ComfyUIService } from './comfyui'
import { ClaudePromptingService } from './claudePrompting'
import { StorageService } from './storage'
import { PrintifyService } from './printify'
import { ShopifyService } from './shopify'
import { TikTokShopService } from './platforms/tiktok'
import { EtsyService } from './platforms/etsy'
import { InstagramService } from './platforms/instagram'
import { FacebookShopService } from './platforms/facebook'
import { MockupService } from './mockupService'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

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
    enableBackgroundRemoval?: boolean
    enableMockups?: boolean
  }
  mockup?: {
    templatesDir: string
    outputDir: string
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
    transparentUrl?: string
    mockups?: {
      tshirt?: string
      hoodie?: string
    }
    prompt: string
  }>
  products: Array<{
    platform: string
    productId: string
    url: string
    type: 'tshirt' | 'hoodie'
  }>
  errors: string[]
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
  private mockup?: MockupService
  private config: OrchestratorConfig
  private logCallback?: (message: string, type: string) => void

  constructor(config: OrchestratorConfig) {
    this.config = config

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
    if (config.mockup) {
      this.mockup = new MockupService(config.mockup)
    }
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
    const result: PipelineResult = {
      success: false,
      generatedImages: [],
      products: [],
      errors: [],
      totalTime: 0
    }

    try {
      this.log('🚀 Starting POD automation pipeline...', 'INFO')

      // Step 1: Generate prompts using Claude
      this.log('📝 Generating creative prompts with Claude...', 'INFO')
      const prompts = await this.generatePrompts(request)
      this.log(`✓ Generated ${prompts.length} creative prompts`, 'SUCCESS')

      // Step 2: Generate images with ComfyUI
      this.log('🎨 Generating AI images with ComfyUI...', 'INFO')
      const images = await this.generateImages(prompts)
      this.log(`✓ Generated ${images.length} images`, 'SUCCESS')

      // Step 3: Save images to storage
      this.log('💾 Saving images to storage...', 'INFO')
      const savedImages = await this.saveImages(images, prompts)
      this.log(`✓ Saved ${savedImages.length} images`, 'SUCCESS')

      // Step 4: Process images (background removal + mockups)
      const processedImages = await this.processImages(savedImages, prompts, request.productTypes)
      result.generatedImages = processedImages
      this.log(`✓ Processed ${processedImages.length} images`, 'SUCCESS')

      // Step 5: Create products on enabled platforms
      for (let i = 0; i < processedImages.length; i++) {
        const processedImage = processedImages[i]
        const savedImage = savedImages[i]
        const promptData = prompts[i]

        for (const productType of request.productTypes) {
          this.log(`📦 Creating ${productType} products for: ${promptData.title}`, 'INFO')

          try {
            // Use transparent image if available, otherwise use original
            const imageToPublish = {
              ...savedImage,
              url: processedImage.transparentUrl || savedImage.url
            }

            const products = await this.createProducts(
              imageToPublish,
              promptData,
              productType,
              request.autoPublish ?? this.config.options?.autoPublish ?? true
            )
            result.products.push(...products)
            this.log(`✓ Created ${products.length} products`, 'SUCCESS')
          } catch (error) {
            const errorMsg = `Failed to create ${productType}: ${error}`
            this.log(errorMsg, 'ERROR')
            result.errors.push(errorMsg)
          }
        }
      }

      result.success = result.products.length > 0
      result.totalTime = Date.now() - startTime

      this.log(
        `✅ Pipeline complete! Created ${result.products.length} products in ${(result.totalTime / 1000).toFixed(2)}s`,
        'SUCCESS'
      )

      return result
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      this.log(`❌ Pipeline failed: ${errorMsg}`, 'ERROR')
      result.errors.push(errorMsg)
      result.totalTime = Date.now() - startTime
      return result
    }
  }

  /**
   * Generate prompts using Claude
   */
  private async generatePrompts(request: PipelineRequest): Promise<any[]> {
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
   * Generate images with ComfyUI
   */
  private async generateImages(prompts: any[]): Promise<string[]> {
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
   * Save images to storage
   */
  private async saveImages(imageUrls: string[], prompts: any[]): Promise<any[]> {
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
   * Process images: background removal + mockup generation
   */
  private async processImages(
    savedImages: any[],
    prompts: any[],
    productTypes: ('tshirt' | 'hoodie')[]
  ): Promise<any[]> {
    const processed = []

    for (let i = 0; i < savedImages.length; i++) {
      const savedImage = savedImages[i]
      const prompt = prompts[i]

      const result: any = {
        id: savedImage.id,
        url: savedImage.url,
        prompt: prompt.prompt
      }

      // Background removal (if enabled)
      if (this.config.options?.enableBackgroundRemoval !== false) {
        try {
          this.log(`🎨 Removing background for: ${prompt.title}`, 'INFO')
          const transparentPath = savedImage.path.replace('.png', '_transparent.png')

          const { stdout, stderr } = await execAsync(
            `python /workspace/app/services/remove_bg.py "${savedImage.path}" "${transparentPath}"`
          )

          if (stderr && !stderr.includes('WARNING')) {
            this.log(`Background removal stderr: ${stderr}`, 'WARNING')
          }

          // Check if file was created
          const fs = require('fs')
          if (fs.existsSync(transparentPath)) {
            result.transparentUrl = `file://${transparentPath}`
            this.log(`✓ Background removed: ${transparentPath}`, 'SUCCESS')
          }
        } catch (error) {
          this.log(`Background removal failed: ${error}`, 'WARNING')
          // Continue without transparent version
        }
      }

      // Mockup generation (if enabled and mockup service available)
      if (this.config.options?.enableMockups !== false && this.mockup) {
        try {
          this.log(`🖼️  Generating mockups for: ${prompt.title}`, 'INFO')

          // Use transparent version if available, otherwise original
          const designPath = result.transparentUrl
            ? result.transparentUrl.replace('file://', '')
            : savedImage.path

          const mockups = await this.mockup.generateMockups(
            designPath,
            productTypes,
            savedImage.id
          )

          if (Object.keys(mockups).length > 0) {
            result.mockups = mockups
            this.log(`✓ Generated ${Object.keys(mockups).length} mockup(s)`, 'SUCCESS')
          }
        } catch (error) {
          this.log(`Mockup generation failed: ${error}`, 'WARNING')
          // Continue without mockups
        }
      }

      processed.push(result)
    }

    return processed
  }

  /**
   * Create products on all enabled platforms
   */
  private async createProducts(
    image: any,
    promptData: any,
    productType: 'tshirt' | 'hoodie',
    autoPublish: boolean
  ): Promise<Array<{ platform: string; productId: string; url: string; type: 'tshirt' | 'hoodie' }>> {
    const products = []
    const enabledPlatforms = this.config.options?.enabledPlatforms || ['printify', 'shopify']

    const price = productType === 'tshirt'
      ? this.config.options?.tshirtPrice || 19.99
      : this.config.options?.hoodiePrice || 34.99

    // Printify
    if (enabledPlatforms.includes('printify') && this.printify) {
      try {
        const method = productType === 'tshirt' ? 'createTShirt' : 'createHoodie'
        const product = await this.printify[method](
          image.url,
          promptData.title,
          promptData.description,
          { price, tags: promptData.tags }
        )

        if (autoPublish && product.id) {
          await this.printify.publishProduct(product.id)
        }

        products.push({
          platform: 'printify',
          productId: product.id,
          url: product.printifyUrl,
          type: productType
        })
      } catch (error) {
        this.log(`Printify error: ${error}`, 'WARNING')
      }
    }

    // Shopify
    if (enabledPlatforms.includes('shopify') && this.shopify) {
      try {
        const product = await this.shopify.createFromPrintify(
          promptData.title,
          promptData.description,
          image.url,
          price,
          promptData.tags,
          productType === 'tshirt' ? 'T-Shirt' : 'Hoodie'
        )

        products.push({
          platform: 'shopify',
          productId: product.id,
          url: product.storeUrl,
          type: productType
        })
      } catch (error) {
        this.log(`Shopify error: ${error}`, 'WARNING')
      }
    }

    // TikTok Shop
    if (enabledPlatforms.includes('tiktok') && this.tiktok) {
      try {
        const productId = await this.tiktok.createFromPOD(
          promptData.title,
          promptData.description,
          image.url,
          price,
          productType
        )

        if (productId) {
          products.push({
            platform: 'tiktok',
            productId,
            url: `https://seller.tiktok.com/product/${productId}`,
            type: productType
          })
        }
      } catch (error) {
        this.log(`TikTok error: ${error}`, 'WARNING')
      }
    }

    // Etsy
    if (enabledPlatforms.includes('etsy') && this.etsy) {
      try {
        const listingId = await this.etsy.createFromPOD(
          promptData.title,
          promptData.description,
          image.url,
          price,
          promptData.tags,
          productType
        )

        if (listingId && autoPublish) {
          await this.etsy.publishListing(listingId)
        }

        if (listingId) {
          products.push({
            platform: 'etsy',
            productId: listingId,
            url: `https://www.etsy.com/listing/${listingId}`,
            type: productType
          })
        }
      } catch (error) {
        this.log(`Etsy error: ${error}`, 'WARNING')
      }
    }

    // Instagram
    if (enabledPlatforms.includes('instagram') && this.instagram) {
      try {
        const productId = await this.instagram.createFromPOD(
          this.config.instagram!.businessAccountId,
          promptData.title,
          promptData.description,
          image.url,
          price,
          `https://yourstore.com/products/${promptData.title.toLowerCase().replace(/\s+/g, '-')}`
        )

        if (productId) {
          products.push({
            platform: 'instagram',
            productId,
            url: `https://www.instagram.com/`,
            type: productType
          })
        }
      } catch (error) {
        this.log(`Instagram error: ${error}`, 'WARNING')
      }
    }

    // Facebook
    if (enabledPlatforms.includes('facebook') && this.facebook) {
      try {
        const productId = await this.facebook.createFromPOD(
          promptData.title,
          promptData.description,
          image.url,
          price,
          `https://yourstore.com/products/${promptData.title.toLowerCase().replace(/\s+/g, '-')}`
        )

        if (productId) {
          products.push({
            platform: 'facebook',
            productId,
            url: `https://www.facebook.com/commerce/products/${productId}`,
            type: productType
          })
        }
      } catch (error) {
        this.log(`Facebook error: ${error}`, 'WARNING')
      }
    }

    return products
  }

  /**
   * Get pipeline statistics
   */
  async getStats(): Promise<any> {
    const storageStats = this.storage.getStats()

    return {
      storage: storageStats,
      services: {
        comfyui: await this.comfyui.healthCheck(),
        printify: !!this.printify,
        shopify: !!this.shopify,
        tiktok: !!this.tiktok,
        etsy: !!this.etsy,
        instagram: !!this.instagram,
        facebook: !!this.facebook
      }
    }
  }
}
