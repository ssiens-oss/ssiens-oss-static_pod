/**
 * Instagram Shopping Integration Service
 * Tags products in Instagram posts and manages Instagram Shop
 */

interface InstagramConfig {
  accessToken: string
  businessAccountId: string
}

interface InstagramProduct {
  catalogId: string
  retailerId: string
  name: string
  description: string
  imageUrl: string
  price: number
  url: string
}

export class InstagramService {
  private config: InstagramConfig
  private baseUrl = 'https://graph.facebook.com/v18.0'

  constructor(config: InstagramConfig) {
    this.config = config
  }

  /**
   * Create product in Instagram catalog (via Facebook Catalog)
   */
  async createProduct(product: InstagramProduct): Promise<string | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${product.catalogId}/products`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            retailer_id: product.retailerId,
            name: product.name,
            description: product.description,
            image_url: product.imageUrl,
            price: product.price,
            url: product.url,
            availability: 'in stock'
          })
        }
      )

      if (!response.ok) {
        const error = await response.json()
        console.error('Instagram API error:', error)
        return null
      }

      const data = await response.json()
      return data.id || null
    } catch (error) {
      console.error('Error creating Instagram product:', error)
      return null
    }
  }

  /**
   * Create media post with product tag
   */
  async createPost(
    imageUrl: string,
    caption: string,
    productTags?: Array<{ productId: string; x: number; y: number }>
  ): Promise<string | null> {
    try {
      // Step 1: Create media container
      const containerResponse = await fetch(
        `${this.baseUrl}/${this.config.businessAccountId}/media`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            image_url: imageUrl,
            caption: caption,
            product_tags: productTags
          })
        }
      )

      if (!containerResponse.ok) {
        console.error('Error creating media container')
        return null
      }

      const containerData = await containerResponse.json()
      const creationId = containerData.id

      // Step 2: Publish media
      const publishResponse = await fetch(
        `${this.baseUrl}/${this.config.businessAccountId}/media_publish`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            creation_id: creationId
          })
        }
      )

      if (!publishResponse.ok) {
        console.error('Error publishing media')
        return null
      }

      const publishData = await publishResponse.json()
      return publishData.id || null
    } catch (error) {
      console.error('Error creating Instagram post:', error)
      return null
    }
  }

  /**
   * Tag product in existing post
   */
  async tagProductInPost(
    mediaId: string,
    productId: string,
    position: { x: number; y: number }
  ): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${mediaId}/product_tags`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            updated_tags: [
              {
                product_id: productId,
                x: position.x,
                y: position.y
              }
            ]
          })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error tagging product:', error)
      return false
    }
  }

  /**
   * Get catalog products
   */
  async getCatalogProducts(catalogId: string, limit: number = 25): Promise<any[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${catalogId}/products?access_token=${this.config.accessToken}&limit=${limit}`
      )

      if (!response.ok) {
        return []
      }

      const data = await response.json()
      return data.data || []
    } catch (error) {
      console.error('Error getting catalog products:', error)
      return []
    }
  }

  /**
   * Get account insights
   */
  async getInsights(metric: string = 'impressions,reach,profile_views'): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${this.config.businessAccountId}/insights?metric=${metric}&period=day&access_token=${this.config.accessToken}`
      )

      if (!response.ok) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting insights:', error)
      return null
    }
  }

  /**
   * Create product from POD data
   */
  async createFromPOD(
    catalogId: string,
    title: string,
    description: string,
    imageUrl: string,
    price: number,
    productUrl: string
  ): Promise<string | null> {
    const retailerId = `POD_${Date.now()}_${Math.random().toString(36).substring(7)}`

    return this.createProduct({
      catalogId,
      retailerId,
      name: title,
      description,
      imageUrl,
      price,
      url: productUrl
    })
  }
}
