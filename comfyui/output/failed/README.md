# ComfyUI Failed Outputs - Printify Push

This folder contains images that will be pushed to Printify as T-shirt and Hoodie products.

## Usage

1. **Add your images** to this folder:
   - Supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`
   - Images should be high resolution (recommended: at least 2400x3200px for best print quality)
   - File names will be converted to product titles (e.g., `my-awesome-design.png` → "My Awesome Design")

2. **Configure your Printify credentials** in `.env`:
   ```bash
   PRINTIFY_API_KEY=your-printify-api-key
   PRINTIFY_SHOP_ID=your-shop-id
   ```

3. **Run the push script**:
   ```bash
   npm run printify:push
   ```

## What the script does

For each image in this folder, the script will:
1. ✅ Upload the image to Printify
2. 👕 Create a T-Shirt product (default: $19.99)
3. 🧥 Create a Hoodie product (default: $34.99)
4. 📤 Publish products (if `AUTO_PUBLISH=true` in `.env`)

## Configuration

You can customize prices and other settings in your `.env` file:

```bash
DEFAULT_TSHIRT_PRICE=19.99
DEFAULT_HOODIE_PRICE=34.99
AUTO_PUBLISH=true
```

## Output

The script will display:
- Progress for each image processed
- Product URLs for created items
- Summary of successful and failed products

## Example Output

```
🚀 Printify Product Push Started
📁 Image Directory: comfyui/output/failed
🏪 Shop ID: 12345

📸 Found 3 image(s)

📦 Processing: cool-design.png
   Title: Cool Design
   👕 Creating T-Shirt...
   ✅ T-Shirt created: https://printify.com/app/products/abc123
   🧥 Creating Hoodie...
   ✅ Hoodie created: https://printify.com/app/products/def456

====================================
📊 SUMMARY
====================================

✅ Successful: 3
❌ Failed: 0
```
