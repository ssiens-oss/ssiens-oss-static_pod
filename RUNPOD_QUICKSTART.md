# RunPod Quick Start Guide

## 🚀 One-Click Deployment

SSH into your RunPod instance and run:

```bash
cd ~/ssiens-oss-static_pod
bash bootstrap-runpod.sh
```

That's it! The script will:
- ✅ Install/upgrade Node.js to v20+
- ✅ Install required tools (git, npm, pm2)
- ✅ Pull latest code
- ✅ Validate environment variables
- ✅ Install dependencies
- ✅ Build frontend
- ✅ Clean up old processes
- ✅ Start API server
- ✅ Run health checks
- ✅ Display access URLs

## 📋 Prerequisites

Create a `.env` file in the project root with:

```bash
# Claude API (required)
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-3-haiku-20240307

# Printify API (required)
PRINTIFY_API_KEY=eyJ0eXAiOiJKV1Qi...
PRINTIFY_SHOP_ID=25860767

# Shopify (optional)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_...

# ComfyUI (optional - uses placeholders if not available)
COMFYUI_API_URL=http://localhost:8188
```

## 🌐 Access Your Dashboard

After deployment, access your dashboard at:

```
https://<runpod-id>-3001.proxy.runpod.net
```

Example: `https://nfre49elqpt6su-3001.proxy.runpod.net`

## 🧪 Test Production Run

### Option 1: Via GUI Dashboard

1. Open dashboard URL in browser
2. Configure your drop:
   - **Drop Name**: "Test Drop 1"
   - **Theme**: "Cyberpunk streetwear"
   - **Style**: "Bold graphic design"
   - **Count**: 3 (creates 3 designs)
   - **Blueprint**: 6 (T-shirt) or 1 (Hoodie)
3. Click **"Run Pipeline"**
4. Watch the terminal output

### Option 2: Via Test Script

SSH into RunPod and run:

```bash
cd ~/ssiens-oss-static_pod
npx tsx test-printify.ts
```

This will:
1. Fetch real T-shirt variants from Printify
2. Upload a test image
3. Create a test product with print_areas
4. Display the product URL

## 📊 Verify Services

Check API health:
```bash
curl http://localhost:3001/health
```

Check service configuration:
```bash
curl http://localhost:3001/api/config/test
```

Expected output:
```json
{
  "comfyui": false,     // No GPU - uses placeholders
  "claude": true,       // ✅ AI prompt generation
  "printify": true,     // ✅ Product creation
  "shopify": false      // Optional
}
```

## 🔧 Useful Commands

```bash
# View server logs
pm2 logs pod-studio-api

# Restart server
pm2 restart pod-studio-api

# Stop server
pm2 stop pod-studio-api

# Check server status
pm2 list

# Pull latest updates
cd ~/ssiens-oss-static_pod
git pull origin claude/repo-analysis-g6UHk
npm install
npm run build
pm2 restart pod-studio-api
```

## 📦 Production Pipeline Flow

When you run a pipeline, here's what happens:

1. **Claude AI** generates creative product prompts based on your theme/style
2. **Image Generation**:
   - If ComfyUI available: Real AI-generated designs
   - If no GPU: Placeholder images (for testing)
3. **Printify Integration**:
   - Upload images to Printify
   - Fetch real product variants (sizes, colors)
   - Create products with proper print_areas
   - Set pricing
4. **Publishing** (if enabled):
   - Publish to Printify shop
   - Sync to Shopify (if configured)
5. **Results**: View created products in Printify dashboard

## 🎯 Supported Blueprints

### T-Shirt (Blueprint 3)
- Product: Unisex Heavy Cotton Tee (Gildan 5000)
- Provider: SwiftPOD (ID: 99)
- Default Price: $19.99
- Variants: Multiple sizes and colors

### Hoodie (Blueprint 165)
- Product: Unisex Heavy Blend Hoodie (Gildan 18500)
- Provider: SwiftPOD (ID: 99)
- Default Price: $34.99
- Variants: Multiple sizes and colors

## 🐛 Troubleshooting

### "API Server Offline" in Dashboard

1. Check server is running:
   ```bash
   pm2 list
   curl http://localhost:3001/health
   ```

2. Restart if needed:
   ```bash
   pm2 restart pod-studio-api
   ```

### Port Already in Use

```bash
pm2 delete all
pkill -f node
pkill -f tsx
bash bootstrap-runpod.sh
```

### Printify API Errors

1. Verify API key in `.env`
2. Check API key has required scopes:
   - `products.read`
   - `products.write`
   - `shops.read`
   - `uploads.write`

### Missing Environment Variables

```bash
cat .env
```

Make sure all required variables are set.

## 📈 Next Steps

1. ✅ Deploy with `bootstrap-runpod.sh`
2. ✅ Test with placeholder images
3. 🎨 Add ComfyUI with GPU for real AI designs
4. 🛍️ Connect Shopify for automatic publishing
5. 📊 Scale up production runs

## 💡 Tips

- Start with small counts (3-5 products) for testing
- Monitor Printify API rate limits
- Use descriptive drop names for organization
- Check product designs in Printify before publishing
- Enable auto-publish only after testing

---

**Ready to create POD products at scale! 🚀**
