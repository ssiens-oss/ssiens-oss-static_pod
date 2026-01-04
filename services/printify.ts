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
  blueprint_id: number
  print_provider_id: number
  variants: ProductVariant[]
  print_areas: PrintArea[]
  tags?: string[]
}

interface ProductVariant {
  id: number
  price: number
  is_enabled: boolean
}

interface PrintArea {
  variant_ids: number[]
  placeholders: Array<{
    position: string
    images: Array<{
      id: string
      x: number
      y: number
      scale: number
      angle: number
    }>
  }>
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

    // Upload image to Printify first
    const uploadedImageId = await this.uploadImage(imageUrl, `${title.replace(/[^a-z0-9]/gi, '_')}.png`)

    // Blueprint 3: Unisex Heavy Cotton Tee (Gildan 5000)
    // Provider 99: SwiftPOD
    // Get variants for this blueprint
    const variants = await this.getBlueprintVariants(3, 99, price)
    const variantIds = variants.map(v => v.id)

    return this.createProduct({
      title,
      description,
      blueprint_id: 3,
      print_provider_id: 99,
      variants,
      print_areas: [{
        variant_ids: variantIds,
        placeholders: [{
          position: 'front',
          images: [{
            id: uploadedImageId,
            x: 0.5,
            y: 0.5,
            scale: 1,
            angle: 0
          }]
        }]
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

    // Upload image to Printify first
    const uploadedImageId = await this.uploadImage(imageUrl, `${title.replace(/[^a-z0-9]/gi, '_')}.png`)

    // Blueprint 165: Unisex Heavy Blend Hoodie (Gildan 18500)
    // Provider 99: SwiftPOD
    // Get variants for this blueprint
    const variants = await this.getBlueprintVariants(165, 99, price)
    const variantIds = variants.map(v => v.id)

    return this.createProduct({
      title,
      description,
      blueprint_id: 165,
      print_provider_id: 99,
      variants,
      print_areas: [{
        variant_ids: variantIds,
        placeholders: [{
          position: 'front',
          images: [{
            id: uploadedImageId,
            x: 0.5,
            y: 0.5,
            scale: 1,
            angle: 0
          }]
        }]
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
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(product)
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
  private generateVariants(
    blueprintId: number,
    providerId: number,
    colors: string[],
    sizes: string[],
    basePrice: number
  ): ProductVariant[] {
    // Note: In production, you would fetch variant IDs from Printify API
    // For now, using mock variant IDs
    const variants: ProductVariant[] = []
    let variantId = 1

    for (const color of colors) {
      for (const size of sizes) {
        variants.push({
          id: variantId++,
          price: Math.round(basePrice * 100), // Price in cents
          is_enabled: true
        })
      }
    }

    return variants
  }

  /**
   * Get blueprint variants from Printify API
   */
  private async getBlueprintVariants(
    blueprintId: number,
    providerId: number,
    price: number
  ): Promise<ProductVariant[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/catalog/blueprints/${blueprintId}/print_providers/${providerId}/variants.json`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to fetch blueprint variants: ${response.statusText}`)
      }

      const data = await response.json()

      // Transform variants to include price and enable all
      return data.variants.map((variant: any) => ({
        id: variant.id,
        price: Math.round(price * 100), // Price in cents
        is_enabled: true
      }))
    } catch (error) {
      console.error('Error fetching blueprint variants:', error)
      throw error
    }
  }

  /**
   * Upload image to Printify
   */
  async uploadImage(imageUrl: string, filename: string): Promise<string> {
    try {
      let uploadPayload: any = { file_name: filename }

      // If it's a local file (file:// or absolute path), convert to base64
      if (imageUrl.startsWith('file://') || imageUrl.startsWith('/')) {
        const fs = await import('fs')
        const filePath = imageUrl.replace('file://', '')

        // Read file and convert to base64
        const fileBuffer = fs.readFileSync(filePath)
        const base64Data = fileBuffer.toString('base64')

        // Printify expects base64 with data URI format
        uploadPayload.contents = `data:image/png;base64,${base64Data}`
      } else {
        // It's a public URL, use it directly
        uploadPayload.url = imageUrl
      }

      const response = await fetch(
        `${this.baseUrl}/uploads/images.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(uploadPayload)
        }
      )

      if (!response.ok) {
        const errorBody = await response.text()
        throw new Error(`Failed to upload image: ${response.statusText} - ${errorBody}`)
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
