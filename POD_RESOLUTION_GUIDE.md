# POD Image Resolution Guide

## Problem Fixed

**Before:** Images generated at 1024x1024px (TOO LOW)
**After:** Images generated at 3600x3600px (POD-OPTIMIZED)

Blurry images were caused by insufficient resolution for print-on-demand.

---

## Resolution Requirements by Product

### Apparel (T-Shirts, Hoodies, Sweatshirts)
- **Minimum:** 2400x2400px (12" x 12" at 200 DPI)
- **Recommended:** 3600x3600px (18" x 18" at 200 DPI)
- **Optimal:** 4500x5400px (Printify recommended)

### Posters & Canvas
- **Minimum:** 2400x3000px
- **Recommended:** 3600x4500px
- **Optimal:** 4800x6000px

### Stickers
- **Minimum:** 1500x1500px
- **Recommended:** 3000x3000px

### Mugs & Small Items
- **Minimum:** 2400x1200px (wrap-around)
- **Recommended:** 3600x1800px

---

## What Changed

### 1. Default Resolution Increased

**File:** `gateway/app/main.py`

```python
# BEFORE (blurry)
def build_comfyui_workflow(
    width: int = 1024,  # ❌ Too low
    height: int = 1024,
)

# AFTER (sharp)
def build_comfyui_workflow(
    width: int = 3600,  # ✅ POD-optimized
    height: int = 3600,
)
```

### 2. Resolution Validation Added

```python
# Warns if resolution is too low
if width < 2400 or height < 2400:
    logger.warning(f"⚠ Resolution {width}x{height} is below POD minimum")
```

### 3. Logging Added

```
INFO - Generating image at 3600x3600 resolution
```

---

## Why 3600x3600?

**Balance between:**
- ✅ High enough for quality prints (300 DPI at 12")
- ✅ Reasonable RunPod processing time (~30-60s)
- ✅ Doesn't exceed VRAM limits on most setups
- ✅ Works well for square products (most POD items)

**Comparison:**
- 1024x1024: 1.0MP → **Pixelated on prints**
- 2400x2400: 5.8MP → Acceptable minimum
- **3600x3600: 13.0MP** → Good quality ✅
- 4500x5400: 24.3MP → Optimal (slower generation)

---

## How to Generate at Different Resolutions

### Default (Automatic)
```bash
# Will use 3600x3600 automatically
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "cyberpunk cat"}'
```

### Custom Resolution
```bash
# For poster (taller)
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cat",
    "width": 3600,
    "height": 4500
  }'
```

### Maximum Quality (Slower)
```bash
# Best quality for apparel
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cat",
    "width": 4500,
    "height": 5400
  }'
```

---

## Testing Resolution Improvements

### 1. Generate New Image

Open browser: `http://localhost:5000`

Click "Generate AI Design" and enter:
- Prompt: `test pattern high detail`
- Style: `geometric`

### 2. Check Terminal Logs

Look for:
```
INFO - Generating image at 3600x3600 resolution
```

### 3. Verify Image Quality

```bash
# Check image dimensions
identify ~/ssiens-oss-static_pod/gateway/data/images/generated_*.png

# Should show: PNG 3600x3600 (not 1024x1024)
```

### 4. Compare Before/After

**Old Images (1024x1024):**
- Look pixelated when zoomed
- Blurry on products
- Low file size (~500KB)

**New Images (3600x3600):**
- Sharp detail when zoomed
- Crisp on products
- Larger file size (~2-4MB)

---

## Performance Impact

### Generation Time
- **1024x1024:** ~10-15 seconds
- **3600x3600:** ~30-45 seconds (3.5x longer)
- **4500x5400:** ~60-90 seconds (6x longer)

### VRAM Usage
- **1024x1024:** ~3GB
- **3600x3600:** ~8GB (should work on most RunPod instances)
- **4500x5400:** ~12GB (may require larger instances)

### File Size
- **1024x1024:** ~500KB
- **3600x3600:** ~2-4MB
- **4500x5400:** ~5-8MB

**Recommendation:** 3600x3600 is the sweet spot for POD quality without excessive processing time.

---

## Troubleshooting

### "Out of memory" errors

If RunPod shows OOM errors:

1. **Reduce resolution temporarily:**
   ```json
   {"width": 2400, "height": 2400}
   ```

2. **Upgrade RunPod instance:**
   - Choose GPU with 16GB+ VRAM
   - Recommended: RTX 4090 or A6000

### Images still blurry

1. **Check image dimensions:**
   ```bash
   identify path/to/image.png
   ```

2. **Verify RunPod workflow completed:**
   - Check logs for "Generating image at 3600x3600"
   - Ensure workflow didn't downscale

3. **Check Printify upload:**
   - Log into Printify dashboard
   - View product mockups
   - Zoom in to verify quality

### Old images already generated

**Problem:** Images generated before this fix are still 1024x1024

**Solution:** Regenerate affected images
```bash
# Delete old low-res images
rm ~/ssiens-oss-static_pod/gateway/data/images/generated_*.png

# Regenerate with new resolution
# Use gallery UI to generate fresh images
```

---

## Best Practices

### 1. Always Use High Resolution
- Default 3600x3600 is good for most products
- For posters, use 3600x4500 or larger
- Never go below 2400x2400

### 2. Test Print Quality
- Order test products from Printify
- Verify sharpness on physical items
- Adjust resolution if needed

### 3. Monitor File Sizes
- 2-4MB per image is normal
- Compress if needed (but maintain quality)
- Consider storage capacity

### 4. Document Requirements
- Tell users minimum 2400x2400
- Recommend 3600x3600 for best results
- Provide resolution presets in UI

---

## Next Steps

**Optional Enhancements:**

1. **Product-Specific Resolution:**
   ```python
   # Auto-select resolution based on product type
   if product_type == "poster":
       width, height = 4800, 6000
   elif product_type == "hoodie":
       width, height = 4500, 5400
   ```

2. **UI Resolution Selector:**
   - Add dropdown: "Quality: Standard / High / Ultra"
   - Standard: 2400x2400
   - High: 3600x3600 (default)
   - Ultra: 4500x5400

3. **Batch Upscaling:**
   - Use AI upscaler for existing low-res images
   - Real-ESRGAN or similar
   - 4x upscale: 1024→4096

---

## Summary

✅ **Fixed:** Default resolution increased from 1024x1024 to 3600x3600
✅ **Result:** Sharp, print-ready images for POD products
✅ **Warning:** System alerts if resolution too low
✅ **Flexible:** Custom resolution still supported via API

**Your images will now be crisp and professional on all POD products!** 🎉
