/**
 * Shopify Integration Service
 * Publishes products to Shopify store
 */

interface ShopifyConfig {
  storeUrl: string
  accessToken: string
  apiVersion?: string
}

interface ShopifyProduct {
  title: string
  bodyHtml: string
  vendor: string
  productType: string
  tags: string[]
  images: Array<{ src: string }>
  variants: Array<{
    title: string
    price: string
    sku?: string
    inventoryQuantity?: number
  }>
}

interface PublishedProduct {
  id: string
  handle: string
  storeUrl: string
}

export class ShopifyService {
  private config: ShopifyConfig
  private baseUrl: string

  constructor(config: ShopifyConfig) {
    this.config = {
      apiVersion: '2024-01',
      ...config
    }
    this.baseUrl = `https://${this.config.storeUrl}/admin/api/${this.config.apiVersion}`
  }

  /**
   * Create product in Shopify
   */
  async createProduct(product: ShopifyProduct): Promise<PublishedProduct> {
    try {
      const response = await fetch(`${this.baseUrl}/products.json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Shopify-Access-Token': this.config.accessToken
        },
        body: JSON.stringify({ product })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(`Shopify API error: ${JSON.stringify(error)}`)
      }

      const data = await response.json()
      const createdProduct = data.product

      return {
        id: createdProduct.id,
        handle: createdProduct.handle,
        storeUrl: `https://${this.config.storeUrl}/products/${createdProduct.handle}`
      }
    } catch (error) {
      console.error('Error creating Shopify product:', error)
      throw error
    }
  }

  /**
   * Create product from Printify data
   */
  async createFromPrintify(
    title: string,
    description: string,
    imageUrl: string,
    price: number,
    tags: string[] = [],
    productType: 'T-Shirt' | 'Hoodie' = 'T-Shirt'
  ): Promise<PublishedProduct> {
    const variants = this.generateStandardVariants(productType, price)

    return this.createProduct({
      title,
      bodyHtml: description,
      vendor: 'POD Studio',
      productType,
      tags,
      images: [{ src: imageUrl }],
      variants
    })
  }

  /**
   * Generate standard size variants
   */
  private generateStandardVariants(
    productType: string,
    basePrice: number
  ): Array<{ title: string; price: string }> {
    const sizes = ['S', 'M', 'L', 'XL', '2XL', '3XL']
    const priceDelta = productType === 'Hoodie' ? 2 : 0

    return sizes.map((size, index) => ({
      title: size,
      price: (basePrice + (index > 3 ? priceDelta : 0)).toFixed(2),
      sku: `${productType.toUpperCase()}-${size}`,
      inventoryQuantity: 0  // POD products don't have inventory
    }))
  }

  /**
   * Update product
   */
  async updateProduct(
    productId: string,
    updates: Partial<ShopifyProduct>
  ): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/products/${productId}.json`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': this.config.accessToken
          },
          body: JSON.stringify({ product: updates })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error updating Shopify product:', error)
      return false
    }
  }

  /**
   * Delete product
   */
  async deleteProduct(productId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/products/${productId}.json`,
        {
          method: 'DELETE',
          headers: {
            'X-Shopify-Access-Token': this.config.accessToken
          }
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error deleting Shopify product:', error)
      return false
    }
  }

  /**
   * Get product by ID
   */
  async getProduct(productId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/products/${productId}.json`,
        {
          headers: {
            'X-Shopify-Access-Token': this.config.accessToken
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to get product: ${response.statusText}`)
      }

      const data = await response.json()
      return data.product
    } catch (error) {
      console.error('Error getting Shopify product:', error)
      throw error
    }
  }

  /**
   * List products
   */
  async listProducts(params: {
    limit?: number
    sinceId?: string
    createdAtMin?: string
  } = {}): Promise<any[]> {
    try {
      const queryParams = new URLSearchParams()
      if (params.limit) queryParams.append('limit', params.limit.toString())
      if (params.sinceId) queryParams.append('since_id', params.sinceId)
      if (params.createdAtMin) queryParams.append('created_at_min', params.createdAtMin)

      const response = await fetch(
        `${this.baseUrl}/products.json?${queryParams}`,
        {
          headers: {
            'X-Shopify-Access-Token': this.config.accessToken
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to list products: ${response.statusText}`)
      }

      const data = await response.json()
      return data.products || []
    } catch (error) {
      console.error('Error listing Shopify products:', error)
      return []
    }
  }

  /**
   * Add product to collection
   */
  async addToCollection(productId: string, collectionId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/collects.json`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': this.config.accessToken
          },
          body: JSON.stringify({
            collect: {
              product_id: productId,
              collection_id: collectionId
            }
          })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error adding product to collection:', error)
      return false
    }
  }

  /**
   * Create collection
   */
  async createCollection(
    title: string,
    description: string,
    rules?: any[]
  ): Promise<string | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/smart_collections.json`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': this.config.accessToken
          },
          body: JSON.stringify({
            smart_collection: {
              title,
              body_html: description,
              rules: rules || []
            }
          })
        }
      )

      if (!response.ok) {
        return null
      }

      const data = await response.json()
      return data.smart_collection.id
    } catch (error) {
      console.error('Error creating collection:', error)
      return null
    }
  }

  /**
   * Update product SEO
   */
  async updateSEO(
    productId: string,
    metafields: {
      title?: string
      description?: string
      keywords?: string[]
    }
  ): Promise<boolean> {
    try {
      const updates: any = {}

      if (metafields.title) {
        updates.metafields_global_title_tag = metafields.title
      }

      if (metafields.description) {
        updates.metafields_global_description_tag = metafields.description
      }

      return this.updateProduct(productId, updates)
    } catch (error) {
      console.error('Error updating SEO:', error)
      return false
    }
  }

  /**
   * Publish product (make visible)
   */
  async publishProduct(productId: string): Promise<boolean> {
    return this.updateProduct(productId, {
      //@ts-ignore
      status: 'active'
    })
  }

  /**
   * Unpublish product
   */
  async unpublishProduct(productId: string): Promise<boolean> {
    return this.updateProduct(productId, {
      //@ts-ignore
      status: 'draft'
    })
  }
}
