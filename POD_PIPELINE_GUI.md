# POD Pipeline GUI - Multi-Platform Studio

Complete web-based interface for automating print-on-demand (POD) product creation and distribution across multiple platforms.

## Features

### 🎨 AI-Powered Design Generation
- **Claude Integration**: Generate creative prompts automatically
- **ComfyUI Integration**: Create high-quality AI images
- **Customizable Styles**: Minimalist, Abstract, Geometric, Watercolor, Vintage, Modern
- **Niche Targeting**: Specify themes like Nature, Gaming, Abstract Art, etc.

### 🛍️ Multi-Platform Distribution
Automatically publish products to:
- **Printify** - Print-on-demand fulfillment
- **Shopify** - E-commerce store
- **TikTok Shop** - Social commerce
- **Etsy** - Handmade marketplace
- **Instagram Shopping** - Visual commerce
- **Facebook Shop** - Social selling

### 📦 Product Management
- **T-Shirts & Hoodies**: Create multiple product types
- **Custom Pricing**: Set individual prices for each product type
- **Auto-Publish**: Automatically publish to enabled platforms
- **Batch Processing**: Generate multiple designs in one run

### 📊 Analytics Dashboard
- Real-time statistics
- Platform breakdown
- Success rate tracking
- Design and product counts

## Quick Start

### 1. Start the POD Pipeline GUI

```bash
./start-pod-pipeline.sh
```

Or manually:

```bash
npm run dev:pod
```

The GUI will be available at: **http://localhost:5174**

### 2. Configure Your Pipeline

#### Configuration Tab
1. **Prompt Generation**
   - Enter a theme/niche (e.g., "Abstract Art", "Nature Photography")
   - Select an art style
   - Optionally provide a custom prompt

2. **Product Settings**
   - Select product types (T-Shirt, Hoodie, or both)
   - Set design count (1-50)
   - Enable/disable auto-publish
   - Set pricing for each product type

#### Platforms Tab
3. **Enable Distribution Platforms**
   - Click on each platform to enable/disable
   - Enabled platforms show with a green checkmark
   - Products will be published to all enabled platforms

### 3. Run the Pipeline

Click **"Start POD Pipeline"** to begin automation:

1. **Prompt Generation** - Claude generates creative prompts
2. **Image Generation** - ComfyUI creates AI designs
3. **Storage** - Images saved to local/cloud storage
4. **Product Creation** - Products created on all enabled platforms
5. **Publishing** - Products automatically published (if enabled)

### 4. Monitor Progress

- **Live Preview**: See generated designs in real-time
- **Terminal Logs**: Track pipeline execution
- **Progress Bar**: Visual progress indicator
- **Product Table**: View all published products

### 5. View Analytics

Switch to the **Stats** tab to see:
- Total designs generated
- Total products created
- Success rate
- Platform breakdown

## Configuration

### Environment Variables

Create a `.env` file with your API keys:

```bash
# ComfyUI
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/path/to/comfyui/output

# Claude
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Printify
PRINTIFY_API_KEY=...
PRINTIFY_SHOP_ID=...

# Shopify
SHOPIFY_STORE_URL=mystore.myshopify.com
SHOPIFY_ACCESS_TOKEN=...
SHOPIFY_API_VERSION=2024-01

# TikTok Shop
TIKTOK_APP_KEY=...
TIKTOK_APP_SECRET=...
TIKTOK_SHOP_ID=...
TIKTOK_ACCESS_TOKEN=...

# Etsy
ETSY_API_KEY=...
ETSY_SHOP_ID=...
ETSY_OAUTH_TOKEN=...

# Instagram
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_BUSINESS_ACCOUNT_ID=...

# Facebook
FACEBOOK_PAGE_ID=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_CATALOG_ID=...
```

### Platform Setup

#### Printify
1. Create account at [printify.com](https://printify.com)
2. Generate API key in Settings → API
3. Get your Shop ID from the URL

#### Shopify
1. Create Shopify store
2. Install Printify app
3. Generate Admin API access token
4. Enable product publishing

#### TikTok Shop
1. Register at [TikTok Shop Seller Center](https://seller.tiktok.com)
2. Create app in Developer Portal
3. Get App Key, Secret, and Access Token
4. Enable product API permissions

#### Etsy
1. Create Etsy shop
2. Register app at [etsy.com/developers](https://www.etsy.com/developers)
3. Get API key and OAuth token
4. Enable shop management permissions

#### Instagram Shopping
1. Convert to Instagram Business account
2. Connect to Facebook Page
3. Set up Instagram Shopping
4. Get access token from Meta Business Suite

#### Facebook Shop
1. Create Facebook Page
2. Set up Facebook Shop
3. Create Commerce account
4. Get Page ID, Catalog ID, and access token

## Usage Examples

### Example 1: Abstract Art Collection

**Configuration:**
- Theme: "Abstract Geometric Patterns"
- Style: Geometric
- Product Types: T-Shirt, Hoodie
- Design Count: 10
- Platforms: Printify, Shopify, Etsy

**Result:** 20 products (10 designs × 2 types) published to 3 platforms = 60 total listings

### Example 2: Nature Photography Series

**Configuration:**
- Theme: "Minimalist Mountain Landscapes"
- Style: Minimalist
- Product Types: T-Shirt
- Design Count: 5
- Platforms: All platforms enabled

**Result:** 5 products published to 6 platforms = 30 total listings

### Example 3: Custom Prompt

**Configuration:**
- Custom Prompt: "Cyberpunk cityscape with neon lights, synthwave aesthetic, 4k quality"
- Style: Modern
- Product Types: T-Shirt, Hoodie
- Design Count: 3
- Platforms: TikTok, Instagram, Facebook

**Result:** 6 products (3 designs × 2 types) published to 3 platforms = 18 total listings

## Development Mode

The GUI includes a **simulation mode** for development and testing:

- Runs when backend API is not available
- Generates mock images and products
- Simulates pipeline execution timing
- Perfect for frontend development

To connect to real backend:
- Ensure backend services are running
- API should be available at `/api`
- Backend will be automatically detected

## Architecture

```
┌─────────────────────────────────────────────────┐
│           POD Pipeline GUI (React)              │
│  ┌──────────────┬──────────────┬─────────────┐ │
│  │    Config    │  Platforms   │  Analytics  │ │
│  └──────────────┴──────────────┴─────────────┘ │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Orchestrator Client (Frontend)           │
│     - API Communication                          │
│     - Simulation Mode                            │
│     - Progress Tracking                          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         Backend Orchestrator (Node.js)          │
│  ┌──────────┬──────────┬────────┬─────────────┐│
│  │ ComfyUI  │  Claude  │ Storage│  Platforms  ││
│  └──────────┴──────────┴────────┴─────────────┘│
└─────────────────────────────────────────────────┘
```

## Troubleshooting

### Issue: Pipeline stuck at "Generating images"
- Check ComfyUI is running at configured URL
- Verify ComfyUI has required models installed
- Check ComfyUI logs for errors

### Issue: Platform publishing fails
- Verify API keys in `.env` file
- Check platform API rate limits
- Ensure platform accounts are properly configured
- Review terminal logs for specific errors

### Issue: Images not appearing
- Check storage configuration
- Verify image URLs are accessible
- Check browser console for CORS errors

### Issue: "Platform not available"
- Ensure platform credentials in `.env`
- Check platform API status
- Verify network connectivity

## Advanced Features

### Batch Processing
Set design count to generate multiple designs in one run. Each design will be created as separate products across all enabled platforms.

### Custom Prompts
Use the custom prompt field to override AI generation and use your exact specifications. Leave blank for Claude to generate creative prompts.

### Pricing Strategy
- **T-Shirt Price**: Typically $19.99 - $29.99
- **Hoodie Price**: Typically $34.99 - $49.99
- Consider platform fees and profit margins

### Platform Selection Strategy
- **Printify + Shopify**: Best for full control and branding
- **TikTok Shop**: Best for viral/trending products
- **Etsy**: Best for artistic/handmade aesthetic
- **Instagram/Facebook**: Best for social engagement

## Performance

- **Concurrent Processing**: Multiple platforms process in parallel
- **Image Optimization**: Automatic image compression and formatting
- **Caching**: Generated designs cached for reuse
- **Rate Limiting**: Automatic API rate limit handling

## Security

- API keys stored in environment variables
- No sensitive data in frontend
- HTTPS required for production
- OAuth tokens encrypted at rest

## Support

For issues or questions:
1. Check this documentation
2. Review terminal logs
3. Check platform-specific documentation
4. Review backend orchestrator logs

## License

Part of the StaticWaves POD Studio project.
