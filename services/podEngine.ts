/**
 * Pod Engine Pipeline
 * Complete automation engine for ComfyUI + RunPod with proofing and publishing
 */

import { ComfyUIService } from './comfyui'
import { ClaudePromptingService } from './claudePrompting'
import { StorageService } from './storage'
import { ProofingService } from './proofing'
import { PrintifyService } from './printify'
import { ShopifyService } from './shopify'
import { TikTokShopService } from './platforms/tiktok'
import { EtsyService } from './platforms/etsy'
import { InstagramService } from './platforms/instagram'
import { FacebookShopService } from './platforms/facebook'

export interface PodEngineConfig {
  // Core Services
  comfyui: {
    apiUrl: string
    outputDir: string
    runpodMode?: boolean
    runpodApiKey?: string
    runpodPodId?: string
  }
  claude: {
    apiKey: string
  }
  storage: {
    type: 'local' | 's3' | 'gcs' | 'runpod'
    basePath: string
    runpodSyncEnabled?: boolean
  }

  // Proofing
  proofing?: {
    enabled: boolean
    autoApprove?: boolean
    requireManualReview?: boolean
  }

  // Publishing Platforms
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

  // Options
  options?: {
    enabledPlatforms?: string[]
    autoPublish?: boolean
    tshirtPrice?: number
    hoodiePrice?: number
    batchSize?: number
  }
}

export interface PodPipelineRequest {
  // Generation
  prompt?: string
  theme?: string
  style?: string
  niche?: string

  // Products
  productTypes: ('tshirt' | 'hoodie' | 'mug' | 'poster')[]
  count?: number

  // Workflow
  autoProof?: boolean
  autoPublish?: boolean

  // Advanced
  comfyWorkflow?: string
  customParams?: Record<string, any>
}

export interface GeneratedAsset {
  id: string
  url: string
  localPath?: string
  prompt: string
  metadata: {
    title: string
    description: string
    tags: string[]
    timestamp: string
  }
  proofStatus: 'pending' | 'approved' | 'rejected'
  proofNotes?: string
}

export interface PublishedProduct {
  platform: string
  productId: string
  url: string
  type: string
  status: 'created' | 'published' | 'failed'
  assetId: string
}

export interface PipelineStatus {
  stage: 'idle' | 'generating' | 'proofing' | 'publishing' | 'completed' | 'failed'
  progress: number
  currentItem?: string
  assetsGenerated: number
  assetsApproved: number
  productsPublished: number
  errors: string[]
}

export class PodEngine {
  private comfyui: ComfyUIService
  private claude: ClaudePromptingService
  private storage: StorageService
  private proofing?: ProofingService
  private printify?: PrintifyService
  private shopify?: ShopifyService
  private tiktok?: TikTokShopService
  private etsy?: EtsyService
  private instagram?: InstagramService
  private facebook?: FacebookShopService

  private config: PodEngineConfig
  private logCallback?: (message: string, type: string) => void
  private statusCallback?: (status: PipelineStatus) => void

  private currentStatus: PipelineStatus = {
    stage: 'idle',
    progress: 0,
    assetsGenerated: 0,
    assetsApproved: 0,
    productsPublished: 0,
    errors: []
  }

  private generatedAssets: GeneratedAsset[] = []
  private publishedProducts: PublishedProduct[] = []

  constructor(config: PodEngineConfig) {
    this.config = config

    // Initialize core services
    this.comfyui = new ComfyUIService(config.comfyui)
    this.claude = new ClaudePromptingService(config.claude)
    this.storage = new StorageService(config.storage)

    // Initialize proofing if enabled
    if (config.proofing?.enabled) {
      this.proofing = new ProofingService({
        autoApprove: config.proofing.autoApprove || false,
        requireManualReview: config.proofing.requireManualReview || false
      })
    }

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
  }

  /**
   * Set logging callback
   */
  setLogger(callback: (message: string, type: string) => void): void {
    this.logCallback = callback
  }

  /**
   * Set status update callback
   */
  setStatusCallback(callback: (status: PipelineStatus) => void): void {
    this.statusCallback = callback
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
   * Update pipeline status
   */
  private updateStatus(updates: Partial<PipelineStatus>): void {
    this.currentStatus = { ...this.currentStatus, ...updates }
    if (this.statusCallback) {
      this.statusCallback(this.currentStatus)
    }
  }

  /**
   * Run complete pod engine pipeline
   */
  async run(request: PodPipelineRequest): Promise<{
    success: boolean
    assets: GeneratedAsset[]
    products: PublishedProduct[]
    status: PipelineStatus
  }> {
    const startTime = Date.now()

    try {
      this.log('🚀 Starting Pod Engine Pipeline...', 'INFO')
      this.updateStatus({
        stage: 'generating',
        progress: 0,
        assetsGenerated: 0,
        assetsApproved: 0,
        productsPublished: 0,
        errors: []
      })

      // STAGE 1: Generate prompts
      this.log('📝 Generating creative prompts...', 'INFO')
      const prompts = await this.generatePrompts(request)
      this.log(`✓ Generated ${prompts.length} prompts`, 'SUCCESS')

      // STAGE 2: Generate images with ComfyUI
      this.updateStatus({ stage: 'generating', progress: 20, currentItem: 'Generating images' })
      this.log('🎨 Generating images with ComfyUI...', 'INFO')
      const assets = await this.generateAssets(prompts, request)
      this.generatedAssets = assets
      this.updateStatus({ assetsGenerated: assets.length, progress: 40 })
      this.log(`✓ Generated ${assets.length} assets`, 'SUCCESS')

      // STAGE 3: Save to local/RunPod storage
      this.log('💾 Saving to storage...', 'INFO')
      await this.saveAssets(assets)
      this.log(`✓ Saved ${assets.length} assets`, 'SUCCESS')

      // STAGE 4: Proofing
      if (this.proofing && this.config.proofing?.enabled) {
        this.updateStatus({ stage: 'proofing', progress: 50, currentItem: 'Proofing assets' })
        this.log('🔍 Proofing assets...', 'INFO')
        const approvedAssets = await this.proofAssets(assets, request.autoProof || false)
        this.updateStatus({ assetsApproved: approvedAssets.length, progress: 70 })
        this.log(`✓ Approved ${approvedAssets.length}/${assets.length} assets`, 'SUCCESS')

        // Filter to only approved
        assets.splice(0, assets.length, ...approvedAssets)
      } else {
        // Auto-approve all if proofing disabled
        assets.forEach(asset => asset.proofStatus = 'approved')
        this.updateStatus({ assetsApproved: assets.length })
      }

      // STAGE 5: Publishing
      if (assets.length > 0) {
        this.updateStatus({ stage: 'publishing', progress: 75, currentItem: 'Publishing products' })
        this.log('📦 Publishing products...', 'INFO')
        const products = await this.publishProducts(
          assets,
          request.productTypes,
          request.autoPublish ?? this.config.options?.autoPublish ?? true
        )
        this.publishedProducts = products
        this.updateStatus({ productsPublished: products.length, progress: 95 })
        this.log(`✓ Published ${products.length} products`, 'SUCCESS')
      }

      // COMPLETE
      const totalTime = Date.now() - startTime
      this.updateStatus({
        stage: 'completed',
        progress: 100,
        currentItem: undefined
      })
      this.log(
        `✅ Pipeline complete! Generated ${assets.length} assets, published ${this.publishedProducts.length} products in ${(totalTime / 1000).toFixed(2)}s`,
        'SUCCESS'
      )

      return {
        success: true,
        assets: this.generatedAssets,
        products: this.publishedProducts,
        status: this.currentStatus
      }

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      this.log(`❌ Pipeline failed: ${errorMsg}`, 'ERROR')
      this.updateStatus({
        stage: 'failed',
        errors: [...this.currentStatus.errors, errorMsg]
      })

      return {
        success: false,
        assets: this.generatedAssets,
        products: this.publishedProducts,
        status: this.currentStatus
      }
    }
  }

  /**
   * Generate prompts using Claude
   */
  private async generatePrompts(request: PodPipelineRequest): Promise<any[]> {
    if (request.prompt) {
      return [{
        prompt: request.prompt,
        title: 'Custom Design',
        tags: ['custom', 'ai-art'],
        description: 'Unique AI-generated design'
      }]
    }

    return this.claude.generatePrompts({
      theme: request.theme,
      style: request.style,
      niche: request.niche,
      count: request.count || 1,
      productType: request.productTypes[0]
    })
  }

  /**
   * Generate assets with ComfyUI
   */
  private async generateAssets(
    prompts: any[],
    request: PodPipelineRequest
  ): Promise<GeneratedAsset[]> {
    const assets: GeneratedAsset[] = []

    for (let i = 0; i < prompts.length; i++) {
      const promptData = prompts[i]
      this.updateStatus({
        currentItem: `Generating: ${promptData.title}`,
        progress: 20 + (i / prompts.length) * 20
      })

      this.log(`Generating image ${i + 1}/${prompts.length}: ${promptData.title}`, 'INFO')

      const result = await this.comfyui.generate({
        prompt: promptData.prompt,
        width: 1024,
        height: 1024,
        steps: 20,
        ...request.customParams
      })

      if (result.status === 'completed' && result.images.length > 0) {
        for (const imageUrl of result.images) {
          assets.push({
            id: `asset-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            url: imageUrl,
            prompt: promptData.prompt,
            metadata: {
              title: promptData.title,
              description: promptData.description,
              tags: promptData.tags,
              timestamp: new Date().toISOString()
            },
            proofStatus: 'pending'
          })
        }
      } else {
        throw new Error(`Failed to generate image: ${result.error}`)
      }
    }

    return assets
  }

  /**
   * Save assets to storage (with RunPod sync support)
   */
  private async saveAssets(assets: GeneratedAsset[]): Promise<void> {
    for (const asset of assets) {
      const saved = await this.storage.saveImage(asset.url, {
        prompt: asset.prompt,
        title: asset.metadata.title,
        tags: asset.metadata.tags,
        description: asset.metadata.description
      })

      asset.localPath = saved.localPath
      asset.url = saved.url
    }
  }

  /**
   * Proof assets (manual or auto)
   */
  private async proofAssets(
    assets: GeneratedAsset[],
    autoApprove: boolean
  ): Promise<GeneratedAsset[]> {
    if (!this.proofing) {
      return assets
    }

    const approvedAssets: GeneratedAsset[] = []

    for (const asset of assets) {
      if (autoApprove || this.config.proofing?.autoApprove) {
        asset.proofStatus = 'approved'
        approvedAssets.push(asset)
        this.log(`Auto-approved: ${asset.metadata.title}`, 'SUCCESS')
      } else {
        // Add to proofing queue (manual review required)
        const proofResult = await this.proofing.submitForReview(asset)
        if (proofResult.approved) {
          asset.proofStatus = 'approved'
          approvedAssets.push(asset)
          this.log(`Approved: ${asset.metadata.title}`, 'SUCCESS')
        } else {
          asset.proofStatus = 'rejected'
          asset.proofNotes = proofResult.notes
          this.log(`Rejected: ${asset.metadata.title} - ${proofResult.notes}`, 'WARNING')
        }
      }
    }

    return approvedAssets
  }

  /**
   * Publish products to all enabled platforms
   */
  private async publishProducts(
    assets: GeneratedAsset[],
    productTypes: string[],
    autoPublish: boolean
  ): Promise<PublishedProduct[]> {
    const products: PublishedProduct[] = []
    const enabledPlatforms = this.config.options?.enabledPlatforms || ['printify', 'shopify']

    for (const asset of assets) {
      for (const productType of productTypes) {
        this.log(`Creating ${productType} for: ${asset.metadata.title}`, 'INFO')

        const price = this.getPrice(productType)

        // Printify
        if (enabledPlatforms.includes('printify') && this.printify) {
          try {
            const product = await this.createPrintifyProduct(asset, productType, price, autoPublish)
            products.push(product)
          } catch (error) {
            this.log(`Printify error: ${error}`, 'WARNING')
          }
        }

        // Shopify
        if (enabledPlatforms.includes('shopify') && this.shopify) {
          try {
            const product = await this.createShopifyProduct(asset, productType, price)
            products.push(product)
          } catch (error) {
            this.log(`Shopify error: ${error}`, 'WARNING')
          }
        }

        // TikTok
        if (enabledPlatforms.includes('tiktok') && this.tiktok) {
          try {
            const product = await this.createTikTokProduct(asset, productType, price)
            products.push(product)
          } catch (error) {
            this.log(`TikTok error: ${error}`, 'WARNING')
          }
        }

        // Etsy
        if (enabledPlatforms.includes('etsy') && this.etsy) {
          try {
            const product = await this.createEtsyProduct(asset, productType, price, autoPublish)
            products.push(product)
          } catch (error) {
            this.log(`Etsy error: ${error}`, 'WARNING')
          }
        }
      }
    }

    return products
  }

  /**
   * Helper: Get price for product type
   */
  private getPrice(productType: string): number {
    const prices: Record<string, number> = {
      tshirt: this.config.options?.tshirtPrice || 19.99,
      hoodie: this.config.options?.hoodiePrice || 34.99,
      mug: 12.99,
      poster: 15.99
    }
    return prices[productType] || 19.99
  }

  /**
   * Create Printify product
   */
  private async createPrintifyProduct(
    asset: GeneratedAsset,
    productType: string,
    price: number,
    autoPublish: boolean
  ): Promise<PublishedProduct> {
    const method = productType === 'tshirt' ? 'createTShirt' : 'createHoodie'
    const product = await this.printify![method](
      asset.url,
      asset.metadata.title,
      asset.metadata.description,
      { price, tags: asset.metadata.tags }
    )

    if (autoPublish && product.id) {
      await this.printify!.publishProduct(product.id)
    }

    return {
      platform: 'printify',
      productId: product.id,
      url: product.printifyUrl,
      type: productType,
      status: autoPublish ? 'published' : 'created',
      assetId: asset.id
    }
  }

  /**
   * Create Shopify product
   */
  private async createShopifyProduct(
    asset: GeneratedAsset,
    productType: string,
    price: number
  ): Promise<PublishedProduct> {
    const product = await this.shopify!.createFromPrintify(
      asset.metadata.title,
      asset.metadata.description,
      asset.url,
      price,
      asset.metadata.tags,
      productType === 'tshirt' ? 'T-Shirt' : 'Hoodie'
    )

    return {
      platform: 'shopify',
      productId: product.id,
      url: product.storeUrl,
      type: productType,
      status: 'published',
      assetId: asset.id
    }
  }

  /**
   * Create TikTok product
   */
  private async createTikTokProduct(
    asset: GeneratedAsset,
    productType: string,
    price: number
  ): Promise<PublishedProduct> {
    const productId = await this.tiktok!.createFromPOD(
      asset.metadata.title,
      asset.metadata.description,
      asset.url,
      price,
      productType
    )

    return {
      platform: 'tiktok',
      productId,
      url: `https://seller.tiktok.com/product/${productId}`,
      type: productType,
      status: 'published',
      assetId: asset.id
    }
  }

  /**
   * Create Etsy product
   */
  private async createEtsyProduct(
    asset: GeneratedAsset,
    productType: string,
    price: number,
    autoPublish: boolean
  ): Promise<PublishedProduct> {
    const listingId = await this.etsy!.createFromPOD(
      asset.metadata.title,
      asset.metadata.description,
      asset.url,
      price,
      asset.metadata.tags,
      productType
    )

    if (autoPublish && listingId) {
      await this.etsy!.publishListing(listingId)
    }

    return {
      platform: 'etsy',
      productId: listingId,
      url: `https://www.etsy.com/listing/${listingId}`,
      type: productType,
      status: autoPublish ? 'published' : 'created',
      assetId: asset.id
    }
  }

  /**
   * Get current pipeline status
   */
  getStatus(): PipelineStatus {
    return this.currentStatus
  }

  /**
   * Get all generated assets
   */
  getAssets(): GeneratedAsset[] {
    return this.generatedAssets
  }

  /**
   * Get all published products
   */
  getProducts(): PublishedProduct[] {
    return this.publishedProducts
  }

  /**
   * Manually approve/reject an asset
   */
  async updateAssetProof(
    assetId: string,
    status: 'approved' | 'rejected',
    notes?: string
  ): Promise<void> {
    const asset = this.generatedAssets.find(a => a.id === assetId)
    if (asset) {
      asset.proofStatus = status
      asset.proofNotes = notes
      this.log(`Asset ${assetId} ${status}`, 'INFO')
    }
  }
}
