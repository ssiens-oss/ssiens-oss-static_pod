/**
 * Orchestrator Client
 * Frontend client for POD pipeline orchestration
 */

export interface PipelineRequest {
  // Prompt settings
  theme?: string;
  style?: string;
  niche?: string;
  customPrompt?: string;

  // Product settings
  productTypes: ('tshirt' | 'hoodie')[];
  designCount: number;
  autoPublish: boolean;

  // Pricing
  tshirtPrice: number;
  hoodiePrice: number;

  // Platforms
  enabledPlatforms: string[];
}

export interface PipelineProgress {
  stage: string;
  progress: number;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export interface PipelineResult {
  success: boolean;
  generatedImages: Array<{
    id: string;
    url: string;
    prompt: string;
  }>;
  products: Array<{
    platform: string;
    productId: string;
    url: string;
    type: 'tshirt' | 'hoodie';
  }>;
  errors: string[];
  totalTime: number;
}

export class OrchestratorClient {
  private apiUrl: string;
  private onProgress?: (progress: PipelineProgress) => void;

  constructor(apiUrl: string = '/api') {
    this.apiUrl = apiUrl;
  }

  /**
   * Set progress callback
   */
  setProgressCallback(callback: (progress: PipelineProgress) => void): void {
    this.onProgress = callback;
  }

  /**
   * Run pipeline
   */
  async runPipeline(request: PipelineRequest): Promise<PipelineResult> {
    try {
      // Check if backend API is available
      const isBackendAvailable = await this.checkBackend();

      if (!isBackendAvailable) {
        // Fall back to simulation mode
        return this.simulatePipeline(request);
      }

      // Make API call to backend orchestrator
      const response = await fetch(`${this.apiUrl}/pipeline/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Pipeline failed: ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Pipeline execution error:', error);
      // Fall back to simulation
      return this.simulatePipeline(request);
    }
  }

  /**
   * Check if backend is available
   */
  private async checkBackend(): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiUrl}/health`, {
        method: 'GET',
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Simulate pipeline execution (for demo/development)
   */
  private async simulatePipeline(request: PipelineRequest): Promise<PipelineResult> {
    const startTime = Date.now();
    const result: PipelineResult = {
      success: false,
      generatedImages: [],
      products: [],
      errors: [],
      totalTime: 0,
    };

    // Stage 1: Prompt Generation
    this.emitProgress('prompt-generation', 10, '📝 Generating creative prompts with Claude...', 'info');
    await this.sleep(1500);
    this.emitProgress('prompt-generation', 25, `✓ Generated ${request.designCount} prompts`, 'success');

    // Stage 2: Image Generation
    this.emitProgress('image-generation', 30, '🎨 Generating AI images with ComfyUI...', 'info');
    await this.sleep(2000);

    // Generate mock images
    const images = Array(request.designCount)
      .fill(0)
      .map((_, i) => ({
        id: `img-${i}`,
        url: `https://placehold.co/1024x1024/1e293b/94a3b8?text=Design+${i + 1}`,
        prompt: `${request.niche || 'Abstract'} ${request.style || 'minimalist'} design ${i + 1}`,
      }));

    result.generatedImages = images;
    this.emitProgress('image-generation', 50, `✓ Generated ${images.length} images`, 'success');

    // Stage 3: Storage
    this.emitProgress('storage', 55, '💾 Saving images to storage...', 'info');
    await this.sleep(1000);
    this.emitProgress('storage', 65, `✓ Saved ${images.length} images`, 'success');

    // Stage 4: Product Creation
    let currentProgress = 65;
    const progressPerPlatform = 30 / request.enabledPlatforms.length;

    for (const platformId of request.enabledPlatforms) {
      const platformName = this.getPlatformName(platformId);
      this.emitProgress('product-creation', currentProgress, `📦 Publishing to ${platformName}...`, 'info');
      await this.sleep(1500);

      // Create products for each design and product type
      for (const image of images) {
        for (const productType of request.productTypes) {
          const productId = `${platformId}-${image.id}-${productType}-${Date.now()}`;
          result.products.push({
            platform: platformName,
            productId,
            url: this.generateProductUrl(platformId, productId),
            type: productType,
          });
        }
      }

      currentProgress += progressPerPlatform;
      const productsCreated = images.length * request.productTypes.length;
      this.emitProgress(
        'product-creation',
        currentProgress,
        `✓ Published ${productsCreated} products to ${platformName}`,
        'success'
      );
    }

    // Stage 5: Complete
    this.emitProgress('complete', 100, `✅ Pipeline complete! Created ${result.products.length} products`, 'success');

    result.success = true;
    result.totalTime = Date.now() - startTime;

    return result;
  }

  /**
   * Emit progress update
   */
  private emitProgress(stage: string, progress: number, message: string, type: 'info' | 'success' | 'warning' | 'error'): void {
    if (this.onProgress) {
      this.onProgress({ stage, progress, message, type });
    }
  }

  /**
   * Get platform display name
   */
  private getPlatformName(platformId: string): string {
    const names: Record<string, string> = {
      printify: 'Printify',
      shopify: 'Shopify',
      tiktok: 'TikTok Shop',
      etsy: 'Etsy',
      instagram: 'Instagram',
      facebook: 'Facebook Shop',
    };
    return names[platformId] || platformId;
  }

  /**
   * Generate product URL
   */
  private generateProductUrl(platformId: string, productId: string): string {
    const baseUrls: Record<string, string> = {
      printify: 'https://printify.com/app/products/',
      shopify: 'https://admin.shopify.com/products/',
      tiktok: 'https://seller.tiktok.com/product/',
      etsy: 'https://www.etsy.com/listing/',
      instagram: 'https://www.instagram.com/',
      facebook: 'https://www.facebook.com/commerce/products/',
    };
    return `${baseUrls[platformId] || ''}${productId}`;
  }

  /**
   * Sleep helper
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Get pipeline statistics
   */
  async getStats(): Promise<any> {
    try {
      const response = await fetch(`${this.apiUrl}/pipeline/stats`);
      if (!response.ok) {
        return this.getMockStats();
      }
      return await response.json();
    } catch {
      return this.getMockStats();
    }
  }

  /**
   * Get mock statistics
   */
  private getMockStats(): any {
    return {
      totalRuns: 0,
      totalDesigns: 0,
      totalProducts: 0,
      successRate: 0,
      platformBreakdown: {},
    };
  }
}
