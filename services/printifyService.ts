import { ApiCredentials, PublishResult, LogType, LogEntry } from '../types';

const generateId = () => Math.random().toString(36).substr(2, 9);
const timestamp = () => new Date().toLocaleTimeString('en-US', { hour12: false });

type LogCallback = (entry: LogEntry) => void;

export class PrintifyService {
  private apiKey: string;
  private shopId: string;
  private baseUrl = 'https://api.printify.com/v1';

  constructor(credentials: ApiCredentials) {
    this.apiKey = credentials.printifyApiKey;
    this.shopId = credentials.printifyShopId;
  }

  /**
   * Create a product on Printify
   */
  async createProduct(
    designUrl: string,
    productTitle: string,
    blueprintId: number,
    onLog: LogCallback
  ): Promise<PublishResult> {
    try {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Printify] Creating product: ${productTitle}`,
        type: LogType.INFO
      });

      // Simulate API delay
      await this.sleep(1500);

      // In production, this would make actual API call:
      // const response = await fetch(`${this.baseUrl}/shops/${this.shopId}/products.json`, {
      //   method: 'POST',
      //   headers: {
      //     'Authorization': `Bearer ${this.apiKey}`,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({
      //     title: productTitle,
      //     description: 'Auto-generated product from StaticWaves POD Studio',
      //     blueprint_id: blueprintId,
      //     print_provider_id: 1,
      //     variants: [{ /* variant config */ }],
      //     print_areas: [{ /* print area with design URL */ }]
      //   })
      // });

      const mockProductId = `pfy_${generateId()}`;

      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Printify] ✓ Product created successfully (ID: ${mockProductId})`,
        type: LogType.SUCCESS
      });

      return {
        platform: 'printify',
        productId: mockProductId,
        productUrl: `https://printify.com/app/products/${mockProductId}`,
        status: 'success',
        message: 'Product created on Printify'
      };
    } catch (error) {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Printify] ✗ Failed to create product: ${error}`,
        type: LogType.ERROR
      });

      return {
        platform: 'printify',
        status: 'failed',
        message: `Printify error: ${error}`
      };
    }
  }

  /**
   * Publish product to connected store (Shopify)
   */
  async publishToStore(productId: string, onLog: LogCallback): Promise<boolean> {
    try {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Printify] Publishing product ${productId} to store...`,
        type: LogType.INFO
      });

      await this.sleep(1000);

      // In production:
      // await fetch(`${this.baseUrl}/shops/${this.shopId}/products/${productId}/publish.json`, {
      //   method: 'POST',
      //   headers: { 'Authorization': `Bearer ${this.apiKey}` }
      // });

      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Printify] ✓ Product published to connected store`,
        type: LogType.SUCCESS
      });

      return true;
    } catch (error) {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `[Printify] ✗ Failed to publish: ${error}`,
        type: LogType.ERROR
      });
      return false;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
