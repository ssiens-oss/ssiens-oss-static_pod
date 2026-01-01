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
  print_areas: PrintArea[]
  images?: PrintifyImage[]
  tags?: string[]
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

interface PrintAreaPlaceholder {
  position: string
  images: Array<{
    id: string
    x: number
    y: number
    scale: number
    angle: number
  }>
}

interface PrintArea {
  variant_ids: number[]
  placeholders: PrintAreaPlaceholder[]
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
      tags = []
    } = options

    // Blueprint 3: Unisex Heavy Cotton Tee (Gildan 5000)
    // Provider 99: SwiftPOD
    const blueprintId = 3
    const providerId = 99

    // Step 1: Upload image to Printify
    console.log('Uploading image to Printify...')
    const imageId = await this.uploadImage(imageUrl, `${title}-design.png`)
    console.log('Image uploaded with ID:', imageId)

    // Step 2: Get real variants from Printify API
    console.log('Fetching variants from Printify API...')
    const variantsData = await this.getVariants(blueprintId, providerId)
    console.log('Fetched variants:', variantsData.variants?.length || 0)

    // Step 3: Build variants array with pricing
    const variants = variantsData.variants.map((variant: any) => ({
      id: variant.id,
      price: Math.round(price * 100), // Price in cents
      isEnabled: true
    }))

    // Step 4: Build print_areas with all variant IDs
    const variantIds = variants.map((v: any) => v.id)
    const print_areas = [{
      variant_ids: variantIds,
      placeholders: [{
        position: 'front',
        images: [{
          id: imageId,
          x: 0.5,
          y: 0.5,
          scale: 1,
          angle: 0
        }]
      }]
    }]

    // Step 5: Create product with print_areas
    return this.createProduct({
      title,
      description,
      blueprintId,
      providerId,
      variants,
      print_areas,
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
      tags = []
    } = options

    // Blueprint 165: Unisex Heavy Blend Hoodie (Gildan 18500)
    // Provider 99: SwiftPOD
    const blueprintId = 165
    const providerId = 99

    // Step 1: Upload image to Printify
    console.log('Uploading image to Printify...')
    const imageId = await this.uploadImage(imageUrl, `${title}-design.png`)
    console.log('Image uploaded with ID:', imageId)

    // Step 2: Get real variants from Printify API
    console.log('Fetching variants from Printify API...')
    const variantsData = await this.getVariants(blueprintId, providerId)
    console.log('Fetched variants:', variantsData.variants?.length || 0)

    // Step 3: Build variants array with pricing
    const variants = variantsData.variants.map((variant: any) => ({
      id: variant.id,
      price: Math.round(price * 100), // Price in cents
      isEnabled: true
    }))

    // Step 4: Build print_areas with all variant IDs
    const variantIds = variants.map((v: any) => v.id)
    const print_areas = [{
      variant_ids: variantIds,
      placeholders: [{
        position: 'front',
        images: [{
          id: imageId,
          x: 0.5,
          y: 0.5,
          scale: 1,
          angle: 0
        }]
      }]
    }]

    // Step 5: Create product with print_areas
    return this.createProduct({
      title,
      description,
      blueprintId,
      providerId,
      variants,
      print_areas,
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
          isEnabled: true
        })
      }
    }

    return variants
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

  /**
   * Get variants for a specific blueprint and provider
   */
  async getVariants(blueprintId: number, providerId: number): Promise<any> {
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
        throw new Error(`Failed to get variants: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting variants:', error)
      throw error
    }
  }
}
