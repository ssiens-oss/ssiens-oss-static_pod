# Batch Generation Guide

## Overview

Generate up to 25 variations of the same prompt in a single request. Perfect for:
- Creating product line variations
- A/B testing different designs
- Building diverse portfolio quickly
- Testing prompt consistency

---

## Quick Start

### Single Image (Default)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cat neon lights"
  }'
```

### Batch Generation (5 Images)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cat neon lights",
    "batch_size": 5
  }'
```

---

## API Reference

### POST /api/generate

**Request Body:**
```json
{
  "prompt": "Base prompt text (required)",
  "style": "Optional style descriptor",
  "genre": "Optional genre descriptor",
  "batch_size": 1-25,
  "width": 4500,
  "height": 5400,
  "steps": 30,
  "cfg_scale": 2.0,
  "seed": null
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | **required** | Base prompt text |
| `batch_size` | int | 1 | Number of images to generate (1-25) |
| `style` | string | "" | Style descriptor (e.g., "digital art") |
| `genre` | string | "" | Genre descriptor (e.g., "futuristic") |
| `width` | int | 4500 | Image width (t-shirt template standard) |
| `height` | int | 5400 | Image height (t-shirt template standard) |
| `steps` | int | 30 | Sampling steps (Flux: 30-50) |
| `cfg_scale` | float | 2.0 | CFG scale (Flux: 1.0-3.5) |
| `seed` | int | null | Random seed (first image only in batch) |

**Response (Success):**
```json
{
  "status": "completed",
  "batch_id": "batch_abc123def456",
  "batch_size": 5,
  "success_count": 5,
  "failed_count": 0,
  "prompt": "cyberpunk cat neon lights, high contrast, bold colors...",
  "images": [
    "generated_xyz123.png",
    "generated_abc456.png",
    "generated_def789.png",
    "generated_ghi012.png",
    "generated_jkl345.png"
  ],
  "prompt_ids": ["prompt_1", "prompt_2", "prompt_3", "prompt_4", "prompt_5"],
  "message": "Generated 5 of 5 image(s)"
}
```

**Response (Partial Success):**
```json
{
  "status": "completed",
  "batch_id": "batch_abc123def456",
  "batch_size": 10,
  "success_count": 8,
  "failed_count": 2,
  "images": [...],
  "message": "Generated 8 of 10 image(s)"
}
```

**Response (Failure):**
```json
{
  "status": "failed",
  "batch_id": "batch_abc123def456",
  "error": "No images were generated",
  "failed_count": 5
}
```

---

## Batch Info Endpoint

### GET /api/batch/<batch_id>

Query information about a completed batch.

**Example:**
```bash
curl http://localhost:5000/api/batch/batch_abc123def456 | python3 -m json.tool
```

**Response:**
```json
{
  "success": true,
  "batch_id": "batch_abc123def456",
  "batch_size": 5,
  "images": [
    {
      "id": "generated_xyz123",
      "filename": "generated_xyz123.png",
      "batch_index": 0,
      "status": "approved",
      "metadata": {
        "original_prompt": "cyberpunk cat neon lights",
        "style": "digital art",
        "genre": "futuristic"
      }
    },
    ...
  ],
  "metadata": {
    "original_prompt": "cyberpunk cat neon lights",
    "style": "digital art",
    "genre": "futuristic",
    "full_prompt": "cyberpunk cat neon lights, digital art style...",
    "batch_size": 5
  }
}
```

---

## How It Works

### Sequential Generation
Batch images are generated **sequentially** (one at a time):

1. Generate image 1 → wait for completion
2. Generate image 2 → wait for completion
3. Continue until batch_size reached

**Why Sequential?**
- RunPod serverless processes one request at a time
- Prevents overwhelming the GPU
- Better error handling and progress tracking
- Avoids timeout issues

### Random Seed Behavior

- **First image:** Uses provided `seed` if specified, otherwise random
- **Remaining images:** Always use random seeds for variation
- **Result:** Each image in batch is unique

**Example:**
```bash
# First image uses seed 12345, rest are random
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "geometric pattern",
    "batch_size": 10,
    "seed": 12345
  }'
```

### Batch Tracking

Each image stores batch metadata:
```json
{
  "batch_id": "batch_abc123def456",
  "batch_index": 0,
  "batch_size": 10,
  "original_prompt": "cyberpunk cat",
  "style": "digital art"
}
```

Use `/api/batch/<batch_id>` to retrieve all images in a batch.

---

## Performance & Timing

### Generation Time Estimates

**Per Image:** ~60-90 seconds (4500x5400, 30 steps, CFG 2.0)

**Batch Times:**

| Batch Size | Total Time | Use Case |
|------------|------------|----------|
| 1 | ~1 min | Single design |
| 5 | ~5-7 min | Small product line |
| 10 | ~10-15 min | Medium collection |
| 25 | ~25-37 min | Full portfolio batch |

**Recommendation:** Start with batch_size 5-10 for testing, scale up as needed.

### Progress Tracking

Watch terminal logs for real-time progress:

```
INFO - Starting batch generation: 10 images (batch_id: batch_abc123def456)
INFO - Generating image 1/10...
INFO - Submitting workflow to RunPod serverless...
INFO - RunPod result status: COMPLETED
INFO - ✓ Image 1/10 downloaded
INFO - Generating image 2/10...
...
INFO - ✓ Image 10/10 downloaded
INFO - Batch generation complete: 10/10 images generated
```

---

## Use Cases

### 1. Product Line Variations

Generate multiple variations for different products:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "mountain landscape sunset",
    "batch_size": 10,
    "style": "minimalist",
    "genre": "nature"
  }'
```

**Result:** 10 unique variations of the same concept for hoodies, t-shirts, posters, etc.

### 2. A/B Testing

Generate variations to test which design performs best:

```bash
# Generate 5 variations
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "retro gaming controller",
    "batch_size": 5
  }'

# Approve all 5
# Publish all 5 to Shopify
# Monitor performance metrics
# Disable low performers after 14 days
```

### 3. Quick Portfolio Building

Generate diverse designs quickly:

```bash
# Morning batch
curl -X POST http://localhost:5000/api/generate \
  -d '{"prompt": "abstract geometric", "batch_size": 25}'

# Afternoon batch
curl -X POST http://localhost:5000/api/generate \
  -d '{"prompt": "nature landscape", "batch_size": 25}'

# Result: 50 designs in one day
```

### 4. Seasonal Collections

Generate themed collections for holidays/seasons:

```bash
# Halloween collection
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "spooky halloween pumpkin",
    "batch_size": 15,
    "style": "vintage",
    "genre": "horror"
  }'
```

---

## Batch Management Workflow

### 1. Generate Batch
```bash
BATCH_RESULT=$(curl -s -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cityscape",
    "batch_size": 5
  }')

echo "$BATCH_RESULT" | python3 -m json.tool
```

### 2. Extract Batch ID
```bash
BATCH_ID=$(echo "$BATCH_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['batch_id'])")
echo "Batch ID: $BATCH_ID"
```

### 3. Query Batch Info
```bash
curl -s "http://localhost:5000/api/batch/$BATCH_ID" | python3 -m json.tool
```

### 4. Approve All Images in Batch
```bash
# Get all image IDs from batch
IMAGE_IDS=$(curl -s "http://localhost:5000/api/batch/$BATCH_ID" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([img['id'] for img in data['images']]))")

# Approve each image
for IMG_ID in $IMAGE_IDS; do
  echo "Approving $IMG_ID..."
  curl -s -X POST "http://localhost:5000/api/approve/$IMG_ID"
done
```

### 5. Publish All Images in Batch
```bash
# Publish each approved image
for IMG_ID in $IMAGE_IDS; do
  echo "Publishing $IMG_ID..."
  curl -s -X POST "http://localhost:5000/api/publish/$IMG_ID" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "",
      "product_type": "hoodie",
      "platform": "printify"
    }'
done
```

---

## Best Practices

### 1. Start Small
- Begin with `batch_size: 5` to test prompts
- Scale up to 10-25 once you're confident in the prompt

### 2. Monitor Progress
- Watch terminal logs during generation
- Look for "✓ Image X/Y downloaded" progress indicators
- Check for any warnings or errors

### 3. Use Batch IDs
- Always save the `batch_id` from the response
- Use `/api/batch/<batch_id>` to retrieve batch info later
- Helps with organization and tracking

### 4. Optimize for Speed vs Quality
**Fast (test batches):**
```json
{
  "batch_size": 5,
  "steps": 25,
  "cfg_scale": 2.5,
  "width": 3600,
  "height": 3600
}
```

**Quality (production batches):**
```json
{
  "batch_size": 10,
  "steps": 30,
  "cfg_scale": 2.0,
  "width": 4500,
  "height": 5400
}
```

### 5. Handle Partial Failures
```bash
# Check if any images failed
SUCCESS_COUNT=$(echo "$BATCH_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['success_count'])")
BATCH_SIZE=$(echo "$BATCH_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['batch_size'])")

if [ "$SUCCESS_COUNT" -lt "$BATCH_SIZE" ]; then
  echo "Warning: Only $SUCCESS_COUNT of $BATCH_SIZE images generated"
  # Re-run failed images individually
fi
```

---

## Limitations

### RunPod Serverless Only
- Batch generation requires RunPod serverless
- Direct ComfyUI connection does not support batch mode
- Returns error if batch_size > 1 with direct ComfyUI

### Maximum Batch Size: 25
- Hard limit: 25 images per request
- Requests with batch_size > 25 will be capped to 25
- For larger batches, make multiple requests

### Sequential Processing
- Images generated one at a time (not parallel)
- Total time = batch_size × per-image time
- 25 images could take ~25-37 minutes

### Timeout Considerations
- Each image has 120-second timeout
- If RunPod is slow, some images may timeout
- Check `failed_count` in response

---

## Troubleshooting

### "Batch generation not supported with direct ComfyUI"

**Problem:** Trying to use batch_size > 1 with direct ComfyUI

**Solution:** Configure RunPod serverless:
```bash
export RUNPOD_API_KEY="your_key"
export RUNPOD_ENDPOINT_ID="your_endpoint_id"
```

### Batch takes too long

**Problem:** 25-image batch taking 30+ minutes

**Options:**
1. **Reduce batch size:** Use 10-15 instead of 25
2. **Reduce resolution:** 3600x3600 instead of 4500x5400
3. **Reduce steps:** 25 instead of 30
4. **Upgrade RunPod instance:** Faster GPU = faster generation

### Some images failed in batch

**Problem:** `success_count < batch_size`

**Check:**
1. RunPod endpoint status (may be throttling)
2. Terminal logs for specific error messages
3. VRAM usage (may need larger GPU)

**Solution:**
```bash
# Get successfully generated images
curl -s "http://localhost:5000/api/batch/$BATCH_ID" | python3 -m json.tool

# Re-run failed images individually
curl -X POST http://localhost:5000/api/generate \
  -d '{"prompt": "same prompt", "batch_size": 1}'
```

### Can't find batch_id

**Problem:** Lost batch_id from generation response

**Solution:** Search state file for images:
```bash
# All images store batch metadata
curl -s http://localhost:5000/api/images | python3 -m json.tool

# Look for images with same prompt/timestamp
# Check metadata.batch_id field
```

---

## Advanced: Batch Analytics

### Track Batch Performance

After publishing all images in a batch, compare performance:

```bash
# Get batch info
BATCH_DATA=$(curl -s "http://localhost:5000/api/batch/$BATCH_ID")

# For each image, get metrics
echo "$BATCH_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for img in data['images']:
    print(f\"{img['id']}: {img['status']}\")
"

# Compare which variations performed best
# Disable low performers
# Expand top performers to more product types
```

### Batch Success Rate

Track how many images from each batch get approved:

```bash
# Get batch
BATCH_DATA=$(curl -s "http://localhost:5000/api/batch/$BATCH_ID")

# Count approved
APPROVED=$(echo "$BATCH_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(sum(1 for img in data['images'] if img['status'] == 'approved'))
")

echo "Approval rate: $APPROVED / ${BATCH_SIZE}"
```

---

## Summary

✅ **Batch generation enabled:** Generate 1-25 images per request
✅ **Sequential processing:** Reliable, progress-tracked generation
✅ **Batch tracking:** Query batch info via `/api/batch/<batch_id>`
✅ **Unique variations:** Random seeds for diversity
✅ **Production-ready:** Optimized for POD workflows

**Next Steps:**
1. Test with small batches (5 images)
2. Optimize prompt and settings
3. Scale up to larger batches (10-25)
4. Build automated batch workflows
5. Track batch performance analytics
