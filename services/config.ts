/**
 * Configuration Management System
 * Centralized configuration loading and validation from environment variables
 */

export interface AppConfig {
  // ComfyUI Configuration
  comfyui: {
    apiUrl: string
    outputDir: string
    timeout?: number
  }

  // Claude API Configuration
  claude: {
    apiKey: string
    model?: string
  }

  // Storage Configuration
  storage: {
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

  // Printify Configuration
  printify?: {
    apiKey: string
    shopId: string
  }

  // Shopify Configuration
  shopify?: {
    storeUrl: string
    accessToken: string
    apiVersion?: string
  }

  // TikTok Shop Configuration
  tiktok?: {
    appKey: string
    appSecret: string
    shopId: string
    accessToken: string
  }

  // Etsy Configuration
  etsy?: {
    apiKey: string
    shopId: string
    accessToken: string
  }

  // Instagram Configuration
  instagram?: {
    accessToken: string
    businessAccountId: string
    catalogId?: string
  }

  // Facebook Configuration
  facebook?: {
    pageId: string
    accessToken: string
    catalogId: string
  }

  // Pipeline Options
  options?: {
    enabledPlatforms?: string[]
    autoPublish?: boolean
    tshirtPrice?: number
    hoodiePrice?: number
    batchSize?: number
  }

  // RunPod Configuration
  runpod?: {
    podId?: string
    apiKey?: string
  }

  // Webhook Configuration
  webhook?: {
    url?: string
    onSuccess?: boolean
    onError?: boolean
  }
}

export class ConfigurationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ConfigurationError'
  }
}

export class ConfigManager {
  private static instance: ConfigManager
  private config: AppConfig | null = null

  private constructor() {}

  /**
   * Get singleton instance
   */
  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager()
    }
    return ConfigManager.instance
  }

  /**
   * Load configuration from environment variables
   */
  loadFromEnv(): AppConfig {
    // Check if running in Node.js environment
    const env = typeof process !== 'undefined' ? process.env : {}

    // Core required configurations
    const comfyuiUrl = env.COMFYUI_API_URL || env.VITE_COMFYUI_API_URL
    const claudeKey = env.ANTHROPIC_API_KEY || env.VITE_ANTHROPIC_API_KEY

    if (!comfyuiUrl) {
      throw new ConfigurationError('COMFYUI_API_URL is required')
    }

    if (!claudeKey) {
      throw new ConfigurationError('ANTHROPIC_API_KEY is required')
    }

    // Build configuration
    this.config = {
      comfyui: {
        apiUrl: comfyuiUrl,
        outputDir: env.COMFYUI_OUTPUT_DIR || '/data/comfyui/output',
        timeout: parseInt(env.COMFYUI_TIMEOUT || '300000')
      },

      claude: {
        apiKey: claudeKey,
        model: env.CLAUDE_MODEL || 'claude-3-5-sonnet-20241022'
      },

      storage: this.loadStorageConfig(env),

      // Optional platform configs
      printify: this.loadPrintifyConfig(env),
      shopify: this.loadShopifyConfig(env),
      tiktok: this.loadTikTokConfig(env),
      etsy: this.loadEtsyConfig(env),
      instagram: this.loadInstagramConfig(env),
      facebook: this.loadFacebookConfig(env),

      options: {
        enabledPlatforms: env.ENABLE_PLATFORMS?.split(',').map(p => p.trim()) || ['printify', 'shopify'],
        autoPublish: env.AUTO_PUBLISH === 'true',
        tshirtPrice: parseFloat(env.DEFAULT_TSHIRT_PRICE || '19.99'),
        hoodiePrice: parseFloat(env.DEFAULT_HOODIE_PRICE || '34.99'),
        batchSize: parseInt(env.BATCH_SIZE || '5')
      },

      runpod: env.RUNPOD_API_KEY ? {
        podId: env.RUNPOD_POD_ID,
        apiKey: env.RUNPOD_API_KEY
      } : undefined,

      webhook: env.WEBHOOK_URL ? {
        url: env.WEBHOOK_URL,
        onSuccess: env.WEBHOOK_ON_SUCCESS === 'true',
        onError: env.WEBHOOK_ON_ERROR === 'true'
      } : undefined
    }

    this.validate()
    return this.config
  }

  /**
   * Load storage configuration
   */
  private loadStorageConfig(env: any): AppConfig['storage'] {
    const type = (env.STORAGE_TYPE || 'local') as 'local' | 's3' | 'gcs'
    const basePath = env.STORAGE_PATH || '/data/designs'

    const config: AppConfig['storage'] = {
      type,
      basePath
    }

    if (type === 's3') {
      if (!env.AWS_S3_BUCKET || !env.AWS_ACCESS_KEY_ID || !env.AWS_SECRET_ACCESS_KEY) {
        throw new ConfigurationError('S3 storage requires AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, and AWS_SECRET_ACCESS_KEY')
      }
      config.s3Config = {
        bucket: env.AWS_S3_BUCKET,
        region: env.AWS_REGION || 'us-east-1',
        accessKeyId: env.AWS_ACCESS_KEY_ID,
        secretAccessKey: env.AWS_SECRET_ACCESS_KEY
      }
    }

    if (type === 'gcs') {
      if (!env.GCS_BUCKET || !env.GCS_PROJECT_ID || !env.GCS_KEY_FILENAME) {
        throw new ConfigurationError('GCS storage requires GCS_BUCKET, GCS_PROJECT_ID, and GCS_KEY_FILENAME')
      }
      config.gcsConfig = {
        bucket: env.GCS_BUCKET,
        projectId: env.GCS_PROJECT_ID,
        keyFilename: env.GCS_KEY_FILENAME
      }
    }

    return config
  }

  /**
   * Load Printify configuration
   */
  private loadPrintifyConfig(env: any): AppConfig['printify'] | undefined {
    if (!env.PRINTIFY_API_KEY || !env.PRINTIFY_SHOP_ID) {
      return undefined
    }
    return {
      apiKey: env.PRINTIFY_API_KEY,
      shopId: env.PRINTIFY_SHOP_ID
    }
  }

  /**
   * Load Shopify configuration
   */
  private loadShopifyConfig(env: any): AppConfig['shopify'] | undefined {
    if (!env.SHOPIFY_STORE_URL || !env.SHOPIFY_ACCESS_TOKEN) {
      return undefined
    }
    return {
      storeUrl: env.SHOPIFY_STORE_URL,
      accessToken: env.SHOPIFY_ACCESS_TOKEN,
      apiVersion: env.SHOPIFY_API_VERSION || '2024-01'
    }
  }

  /**
   * Load TikTok Shop configuration
   */
  private loadTikTokConfig(env: any): AppConfig['tiktok'] | undefined {
    if (!env.TIKTOK_APP_KEY || !env.TIKTOK_APP_SECRET || !env.TIKTOK_SHOP_ID || !env.TIKTOK_ACCESS_TOKEN) {
      return undefined
    }
    return {
      appKey: env.TIKTOK_APP_KEY,
      appSecret: env.TIKTOK_APP_SECRET,
      shopId: env.TIKTOK_SHOP_ID,
      accessToken: env.TIKTOK_ACCESS_TOKEN
    }
  }

  /**
   * Load Etsy configuration
   */
  private loadEtsyConfig(env: any): AppConfig['etsy'] | undefined {
    if (!env.ETSY_API_KEY || !env.ETSY_SHOP_ID || !env.ETSY_ACCESS_TOKEN) {
      return undefined
    }
    return {
      apiKey: env.ETSY_API_KEY,
      shopId: env.ETSY_SHOP_ID,
      accessToken: env.ETSY_ACCESS_TOKEN
    }
  }

  /**
   * Load Instagram configuration
   */
  private loadInstagramConfig(env: any): AppConfig['instagram'] | undefined {
    if (!env.INSTAGRAM_ACCESS_TOKEN || !env.INSTAGRAM_BUSINESS_ACCOUNT_ID) {
      return undefined
    }
    return {
      accessToken: env.INSTAGRAM_ACCESS_TOKEN,
      businessAccountId: env.INSTAGRAM_BUSINESS_ACCOUNT_ID,
      catalogId: env.INSTAGRAM_CATALOG_ID
    }
  }

  /**
   * Load Facebook configuration
   */
  private loadFacebookConfig(env: any): AppConfig['facebook'] | undefined {
    if (!env.FACEBOOK_PAGE_ID || !env.FACEBOOK_ACCESS_TOKEN || !env.FACEBOOK_CATALOG_ID) {
      return undefined
    }
    return {
      pageId: env.FACEBOOK_PAGE_ID,
      accessToken: env.FACEBOOK_ACCESS_TOKEN,
      catalogId: env.FACEBOOK_CATALOG_ID
    }
  }

  /**
   * Validate configuration
   */
  private validate(): void {
    if (!this.config) {
      throw new ConfigurationError('Configuration not loaded')
    }

    // Validate enabled platforms have their configs
    const enabledPlatforms = this.config.options?.enabledPlatforms || []

    for (const platform of enabledPlatforms) {
      switch (platform) {
        case 'printify':
          if (!this.config.printify) {
            throw new ConfigurationError('Printify is enabled but configuration is missing')
          }
          break
        case 'shopify':
          if (!this.config.shopify) {
            throw new ConfigurationError('Shopify is enabled but configuration is missing')
          }
          break
        case 'tiktok':
          if (!this.config.tiktok) {
            throw new ConfigurationError('TikTok is enabled but configuration is missing')
          }
          break
        case 'etsy':
          if (!this.config.etsy) {
            throw new ConfigurationError('Etsy is enabled but configuration is missing')
          }
          break
        case 'instagram':
          if (!this.config.instagram) {
            throw new ConfigurationError('Instagram is enabled but configuration is missing')
          }
          break
        case 'facebook':
          if (!this.config.facebook) {
            throw new ConfigurationError('Facebook is enabled but configuration is missing')
          }
          break
      }
    }

    // Validate API URLs
    if (!this.isValidUrl(this.config.comfyui.apiUrl)) {
      throw new ConfigurationError('Invalid ComfyUI API URL')
    }

    // Validate prices
    if (this.config.options) {
      if (this.config.options.tshirtPrice && this.config.options.tshirtPrice <= 0) {
        throw new ConfigurationError('T-shirt price must be positive')
      }
      if (this.config.options.hoodiePrice && this.config.options.hoodiePrice <= 0) {
        throw new ConfigurationError('Hoodie price must be positive')
      }
    }
  }

  /**
   * Check if string is valid URL
   */
  private isValidUrl(url: string): boolean {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): AppConfig {
    if (!this.config) {
      throw new ConfigurationError('Configuration not loaded. Call loadFromEnv() first.')
    }
    return this.config
  }

  /**
   * Get configuration for specific platform
   */
  getPlatformConfig<T extends keyof AppConfig>(platform: T): AppConfig[T] {
    const config = this.getConfig()
    return config[platform]
  }

  /**
   * Check if platform is enabled
   */
  isPlatformEnabled(platform: string): boolean {
    const config = this.getConfig()
    return config.options?.enabledPlatforms?.includes(platform) || false
  }

  /**
   * Get enabled platforms
   */
  getEnabledPlatforms(): string[] {
    const config = this.getConfig()
    return config.options?.enabledPlatforms || []
  }

  /**
   * Print configuration summary (without sensitive data)
   */
  printSummary(): void {
    if (!this.config) {
      console.log('Configuration not loaded')
      return
    }

    console.log('=== POD Pipeline Configuration ===')
    console.log(`ComfyUI URL: ${this.config.comfyui.apiUrl}`)
    console.log(`Claude Model: ${this.config.claude.model}`)
    console.log(`Storage Type: ${this.config.storage.type}`)
    console.log(`Storage Path: ${this.config.storage.basePath}`)
    console.log(`Auto Publish: ${this.config.options?.autoPublish ? 'Yes' : 'No'}`)
    console.log(`T-Shirt Price: $${this.config.options?.tshirtPrice}`)
    console.log(`Hoodie Price: $${this.config.options?.hoodiePrice}`)
    console.log(`Batch Size: ${this.config.options?.batchSize}`)
    console.log('\nEnabled Platforms:')

    const platforms = this.getEnabledPlatforms()
    if (platforms.length === 0) {
      console.log('  None')
    } else {
      platforms.forEach(p => console.log(`  - ${p}`))
    }

    console.log('\nConfigured Services:')
    if (this.config.printify) console.log('  ✓ Printify')
    if (this.config.shopify) console.log('  ✓ Shopify')
    if (this.config.tiktok) console.log('  ✓ TikTok Shop')
    if (this.config.etsy) console.log('  ✓ Etsy')
    if (this.config.instagram) console.log('  ✓ Instagram')
    if (this.config.facebook) console.log('  ✓ Facebook')
    if (this.config.runpod) console.log('  ✓ RunPod')
    if (this.config.webhook) console.log('  ✓ Webhooks')

    console.log('==================================')
  }
}

/**
 * Convenience function to get config manager
 */
export function getConfigManager(): ConfigManager {
  return ConfigManager.getInstance()
}

/**
 * Convenience function to load and get configuration
 */
export function loadConfig(): AppConfig {
  const manager = getConfigManager()
  return manager.loadFromEnv()
}
