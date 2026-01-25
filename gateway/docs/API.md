# POD Gateway API Documentation

Complete API reference for the POD (Print-on-Demand) Gateway.

**Base URL**: `http://localhost:5000`

**Version**: v1.2.1

---

## Table of Contents

- [Image Generation](#image-generation)
- [Image Management](#image-management)
- [Publishing](#publishing)
- [Batch Operations](#batch-operations)
- [System](#system)

---

## Image Generation

### Generate Image

Generate a new image using AI.

**Endpoint**: `POST /api/generate`

**Request Body**:
```json
{
  "prompt": "string (required, 1-5000 chars)",
  "style": "string (optional)",
  "genre": "string (optional)",
  "seed": "integer (optional)",
  "width": "integer (optional, default: 1024)",
  "height": "integer (optional, default: 1024)",
  "steps": "integer (optional, default: 20)",
  "cfg_scale": "number (optional, default: 7.0)"
}
```

**Validation**:
- `prompt`: Required, 1-5000 characters
- `width`: Must be 512-2048
- `height`: Must be 512-2048
- `steps`: Must be 1-100
- `cfg_scale`: Must be 1.0-20.0

**Response** (202 Accepted):
```json
{
  "success": true,
  "message": "Image generation started",
  "prompt_id": "abc123",
  "image_id": "generated_abc123_0",
  "status": "generating"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Validation error message"
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cityscape at night",
    "style": "neon",
    "seed": 42
  }'
```

---

## Image Management

### List Images

Get all images with optional status filtering.

**Endpoint**: `GET /api/images`

**Query Parameters**:
- `status` (optional): Filter by status (generating, ready, publishing, published, failed)

**Response**:
```json
{
  "images": [
    {
      "image_id": "generated_abc123_0",
      "status": "ready",
      "prompt": "cyberpunk cityscape",
      "created_at": "2026-01-25T10:30:00Z",
      "file_path": "/path/to/image.png"
    }
  ],
  "total": 1
}
```

**Example**:
```bash
# Get all images
curl http://localhost:5000/api/images

# Get only ready images
curl http://localhost:5000/api/images?status=ready
```

### Get Image Status

Get detailed status of a specific image.

**Endpoint**: `GET /api/images/<image_id>`

**Response**:
```json
{
  "image_id": "generated_abc123_0",
  "status": "ready",
  "prompt": "cyberpunk cityscape",
  "file_path": "/path/to/image.png",
  "created_at": "2026-01-25T10:30:00Z",
  "metadata": {
    "seed": 42,
    "style": "neon"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Image not found"
}
```

**Example**:
```bash
curl http://localhost:5000/api/images/generated_abc123_0
```

### Get Image File

Download the actual image file.

**Endpoint**: `GET /api/images/<image_id>/file`

**Response**: Binary image data (PNG format)

**Error Response** (404 Not Found):
```json
{
  "error": "Image file not found"
}
```

**Example**:
```bash
# Download image
curl http://localhost:5000/api/images/generated_abc123_0/file -o image.png

# Display in browser
open http://localhost:5000/api/images/generated_abc123_0/file
```

### Delete Image

Delete an image and its file.

**Endpoint**: `DELETE /api/images/<image_id>`

**Response**:
```json
{
  "success": true,
  "message": "Image deleted successfully"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Image not found"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:5000/api/images/generated_abc123_0
```

---

## Publishing

### Publish Single Image

Publish an image to Printify.

**Endpoint**: `POST /api/publish/<image_id>`

**Request Body** (all optional):
```json
{
  "title": "string (optional, 2-100 chars, auto-generated if omitted)",
  "prompt": "string (optional, helps auto-title generation)",
  "style": "string (optional, for auto-description)",
  "description": "string (optional, auto-generated if omitted)",
  "tags": ["string"] (optional, auto-generated if omitted),
  "price_cents": "integer (optional, default from config)",
  "blueprint_id": "integer (optional, default: 77 for hoodie)",
  "color_filter": "string (optional, default: 'black')",
  "max_variants": "integer (optional, default: 50)"
}
```

**Auto-Title Generation**:
- Format: `[Subject] [Style] [Product Type]`
- Length: 50-70 characters (SEO-optimized)
- Product type determined by blueprint_id:
  - 77 → "Hoodie"
  - 3, 5 → "Tee"
  - 6 → "Poster"
  - 384 → "Canvas"

**Response**:
```json
{
  "success": true,
  "message": "Image published successfully",
  "product_id": "12345",
  "product_url": "https://printify.com/app/products/12345"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Title must be between 2 and 100 characters"
}
```

**Example**:
```bash
# Publish with auto-generated title
curl -X POST http://localhost:5000/api/publish/generated_abc123_0 \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cityscape",
    "style": "neon"
  }'

# Publish with custom title
curl -X POST http://localhost:5000/api/publish/generated_abc123_0 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Neon Cityscape Cyberpunk Hoodie",
    "description": "Amazing cyberpunk hoodie",
    "tags": ["cyberpunk", "neon", "city"]
  }'

# Publish to different product type
curl -X POST http://localhost:5000/api/publish/generated_abc123_0 \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "abstract art",
    "blueprint_id": 6
  }'
# Result: "Abstract Art Poster" (blueprint 6 = Poster)
```

---

## Batch Operations

### Batch Publish

Publish multiple images at once.

**Endpoint**: `POST /api/batch-publish`

**Request Body**:
```json
{
  "image_ids": ["string"] (required if publish_all is false),
  "publish_all": "boolean (optional, default: false)",
  "title_template": "string (optional)",
  "description_template": "string (optional)",
  "tags": ["string"] (optional),
  "price_cents": "integer (optional)",
  "blueprint_id": "integer (optional)",
  "color_filter": "string (optional)",
  "max_variants": "integer (optional)"
}
```

**Templates**:
- Use `{image_id}`, `{index}`, `{total}` placeholders
- Example: `"Design #{index} of {total}"`

**Response**:
```json
{
  "success": true,
  "message": "Batch publish completed",
  "total": 10,
  "published": 8,
  "failed": 2,
  "results": {
    "published": [
      {
        "image_id": "generated_abc123_0",
        "product_id": "12345",
        "title": "Auto-generated title"
      }
    ],
    "failed": [
      {
        "image_id": "generated_xyz789_0",
        "error": "File not found"
      }
    ]
  }
}
```

**Example**:
```bash
# Publish specific images
curl -X POST http://localhost:5000/api/batch-publish \
  -H "Content-Type: application/json" \
  -d '{
    "image_ids": ["generated_abc123_0", "generated_def456_0"],
    "tags": ["batch", "hoodie"]
  }'

# Publish all ready images
curl -X POST http://localhost:5000/api/batch-publish \
  -H "Content-Type: application/json" \
  -d '{
    "publish_all": true,
    "blueprint_id": 77,
    "color_filter": "black"
  }'

# Publish with templates
curl -X POST http://localhost:5000/api/batch-publish \
  -H "Content-Type: application/json" \
  -d '{
    "image_ids": ["img1", "img2", "img3"],
    "title_template": "Design #{index} - Limited Edition",
    "tags": ["limited", "exclusive"]
  }'
```

---

## System

### Health Check

Check if the gateway is healthy.

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "printify": true,
  "image_dir": true,
  "state_file": true
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "printify": true,
  "image_dir": false,
  "state_file": true
}
```

**Example**:
```bash
curl http://localhost:5000/health
```

### Statistics

Get system statistics.

**Endpoint**: `GET /api/stats`

**Response**:
```json
{
  "total_images": 100,
  "by_status": {
    "ready": 45,
    "published": 30,
    "generating": 15,
    "failed": 10
  },
  "recent_activity": {
    "last_24h": {
      "generated": 20,
      "published": 15
    }
  }
}
```

**Example**:
```bash
curl http://localhost:5000/api/stats
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 202 | Accepted - Async operation started |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - System unhealthy |

---

## Error Handling

All errors follow this format:

```json
{
  "error": "Human-readable error message"
}
```

Common errors:
- `"Prompt is required"` - Missing required field
- `"Title must be between 2 and 100 characters"` - Validation error
- `"Image not found"` - Resource doesn't exist
- `"Image file not found"` - File missing on disk
- `"Printify API error: ..."` - External API error

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider:
- Max 60 requests/minute per IP
- Max 10 concurrent batch operations
- Max 100 images per batch

---

## Best Practices

### Title Optimization
- Let auto-generation handle it (SEO-optimized)
- If custom: 50-70 characters ideal
- Include product type: "... Hoodie"
- Use keywords but avoid keyword stuffing

### Batch Publishing
- Use `publish_all: false` for controlled batches
- Test with 1-2 images first
- Monitor failed array for issues
- Use templates for consistent branding

### Error Recovery
- Check `/api/images?status=failed` regularly
- Review error messages for patterns
- Retry failed images after fixing issues
- Use `/health` to verify system status

### Performance
- Generate images in batches (parallel)
- Publish in smaller batches (50-100)
- Use `status` filter to query only needed images
- Clean up failed/old images periodically

---

## Examples: Complete Workflows

### Workflow 1: Generate and Publish Single Image

```bash
# 1. Generate image
RESULT=$(curl -s -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "cyberpunk cat wearing hoodie"}')

IMAGE_ID=$(echo $RESULT | jq -r '.image_id')
echo "Generated: $IMAGE_ID"

# 2. Wait for generation (poll status)
while true; do
  STATUS=$(curl -s http://localhost:5000/api/images/$IMAGE_ID | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "ready" ]; then
    break
  fi
  sleep 5
done

# 3. Preview image
curl http://localhost:5000/api/images/$IMAGE_ID/file -o preview.png
open preview.png

# 4. Publish with auto-title
curl -X POST http://localhost:5000/api/publish/$IMAGE_ID \
  -H "Content-Type: application/json" \
  -d '{"prompt": "cyberpunk cat wearing hoodie"}'
```

### Workflow 2: Batch Generate and Publish

```bash
# 1. Generate multiple images
for i in {1..10}; do
  curl -s -X POST http://localhost:5000/api/generate \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"abstract design $i\", \"seed\": $i}" &
done
wait

# 2. Wait for all to complete
echo "Waiting for generation..."
sleep 60

# 3. Get all ready images
READY=$(curl -s 'http://localhost:5000/api/images?status=ready' | jq -r '.images[].image_id')
echo "Ready images: $(echo $READY | wc -l)"

# 4. Batch publish all
curl -X POST http://localhost:5000/api/batch-publish \
  -H "Content-Type: application/json" \
  -d '{"publish_all": true, "blueprint_id": 77}'
```

### Workflow 3: Monitor and Retry Failed

```bash
# 1. Check failed images
FAILED=$(curl -s 'http://localhost:5000/api/images?status=failed')
echo $FAILED | jq '.images[] | {id: .image_id, error: .metadata.error_message}'

# 2. Retry specific failed image
curl -X POST http://localhost:5000/api/publish/generated_failed_0 \
  -H "Content-Type: application/json" \
  -d '{"title": "Fixed Title"}'

# 3. Clean up old failed images
curl -s 'http://localhost:5000/api/images?status=failed' | \
  jq -r '.images[].image_id' | \
  while read id; do
    curl -X DELETE http://localhost:5000/api/images/$id
  done
```

---

## Changelog

### v1.2.1 (2026-01-25)
- **New**: Product-aware auto-title generation
- **New**: SEO-optimized title length (50-70 chars)
- **New**: Startup config validation
- **New**: Exponential backoff for polling
- **Improved**: Input validation for generate endpoint
- **Improved**: Specific exception handling
- **Improved**: Better error messages

### v1.2.0
- **New**: Batch publishing endpoint
- **New**: Auto-description generation
- **Improved**: State management

### v1.1.0
- **New**: RunPod integration
- **New**: Auto-title generation
- **Improved**: Image status tracking

---

## Support

For issues or questions:
- GitHub: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- Check `/health` endpoint for system status
- Review logs in `gateway/logs/`

**Current Version**: v1.2.1
**Last Updated**: 2026-01-25
