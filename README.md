<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Studio

A web-based simulation of the StaticWaves Print-on-Demand automation suite with **full auto-publish pipeline integration** for Printify → Shopify → TikTok Shop.

View your app in AI Studio: https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

## Features

### 🎨 Design Generation & Editor
- Real-time design preview
- Interactive image editor with zoom and pan controls
- Product mockup visualization
- Live editing capabilities

### ⚡ Auto-Publish Pipeline
**NEW!** Fully automated product publishing across multiple platforms:
- **Printify**: Create products with your designs
- **Shopify**: Auto-sync products to your store
- **TikTok Shop**: Publish directly to TikTok marketplace

### 🚀 Batch Processing
- Single drop execution
- Batch mode for multiple drops
- Real-time progress tracking
- Queue management system

### 📊 Live Monitoring
- Terminal-style logging system
- Color-coded status messages
- Pipeline status visualization
- Upload queue tracking

## Run Locally

**Prerequisites:** Node.js (v16+)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment** (optional):
   Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key

3. **Run the app:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Auto-Publish Pipeline Setup

To use the **Auto-Publish Pipeline** feature, you need to configure API credentials:

### 1. Printify Setup
- Get your API key from [Printify API Settings](https://printify.com/app/account/api)
- Find your Shop ID in your Printify account settings

### 2. Shopify Setup
- Create a private app or custom app in your Shopify admin
- Generate an Admin API access token with product write permissions
- Your store name is the subdomain (e.g., "mystore" from mystore.myshopify.com)

### 3. TikTok Shop Setup
- Register as a TikTok Shop developer at [TikTok Shop Partner Portal](https://partner.tiktokshop.com/)
- Create an app and get your App Key and App Secret
- Find your Shop ID in the TikTok Seller Center

### 4. Configure in the App
1. Click "API Configuration" in the left sidebar
2. Enter your credentials for each platform
3. Click "Auto-Publish Pipeline" to run the full workflow

## How It Works

The auto-publish pipeline follows this workflow:

```
Design Generation → Printify Product Creation → Shopify Sync → TikTok Shop Publish
```

1. **Design Creation**: Generates product design and mockup
2. **Printify**: Creates the product with your design
3. **Shopify**: Syncs the product to your Shopify store
4. **TikTok Shop**: Publishes the product to TikTok marketplace
5. **Inventory Update**: Sets initial stock levels

## Project Structure

```
├── App.tsx                      # Main application component
├── components/
│   ├── Terminal.tsx            # Log display component
│   ├── EditorControls.tsx      # Image editor controls
│   └── PipelineStatus.tsx      # Pipeline status tracker
├── services/
│   ├── mockEngine.ts           # Simulation engine
│   ├── printifyService.ts      # Printify API integration
│   ├── shopifyService.ts       # Shopify API integration
│   ├── tiktokService.ts        # TikTok Shop API integration
│   └── pipelineOrchestrator.ts # Pipeline coordination
└── types.ts                    # TypeScript type definitions
```

## Development

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling (via CDN)
- **Lucide React** - Icon library

## API Integration Notes

This is a **simulation/demo version** with mock API calls. For production use:

1. Uncomment the actual API calls in the service files
2. Implement proper error handling
3. Add rate limiting and retry logic
4. Secure API credentials using environment variables
5. Add webhook handlers for real-time status updates
6. Implement proper authentication flows

## License

MIT
