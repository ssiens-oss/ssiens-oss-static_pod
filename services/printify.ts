/**
 * Printify Integration Service
 * Creates and publishes POD products (T-shirts, Hoodies) to Printify
 */

import { retryWithBackoff } from '../utils/retry';
import { CircuitBreaker } from '../utils/circuitBreaker';
import { Cache } from '../utils/cache';
import {
  APIError,
  AuthenticationError,
  RateLimitError,
  ServiceError,
  ValidationError
} from '../utils/errors';

interface PrintifyConfig {
  apiKey: string
  shopId: string
  maxRetries?: number
  enableCircuitBreaker?: boolean
  enableCache?: boolean
}

interface Product {
  title: string
  description: string
  blueprintId: number
  providerId: number
  variants: ProductVariant[]
  images: PrintifyImage[]
  tags?: string[]
}

interface PrintifyVariant {
  id: number
  title?: string
  options?: Record<string, string>
  is_available?: boolean
  is_enabled?: boolean
}

interface ProductVariant {
  id: number
  price: number
  isEnabled: boolean
}

interface PrintifyImage {
  src: string  // URL or base64
  position: string  // 'front', 'back', etc.
  x?: number
  y?: number
  scale?: number
  angle?: number
}

interface CreatedProduct {
  id: string
  title: string
  handle: string
  shopId: string
  printifyUrl: string
}

interface PrintifyAPIResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

export class PrintifyService {
  private config: PrintifyConfig
  private baseUrl = 'https://api.printify.com/v1'
  private circuitBreaker?: CircuitBreaker
  private variantCache?: Cache<string, PrintifyVariant[]>
  private readonly maxRetries: number

  constructor(config: PrintifyConfig) {
    this.config = {
      maxRetries: 3,
      enableCircuitBreaker: true,
      enableCache: true,
      ...config
    };

    this.maxRetries = this.config.maxRetries!;

    if (this.config.enableCircuitBreaker) {
      this.circuitBreaker = new CircuitBreaker('Printify', {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 60000,
        onStateChange: (state) => {
          console.log(`[Printify] Circuit breaker state: ${state}`);
        }
      });
    }

    if (this.config.enableCache) {
      this.variantCache = new Cache({
        ttl: 3600000, // 1 hour cache for variants
        maxSize: 100
      });
    }

    // Validate config
    this.validateConfig();
  }

  /**
   * Validate configuration
   */
  private validateConfig(): void {
    if (!this.config.apiKey) {
      throw new ValidationError('Printify API key is required', 'apiKey');
    }
    if (!this.config.shopId) {
      throw new ValidationError('Printify shop ID is required', 'shopId');
    }
  }

  /**
   * Make API request with retry logic
   */
  private async apiRequest<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const operation = async () => {
      const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;

      const response = await fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      // Handle specific error codes
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));

        if (response.status === 401 || response.status === 403) {
          throw new AuthenticationError(
            errorBody.message || 'Authentication failed',
            'Printify'
          );
        }

        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After');
          throw new RateLimitError(
            'Rate limit exceeded',
            'Printify',
            retryAfter ? parseInt(retryAfter) * 1000 : undefined
          );
        }

        throw new APIError(
          errorBody.message || `Request failed: ${response.statusText}`,
          'Printify',
          response.status,
          errorBody
        );
      }

      return response.json();
    };

    // Use circuit breaker if enabled
    if (this.circuitBreaker) {
      return this.circuitBreaker.execute(() =>
        retryWithBackoff(operation, {
          maxRetries: this.maxRetries,
          initialDelay: 1000,
          maxDelay: 30000,
          backoffMultiplier: 2,
          onRetry: (error, attempt) => {
            console.log(`[Printify] Retry attempt ${attempt} after error:`, error.message);
          }
        })
      );
    }

    return retryWithBackoff(operation, {
      maxRetries: this.maxRetries,
      initialDelay: 1000,
      maxDelay: 30000,
      backoffMultiplier: 2
    });
  }

  /**
   * Create a T-shirt product
   */
  async createTShirt(
    imageUrl: string,
    title: string,
    description: string,
    options: {
      price?: number
      tags?: string[]
      colors?: string[]
      sizes?: string[]
    } = {}
  ): Promise<CreatedProduct> {
    const {
      price = 19.99,
      tags = [],
      colors = ['Black', 'White', 'Navy', 'Heather Grey'],
      sizes = ['S', 'M', 'L', 'XL', '2XL', '3XL']
    } = options

    // Blueprint 3: Unisex Heavy Cotton Tee (Gildan 5000)
    // Provider 99: SwiftPOD
    return this.createProduct({
      title,
      description,
      blueprintId: 3,
      providerId: 99,
      variants: await this.buildVariants(3, 99, colors, sizes, price),
      images: [{
        src: imageUrl,
        position: 'front',
        x: 0.5,
        y: 0.5,
        scale: 1,
        angle: 0
      }],
      tags
    })
  }

  /**
   * Create a Hoodie product
   */
  async createHoodie(
    imageUrl: string,
    title: string,
    description: string,
    options: {
      price?: number
      tags?: string[]
      colors?: string[]
      sizes?: string[]
    } = {}
  ): Promise<CreatedProduct> {
    const {
      price = 34.99,
      tags = [],
      colors = ['Black', 'Navy', 'Heather Grey'],
      sizes = ['S', 'M', 'L', 'XL', '2XL']
    } = options

    // Blueprint 165: Unisex Heavy Blend Hoodie (Gildan 18500)
    // Provider 99: SwiftPOD
    return this.createProduct({
      title,
      description,
      blueprintId: 165,
      providerId: 99,
      variants: await this.buildVariants(165, 99, colors, sizes, price),
      images: [{
        src: imageUrl,
        position: 'front',
        x: 0.5,
        y: 0.5,
        scale: 1,
        angle: 0
      }],
      tags
    })
  }

  /**
   * Create both T-shirt and Hoodie with same design
   */
  async createBothProducts(
    imageUrl: string,
    title: string,
    description: string,
    options: {
      tshirtPrice?: number
      hoodiePrice?: number
      tags?: string[]
    } = {}
  ): Promise<CreatedProduct[]> {
    const { tshirtPrice, hoodiePrice, tags } = options

    const [tshirt, hoodie] = await Promise.all([
      this.createTShirt(imageUrl, `${title} - T-Shirt`, description, {
        price: tshirtPrice,
        tags
      }),
      this.createHoodie(imageUrl, `${title} - Hoodie`, description, {
        price: hoodiePrice,
        tags
      })
    ])

    return [tshirt, hoodie]
  }

  /**
   * Create a product in Printify
   */
  private async createProduct(product: Product): Promise<CreatedProduct> {
    try {
      // Upload images in parallel
      const imageIds = await Promise.all(
        product.images.map((image, index) => {
          const filename = `${product.title.replace(/\s+/g, '-').toLowerCase()}-${index + 1}.png`;
          return this.uploadImage(image.src, filename);
        })
      );

      if (imageIds.length === 0) {
        throw new ValidationError('Unable to upload product artwork to Printify');
      }

      const placeholders = product.images.map((image, index) => ({
        position: image.position,
        images: [{
          id: imageIds[index],
          x: image.x ?? 0.5,
          y: image.y ?? 0.5,
          scale: image.scale ?? 1,
          angle: image.angle ?? 0
        }]
      }));

      const variantIds = product.variants.map(variant => variant.id);
      if (variantIds.length === 0) {
        throw new ValidationError('No variants selected for this product');
      }

      const data = await this.apiRequest<any>(
        `/shops/${this.config.shopId}/products.json`,
        {
          method: 'POST',
          body: JSON.stringify({
            title: product.title,
            description: product.description,
            blueprint_id: product.blueprintId,
            print_provider_id: product.providerId,
            variants: product.variants.map(variant => ({
              id: variant.id,
              price: variant.price,
              is_enabled: variant.isEnabled
            })),
            print_areas: [{
              variant_ids: variantIds,
              placeholders
            }],
            tags: product.tags ?? []
          })
        }
      );

      console.log(`[Printify] Created product: ${data.id} - ${data.title}`);

      return {
        id: data.id,
        title: data.title,
        handle: data.handle || data.id,
        shopId: this.config.shopId,
        printifyUrl: `https://printify.com/app/products/${data.id}`
      };
    } catch (error) {
      console.error('[Printify] Error creating product:', error);
      throw error;
    }
  }

  /**
   * Publish product to connected sales channel
   */
  async publishProduct(productId: string): Promise<boolean> {
    try {
      await this.apiRequest(
        `/shops/${this.config.shopId}/products/${productId}/publish.json`,
        {
          method: 'POST',
          body: JSON.stringify({
            title: true,
            description: true,
            images: true,
            variants: true,
            tags: true
          })
        }
      );

      console.log(`[Printify] Published product: ${productId}`);
      return true;
    } catch (error) {
      console.error('[Printify] Error publishing product:', error);
      return false;
    }
  }

  /**
   * Generate product variants (size/color combinations)
   */
  private async buildVariants(
    blueprintId: number,
    providerId: number,
    colors: string[],
    sizes: string[],
    basePrice: number
  ): ProductVariant[] {
    const availableVariants = await this.fetchVariants(blueprintId, providerId)
    const selectedVariantIds = this.filterVariantIds(availableVariants, colors, sizes)

    if (selectedVariantIds.length === 0) {
      console.warn('No variants matched requested colors/sizes; falling back to all available variants.')
      selectedVariantIds.push(
        ...availableVariants
          .filter(variant => variant.is_available !== false && variant.is_enabled !== false)
          .map(variant => variant.id)
      )
    }

    return selectedVariantIds.map(variantId => ({
      id: variantId,
      price: Math.round(basePrice * 100),
      isEnabled: true
    }))
  }

  private async fetchVariants(
    blueprintId: number,
    providerId: number
  ): Promise<PrintifyVariant[]> {
    const cacheKey = `variants-${blueprintId}-${providerId}`;

    // Check cache first
    if (this.variantCache) {
      const cached = this.variantCache.get(cacheKey);
      if (cached) {
        console.log(`[Printify] Using cached variants for blueprint ${blueprintId}, provider ${providerId}`);
        return cached;
      }
    }

    // Fetch from API
    const data = await this.apiRequest<{ variants: PrintifyVariant[] }>(
      `/catalog/blueprints/${blueprintId}/print_providers/${providerId}/variants.json`
    );

    const variants = data.variants || [];

    // Cache the result
    if (this.variantCache && variants.length > 0) {
      this.variantCache.set(cacheKey, variants);
    }

    return variants;
  }

  private filterVariantIds(
    variants: PrintifyVariant[],
    colors: string[],
    sizes: string[]
  ): number[] {
    const normalizedColors = colors.map(color => color.toLowerCase())
    const normalizedSizes = sizes.map(size => size.toLowerCase())

    return variants
      .filter(variant => variant.is_available !== false && variant.is_enabled !== false)
      .filter(variant => {
        const title = (variant.title || '').toLowerCase()
        const optionValues = Object.values(variant.options || {}).map(value => value.toLowerCase())

        const matchesColor = normalizedColors.length === 0
          || normalizedColors.some(color => title.includes(color) || optionValues.includes(color))
        const matchesSize = normalizedSizes.length === 0
          || normalizedSizes.some(size => title.includes(size) || optionValues.includes(size))

        return matchesColor && matchesSize
      })
      .map(variant => variant.id)
  }

  /**
   * Upload image to Printify
   */
  async uploadImage(imageUrl: string, filename: string): Promise<string> {
    try {
      const data = await this.apiRequest<{ id: string }>(
        '/uploads/images.json',
        {
          method: 'POST',
          body: JSON.stringify({
            file_name: filename,
            url: imageUrl
          })
        }
      );

      console.log(`[Printify] Uploaded image: ${filename} -> ${data.id}`);
      return data.id;
    } catch (error) {
      console.error('[Printify] Error uploading image:', error);
      throw error;
    }
  }

  /**
   * Get product details
   */
  async getProduct(productId: string): Promise<any> {
    return this.apiRequest(
      `/shops/${this.config.shopId}/products/${productId}.json`
    );
  }

  /**
   * List all products
   */
  async listProducts(page: number = 1, limit: number = 10): Promise<any[]> {
    try {
      const data = await this.apiRequest<PrintifyAPIResponse>(
        `/shops/${this.config.shopId}/products.json?page=${page}&limit=${limit}`
      );
      return data.data || [];
    } catch (error) {
      console.error('[Printify] Error listing products:', error);
      return [];
    }
  }

  /**
   * Delete a product
   */
  async deleteProduct(productId: string): Promise<boolean> {
    try {
      await this.apiRequest(
        `/shops/${this.config.shopId}/products/${productId}.json`,
        { method: 'DELETE' }
      );
      console.log(`[Printify] Deleted product: ${productId}`);
      return true;
    } catch (error) {
      console.error('[Printify] Error deleting product:', error);
      return false;
    }
  }

  /**
   * Get available blueprints (product types)
   */
  async getBlueprints(): Promise<any[]> {
    try {
      return await this.apiRequest('/catalog/blueprints.json');
    } catch (error) {
      console.error('[Printify] Error getting blueprints:', error);
      return [];
    }
  }

  /**
   * Get providers for a blueprint
   */
  async getProviders(blueprintId: number): Promise<any[]> {
    try {
      return await this.apiRequest(
        `/catalog/blueprints/${blueprintId}/print_providers.json`
      );
    } catch (error) {
      console.error('[Printify] Error getting providers:', error);
      return [];
    }
  }

  /**
   * Get metrics and statistics
   */
  getMetrics() {
    return {
      circuitBreaker: this.circuitBreaker?.getMetrics(),
      cache: this.variantCache?.getStats(),
      config: {
        maxRetries: this.maxRetries,
        circuitBreakerEnabled: !!this.circuitBreaker,
        cacheEnabled: !!this.variantCache
      }
    };
  }

  /**
   * Clear variant cache
   */
  clearCache(): void {
    if (this.variantCache) {
      this.variantCache.clear();
      console.log('[Printify] Cache cleared');
    }
  }
}
