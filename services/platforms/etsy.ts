/**
 * Etsy Integration Service
 * Creates listings in Etsy shop
 */

interface EtsyConfig {
  apiKey: string
  shopId: string
  accessToken: string
}

interface EtsyListing {
  title: string
  description: string
  price: number
  quantity: number
  tags: string[]
  images: string[]
  shippingProfileId?: string
  taxonomyId?: number
  whoMade: 'i_did' | 'someone_else' | 'collective'
  whenMade: string
  isSupply: boolean
}

export class EtsyService {
  private config: EtsyConfig
  private baseUrl = 'https://openapi.etsy.com/v3/application'

  constructor(config: EtsyConfig) {
    this.config = config
  }

  /**
   * Create listing in Etsy
   */
  async createListing(listing: EtsyListing): Promise<string | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/listings`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': this.config.apiKey,
            'Authorization': `Bearer ${this.config.accessToken}`
          },
          body: JSON.stringify({
            ...listing,
            quantity: 999, // POD products
            state: 'draft' // Start as draft
          })
        }
      )

      if (!response.ok) {
        const error = await response.json()
        console.error('Etsy API error:', error)
        return null
      }

      const data = await response.json()
      return data.listing_id?.toString() || null
    } catch (error) {
      console.error('Error creating Etsy listing:', error)
      return null
    }
  }

  /**
   * Upload image to listing
   */
  async uploadImage(listingId: string, imageUrl: string): Promise<boolean> {
    try {
      // Download image
      const imageResponse = await fetch(imageUrl)
      const imageBlob = await imageResponse.blob()

      // Upload to Etsy
      const formData = new FormData()
      formData.append('image', imageBlob)

      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/listings/${listingId}/images`,
        {
          method: 'POST',
          headers: {
            'x-api-key': this.config.apiKey,
            'Authorization': `Bearer ${this.config.accessToken}`
          },
          body: formData
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error uploading image to Etsy:', error)
      return false
    }
  }

  /**
   * Create listing from POD data
   */
  async createFromPOD(
    title: string,
    description: string,
    imageUrl: string,
    price: number,
    tags: string[],
    productType: 'tshirt' | 'hoodie'
  ): Promise<string | null> {
    // Create listing
    const listingId = await this.createListing({
      title,
      description,
      price,
      quantity: 999,
      tags: tags.slice(0, 13), // Etsy allows max 13 tags
      images: [],
      taxonomyId: productType === 'tshirt' ? 1015 : 1016, // Example taxonomy IDs
      whoMade: 'i_did',
      whenMade: 'made_to_order',
      isSupply: false
    })

    if (!listingId) {
      return null
    }

    // Upload image
    await this.uploadImage(listingId, imageUrl)

    return listingId
  }

  /**
   * Publish listing (make active)
   */
  async publishListing(listingId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/listings/${listingId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': this.config.apiKey,
            'Authorization': `Bearer ${this.config.accessToken}`
          },
          body: JSON.stringify({
            state: 'active'
          })
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error publishing Etsy listing:', error)
      return false
    }
  }

  /**
   * Get listing details
   */
  async getListing(listingId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/listings/${listingId}`,
        {
          headers: {
            'x-api-key': this.config.apiKey,
            'Authorization': `Bearer ${this.config.accessToken}`
          }
        }
      )

      if (!response.ok) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting Etsy listing:', error)
      return null
    }
  }

  /**
   * Delete listing
   */
  async deleteListing(listingId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.baseUrl}/shops/${this.config.shopId}/listings/${listingId}`,
        {
          method: 'DELETE',
          headers: {
            'x-api-key': this.config.apiKey,
            'Authorization': `Bearer ${this.config.accessToken}`
          }
        }
      )

      return response.ok
    } catch (error) {
      console.error('Error deleting Etsy listing:', error)
      return false
    }
  }
}
