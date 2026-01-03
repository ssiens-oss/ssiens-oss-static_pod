# 🎨 Background Removal & Mockup Generation Guide

**Complete guide for transparent PNGs and product mockups in the POD Engine**

---

## 🌟 Features Overview

The POD Engine now automatically:

1. **Removes backgrounds** from generated designs → transparent PNGs
2. **Generates product mockups** → shirt/hoodie previews
3. **Publishes transparent PNGs** to Printify (no white backgrounds!)

All integrated into the pipeline, zero manual work required.

---

## 🚀 Quick Start

### Already Enabled by Default

Background removal and mockups are **enabled by default**. Just run your normal pipeline:

```bash
# Submit a job
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Urban street art design",
    "productTypes": ["tshirt", "hoodie"],
    "autoPublish": true
  }'
```

**What happens automatically:**

1. ✓ AI generates design
2. ✓ Background removed → transparent PNG created
3. ✓ Mockups generated (t-shirt + hoodie)
4. ✓ **Transparent PNG** uploaded to Printify (not original!)
5. ✓ Products published with no white background

---

## 🎨 Background Removal

### How It Works

After each design is generated:

1. Original saved: `/workspace/data/designs/img_123.png`
2. Background removed automatically
3. Transparent saved: `/workspace/data/designs/img_123_transparent.png`

The transparent version is used for:
- Printify uploads
- Mockup generation
- Product publishing

### Example Result

```json
{
  "generatedImages": [
    {
      "id": "img_1234567890_abc",
      "url": "file:///workspace/data/designs/img_1234567890_abc.png",
      "transparentUrl": "file:///workspace/data/designs/img_1234567890_abc_transparent.png",
      "mockups": {
        "tshirt": "/workspace/data/mockups/img_1234567890_abc_tshirt_mockup.png",
        "hoodie": "/workspace/data/mockups/img_1234567890_abc_hoodie_mockup.png"
      }
    }
  ]
}
```

### Disable Background Removal

If you want original images (with background):

```bash
# In .env
ENABLE_BACKGROUND_REMOVAL=false
```

---

## 🖼️ Product Mockups

### Automatic Mockup Generation

For each design and product type, a mockup is automatically generated:

- **T-Shirt Mockup**: Design centered on t-shirt template
- **Hoodie Mockup**: Design centered on hoodie template

**Mockups saved to:** `/workspace/data/mockups/`

### Mockup Templates

The engine needs base templates (apparel product photos):

**Location:** `/workspace/data/mockup-templates/`

**Required files:**
```
/workspace/data/mockup-templates/
├── tshirt_base.png    # T-shirt product photo (transparent background)
└── hoodie_base.png    # Hoodie product photo (transparent background)
```

### Default Placeholder Templates

On first run, the engine creates **placeholder templates** automatically.

**⚠️ Important:** These are simple gray shapes for testing only.

**For production**, replace with real product photos:

#### Option 1: Use Printify Mockups (Recommended)

1. Download product mockup templates from Printify
2. Choose "Blank" mockups with transparent backgrounds
3. Save as `tshirt_base.png` and `hoodie_base.png`
4. Place in `/workspace/data/mockup-templates/`

#### Option 2: Use Professional Mockup Services

Services like:
- **Placeit** - https://placeit.net
- **Smartmockups** - https://smartmockups.com
- **Printful Mockup Generator** - https://www.printful.com/mockup-generator

Download PNG mockups with transparent backgrounds.

#### Option 3: Create Your Own

Requirements:
- PNG format with **transparent background**
- Minimum 1200x1400px (higher is better)
- Clear chest area for design placement
- Straight-on view (not angled)

### Mockup Placement Settings

Default settings (good for most designs):
- **Scale:** 70% of template width
- **Vertical Position:** 45% from top (chest area)

To customize, edit `services/mockupService.ts`:

```typescript
const mockups = await this.mockup.generateMockups(
  designPath,
  productTypes,
  designId,
  0.7,   // scale: 0.0-1.0 (70%)
  0.45   // y_offset: 0.0-1.0 (45% from top)
)
```

### Disable Mockups

If you don't need mockups:

```bash
# In .env
ENABLE_MOCKUPS=false
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Background Removal
ENABLE_BACKGROUND_REMOVAL=true   # Set to 'false' to disable

# Mockups
ENABLE_MOCKUPS=true              # Set to 'false' to disable
MOCKUP_TEMPLATES_DIR=/workspace/data/mockup-templates
MOCKUP_OUTPUT_DIR=/workspace/data/mockups
```

### File Locations

```
/workspace/
├── data/
│   ├── designs/                      # Original generated designs
│   │   ├── img_123.png              # Original
│   │   └── img_123_transparent.png  # Transparent (auto-created)
│   ├── mockups/                      # Generated mockups
│   │   ├── img_123_tshirt_mockup.png
│   │   └── img_123_hoodie_mockup.png
│   └── mockup-templates/            # Base templates (user-provided)
│       ├── tshirt_base.png
│       └── hoodie_base.png
```

---

## 📊 API Response Format

When you submit a job, the response includes all variants:

```json
{
  "success": true,
  "generatedImages": [
    {
      "id": "img_1704556789_x7k2m",
      "url": "file:///workspace/data/designs/img_1704556789_x7k2m.png",
      "transparentUrl": "file:///workspace/data/designs/img_1704556789_x7k2m_transparent.png",
      "mockups": {
        "tshirt": "/workspace/data/mockups/img_1704556789_x7k2m_tshirt_mockup.png",
        "hoodie": "/workspace/data/mockups/img_1704556789_x7k2m_hoodie_mockup.png"
      },
      "prompt": "Urban street art design"
    }
  ],
  "products": [
    {
      "platform": "printify",
      "productId": "prod_abc123",
      "url": "https://printify.com/app/products/prod_abc123",
      "type": "tshirt"
    }
  ]
}
```

---

## ✅ Printify Integration

### Transparent PNG Upload

The engine **automatically** uses the transparent PNG when uploading to Printify:

```typescript
// In orchestrator.ts - line ~217
const imageToPublish = {
  ...savedImage,
  url: processedImage.transparentUrl || savedImage.url
}

// Printify receives transparent PNG, not original
await this.printify.createTShirt(
  imageToPublish.url,  // ← transparent PNG!
  ...
)
```

**Result:** Products published to Printify have **no white background**.

### Verify Transparent Upload

Check the job result:

```bash
curl http://localhost:3000/api/jobs/JOB_ID | jq '.result.generatedImages[0]'
```

Look for:
```json
{
  "transparentUrl": "file:///workspace/data/designs/img_123_transparent.png"
}
```

If `transparentUrl` exists, that's what was uploaded to Printify.

---

## 🎯 Production Workflow

### 1. Replace Placeholder Templates

**Before production**, replace placeholders with real mockups:

```bash
# Download your actual product photos
# Place them in the templates directory
cp your_tshirt_photo.png /workspace/data/mockup-templates/tshirt_base.png
cp your_hoodie_photo.png /workspace/data/mockup-templates/hoodie_base.png

# Restart the engine
pkill -f pod-engine-api
npm run engine &
```

### 2. Test the Pipeline

Submit a test job:

```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test design - minimalist geometric pattern",
    "productTypes": ["tshirt"],
    "autoPublish": false
  }'
```

### 3. Verify Results

Check the generated files:

```bash
# View all outputs
ls -lh /workspace/data/designs/img_*
ls -lh /workspace/data/mockups/

# View transparent PNG
# (Use file viewer or download to inspect)

# Check mockup quality
# Mockup should show your design on the actual product photo
```

### 4. Enable Auto-Publish

Once satisfied:

```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Production design",
    "productTypes": ["tshirt", "hoodie"],
    "autoPublish": true  ← Enable publishing
  }'
```

---

## 🐛 Troubleshooting

### Background Removal Fails

**Check Python dependencies:**

```bash
python -c "import rembg; print('rembg installed')"
```

**If missing:**

```bash
pip install rembg pillow
```

**Check logs:**

```bash
tail -f /workspace/logs/pod-engine.log | grep -i "background"
```

### Mockups Not Generated

**Check templates exist:**

```bash
ls -lh /workspace/data/mockup-templates/
```

**Should show:**
```
tshirt_base.png
hoodie_base.png
```

**If missing, create placeholders:**

```bash
python /workspace/app/services/create_mockup_templates.py
```

**Check mockup service:**

```bash
tail -f /workspace/logs/pod-engine.log | grep -i "mockup"
```

### Printify Gets Original (Not Transparent)

**Check job result:**

```bash
curl http://localhost:3000/api/jobs/JOB_ID | jq '.result.generatedImages[0]'
```

**If `transparentUrl` is missing:**

1. Check background removal is enabled
2. Check logs for errors
3. Verify rembg is installed

**Manual fix:**

```bash
# Remove background manually
python /workspace/app/services/remove_bg.py \
  /workspace/data/designs/img_123.png \
  /workspace/data/designs/img_123_transparent.png
```

---

## 📚 Advanced Usage

### Custom Mockup Script

Use the mockup generator directly:

```bash
python /workspace/app/services/mockup.py \
  /workspace/data/mockup-templates/tshirt_base.png \
  /workspace/data/designs/img_123_transparent.png \
  /workspace/data/mockups/custom_mockup.png \
  0.7 \    # scale
  0.45     # y_offset
```

### Batch Process Existing Designs

Remove backgrounds for all existing designs:

```bash
cd /workspace/data/designs

for img in img_*.png; do
  # Skip if already transparent
  if [[ ! "$img" =~ "_transparent.png" ]]; then
    output="${img%.png}_transparent.png"
    python /workspace/app/services/remove_bg.py "$img" "$output"
  fi
done
```

### Generate Mockups for Existing Designs

```bash
cd /workspace/data/designs

for img in *_transparent.png; do
  id=$(basename "$img" _transparent.png)

  # T-shirt mockup
  python /workspace/app/services/mockup.py \
    /workspace/data/mockup-templates/tshirt_base.png \
    "$img" \
    "/workspace/data/mockups/${id}_tshirt_mockup.png"

  # Hoodie mockup
  python /workspace/app/services/mockup.py \
    /workspace/data/mockup-templates/hoodie_base.png \
    "$img" \
    "/workspace/data/mockups/${id}_hoodie_mockup.png"
done
```

---

## 🎉 Summary

**What You Get:**

✅ Automatic background removal for all designs
✅ Transparent PNGs uploaded to Printify (no white backgrounds)
✅ Product mockups generated automatically
✅ Professional-looking previews for QA and marketing
✅ All integrated into the pipeline

**Zero manual work required!**

---

## 📞 Support

**Logs:**
```bash
tail -f /workspace/logs/pod-engine.log
```

**Test background removal:**
```bash
python /workspace/app/services/remove_bg.py test_input.png test_output.png
```

**Test mockup generation:**
```bash
python /workspace/app/services/mockup.py template.png design.png output.png
```

**Check configuration:**
```bash
echo "Background removal: $ENABLE_BACKGROUND_REMOVAL"
echo "Mockups: $ENABLE_MOCKUPS"
```

---

**Happy automating with transparent PNGs and professional mockups!** 🚀
