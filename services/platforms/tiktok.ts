/**
 * TikTok Shop Integration Service
 * Publishes products to TikTok Shop
 */

interface TikTokConfig {
  appKey: string
  appSecret: string
  shopId: string
  accessToken: string
}

interface TikTokProduct {
  title: string
  description: string
  categoryId: string
  brandId?: string
  images: string[]
  skus: Array<{
    price: number
    inventory: number
    sellerSku: string
  }>
}

export class TikTokShopService {
  private config: TikTokConfig
  private baseUrl = 'https://open-api.tiktokglobalshop.com'

  constructor(config: TikTokConfig) {
    this.config = config
  }

  /**
   * Create product in TikTok Shop
   */
  async createProduct(product: TikTokProduct): Promise<string | null> {
    try {
      const timestamp = Math.floor(Date.now() / 1000)
      const signature = this.generateSignature(timestamp)

      const response = await fetch(`${this.baseUrl}/api/products/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tts-access-token': this.config.accessToken
        },
        body: JSON.stringify({
          shop_id: this.config.shopId,
          product: product,
          timestamp,
          sign: signature
        })
      })

      if (!response.ok) {
        console.error('TikTok Shop API error:', await response.text())
        return null
      }

      const data = await response.json()
      return data.data?.product_id || null
    } catch (error) {
      console.error('Error creating TikTok Shop product:', error)
      return null
    }
  }

  /**
   * Upload product image to TikTok
   */
  async uploadImage(imageUrl: string): Promise<string | null> {
    try {
      // Download image
      const imageResponse = await fetch(imageUrl)
      const imageBlob = await imageResponse.blob()

      // Upload to TikTok
      const formData = new FormData()
      formData.append('image', imageBlob)
      formData.append('shop_id', this.config.shopId)

      const response = await fetch(`${this.baseUrl}/api/products/upload_image`, {
        method: 'POST',
        headers: {
          'x-tts-access-token': this.config.accessToken
        },
        body: formData
      })

      if (!response.ok) {
        console.error('TikTok image upload error:', await response.text())
        return null
      }

      const data = await response.json()
      return data.data?.image_url || null
    } catch (error) {
      console.error('Error uploading image to TikTok:', error)
      return null
    }
  }

  /**
   * Create product from POD data
   */
  async createFromPOD(
    title: string,
    description: string,
    imageUrl: string,
    price: number,
    productType: 'tshirt' | 'hoodie'
  ): Promise<string | null> {
    // Upload image first
    const tiktokImageUrl = await this.uploadImage(imageUrl)
    if (!tiktokImageUrl) {
      console.error('Failed to upload image to TikTok')
      return null
    }

    // Create product
    return this.createProduct({
      title,
      description,
      categoryId: productType === 'tshirt' ? '100001' : '100002', // Example category IDs
      images: [tiktokImageUrl],
      skus: this.generateStandardSKUs(price, productType)
    })
  }

  /**
   * Generate standard SKUs for sizes
   */
  private generateStandardSKUs(
    basePrice: number,
    productType: string
  ): Array<{ price: number; inventory: number; sellerSku: string }> {
    const sizes = ['S', 'M', 'L', 'XL', '2XL']

    return sizes.map(size => ({
      price: basePrice,
      inventory: 999, // TikTok requires inventory
      sellerSku: `${productType.toUpperCase()}-${size}-${Date.now()}`
    }))
  }

  /**
   * Generate API signature
   */
  private generateSignature(timestamp: number): string {
    // Simplified signature generation
    // In production, use proper HMAC-SHA256 with app_secret
    const crypto = require('crypto')
    const message = `${this.config.appKey}${timestamp}${this.config.shopId}`

    return crypto
      .createHmac('sha256', this.config.appSecret)
      .update(message)
      .digest('hex')
  }

  /**
   * Get product details
   */
  async getProduct(productId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/products/details?product_id=${productId}&shop_id=${this.config.shopId}`,
        {
          headers: {
            'x-tts-access-token': this.config.accessToken
          }
        }
      )

      if (!response.ok) {
        return null
      }

      const data = await response.json()
      return data.data
    } catch (error) {
      console.error('Error getting TikTok product:', error)
      return null
    }
  }

  /**
   * Update product status (activate/deactivate)
   */
  async updateProductStatus(
    productId: string,
    status: 'ACTIVATE' | 'DEACTIVATE'
  ): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/products/update_status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tts-access-token': this.config.accessToken
        },
        body: JSON.stringify({
          shop_id: this.config.shopId,
          product_id: productId,
          status
        })
      })

      return response.ok
    } catch (error) {
      console.error('Error updating TikTok product status:', error)
      return false
    }
  }
}
