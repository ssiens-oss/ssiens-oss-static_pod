/**
 * Printify Integration Service
 * Creates and publishes POD products (T-shirts, Hoodies) to Printify
 */

interface PrintifyConfig {
  apiKey: string
  shopId: string
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

export class PrintifyService {
  private config: PrintifyConfig
  private baseUrl = 'https://api.printify.com/v1'

  constructor(config: PrintifyConfig) {
    this.config = config
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
      const imageIds = await Promise.all(
        product.images.map((image, index) => {
          const filename = `${product.title.replace(/\s+/g, '-').toLowerCase()}-${index + 1}.png`
          return this.uploadImage(image.src, filename)
        })
      )
      if (imageIds.length === 0) {
        throw new Error('Unable to upload product artwork to Printify')
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
      }))

      const variantIds = product.variants.map(variant => variant.id)
      if (variantIds.length === 0) {
        throw new Error('No variants selected for this product')
      }

      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
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
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(`Printify API error: ${JSON.stringify(error)}`)
      }

      const data = await response.json()

      return {
        id: data.id,
        title: data.title,
        handle: data.handle || data.id,
        shopId: this.config.shopId,
        printifyUrl: `https://printify.com/app/products/${data.id}`
      }
    } catch (error) {
      console.error('Error creating product in Printify:', error)
      throw error
    }
  }

  /**
   * Publish product to connected sales channel
   */
  async publishProduct(productId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products/${productId}/publish.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: true,
            description: true,
            images: true,
            variants: true,
            tags: true
          })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error publishing product:', error)
      return false
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
    const response = await fetch(
      `${this.baseUrl}/catalog/blueprints/${blueprintId}/print_providers/${providerId}/variants.json`,
      {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`
        }
      }
    )

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(`Failed to fetch variants: ${JSON.stringify(error)}`)
    }

    const data = await response.json()
    return data.variants || []
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
      const response = await fetch(
        `${this.baseUrl}/uploads/images.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            file_name: filename,
            url: imageUrl
          })
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to upload image: ${response.statusText}`)
      }

      const data = await response.json()
      return data.id
    } catch (error) {
      console.error('Error uploading image to Printify:', error)
      throw error
    }
  }

  /**
   * Get product details
   */
  async getProduct(productId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products/${productId}.json`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to get product: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting product:', error)
      throw error
    }
  }

  /**
   * List all products
   */
  async listProducts(page: number = 1, limit: number = 10): Promise<any[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products.json?page=${page}&limit=${limit}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to list products: ${response.statusText}`)
      }

      const data = await response.json()
      return data.data || []
    } catch (error) {
      console.error('Error listing products:', error)
      return []
    }
  }

  /**
   * Delete a product
   */
  async deleteProduct(productId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products/${productId}.json`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`
          }
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error deleting product:', error)
      return false
    }
  }

  /**
   * Get available blueprints (product types)
   */
  async getBlueprints(): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/catalog/blueprints.json`, {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get blueprints: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting blueprints:', error)
      return []
    }
  }

  /**
   * Get providers for a blueprint
   */
  async getProviders(blueprintId: number): Promise<any[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/catalog/blueprints/${blueprintId}/print_providers.json`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to get providers: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting providers:', error)
      return []
    }
  }
}
