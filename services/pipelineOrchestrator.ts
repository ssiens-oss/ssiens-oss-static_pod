import { PrintifyService } from './printifyService';
import { ShopifyService } from './shopifyService';
import { TikTokService } from './tiktokService';
import { ApiCredentials, PipelineStatus, PublishResult, LogEntry, LogType } from '../types';

const generateId = () => Math.random().toString(36).substr(2, 9);
const timestamp = () => new Date().toLocaleTimeString('en-US', { hour12: false });

type LogCallback = (entry: LogEntry) => void;
type StatusCallback = (status: PipelineStatus) => void;

export interface PipelineResult {
  success: boolean;
  results: {
    printify?: PublishResult;
    shopify?: PublishResult;
    tiktok?: PublishResult;
  };
  productUrls: {
    printify?: string;
    shopify?: string;
    tiktok?: string;
  };
}

/**
 * Orchestrates the full pipeline: Printify → Shopify → TikTok Shop
 */
export class PipelineOrchestrator {
  private printifyService: PrintifyService;
  private shopifyService: ShopifyService;
  private tiktokService: TikTokService;

  constructor(credentials: ApiCredentials) {
    this.printifyService = new PrintifyService(credentials);
    this.shopifyService = new ShopifyService(credentials);
    this.tiktokService = new TikTokService(credentials);
  }

  /**
   * Execute the full auto-populate and publish pipeline
   */
  async executeFullPipeline(
    designUrl: string,
    productTitle: string,
    blueprintId: number,
    price: number,
    category: string,
    onLog: LogCallback,
    onStatus: StatusCallback,
    shouldStop: () => boolean
  ): Promise<PipelineResult> {
    const result: PipelineResult = {
      success: false,
      results: {},
      productUrls: {}
    };

    const status: PipelineStatus = {
      printify: 'pending',
      shopify: 'pending',
      tiktok: 'pending'
    };

    try {
      // ========== STEP 1: Create Product on Printify ==========
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: '🚀 Starting auto-populate pipeline: Printify → Shopify → TikTok',
        type: LogType.INFO
      });

      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        type: LogType.INFO
      });

      if (shouldStop()) return result;

      status.printify = 'processing';
      onStatus({ ...status });

      const printifyResult = await this.printifyService.createProduct(
        designUrl,
        productTitle,
        blueprintId,
        onLog
      );

      result.results.printify = printifyResult;

      if (printifyResult.status === 'failed') {
        status.printify = 'failed';
        onStatus({ ...status });
        return result;
      }

      status.printify = 'completed';
      result.productUrls.printify = printifyResult.productUrl;
      onStatus({ ...status });

      if (shouldStop()) return result;

      // ========== STEP 2: Publish to Shopify via Printify ==========
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        type: LogType.INFO
      });

      status.shopify = 'processing';
      onStatus({ ...status });

      // Publish from Printify to Shopify
      const publishSuccess = await this.printifyService.publishToStore(
        printifyResult.productId!,
        onLog
      );

      if (!publishSuccess) {
        status.shopify = 'failed';
        onStatus({ ...status });
        return result;
      }

      // Generate mock Shopify product ID (in production, this comes from Printify webhook or API)
      const shopifyProductId = `gid://shopify/Product/${Math.floor(Math.random() * 1000000)}`;

      // Update Shopify product metadata for TikTok sync
      const shopifyResult = await this.shopifyService.updateProductMetadata(
        shopifyProductId,
        {
          printify_product_id: printifyResult.productId,
          tiktok_sync_enabled: 'true',
          auto_populated: 'true'
        },
        onLog
      );

      result.results.shopify = shopifyResult;

      if (shopifyResult.status === 'failed') {
        status.shopify = 'failed';
        onStatus({ ...status });
        return result;
      }

      status.shopify = 'completed';
      result.productUrls.shopify = shopifyResult.productUrl;
      onStatus({ ...status });

      if (shouldStop()) return result;

      // ========== STEP 3: Sync to TikTok Shop ==========
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        type: LogType.INFO
      });

      status.tiktok = 'processing';
      onStatus({ ...status });

      const tiktokResult = await this.tiktokService.syncProduct(
        shopifyProductId,
        {
          title: productTitle,
          description: `Premium ${productTitle} - Auto-synced from Shopify`,
          price: price,
          images: [designUrl],
          category: category
        },
        onLog
      );

      result.results.tiktok = tiktokResult;

      if (tiktokResult.status === 'failed') {
        status.tiktok = 'failed';
        onStatus({ ...status });
        return result;
      }

      status.tiktok = 'completed';
      result.productUrls.tiktok = tiktokResult.productUrl;
      onStatus({ ...status });

      // Update inventory on TikTok
      await this.tiktokService.updateInventory(tiktokResult.productId!, 100, onLog);

      // ========== PIPELINE COMPLETE ==========
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        type: LogType.INFO
      });

      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: '🎉 PIPELINE COMPLETE! Product is live across all platforms!',
        type: LogType.SUCCESS
      });

      result.success = true;
      return result;

    } catch (error) {
      onLog({
        id: generateId(),
        timestamp: timestamp(),
        message: `❌ Pipeline failed: ${error}`,
        type: LogType.ERROR
      });

      return result;
    }
  }
}
