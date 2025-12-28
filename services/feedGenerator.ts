import { Product, Region, RegionalFeed } from '../types';

/**
 * Multi-Region Feed Generator
 * Generates product feeds for different regions with localized pricing
 */
export class FeedGenerator {
  private readonly CURRENCY_MAP = {
    [Region.US]: 'USD',
    [Region.EU]: 'EUR',
    [Region.UK]: 'GBP'
  };

  // Exchange rates (in production, these should be fetched from an API)
  private readonly EXCHANGE_RATES = {
    USD_TO_EUR: 0.92,
    USD_TO_GBP: 0.79,
    EUR_TO_USD: 1.09,
    EUR_TO_GBP: 0.86,
    GBP_TO_USD: 1.27,
    GBP_TO_EUR: 1.16
  };

  /**
   * Generate feeds for all regions simultaneously
   */
  async generateAllRegionFeeds(
    products: Product[],
    format: 'xml' | 'json' | 'csv' = 'json'
  ): Promise<RegionalFeed[]> {
    const regions = [Region.US, Region.EU, Region.UK];
    const feeds: RegionalFeed[] = [];

    for (const region of regions) {
      const feed = await this.generateRegionalFeed(products, region, format);
      feeds.push(feed);
    }

    return feeds;
  }

  /**
   * Generate feed for a specific region
   */
  async generateRegionalFeed(
    products: Product[],
    region: Region,
    format: 'xml' | 'json' | 'csv' = 'json'
  ): Promise<RegionalFeed> {
    const regionalProducts = products.map(product => ({
      ...product,
      price: this.getRegionalPrice(product, region)
    }));

    return {
      region,
      products: regionalProducts,
      currency: this.CURRENCY_MAP[region],
      generatedAt: new Date().toISOString(),
      format
    };
  }

  /**
   * Get regional price for a product
   */
  getRegionalPrice(product: Product, region: Region): number {
    return product.regionalPricing[region] || product.basePrice;
  }

  /**
   * Calculate regional pricing from base price
   */
  calculateRegionalPricing(basePrice: number, baseRegion: Region = Region.US): {
    US: number;
    EU: number;
    UK: number;
  } {
    const pricing = {
      [Region.US]: basePrice,
      [Region.EU]: basePrice,
      [Region.UK]: basePrice
    };

    if (baseRegion === Region.US) {
      pricing[Region.EU] = this.roundPrice(basePrice * this.EXCHANGE_RATES.USD_TO_EUR);
      pricing[Region.UK] = this.roundPrice(basePrice * this.EXCHANGE_RATES.USD_TO_GBP);
    } else if (baseRegion === Region.EU) {
      pricing[Region.US] = this.roundPrice(basePrice * this.EXCHANGE_RATES.EUR_TO_USD);
      pricing[Region.UK] = this.roundPrice(basePrice * this.EXCHANGE_RATES.EUR_TO_GBP);
    } else if (baseRegion === Region.UK) {
      pricing[Region.US] = this.roundPrice(basePrice * this.EXCHANGE_RATES.GBP_TO_USD);
      pricing[Region.EU] = this.roundPrice(basePrice * this.EXCHANGE_RATES.GBP_TO_EUR);
    }

    return pricing;
  }

  /**
   * Export feed to JSON format
   */
  exportToJSON(feed: RegionalFeed): string {
    const output = {
      metadata: {
        region: feed.region,
        currency: feed.currency,
        generatedAt: feed.generatedAt,
        productCount: feed.products.length
      },
      products: feed.products.map(p => ({
        id: p.id,
        name: p.name,
        description: p.description,
        price: this.getRegionalPrice(p, feed.region),
        currency: feed.currency,
        tags: p.tags,
        images: p.images,
        blueprintId: p.blueprintId
      }))
    };

    return JSON.stringify(output, null, 2);
  }

  /**
   * Export feed to XML format (Google Shopping compatible)
   */
  exportToXML(feed: RegionalFeed): string {
    const currency = feed.currency;

    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n';
    xml += '  <channel>\n';
    xml += `    <title>Product Feed - ${feed.region}</title>\n`;
    xml += `    <link>https://example.com/feed/${feed.region.toLowerCase()}</link>\n`;
    xml += `    <description>Regional product feed for ${feed.region}</description>\n`;

    for (const product of feed.products) {
      const price = this.getRegionalPrice(product, feed.region);

      xml += '    <item>\n';
      xml += `      <g:id>${product.id}</g:id>\n`;
      xml += `      <g:title><![CDATA[${product.name}]]></g:title>\n`;
      xml += `      <g:description><![CDATA[${product.description}]]></g:description>\n`;
      xml += `      <g:price>${price.toFixed(2)} ${currency}</g:price>\n`;
      xml += `      <g:availability>in stock</g:availability>\n`;
      xml += `      <g:condition>new</g:condition>\n`;

      if (product.images.length > 0) {
        xml += `      <g:image_link>${product.images[0]}</g:image_link>\n`;
        product.images.slice(1, 10).forEach(img => {
          xml += `      <g:additional_image_link>${img}</g:additional_image_link>\n`;
        });
      }

      if (product.tags.length > 0) {
        xml += `      <g:product_type>${product.tags.join(' > ')}</g:product_type>\n`;
      }

      xml += '    </item>\n';
    }

    xml += '  </channel>\n';
    xml += '</rss>';

    return xml;
  }

  /**
   * Export feed to CSV format
   */
  exportToCSV(feed: RegionalFeed): string {
    const headers = ['id', 'name', 'description', 'price', 'currency', 'tags', 'images'];
    let csv = headers.join(',') + '\n';

    for (const product of feed.products) {
      const price = this.getRegionalPrice(product, feed.region);
      const row = [
        product.id,
        `"${product.name.replace(/"/g, '""')}"`,
        `"${product.description.replace(/"/g, '""')}"`,
        price.toFixed(2),
        feed.currency,
        `"${product.tags.join(';')}"`,
        `"${product.images.join(';')}"`
      ];
      csv += row.join(',') + '\n';
    }

    return csv;
  }

  /**
   * Export feed in the specified format
   */
  exportFeed(feed: RegionalFeed): string {
    switch (feed.format) {
      case 'xml':
        return this.exportToXML(feed);
      case 'csv':
        return this.exportToCSV(feed);
      case 'json':
      default:
        return this.exportToJSON(feed);
    }
  }

  /**
   * Generate and export all regional feeds
   */
  async generateAndExportAllFeeds(
    products: Product[],
    format: 'xml' | 'json' | 'csv' = 'json'
  ): Promise<Record<Region, string>> {
    const feeds = await this.generateAllRegionFeeds(products, format);
    const exports: Record<Region, string> = {} as any;

    for (const feed of feeds) {
      exports[feed.region] = this.exportFeed(feed);
    }

    return exports;
  }

  /**
   * Apply regional pricing adjustments
   * Can include VAT, shipping costs, local taxes, etc.
   */
  applyRegionalAdjustments(
    basePrice: number,
    region: Region,
    options: {
      includeVAT?: boolean;
      includeShipping?: boolean;
      customMargin?: number;
    } = {}
  ): number {
    let price = basePrice;

    // Apply currency conversion
    const regionalPricing = this.calculateRegionalPricing(basePrice);
    price = regionalPricing[region];

    // Apply VAT if applicable
    if (options.includeVAT) {
      const vatRates = {
        [Region.US]: 0, // No federal VAT
        [Region.EU]: 0.20, // Average EU VAT 20%
        [Region.UK]: 0.20 // UK VAT 20%
      };
      price *= (1 + vatRates[region]);
    }

    // Apply custom margin
    if (options.customMargin) {
      price *= (1 + options.customMargin);
    }

    return this.roundPrice(price);
  }

  /**
   * Round price to 2 decimal places
   */
  private roundPrice(price: number): number {
    return Math.round(price * 100) / 100;
  }
}
