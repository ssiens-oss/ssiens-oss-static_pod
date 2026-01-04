/**
 * Printify Integration Service - WORKING VERSION
 * Properly integrates with Printify API using correct print_areas format
 */

interface PrintifyConfig {
  apiKey: string
  shopId: string
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
   * Get variants for a blueprint/provider combination
   */
  async getVariants(blueprintId: number, providerId: number): Promise<any[]> {
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

      const data = await response.json()
      return data.variants || []
    } catch (error) {
      console.error('Error getting variants:', error)
      throw error
    }
  }

  /**
   * Upload image to Printify and get image ID
   */
  async uploadImage(base64Image: string, filename: string): Promise<string> {
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
            contents: base64Image.replace(/^data:image\/\w+;base64,/, '')
          })
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(`Failed to upload image: ${JSON.stringify(error)}`)
      }

      const data = await response.json()
      return data.id
    } catch (error) {
      console.error('Error uploading image to Printify:', error)
      throw error
    }
  }

  /**
   * Create a T-shirt product
   */
  async createTShirt(
    imageBase64: string,
    title: string,
    description: string,
    options: {
      price?: number
      tags?: string[]
    } = {}
  ): Promise<CreatedProduct> {
    const { price = 19.99, tags = [] } = options

    // Blueprint 6: Unisex Heavy Cotton Tee, Provider 42: Drive Fulfillment
    return this.createProductWithImage(6, 42, imageBase64, title, description, price, tags)
  }

  /**
   * Create a Hoodie product
   */
  async createHoodie(
    imageBase64: string,
    title: string,
    description: string,
    options: {
      price?: number
      tags?: string[]
    } = {}
  ): Promise<CreatedProduct> {
    const { price = 34.99, tags = [] } = options

    // Blueprint 92: Unisex College Hoodie, Provider 99: Printify Choice
    return this.createProductWithImage(92, 99, imageBase64, title, description, price, tags)
  }

  /**
   * Create product with image using proper Printify API format
   */
  private async createProductWithImage(
    blueprintId: number,
    providerId: number,
    imageBase64: string,
    title: string,
    description: string,
    price: number,
    tags: string[]
  ): Promise<CreatedProduct> {
    try {
      // Step 1: Upload image
      console.log(`   📤 Uploading image...`)
      const imageId = await this.uploadImage(imageBase64, `${title}.png`)
      console.log(`   ✅ Image uploaded: ${imageId}`)

      // Step 2: Get available variants
      console.log(`   🔍 Fetching variants...`)
      const variants = await this.getVariants(blueprintId, providerId)

      if (!variants || variants.length === 0) {
        throw new Error('No variants available for this blueprint/provider')
      }

      // Step 3: Prepare variants with pricing (enable first 10 variants)
      const variantIds = variants.slice(0, 10).map((v: any) => v.id)
      const variantsData = variantIds.map((id: number) => ({
        id,
        price: Math.round(price * 100), // Price in cents
        is_enabled: true
      }))

      console.log(`   ✅ Found ${variantIds.length} variants`)

      // Step 4: Create product with print_areas
      const productData = {
        title,
        description,
        blueprint_id: blueprintId,
        print_provider_id: providerId,
        variants: variantsData,
        print_areas: [
          {
            variant_ids: variantIds,
            placeholders: [
              {
                position: 'front',
                images: [
                  {
                    id: imageId,
                    x: 0.5,
                    y: 0.5,
                    scale: 1,
                    angle: 0
                  }
                ]
              }
            ]
          }
        ],
        tags
      }

      console.log(`   📦 Creating product...`)
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/products.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(productData)
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
        printifyUrl: `https://printify.com/app/stores/${this.config.shopId}/products/${data.id}`
      }
    } catch (error) {
      console.error('Error creating product:', error)
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
}
