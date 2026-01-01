# Mass Production Guide
## Create Multiple Products from One Design

### TikTok-Ready Products

**Configured in `tiktok-products-config.json`:**

1. **Unisex Heavy Cotton Tee** (Blueprint 6) - $24.99
2. **Unisex Heavy Blend Hoodie** (Blueprint 77) - $44.99
3. **Unisex Crewneck Sweatshirt** (Blueprint 49) - $39.99
4. **Unisex Tank Top** (Blueprint 39) - $22.99
5. **Mug 11oz** (Blueprint 68) - $16.99
6. **Tote Bag** (Blueprint 22) - $19.99
7. **Phone Case** (Blueprint 167) - $21.99
8. **Water Bottle** (Blueprint 215) - $27.99
9. **Stickers** (Blueprint 334) - $4.99

### Quick Start

**Option 1: Use Dashboard (Recommended)**

1. Access dashboard: `http://10.0.0.70:3001?mode=dashboard`
2. Configure your design:
   - **Theme**: Select from dropdown
   - **Style**: Select from dropdown
   - **Design Count**: Set to 1 for testing
3. Click **"Start Pipeline"**
4. Pipeline will:
   - Generate AI design with Claude
   - Create image with ComfyUI
   - Create 5 products automatically (TikTok Starter Bundle)
   - Publish to your Printify store

**Option 2: Manual Script**

```bash
# From your repo directory
cd ~/ssiens-oss-static_pod

# Run mass production script
npx tsx scripts/mass-production.ts
```

### Pre-Configured Bundles

**TikTok Starter Bundle** (Best for testing)
- T-Shirt (Blueprint 6)
- Hoodie (Blueprint 77)
- Sweatshirt (Blueprint 49)
- Mug (Blueprint 68)
- Tote Bag (Blueprint 22)

**Viral Bundle** (Maximum reach)
- All Starter Bundle products +
- Tank Top (Blueprint 39)
- Stickers (Blueprint 334)

### Customizing Product Selection

Edit `tiktok-products-config.json` to add/remove products:

```json
{
  "recommendedBundle": {
    "name": "Your Custom Bundle",
    "products": [6, 77, 68, 22, 334],
    "description": "Your description"
  }
}
```

### Testing the Full Pipeline

**Test Run (1 design → 5 products):**

1. Open dashboard
2. Set **Design Count: 1**
3. Select **Theme: Urban streetwear**
4. Select **Style: Bold graphics**
5. Click **Start Pipeline**
6. Wait 5-10 minutes
7. Check your Printify dashboard

**Production Run (10 designs → 50 products):**

1. Set **Design Count: 10**
2. Select your theme/style
3. Click **Start Pipeline**
4. Wait 30-60 minutes
5. You'll have 50 products (10 designs × 5 product types each)

### Estimated Costs

**Per Design (5 products):**
- Claude API: ~$0.05
- ComfyUI: Free (running on RunPod GPU)
- Printify: $0 (only pay when products sell)
- **Total: ~$0.05 per design**

**For 10 Designs (50 products):**
- Total cost: ~$0.50
- Potential revenue: $1,500+ (50 products × $30 avg)
- **ROI: 3000%+**

### Monitoring Progress

Watch the **SYSTEM OUTPUT** section in the dashboard for real-time logs:

```
🚀 Starting POD automation pipeline...
📝 Generating creative prompts with Claude...
✓ Generated 10 prompts
🎨 Generating designs with ComfyUI...
✓ Design 1/10 complete
📦 Creating Printify products...
✓ T-Shirt created
✓ Hoodie created
✓ Sweatshirt created
✓ Mug created
✓ Tote created
🌐 Publishing to store...
✓ All products published!
```

### Troubleshooting

**Issue: "Claude API error"**
- Solution: Check your `ANTHROPIC_API_KEY` in `.env`

**Issue: "ComfyUI not responding"**
- Solution: ComfyUI isn't running yet (optional for now)
- Use manual prompts mode instead

**Issue: "Printify upload failed"**
- Solution: Check your `PRINTIFY_API_KEY` and `PRINTIFY_SHOP_ID`

### Next Steps

1. **Test with 1 design** to verify everything works
2. **Review products** in Printify dashboard
3. **Adjust pricing** if needed
4. **Run production batch** (10-100 designs)
5. **Connect to TikTok Shop** for viral marketing

### Support

- API Documentation: https://developers.printify.com/
- TikTok Shop Setup: https://seller-us.tiktok.com/
