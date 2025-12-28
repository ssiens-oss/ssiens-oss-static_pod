import { Product, ShopifyIntegration, GumroadIntegration } from '../types';

/**
 * Shopify Integration Service
 * Syncs products between the POD system and Shopify stores
 */
export class ShopifyService {
  private integrations: Map<string, ShopifyIntegration> = new Map();

  /**
   * Set up Shopify integration for a tenant
   */
  async setupIntegration(
    tenantId: string,
    shopDomain: string,
    accessToken: string
  ): Promise<ShopifyIntegration> {
    const integration: ShopifyIntegration = {
      tenantId,
      shopDomain,
      accessToken,
      webhooks: [],
      syncEnabled: true
    };

    this.integrations.set(tenantId, integration);

    // Set up webhooks
    await this.setupWebhooks(integration);

    return integration;
  }

  /**
   * Sync product to Shopify
   */
  async syncProductToShopify(product: Product, tenantId: string): Promise<{
    success: boolean;
    shopifyProductId?: string;
    error?: string;
  }> {
    const integration = this.integrations.get(tenantId);
    if (!integration || !integration.syncEnabled) {
      return { success: false, error: 'Integration not configured or disabled' };
    }

    try {
      // In production, this would make actual API calls to Shopify
      const shopifyProduct = this.transformToShopifyProduct(product);

      // Simulate API call
      const shopifyProductId = `gid://shopify/Product/${Math.random().toString(36).substr(2, 9)}`;

      return { success: true, shopifyProductId };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  /**
   * Sync multiple products to Shopify
   */
  async syncMultipleProducts(
    products: Product[],
    tenantId: string
  ): Promise<{ synced: number; failed: number; errors: string[] }> {
    const results = { synced: 0, failed: 0, errors: [] as string[] };

    for (const product of products) {
      const result = await this.syncProductToShopify(product, tenantId);
      if (result.success) {
        results.synced++;
      } else {
        results.failed++;
        if (result.error) results.errors.push(result.error);
      }
    }

    return results;
  }

  /**
   * Transform internal product to Shopify format
   */
  private transformToShopifyProduct(product: Product) {
    return {
      title: product.name,
      body_html: product.description,
      vendor: 'POD Studio',
      product_type: product.tags[0] || 'Apparel',
      tags: product.tags.join(', '),
      variants: [
        {
          price: product.basePrice.toString(),
          sku: product.id,
          inventory_management: 'shopify',
          inventory_quantity: 100
        }
      ],
      images: product.images.map(url => ({ src: url })),
      metafields: [
        {
          namespace: 'pod_studio',
          key: 'blueprint_id',
          value: product.blueprintId.toString(),
          type: 'number_integer'
        }
      ]
    };
  }

  /**
   * Set up Shopify webhooks
   */
  private async setupWebhooks(integration: ShopifyIntegration): Promise<void> {
    const webhookTopics = [
      'orders/create',
      'products/update',
      'products/delete'
    ];

    integration.webhooks = webhookTopics;
  }

  /**
   * Handle Shopify webhook
   */
  async handleWebhook(
    topic: string,
    shopDomain: string,
    payload: any
  ): Promise<{ processed: boolean; action?: string }> {
    switch (topic) {
      case 'orders/create':
        return this.handleOrderCreate(payload);
      case 'products/update':
        return this.handleProductUpdate(payload);
      case 'products/delete':
        return this.handleProductDelete(payload);
      default:
        return { processed: false };
    }
  }

  private async handleOrderCreate(payload: any) {
    // Process order and trigger fulfillment
    return { processed: true, action: 'order_created' };
  }

  private async handleProductUpdate(payload: any) {
    // Sync product updates back to internal system
    return { processed: true, action: 'product_synced' };
  }

  private async handleProductDelete(payload: any) {
    // Handle product deletion
    return { processed: true, action: 'product_deleted' };
  }

  /**
   * Get integration status
   */
  getIntegrationStatus(tenantId: string): ShopifyIntegration | undefined {
    return this.integrations.get(tenantId);
  }

  /**
   * Disable integration
   */
  disableIntegration(tenantId: string): boolean {
    const integration = this.integrations.get(tenantId);
    if (!integration) return false;

    integration.syncEnabled = false;
    return true;
  }
}

/**
 * Gumroad Integration Service
 * Syncs products with Gumroad for digital/physical product sales
 */
export class GumroadService {
  private integrations: Map<string, GumroadIntegration> = new Map();

  /**
   * Set up Gumroad integration for a tenant
   */
  async setupIntegration(
    tenantId: string,
    apiKey: string
  ): Promise<GumroadIntegration> {
    const integration: GumroadIntegration = {
      tenantId,
      apiKey,
      products: [],
      autoSync: true
    };

    this.integrations.set(tenantId, integration);

    return integration;
  }

  /**
   * Sync product to Gumroad
   */
  async syncProductToGumroad(product: Product, tenantId: string): Promise<{
    success: boolean;
    gumroadProductId?: string;
    error?: string;
  }> {
    const integration = this.integrations.get(tenantId);
    if (!integration) {
      return { success: false, error: 'Integration not configured' };
    }

    try {
      const gumroadProduct = this.transformToGumroadProduct(product);

      // Simulate API call to Gumroad
      const gumroadProductId = `gum_${Math.random().toString(36).substr(2, 9)}`;

      integration.products.push(gumroadProductId);

      return { success: true, gumroadProductId };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  /**
   * Transform internal product to Gumroad format
   */
  private transformToGumroadProduct(product: Product) {
    return {
      name: product.name,
      description: product.description,
      price: Math.round(product.basePrice * 100), // Gumroad uses cents
      currency: 'USD',
      customizable_price: false,
      custom_permalink: this.generatePermalink(product.name),
      custom_summary: product.tags.join(', '),
      preview_url: product.images[0],
      file_info: {
        download_url: product.images[0] // Placeholder
      }
    };
  }

  /**
   * Generate URL-friendly permalink
   */
  private generatePermalink(name: string): string {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  /**
   * Get sales data from Gumroad
   */
  async getSalesData(tenantId: string, productId?: string): Promise<{
    sales: number;
    revenue: number;
    averagePrice: number;
  }> {
    const integration = this.integrations.get(tenantId);
    if (!integration) {
      return { sales: 0, revenue: 0, averagePrice: 0 };
    }

    // In production, fetch real data from Gumroad API
    return {
      sales: Math.floor(Math.random() * 100),
      revenue: Math.random() * 1000,
      averagePrice: 29.99
    };
  }

  /**
   * Get integration status
   */
  getIntegrationStatus(tenantId: string): GumroadIntegration | undefined {
    return this.integrations.get(tenantId);
  }

  /**
   * Disable auto-sync
   */
  disableAutoSync(tenantId: string): boolean {
    const integration = this.integrations.get(tenantId);
    if (!integration) return false;

    integration.autoSync = false;
    return true;
  }
}

/**
 * Unified Integration Manager
 * Manages all third-party integrations
 */
export class IntegrationManager {
  public shopify: ShopifyService;
  public gumroad: GumroadService;

  constructor() {
    this.shopify = new ShopifyService();
    this.gumroad = new GumroadService();
  }

  /**
   * Sync product to all enabled integrations
   */
  async syncToAllPlatforms(
    product: Product,
    tenantId: string
  ): Promise<{
    shopify?: { success: boolean; id?: string };
    gumroad?: { success: boolean; id?: string };
  }> {
    const results: any = {};

    const shopifyIntegration = this.shopify.getIntegrationStatus(tenantId);
    if (shopifyIntegration?.syncEnabled) {
      const result = await this.shopify.syncProductToShopify(product, tenantId);
      results.shopify = {
        success: result.success,
        id: result.shopifyProductId
      };
    }

    const gumroadIntegration = this.gumroad.getIntegrationStatus(tenantId);
    if (gumroadIntegration?.autoSync) {
      const result = await this.gumroad.syncProductToGumroad(product, tenantId);
      results.gumroad = {
        success: result.success,
        id: result.gumroadProductId
      };
    }

    return results;
  }

  /**
   * Get integration status for all platforms
   */
  getStatus(tenantId: string) {
    return {
      shopify: this.shopify.getIntegrationStatus(tenantId),
      gumroad: this.gumroad.getIntegrationStatus(tenantId)
    };
  }
}
