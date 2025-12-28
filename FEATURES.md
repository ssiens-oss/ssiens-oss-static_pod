# StaticWaves POD Studio - New Features

Complete implementation of advanced POD automation features for TikTok product linking, dynamic pricing, multi-region feeds, and white-label SaaS.

## 🎯 Features Overview

### 1. Content → Product Auto-Linker

Automatically link TikTok videos to products using AI-powered metadata analysis.

#### Key Capabilities

- **Video Metadata Extraction**: Analyzes captions, hashtags, audio, and mentions
- **Smart Product Matching**: Uses confidence scoring (0-1) to match videos with products
- **Auto-Tag Generation**: Generates relevant tags from video metadata
- **Engagement Analysis**: Factors in views, likes, and engagement rates

#### Usage Example

```typescript
import { ProductLinker } from './services/productLinker';

const linker = new ProductLinker(products);

// Link video to products
const links = await linker.linkVideoToProducts(video);

// Auto-generate tags from video
const tags = ProductLinker.autoGenerateTags(video);
```

#### Confidence Scoring

- **> 0.7**: High confidence match (strong tag/keyword overlap)
- **0.5-0.7**: Medium confidence (moderate overlap)
- **0.3-0.5**: Low confidence (weak but potential match)
- **< 0.3**: Not linked (insufficient relevance)

---

### 2. Winning Price Lock-In Logic

A/B test multiple price points and automatically disable underperforming prices.

#### Key Capabilities

- **Price Bucket Testing**: Test multiple prices simultaneously per region
- **Conversion Tracking**: Track impressions, conversions, and revenue
- **Auto-Disable Losers**: Automatically disable prices below threshold
- **Analytics Dashboard**: Comprehensive performance metrics by region

#### Usage Example

```typescript
import { PricingEngine } from './services/pricingEngine';

const engine = new PricingEngine();

// Create price buckets for A/B testing
const buckets = engine.createPriceBuckets(
  productId,
  [24.99, 29.99, 34.99], // Test prices
  [Region.US, Region.EU, Region.UK]
);

// Track impressions
engine.trackImpression(bucketId);

// Track conversions
engine.trackConversion(productId, bucketId, price, region, 'tiktok');

// Evaluate and disable losing prices
const { disabled, winners } = engine.evaluateAndDisableLosers();

// Lock in winning prices
const lockedPrices = engine.lockInWinningPrices(productId);
```

#### Evaluation Criteria

- **Minimum Impressions**: 100 (configurable)
- **Minimum Conversion Rate**: 2% (configurable)
- **Relative Performance**: Must be within 50% of best performer
- **Evaluation Window**: 24 hours (configurable)

---

### 3. Multi-Region Feeds

Generate product feeds for US, EU, and UK markets simultaneously with region-specific pricing.

#### Key Capabilities

- **Simultaneous Generation**: Create all regional feeds at once
- **Regional Pricing**: Automatic currency conversion with adjustments
- **Multiple Formats**: JSON, XML (Google Shopping), CSV
- **VAT/Tax Support**: Optional VAT and regional tax calculations

#### Usage Example

```typescript
import { FeedGenerator } from './services/feedGenerator';

const generator = new FeedGenerator();

// Generate all regional feeds
const feeds = await generator.generateAllRegionFeeds(products, 'json');

// Generate specific region feed
const usFeed = await generator.generateRegionalFeed(
  products,
  Region.US,
  'xml'
);

// Export to different formats
const jsonExport = generator.exportToJSON(feed);
const xmlExport = generator.exportToXML(feed);
const csvExport = generator.exportToCSV(feed);

// Calculate regional pricing
const pricing = generator.calculateRegionalPricing(29.99, Region.US);
// { US: 29.99, EU: 27.59, UK: 23.69 }
```

#### Regional Pricing

- **US → EU**: 0.92 exchange rate
- **US → UK**: 0.79 exchange rate
- **VAT Options**: 0% (US), 20% (EU/UK)
- **Custom Margins**: Configurable per region

#### Feed Formats

**JSON**: Structured data for APIs and applications
```json
{
  "metadata": {
    "region": "US",
    "currency": "USD",
    "productCount": 10
  },
  "products": [...]
}
```

**XML**: Google Shopping compatible RSS feed
```xml
<rss version="2.0">
  <channel>
    <item>
      <g:id>prod_001</g:id>
      <g:price>29.99 USD</g:price>
      ...
    </item>
  </channel>
</rss>
```

**CSV**: Spreadsheet-compatible format
```csv
id,name,description,price,currency,tags,images
prod_001,"T-Shirt","Description",29.99,USD,"tag1;tag2","img1;img2"
```

---

### 4. White-Label SaaS Package

Multi-tenant architecture with Shopify and Gumroad integration.

#### Key Capabilities

- **Multi-Tenant Support**: Isolated tenant data and settings
- **Plan-Based Features**: Free, Starter, Pro, Enterprise tiers
- **API Key Management**: Secure tenant authentication
- **Custom Branding**: Logo, colors, company name
- **Integration Hub**: Shopify, Gumroad, TikTok, Printify

#### Usage Example

```typescript
import { TenantManager } from './services/tenantManager';
import { IntegrationManager } from './services/integrations';

const tenantManager = new TenantManager();

// Create tenant
const tenant = tenantManager.createTenant(
  'Acme Merch',
  'owner@acme.com',
  'pro'
);

// Validate feature access
const canUsePriceLockIn = tenantManager.validateAction(
  tenant.id,
  'use_price_lock_in'
);

// Upgrade plan
tenantManager.upgradePlan(tenant.id, 'enterprise');

// Set up integrations
const integrations = new IntegrationManager();

await integrations.shopify.setupIntegration(
  tenant.id,
  'acme.myshopify.com',
  'access_token'
);

// Sync product to all platforms
await integrations.syncToAllPlatforms(product, tenant.id);
```

#### Plan Features

| Feature | Free | Starter | Pro | Enterprise |
|---------|------|---------|-----|------------|
| Max Products | 10 | 100 | 1000 | Unlimited |
| Auto-Linking | ❌ | ✅ | ✅ | ✅ |
| Price Lock-In | ❌ | ❌ | ✅ | ✅ |
| Multi-Region | ❌ | ❌ | ✅ | ✅ |
| Integrations | ❌ | Basic | Advanced | Custom |
| Support | Email | Email | Priority | Dedicated |
| Price/month | $0 | $29 | $99 | $299 |

#### Integration Support

**Shopify**
- Product sync (create/update/delete)
- Order webhooks
- Inventory management
- Multi-variant support

**Gumroad**
- Digital product sync
- Sales tracking
- License key management
- Analytics integration

**TikTok**
- Video metadata fetching
- Auto-linking integration
- Performance tracking

**Printify**
- Design upload
- Product creation
- Order fulfillment
- Blueprint management

---

## 🚀 Getting Started

### Installation

```bash
npm install
```

### Run Demo

```bash
npm run demo
```

The demo script showcases all features with mock data:
- Product auto-linking with TikTok videos
- Price bucket A/B testing
- Multi-region feed generation
- Tenant management and integrations

### Integration with Existing App

```typescript
// In your App.tsx or main component
import { ProductLinkerPanel } from './components/ProductLinker';
import { PriceAnalyticsPanel } from './components/PriceAnalytics';
import { FeedManagerPanel } from './components/FeedManager';
import { TenantSettingsPanel } from './components/TenantSettings';

// Use components in your UI
<ProductLinkerPanel
  videos={videos}
  products={products}
  onLinkCreated={handleLinkCreated}
/>

<PriceAnalyticsPanel
  buckets={priceBuckets}
  productId={productId}
  onLockPrice={handleLockPrice}
/>

<FeedManagerPanel
  products={products}
  onGenerateFeed={handleGenerateFeed}
/>

<TenantSettingsPanel
  tenant={currentTenant}
  onUpdateSettings={handleUpdateSettings}
  onUpgradePlan={handleUpgradePlan}
/>
```

---

## 📊 Architecture

### Service Layer

```
services/
├── productLinker.ts      # TikTok → Product linking
├── pricingEngine.ts      # Price A/B testing & lock-in
├── feedGenerator.ts      # Multi-region feed generation
├── tenantManager.ts      # Multi-tenant management
└── integrations.ts       # Shopify/Gumroad sync
```

### Component Layer

```
components/
├── ProductLinker.tsx     # Product linking UI
├── PriceAnalytics.tsx    # Price analytics dashboard
├── FeedManager.tsx       # Feed generation UI
└── TenantSettings.tsx    # Tenant settings panel
```

### Type Definitions

All types are defined in `types.ts`:
- `TikTokVideo`, `VideoMetadata`, `ProductLink`
- `PriceBucket`, `ConversionEvent`
- `RegionalFeed`, `RegionalPricing`
- `Tenant`, `TenantSettings`
- `ShopifyIntegration`, `GumroadIntegration`

---

## 🔧 Configuration

### Price Lock-In Thresholds

```typescript
// In pricingEngine.ts
private readonly MIN_IMPRESSIONS_THRESHOLD = 100;
private readonly MIN_CONVERSION_RATE = 0.02;
private readonly EVALUATION_INTERVAL = 24 * 60 * 60 * 1000;
```

### Exchange Rates

```typescript
// In feedGenerator.ts
private readonly EXCHANGE_RATES = {
  USD_TO_EUR: 0.92,
  USD_TO_GBP: 0.79,
  // ...
};
```

### Product Linking Confidence

```typescript
// In productLinker.ts
if (confidence > 0.3) { // Adjust threshold
  // Create link
}
```

---

## 📈 Analytics & Metrics

### Price Performance Metrics

- **Conversion Rate**: Conversions / Impressions
- **Revenue**: Total sales for each price bucket
- **Performance Ratio**: Bucket conversion rate / Best conversion rate
- **Statistical Significance**: Based on minimum impression threshold

### Product Linking Metrics

- **Confidence Score**: 0-1 scale for match quality
- **Tag Overlap**: Number of matching tags/keywords
- **Engagement Correlation**: Video performance vs. product performance

### Feed Metrics

- **Product Count**: Number of products per region
- **Pricing Variance**: Price differences across regions
- **Currency Exposure**: Revenue by currency
- **Format Distribution**: Usage of JSON/XML/CSV exports

---

## 🔐 Security

- **API Key Management**: Secure tenant API keys
- **Rate Limiting**: Per-tenant request limits
- **Data Isolation**: Tenant data separation
- **Webhook Validation**: HMAC signature verification
- **Token Encryption**: Encrypted integration tokens

---

## 🧪 Testing

Run the comprehensive demo:

```bash
npm run demo
```

Test individual features:

```typescript
import { demoProductLinking } from './demo';
await demoProductLinking();
```

---

## 📝 API Reference

### ProductLinker

- `linkVideoToProducts(video)` - Generate product links
- `autoGenerateTags(video)` - Extract tags from video

### PricingEngine

- `createPriceBuckets(productId, prices, regions)` - Create test buckets
- `trackImpression(bucketId)` - Record view
- `trackConversion(productId, bucketId, price, region, source)` - Record sale
- `evaluateAndDisableLosers()` - Disable underperformers
- `lockInWinningPrices(productId)` - Lock winning prices

### FeedGenerator

- `generateAllRegionFeeds(products, format)` - Generate all feeds
- `generateRegionalFeed(products, region, format)` - Generate single feed
- `exportToJSON/XML/CSV(feed)` - Export in format

### TenantManager

- `createTenant(name, owner, plan)` - Create tenant
- `getTenantByApiKey(apiKey)` - Authenticate
- `validateAction(tenantId, action)` - Check permissions
- `upgradePlan(tenantId, plan)` - Change plan

---

## 🎨 UI Components

All components use Tailwind CSS with dark theme (slate-900 palette).

**Responsive Design**: Mobile-first, responsive grid layouts
**Icons**: Lucide React icon library
**State Management**: React hooks (useState, useCallback)
**Type Safety**: Full TypeScript support

---

## 🚢 Deployment

### Environment Variables

```env
PRINTIFY_API_KEY=your_key
SHOPIFY_APP_SECRET=your_secret
GUMROAD_API_KEY=your_key
TIKTOK_CLIENT_ID=your_id
DATABASE_URL=your_db_url
```

### Production Considerations

- Use real database (PostgreSQL/MongoDB)
- Implement caching (Redis)
- Set up job queues for feed generation
- Monitor conversion tracking accuracy
- Regular price evaluation cron jobs

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please follow:
- TypeScript best practices
- Existing code style
- Add tests for new features
- Update documentation

---

Built with ❤️ by StaticWaves Team
