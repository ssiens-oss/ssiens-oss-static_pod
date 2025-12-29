import { ApiCredentials, PublishResult, LogType, LogEntry } from '../types';

const generateId = () => Math.random().toString(36).substr(2, 9);
const timestamp = () => new Date().toLocaleTimeString('en-US', { hour12: false });

type LogCallback = (entry: LogEntry) => void;

export class ShopifyService {
  private storeName: string;
  private accessToken: string;
  private apiVersion = '2024-01';

  constructor(credentials: ApiCredentials) {
    this.storeName = credentials.shopifyStoreName;
    this.accessToken = credentials.shopifyAccessToken;
  }

  private get baseUrl(): string {
    return `https://${this.storeName}.myshopify.com/admin/api/${this.apiVersion}`;
  }

  /**
   * Get product from Shopify (already synced from Printify)
   */
  async getProduct(productId: string, onLog: LogCallback): Promise<any> {
    try {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Shopify] Fetching product details...`,
        type: LogType.INFO
      });

      await this.sleep(800);

      // In production:
      // const response = await fetch(`${this.baseUrl}/products/${productId}.json`, {
      //   headers: {
      //     'X-Shopify-Access-Token': this.accessToken,
      //     'Content-Type': 'application/json'
      //   }
      // });
      // return await response.json();

      return {
        id: productId,
        title: 'Mock Product',
        handle: 'mock-product-handle'
      };
    } catch (error) {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Shopify] ✗ Failed to fetch product: ${error}`,
        type: LogType.ERROR
      });
      throw error;
    }
  }

  /**
   * Update product metadata for TikTok Shop sync
   */
  async updateProductMetadata(
    productId: string,
    metadata: Record<string, any>,
    onLog: LogCallback
  ): Promise<PublishResult> {
    try {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Shopify] Updating product metadata for marketplace sync...`,
        type: LogType.INFO
      });

      await this.sleep(1000);

      // In production:
      // await fetch(`${this.baseUrl}/products/${productId}.json`, {
      //   method: 'PUT',
      //   headers: {
      //     'X-Shopify-Access-Token': this.accessToken,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({
      //     product: {
      //       metafields: [
      //         { namespace: 'tiktok', key: 'sync_enabled', value: 'true', type: 'boolean' },
      //         ...Object.entries(metadata).map(([key, value]) => ({
      //           namespace: 'integration',
      //           key,
      //           value: String(value),
      //           type: 'single_line_text_field'
      //         }))
      //       ]
      //     }
      //   })
      // });

      const shopifyProductUrl = `https://${this.storeName}.myshopify.com/admin/products/${productId}`;

      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Shopify] ✓ Product ready for marketplace integration`,
        type: LogType.SUCCESS
      });

      return {
        platform: 'shopify',
        productId,
        productUrl: shopifyProductUrl,
        status: 'success',
        message: 'Product updated on Shopify'
      };
    } catch (error) {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Shopify] ✗ Failed to update product: ${error}`,
        type: LogType.ERROR
      });

      return {
        platform: 'shopify',
        status: 'failed',
        message: `Shopify error: ${error}`
      };
    }
  }

  /**
   * Get product handle for TikTok sync
   */
  async getProductHandle(productId: string): Promise<string> {
    await this.sleep(500);
    return `product-${productId.toLowerCase()}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
