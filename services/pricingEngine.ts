import { PriceBucket, ConversionEvent, Region, Product } from '../types';

/**
 * Price Lock-In Engine
 * Tracks conversion rates per price bucket and auto-disables losing prices
 */
export class PricingEngine {
  private priceBuckets: Map<string, PriceBucket> = new Map();
  private conversionEvents: ConversionEvent[] = [];

  // Configuration
  private readonly MIN_IMPRESSIONS_THRESHOLD = 100; // Min impressions before disabling
  private readonly MIN_CONVERSION_RATE = 0.02; // 2% minimum conversion rate
  private readonly EVALUATION_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours

  /**
   * Create price buckets for A/B testing
   */
  createPriceBuckets(
    productId: string,
    basePrices: number[],
    regions: Region[]
  ): PriceBucket[] {
    const buckets: PriceBucket[] = [];

    for (const region of regions) {
      for (const price of basePrices) {
        const bucket: PriceBucket = {
          id: this.generateId(),
          productId,
          price,
          region,
          conversions: 0,
          impressions: 0,
          revenue: 0,
          conversionRate: 0,
          isActive: true,
          createdAt: new Date().toISOString(),
          lastUpdated: new Date().toISOString()
        };

        buckets.push(bucket);
        this.priceBuckets.set(bucket.id, bucket);
      }
    }

    return buckets;
  }

  /**
   * Track impression (product view)
   */
  trackImpression(priceBucketId: string): void {
    const bucket = this.priceBuckets.get(priceBucketId);
    if (!bucket || !bucket.isActive) return;

    bucket.impressions++;
    bucket.lastUpdated = new Date().toISOString();
  }

  /**
   * Track conversion (purchase)
   */
  trackConversion(
    productId: string,
    priceBucketId: string,
    price: number,
    region: Region,
    source: string
  ): ConversionEvent {
    const bucket = this.priceBuckets.get(priceBucketId);

    if (bucket) {
      bucket.conversions++;
      bucket.revenue += price;
      bucket.conversionRate = bucket.conversions / bucket.impressions;
      bucket.lastUpdated = new Date().toISOString();
    }

    const event: ConversionEvent = {
      id: this.generateId(),
      productId,
      priceBucketId,
      price,
      region,
      source,
      timestamp: new Date().toISOString()
    };

    this.conversionEvents.push(event);
    return event;
  }

  /**
   * Evaluate all price buckets and disable losing ones
   */
  evaluateAndDisableLosers(): {
    disabled: PriceBucket[];
    winners: PriceBucket[];
  } {
    const disabled: PriceBucket[] = [];
    const winners: PriceBucket[] = [];

    // Group buckets by product and region
    const groupedBuckets = this.groupBucketsByProductAndRegion();

    for (const [key, buckets] of groupedBuckets.entries()) {
      const eligibleBuckets = buckets.filter(
        b => b.impressions >= this.MIN_IMPRESSIONS_THRESHOLD
      );

      if (eligibleBuckets.length === 0) continue;

      // Find best performing bucket
      const bestBucket = eligibleBuckets.reduce((best, current) =>
        current.conversionRate > best.conversionRate ? current : best
      );

      // Disable underperforming buckets
      for (const bucket of eligibleBuckets) {
        if (bucket.id === bestBucket.id) {
          winners.push(bucket);
          continue;
        }

        // Disable if conversion rate is significantly lower than best
        const performanceRatio = bucket.conversionRate / bestBucket.conversionRate;

        if (
          bucket.conversionRate < this.MIN_CONVERSION_RATE ||
          performanceRatio < 0.5 // Less than 50% of best performer
        ) {
          bucket.isActive = false;
          bucket.lastUpdated = new Date().toISOString();
          disabled.push(bucket);
        }
      }
    }

    return { disabled, winners };
  }

  /**
   * Get winning price for a product in a region
   */
  getWinningPrice(productId: string, region: Region): number | null {
    const buckets = Array.from(this.priceBuckets.values()).filter(
      b => b.productId === productId && b.region === region && b.isActive
    );

    if (buckets.length === 0) return null;

    // Return price of best performing active bucket
    const bestBucket = buckets.reduce((best, current) =>
      current.conversionRate > best.conversionRate ? current : best
    );

    return bestBucket.price;
  }

  /**
   * Get analytics for a product
   */
  getProductAnalytics(productId: string): {
    totalRevenue: number;
    totalConversions: number;
    totalImpressions: number;
    overallConversionRate: number;
    byRegion: Record<Region, {
      revenue: number;
      conversions: number;
      impressions: number;
      conversionRate: number;
      winningPrice: number | null;
    }>;
  } {
    const buckets = Array.from(this.priceBuckets.values()).filter(
      b => b.productId === productId
    );

    const totalRevenue = buckets.reduce((sum, b) => sum + b.revenue, 0);
    const totalConversions = buckets.reduce((sum, b) => sum + b.conversions, 0);
    const totalImpressions = buckets.reduce((sum, b) => sum + b.impressions, 0);

    const byRegion = {} as any;

    for (const region of [Region.US, Region.EU, Region.UK]) {
      const regionBuckets = buckets.filter(b => b.region === region);
      const revenue = regionBuckets.reduce((sum, b) => sum + b.revenue, 0);
      const conversions = regionBuckets.reduce((sum, b) => sum + b.conversions, 0);
      const impressions = regionBuckets.reduce((sum, b) => sum + b.impressions, 0);

      byRegion[region] = {
        revenue,
        conversions,
        impressions,
        conversionRate: impressions > 0 ? conversions / impressions : 0,
        winningPrice: this.getWinningPrice(productId, region)
      };
    }

    return {
      totalRevenue,
      totalConversions,
      totalImpressions,
      overallConversionRate: totalImpressions > 0 ? totalConversions / totalImpressions : 0,
      byRegion
    };
  }

  /**
   * Lock in winning prices for a product
   */
  lockInWinningPrices(productId: string): Record<Region, number> {
    const lockedPrices = {} as Record<Region, number>;

    for (const region of [Region.US, Region.EU, Region.UK]) {
      const winningPrice = this.getWinningPrice(productId, region);
      if (winningPrice) {
        lockedPrices[region] = winningPrice;

        // Disable all other buckets for this product/region
        const buckets = Array.from(this.priceBuckets.values()).filter(
          b => b.productId === productId && b.region === region
        );

        for (const bucket of buckets) {
          if (bucket.price !== winningPrice) {
            bucket.isActive = false;
          }
        }
      }
    }

    return lockedPrices;
  }

  /**
   * Group buckets by product and region for comparison
   */
  private groupBucketsByProductAndRegion(): Map<string, PriceBucket[]> {
    const grouped = new Map<string, PriceBucket[]>();

    for (const bucket of this.priceBuckets.values()) {
      const key = `${bucket.productId}-${bucket.region}`;
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key)!.push(bucket);
    }

    return grouped;
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  /**
   * Get all active price buckets
   */
  getActiveBuckets(): PriceBucket[] {
    return Array.from(this.priceBuckets.values()).filter(b => b.isActive);
  }

  /**
   * Get conversion events for analysis
   */
  getConversionEvents(productId?: string, startDate?: Date, endDate?: Date): ConversionEvent[] {
    let events = this.conversionEvents;

    if (productId) {
      events = events.filter(e => e.productId === productId);
    }

    if (startDate) {
      events = events.filter(e => new Date(e.timestamp) >= startDate);
    }

    if (endDate) {
      events = events.filter(e => new Date(e.timestamp) <= endDate);
    }

    return events;
  }
}
