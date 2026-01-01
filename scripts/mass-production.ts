/**
 * Mass Production Script
 * Create multiple product types from a single design image
 */

import fs from 'fs/promises';
import path from 'path';

interface ProductConfig {
  name: string;
  blueprintId: number;
  printProviderId: number;
  price: number;
  tiktokReady: boolean;
}

interface MassProductionConfig {
  imageUrl: string;
  productTitle: string;
  description: string;
  tags: string[];
  products: number[]; // Blueprint IDs to create
}

export class MassProductionService {
  private apiKey: string;
  private shopId: string;
  private baseUrl = 'https://api.printify.com/v1';

  constructor(apiKey: string, shopId: string) {
    this.apiKey = apiKey;
    this.shopId = shopId;
  }

  /**
   * Upload image to Printify
   */
  async uploadImage(imageUrl: string, fileName: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/uploads/images.json`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_name: fileName,
        url: imageUrl
      })
    });

    const data = await response.json();
    return data.id;
  }

  /**
   * Create a single product variant
   */
  async createProduct(config: {
    blueprintId: number;
    printProviderId: number;
    title: string;
    description: string;
    imageId: string;
    price: number;
    tags: string[];
  }): Promise<any> {
    // Get print areas for this blueprint
    const printAreasResponse = await fetch(
      `${this.baseUrl}/catalog/blueprints/${config.blueprintId}/print_providers/${config.printProviderId}/variants.json`,
      {
        headers: { 'Authorization': `Bearer ${this.apiKey}` }
      }
    );
    const variantsData = await printAreasResponse.json();

    // Get first variant and print area
    const firstVariant = variantsData.variants[0];
    const printAreas = firstVariant.options;

    // Create product
    const productData = {
      title: config.title,
      description: config.description,
      blueprint_id: config.blueprintId,
      print_provider_id: config.printProviderId,
      variants: [
        {
          id: firstVariant.id,
          price: Math.round(config.price * 100), // Convert to cents
          is_enabled: true
        }
      ],
      print_areas: [
        {
          variant_ids: [firstVariant.id],
          placeholders: [
            {
              position: 'front',
              images: [
                {
                  id: config.imageId,
                  x: 0.5,
                  y: 0.5,
                  scale: 1,
                  angle: 0
                }
              ]
            }
          ]
        }
      ]
    };

    const response = await fetch(
      `${this.baseUrl}/shops/${this.shopId}/products.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(productData)
      }
    );

    return await response.json();
  }

  /**
   * Publish product to store
   */
  async publishProduct(productId: string): Promise<void> {
    await fetch(
      `${this.baseUrl}/shops/${this.shopId}/products/${productId}/publish.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
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
    );
  }

  /**
   * Mass produce multiple products from one design
   */
  async massProduceFromDesign(config: MassProductionConfig): Promise<{
    success: boolean;
    products: any[];
    errors: string[];
  }> {
    const results = {
      success: true,
      products: [] as any[],
      errors: [] as string[]
    };

    try {
      console.log('📤 Uploading design image...');
      const imageId = await this.uploadImage(
        config.imageUrl,
        `${config.productTitle}-design.png`
      );
      console.log(`✅ Image uploaded: ${imageId}`);

      // Load product configurations
      const productConfigPath = path.join(__dirname, '../tiktok-products-config.json');
      const productConfigData = await fs.readFile(productConfigPath, 'utf-8');
      const productConfig = JSON.parse(productConfigData);

      const productsToCreate = productConfig.tiktokReadyProducts.filter((p: ProductConfig) =>
        config.products.includes(p.blueprintId)
      );

      console.log(`\n🏭 Creating ${productsToCreate.length} product variants...\n`);

      for (const product of productsToCreate) {
        try {
          console.log(`Creating ${product.name}...`);

          const createdProduct = await this.createProduct({
            blueprintId: product.blueprintId,
            printProviderId: product.printProviderId,
            title: `${config.productTitle} - ${product.name}`,
            description: config.description,
            imageId: imageId,
            price: product.price,
            tags: config.tags
          });

          console.log(`✅ ${product.name} created (ID: ${createdProduct.id})`);

          // Publish to store
          console.log(`Publishing ${product.name}...`);
          await this.publishProduct(createdProduct.id);
          console.log(`✅ ${product.name} published`);

          results.products.push({
            ...createdProduct,
            productType: product.name
          });

          // Wait 2 seconds between products to avoid rate limiting
          await new Promise(resolve => setTimeout(resolve, 2000));

        } catch (error) {
          const errorMsg = `Failed to create ${product.name}: ${error}`;
          console.error(`❌ ${errorMsg}`);
          results.errors.push(errorMsg);
          results.success = false;
        }
      }

      console.log(`\n✅ Mass production complete!`);
      console.log(`   Products created: ${results.products.length}`);
      console.log(`   Errors: ${results.errors.length}`);

    } catch (error) {
      results.success = false;
      results.errors.push(`Mass production failed: ${error}`);
      console.error('❌ Mass production failed:', error);
    }

    return results;
  }
}

// CLI Usage
if (require.main === module) {
  const apiKey = process.env.PRINTIFY_API_KEY;
  const shopId = process.env.PRINTIFY_SHOP_ID;

  if (!apiKey || !shopId) {
    console.error('❌ Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID');
    process.exit(1);
  }

  const service = new MassProductionService(apiKey, shopId);

  // Example: Create TikTok Starter Bundle
  service.massProduceFromDesign({
    imageUrl: 'https://example.com/design.png', // Replace with actual URL
    productTitle: 'Urban Vibes Collection',
    description: 'Premium streetwear design featuring bold graphics and modern aesthetics',
    tags: ['streetwear', 'urban', 'fashion', 'trending', 'tiktok'],
    products: [6, 77, 49, 68, 22] // T-Shirt, Hoodie, Sweatshirt, Mug, Tote
  }).then(result => {
    console.log('\n📊 Final Results:', result);
    process.exit(result.success ? 0 : 1);
  });
}
