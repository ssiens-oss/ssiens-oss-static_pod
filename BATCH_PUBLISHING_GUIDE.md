# Batch Publishing & Auto-Metadata Guide

**Automatically publish multiple POD products with intelligent title and description generation**

---

## 🎯 Features

### ✨ Auto-Metadata Generation
- **Auto-Titles**: Intelligent titles generated from image IDs or prompts
- **Auto-Descriptions**: Dynamic descriptions based on art style
- **Consistent Branding**: Template-based descriptions for professional catalog

### 📦 Batch Processing
- **Bulk Publishing**: Process multiple images in one operation
- **Auto-Approval**: Optionally auto-approve pending images
- **Progress Tracking**: Detailed results for each image
- **Error Handling**: Continues on failures, reports all results

### 🎨 POD Optimizations
- **Black-Only Variants**: Default to black for simplified inventory
- **50 Variant Limit**: Manageable product catalog
- **Configurable Settings**: Override defaults per batch

---

## 🚀 Quick Start

### Single Image with Auto-Metadata

```bash
curl -X POST http://localhost:5000/api/publish/generated_787679c7_0 \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Result:** Automatic title and description generated!

### Batch Publish All Approved Images

```bash
./batch-publish.sh --all
```

### Batch Publish with Auto-Approval

```bash
./batch-publish.sh --all --auto-approve
```

---

## 📝 Auto-Metadata How It Works

### Auto-Title Generation

**Smart title creation based on available information:**

1. **From Prompt** (if provided):
   ```bash
   curl -X POST http://localhost:5000/api/publish/generated_abc123_0 \
     -H "Content-Type: application/json" \
     -d '{"prompt": "vibrant geometric abstract art"}'
   ```
   **Generated Title:** "Vibrant Geometric Abstract Art"

2. **From Image ID** (fallback):
   ```
   Image ID: generated_cosmic_blue_0
   Generated Title: "Cosmic Blue"
   ```

3. **Generic** (last resort):
   ```
   Image ID: generated_787679c7_0
   Generated Title: "Abstract Design 787679C7"
   ```

**Title Features:**
- Capitalizes words properly
- Removes technical terms (like "high quality", "print-ready")
- Limits to 100 characters
- Always unique per image

### Auto-Description Generation

**Template-based descriptions with variety:**

```python
# Templates rotate based on image_id hash for consistency
templates = [
    "Unique {style} design featuring bold colors and striking composition...",
    "Eye-catching {style} creation with vibrant details...",
    "Original {style} artwork transformed into wearable art...",
    "Bold and dynamic {style} piece that combines creativity with comfort...",
    "Stunning {style} design with intricate patterns and vivid colors..."
]
```

**Same image always gets same description** (deterministic based on hash)

**Customizable style:**
```bash
curl -X POST http://localhost:5000/api/publish/IMAGE_ID \
  -H "Content-Type: application/json" \
  -d '{"style": "geometric art"}'
```

**Result:** "Unique geometric art design featuring bold colors..."

---

## 🔧 Single Image Publishing API

### Endpoint
```
POST /api/publish/<image_id>
```

### Request Body (All Optional!)

```json
{
  "title": "Optional custom title",
  "description": "Optional custom description",
  "prompt": "Optional prompt hint for auto-title",
  "style": "abstract art",
  "price_cents": 3499,
  "color_filter": "black",
  "max_variants": 50
}
```

### Examples

**1. Fully Automatic (No parameters)**
```bash
curl -X POST http://localhost:5000/api/publish/generated_787679c7_0 \
  -H "Content-Type: application/json" \
  -d '{}'
```
- ✅ Auto-generated title
- ✅ Auto-generated description
- ✅ Default POD settings (black, 50 variants, $34.99)

**2. Custom Title, Auto Description**
```bash
curl -X POST http://localhost:5000/api/publish/generated_787679c7_0 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cosmic Dreams Hoodie",
    "style": "psychedelic art"
  }'
```
- ✅ Uses your title
- ✅ Auto-generated description with "psychedelic art" style

**3. Everything Custom**
```bash
curl -X POST http://localhost:5000/api/publish/generated_787679c7_0 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Limited Edition Abstract",
    "description": "Exclusive design limited to 100 pieces",
    "price_cents": 4999,
    "color_filter": "white",
    "max_variants": 25
  }'
```
- ✅ All custom settings
- ✅ Premium pricing ($49.99)
- ✅ White variants only, max 25

**4. Auto-Title from Prompt**
```bash
curl -X POST http://localhost:5000/api/publish/generated_787679c7_0 \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "neon cyberpunk cityscape at night"
  }'
```
- ✅ Title: "Neon Cyberpunk Cityscape At Night"
- ✅ Auto-description

---

## 📦 Batch Publishing API

### Endpoint
```
POST /api/batch_publish
```

### Request Body

```json
{
  "image_ids": ["id1", "id2"],     // Optional, empty = all approved
  "auto_approve": false,            // Auto-approve pending images
  "style": "abstract art",          // Style for auto-descriptions
  "price_cents": 3499,              // Optional override
  "color_filter": "black",          // Optional override
  "max_variants": 50                // Optional override
}
```

### Response Format

```json
{
  "success": true,
  "results": {
    "total": 10,
    "succeeded": [
      {
        "image_id": "generated_abc123_0",
        "product_id": "123456789",
        "title": "Abstract Design ABC123"
      }
    ],
    "failed": [
      {
        "image_id": "generated_xyz789_0",
        "error": "Image file not found"
      }
    ],
    "skipped": [
      {
        "image_id": "generated_old_0",
        "reason": "Not approved (status: rejected)"
      }
    ]
  },
  "summary": {
    "total": 10,
    "succeeded": 8,
    "failed": 1,
    "skipped": 1
  }
}
```

### Examples

**1. Publish All Approved Images**
```bash
curl -X POST http://localhost:5000/api/batch_publish \
  -H "Content-Type: application/json" \
  -d '{}'
```

**2. Auto-Approve and Publish Everything**
```bash
curl -X POST http://localhost:5000/api/batch_publish \
  -H "Content-Type: application/json" \
  -d '{
    "auto_approve": true
  }'
```

**3. Publish Specific Images**
```bash
curl -X POST http://localhost:5000/api/batch_publish \
  -H "Content-Type: application/json" \
  -d '{
    "image_ids": ["generated_abc123_0", "generated_xyz789_0"],
    "style": "geometric art"
  }'
```

**4. Premium Batch with Custom Settings**
```bash
curl -X POST http://localhost:5000/api/batch_publish \
  -H "Content-Type: application/json" \
  -d '{
    "auto_approve": true,
    "style": "minimalist design",
    "price_cents": 4499,
    "color_filter": "white",
    "max_variants": 30
  }'
```

---

## 🖥️ CLI Tool Usage

### Basic Commands

**Publish all approved:**
```bash
./batch-publish.sh --all
```

**Auto-approve and publish:**
```bash
./batch-publish.sh --all --auto-approve
```

**Publish specific images:**
```bash
./batch-publish.sh --ids "generated_abc123_0,generated_xyz789_0"
```

### Advanced Options

**Custom style:**
```bash
./batch-publish.sh --all --style "geometric art"
```

**Premium pricing:**
```bash
./batch-publish.sh --all --price 4499  # $44.99
```

**White variants:**
```bash
./batch-publish.sh --all --color "white"
```

**Limit variants:**
```bash
./batch-publish.sh --all --max-variants 25
```

**All together:**
```bash
./batch-publish.sh --all --auto-approve \
  --style "minimalist design" \
  --price 4999 \
  --color "white" \
  --max-variants 20
```

### Output Example

```
🚀 Batch POD Publisher
======================

📋 Publishing all approved images...

🎨 Settings:
   Style: abstract art
   Price: $34.99
   Color: black
   Max variants: 50

🔄 Starting batch publish...

✅ Batch publish complete!

📊 Summary:
   Total:     10
   Succeeded: 8
   Failed:    1
   Skipped:   1

✅ Published products:
   • Abstract Design ABC123 (ID: 123456789)
   • Cosmic Dreams (ID: 123456790)
   • Geometric Patterns (ID: 123456791)
   ...

❌ Failed:
   • generated_bad_0: Image file not found

⏭️  Skipped:
   • generated_old_0: Not approved (status: rejected)
```

---

## 🎨 Customizing Auto-Metadata

### Changing Description Templates

Edit `gateway/app/main.py`, find `generate_auto_description()`:

```python
templates = [
    "Your custom template 1 with {style}...",
    "Your custom template 2 with {style}...",
    # Add more templates
]
```

### Changing Title Generation Logic

Edit `gateway/app/main.py`, find `generate_auto_title()`:

```python
def generate_auto_title(image_id: str, prompt: str = None) -> str:
    # Customize title generation logic
    if prompt:
        # Your custom prompt-to-title logic
        pass
    # Your custom ID-to-title logic
```

---

## 📊 Best Practices

### For High-Volume Stores

**1. Use batch publishing for efficiency:**
```bash
./batch-publish.sh --all --auto-approve
```

**2. Consistent style across catalog:**
```bash
./batch-publish.sh --all --style "abstract geometric"
```

**3. Limit variants aggressively:**
```bash
./batch-publish.sh --all --max-variants 25
```

### For Premium/Curated Stores

**1. Manual approval, then batch:**
```bash
# Approve images in UI first
./batch-publish.sh --all  # No auto-approve
```

**2. Custom descriptions per image:**
```bash
# Use API for each image with custom description
curl -X POST http://localhost:5000/api/publish/IMAGE_ID \
  -d '{"title": "...", "description": "..."}'
```

**3. Higher pricing, limited variants:**
```bash
./batch-publish.sh --all \
  --price 5999 \
  --max-variants 15
```

### For Testing

**1. Test with single image:**
```bash
curl -X POST http://localhost:5000/api/publish/test_image_0 -d '{}'
```

**2. Test batch with specific IDs:**
```bash
./batch-publish.sh --ids "test1,test2,test3"
```

**3. Use different styles to see variety:**
```bash
./batch-publish.sh --all --style "cyberpunk art"
./batch-publish.sh --all --style "minimalist design"
```

---

## 🔍 Troubleshooting

### Auto-Titles Look Wrong

**Problem:** Titles like "Generated 787679C7"

**Solution:** Pass `prompt` parameter for better titles:
```bash
curl -X POST http://localhost:5000/api/publish/IMAGE_ID \
  -d '{"prompt": "vibrant abstract geometric patterns"}'
```

### All Images Skipped

**Problem:** "Not approved (status: pending)"

**Solution:** Use auto-approve or approve images first:
```bash
./batch-publish.sh --all --auto-approve
```

### Batch Fails Midway

**Problem:** Some images fail, stops processing

**Solution:** Batch continues on failures! Check response for details:
- `results.succeeded`: What worked
- `results.failed`: What didn't (with errors)
- `results.skipped`: What was skipped (with reasons)

### Want Different Description Styles

**Problem:** All descriptions sound similar

**Solution:** Add more templates to `generate_auto_description()` or use custom descriptions:
```bash
curl -X POST http://localhost:5000/api/publish/IMAGE_ID \
  -d '{"description": "Your unique description here"}'
```

---

## 📈 Performance

### Single Image
- Auto-title: ~1ms
- Auto-description: ~1ms
- Total publish: ~15-20 seconds (mostly Printify API)

### Batch Processing
- 10 images: ~2-3 minutes
- 50 images: ~12-15 minutes
- 100 images: ~25-30 minutes

**Sequential processing** ensures:
- ✅ Reliable error tracking
- ✅ Detailed per-image results
- ✅ No API rate limiting issues

---

## 🎓 Pro Tips

1. **Test auto-metadata first**: Publish 1-2 images to see how titles/descriptions look
2. **Use consistent style**: Pick one style keyword and stick with it for catalog consistency
3. **Batch in smaller groups**: 25-50 images per batch for better control
4. **Monitor logs**: Gateway logs show detailed progress for each image
5. **Save successful settings**: Once you find settings that work, use them consistently

---

**Last Updated**: 2026-01-21
**Related**: POD_PIPELINE_GUIDE.md, POD_OPTIMIZATION_GUIDE.md
