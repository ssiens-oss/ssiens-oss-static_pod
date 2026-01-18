# Testing Shopify Sync Status

## Quick Test Workflow

### 1. Start the Gateway

```bash
cd ~/ssiens-oss-static_pod/gateway
export PYTHONPATH=$(pwd)
.venv/bin/python app/main.py
```

**Look for in terminal:**
```
INFO - ✓ Printify platform initialized
INFO - 📦 Configured platforms: printify
INFO - 🚀 POD Gateway starting...
```

### 2. Open Gallery in Browser

Navigate to: `http://localhost:5000`

### 3. Generate a Test Image

In the gallery UI:
1. Click "Generate AI Design"
2. Enter prompt: `cyberpunk cat neon lights`
3. Style: `digital art`
4. Genre: `futuristic`
5. Click "Generate"

**Wait for:**
- RunPod to process (look for "Generation complete" toast)
- Image to appear in gallery

### 4. Get the Image ID

**Option A - From Browser Console:**
```javascript
// Open browser console (F12)
fetch('/api/images')
  .then(r => r.json())
  .then(d => console.log(d.images[0]))
```

**Option B - From Terminal:**
```bash
curl -s http://localhost:5000/api/images | python3 -m json.tool
```

**Example response:**
```json
{
  "images": [
    {
      "id": "generated_a1b2c3d4",  // <-- This is your image ID
      "filename": "generated_a1b2c3d4.png",
      "status": "pending",
      "path": "/api/image/generated_a1b2c3d4"
    }
  ]
}
```

### 5. Approve and Publish

**In Gallery UI:**
1. Click "✓ Approve" on your image
2. Click "→ Publish"
3. Product type: Select "1" (Hoodie) or leave blank
4. Platform: Select "1" (Printify)
5. Title: Leave blank for auto-generation

**Watch Terminal for:**
```
INFO - Enabling 100 variants for product 'Cyberpunk Cat Neon Lights Design'
INFO - Creating product: Cyberpunk Cat Neon Lights Design
INFO - Product created successfully: 12345678
INFO - Publishing product 12345678 to connected stores...
INFO - ✓ Product 12345678 published successfully
INFO - → Publishing to connected sales channels (Shopify/Etsy)
INFO - → Sync may take 30-120 seconds
```

### 6. Test Sync Status (WAIT 30-120 seconds first!)

```bash
# Replace with your actual image ID
IMAGE_ID="generated_a1b2c3d4"

# Check sync status
curl -s "http://localhost:5000/api/sync_status/${IMAGE_ID}" | python3 -m json.tool
```

**Expected Response (before sync):**
```json
{
  "success": true,
  "synced": false,
  "external_id": null,
  "shopify_id": null,
  "is_locked": false,
  "visible": false
}
```

**Expected Response (after sync - wait 30-120 seconds):**
```json
{
  "success": true,
  "synced": true,
  "external_id": "shop_12345",
  "shopify_id": "gid://shopify/Product/7891234567890",
  "is_locked": false,
  "visible": true
}
```

### 7. Test Product Metrics

```bash
curl -s "http://localhost:5000/api/product_metrics/${IMAGE_ID}" | python3 -m json.tool
```

**Response:**
```json
{
  "success": true,
  "image_id": "generated_a1b2c3d4",
  "metrics": {
    "views": 0,
    "sales": 0,
    "favorites": 0,
    "add_to_carts": 0,
    "conversion_rate": 0.0
  },
  "performance": {
    "score": 0.0,
    "bestseller": false
  },
  "financial": {
    "revenue_cents": 0,
    "fulfillment_cost_cents": 0,
    "platform_fee_pct": 0.029,
    "net_profit_cents": 0
  }
}
```

## Troubleshooting

### Error: "Image ID not found"
- Make sure you're using the actual image ID from `/api/images`
- The ID format is like: `generated_a1b2c3d4` (not `generated_abc123`)

### Error: "Product not published yet"
- You need to approve and publish the image first
- Check that `/api/publish` returned success

### Sync still shows `synced: false` after 2 minutes
**Check Printify dashboard:**
1. Go to https://printify.com/app/products
2. Find your product
3. Check if "Published" badge is present
4. Check if Shopify store is connected

**Check terminal logs for errors:**
```
ERROR - ✗ Error publishing product
```

### Check Shopify Store

1. Go to your Shopify admin
2. Navigate to Products
3. Look for your new product
4. Should show: Title, variants, images, description

## What Should Happen

### ✅ Success Path
1. Image generated → Downloaded to gateway
2. Approved → Status = "approved"
3. Published → Printify product created
4. Variants enabled (100 max)
5. Publish called → Pushes to Shopify/Etsy
6. Sync (30-120s) → external_id appears
7. Product live on Shopify with:
   - Full title
   - Description
   - All variants (sizes/colors)
   - Mockup images
   - Pricing

### ❌ "Title Only" Problem (Should NOT happen now)

**Before fixes:**
- Product appears in Shopify
- Has title
- No variants
- No mockups
- Can't be purchased

**After fixes:**
- Detailed logging confirms variants enabled
- Publish endpoint called with all fields
- Sync status can be verified
- Full product with sellable variants

## Continuous Monitoring

**During Development:**
```bash
# Watch gateway logs
tail -f /path/to/gateway.log

# Poll sync status every 30s
watch -n 30 "curl -s http://localhost:5000/api/sync_status/YOUR_IMAGE_ID | python3 -m json.tool"
```

## Next Steps After Confirmation

Once you confirm `synced: true`:

1. ✅ Check Shopify product has variants
2. ✅ Verify mockup images loaded
3. ✅ Test adding to cart
4. ✅ Place test order
5. ✅ Confirm Printify receives order

This verifies end-to-end commerce correctness!
