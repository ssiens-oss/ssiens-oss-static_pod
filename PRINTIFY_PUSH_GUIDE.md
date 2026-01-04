# Printify Push Guide

## Quick Start

Push your designs to Printify as T-shirts and Hoodies:

```bash
# 1. Add your images to the folder
cp /path/to/your/designs/*.png comfyui/output/failed/

# 2. Configure your Printify credentials (in .env)
PRINTIFY_API_KEY=your-actual-api-key
PRINTIFY_SHOP_ID=your-actual-shop-id

# 3. Run the push script
npm run printify:push
```

## 📋 Requirements

### Image Requirements
- **Formats**: PNG, JPG, JPEG, WebP, GIF
- **Resolution**: Minimum 2400x3200px recommended for best print quality
- **Location**: Place images in `comfyui/output/failed/`

### Printify Setup
1. Get your API key from [Printify Dashboard](https://printify.com/app/account/api)
2. Find your Shop ID in your Printify account settings
3. Update `.env` file with your credentials

## 🎨 How It Works

The script processes each image in `comfyui/output/failed/` and:

1. **Generates product info** from filename
   - Filename: `my-cool-design.png`
   - Product title: "My Cool Design - T-Shirt" / "My Cool Design - Hoodie"

2. **Creates products** in Printify
   - T-Shirt: Gildan 5000 (Unisex Heavy Cotton Tee)
   - Hoodie: Gildan 18500 (Unisex Heavy Blend Hoodie)

3. **Sets variants**
   - T-Shirt colors: Black, White, Navy, Heather Grey
   - T-Shirt sizes: S, M, L, XL, 2XL, 3XL
   - Hoodie colors: Black, Navy, Heather Grey
   - Hoodie sizes: S, M, L, XL, 2XL

4. **Publishes products** (if `AUTO_PUBLISH=true`)

## ⚙️ Configuration

Edit your `.env` file:

```bash
# Required
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id

# Optional - Customize prices
DEFAULT_TSHIRT_PRICE=19.99
DEFAULT_HOODIE_PRICE=34.99

# Optional - Auto-publish to connected sales channels
AUTO_PUBLISH=true
```

## 📊 Example Output

```
🚀 Printify Product Push Started
📁 Image Directory: comfyui/output/failed
🏪 Shop ID: 12345678

📸 Found 2 image(s)

📦 Processing: awesome-artwork.png
   Title: Awesome Artwork
   👕 Creating T-Shirt...
   ✅ T-Shirt created: https://printify.com/app/products/123456
   📤 Publishing T-Shirt...
   ✅ T-Shirt published
   🧥 Creating Hoodie...
   ✅ Hoodie created: https://printify.com/app/products/123457
   📤 Publishing Hoodie...
   ✅ Hoodie published

📦 Processing: cool-design.png
   Title: Cool Design
   👕 Creating T-Shirt...
   ✅ T-Shirt created: https://printify.com/app/products/123458
   📤 Publishing T-Shirt...
   ✅ T-Shirt published
   🧥 Creating Hoodie...
   ✅ Hoodie created: https://printify.com/app/products/123459
   📤 Publishing Hoodie...
   ✅ Hoodie published

============================================================
📊 SUMMARY
============================================================

✅ Successful: 2
❌ Failed: 0

📦 Created Products:

   awesome-artwork.png
   👕 T-Shirt: https://printify.com/app/products/123456
   🧥 Hoodie: https://printify.com/app/products/123457

   cool-design.png
   👕 T-Shirt: https://printify.com/app/products/123458
   🧥 Hoodie: https://printify.com/app/products/123459

============================================================
```

## 🔧 Troubleshooting

### "No images found in the directory"
- Check that images are in `comfyui/output/failed/`
- Verify file extensions are supported (png, jpg, jpeg, webp, gif)

### "Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID"
- Update your `.env` file with actual credentials
- Get API key from: https://printify.com/app/account/api

### "Printify API error"
- Verify your API key is valid
- Check that your shop ID is correct
- Ensure your Printify account has proper permissions

### Rate Limiting
The script includes a 2-second delay between each image to avoid rate limiting. For large batches, this is normal behavior.

## 🎯 Pro Tips

1. **Filename Conventions**: Use descriptive filenames with hyphens or underscores:
   - ✅ `galaxy-nebula-art.png` → "Galaxy Nebula Art"
   - ✅ `abstract_waves_blue.png` → "Abstract Waves Blue"
   - ❌ `img_001.png` → "Img 001"

2. **Batch Processing**: Process images in batches if you have many:
   - Move 10-20 images at a time to avoid long processing times

3. **Test First**: Start with 1-2 images to verify everything works before processing large batches

4. **Quality**: Higher resolution images = better print quality
   - Minimum: 2400x3200px
   - Recommended: 4500x5400px

## 📝 Next Steps

After pushing to Printify:

1. **Review products** in your Printify dashboard
2. **Adjust pricing** if needed
3. **Add additional variants** (colors/sizes)
4. **Connect sales channels** (Shopify, Etsy, etc.)
5. **Publish to store** if not auto-published

## 🔗 Resources

- [Printify API Documentation](https://developers.printify.com/)
- [Printify Dashboard](https://printify.com/app)
- [Print Quality Guidelines](https://printify.com/print-quality/)
