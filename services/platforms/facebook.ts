/**
 * Facebook Shop Integration Service
 * Manages Facebook Commerce catalog and shop
 */

interface FacebookConfig {
  pageId: string
  accessToken: string
  catalogId: string
}

interface FacebookProduct {
  retailerId: string
  name: string
  description: string
  imageUrl: string
  price: number
  currency: string
  url: string
  brand?: string
  availability: 'in stock' | 'out of stock' | 'preorder'
  condition: 'new' | 'used' | 'refurbished'
}

export class FacebookShopService {
  private config: FacebookConfig
  private baseUrl = 'https://graph.facebook.com/v18.0'

  constructor(config: FacebookConfig) {
    this.config = config
  }

  /**
   * Create product in Facebook catalog
   */
  async createProduct(product: FacebookProduct): Promise<string | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${this.config.catalogId}/products`,
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
            price: product.price * 100, // Price in cents
            currency: product.currency,
            url: product.url,
            brand: product.brand || 'POD Studio',
            availability: product.availability,
            condition: product.condition
          })
        }
      )

      if (!response.ok) {
        const error = await response.json()
        console.error('Facebook API error:', error)
        return null
      }

      const data = await response.json()
      return data.id || null
    } catch (error) {
      console.error('Error creating Facebook product:', error)
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
    productUrl: string,
    currency: string = 'USD'
  ): Promise<string | null> {
    const retailerId = `POD_${Date.now()}_${Math.random().toString(36).substring(7)}`

    return this.createProduct({
      retailerId,
      name: title,
      description,
      imageUrl,
      price,
      currency,
      url: productUrl,
      availability: 'in stock',
      condition: 'new'
    })
  }

  /**
   * Update product
   */
  async updateProduct(
    productId: string,
    updates: Partial<FacebookProduct>
  ): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${productId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            ...updates
          })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error updating Facebook product:', error)
      return false
    }
  }

  /**
   * Delete product
   */
  async deleteProduct(productId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${productId}?access_token=${this.config.accessToken}`,
        {
          method: 'DELETE'
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error deleting Facebook product:', error)
      return false
    }
  }

  /**
   * Get product by ID
   */
  async getProduct(productId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${productId}?access_token=${this.config.accessToken}&fields=id,name,description,image_url,price,url,availability`
      )

      if (!response.ok) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting Facebook product:', error)
      return null
    }
  }

  /**
   * List catalog products
   */
  async listProducts(limit: number = 25): Promise<any[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${this.config.catalogId}/products?access_token=${this.config.accessToken}&limit=${limit}`
      )

      if (!response.ok) {
        return []
      }

      const data = await response.json()
      return data.data || []
    } catch (error) {
      console.error('Error listing Facebook products:', error)
      return []
    }
  }

  /**
   * Create product set (collection)
   */
  async createProductSet(name: string, filter?: any): Promise<string | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${this.config.catalogId}/product_sets`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            name: name,
            filter: filter || {}
          })
        }
      )

      if (!response.ok) {
        return null
      }

      const data = await response.json()
      return data.id || null
    } catch (error) {
      console.error('Error creating product set:', error)
      return null
    }
  }

  /**
   * Sync catalog (trigger refresh)
   */
  async syncCatalog(): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/${this.config.catalogId}/items_batch`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            access_token: this.config.accessToken,
            requests: []
          })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error syncing catalog:', error)
      return false
    }
  }

  /**
   * Create post with product tag on Facebook Page
   */
  async createPagePost(
    message: string,
    imageUrl: string,
    productId?: string
  ): Promise<string | null> {
    try {
      const postData: any = {
        access_token: this.config.accessToken,
        message: message,
        url: imageUrl
      }

      if (productId) {
        postData.attached_media = JSON.stringify([{
          media_fbid: productId
        }])
      }

      const response = await fetch(
        `${this.baseUrl}/${this.config.pageId}/photos`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(postData)
        }
      )

      if (!response.ok) {
        return null
      }

      const data = await response.json()
      return data.id || null
    } catch (error) {
      console.error('Error creating Facebook post:', error)
      return null
    }
  }
}
