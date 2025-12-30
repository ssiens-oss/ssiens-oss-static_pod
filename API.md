# StaticWaves POD API Reference

Complete API documentation for the StaticWaves POD automation system.

**Base URL**: `http://localhost:5000` (default)

---

## Authentication

Currently, the API does not require authentication for local use.

For production deployments, consider adding:
- API key authentication
- JWT tokens
- IP whitelisting

---

## Health & Status

### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "alive",
  "timestamp": "2024-01-15T12:00:00.000000Z",
  "version": "1.0.0"
}
```

---

## License

### `GET /license`

Check license status and tier information.

**Response** (Valid):
```json
{
  "valid": true,
  "license": {
    "client_id": "acme",
    "tier": "agency",
    "expires": "2025-12-31",
    "max_skus_per_day": 50
  }
}
```

**Response** (Invalid):
```json
{
  "valid": false,
  "error": "License expired on 2024-12-31"
}
```

**Status Codes**:
- `200` - Valid license
- `403` - Invalid/expired license

---

## Publishing

### `POST /publish`

Publish a product through the complete POD pipeline.

**Request Body**:
```json
{
  "title": "Cosmic Waves Hoodie",
  "description": "AI-generated cosmic design featuring nebula and stars",
  "prompt": "cosmic waves nebula stars galaxy purple blue",
  "type": "hoodie",
  "base_cost": 35.00,
  "inventory": 100
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Product title (max 60 chars) |
| `description` | string | No | Product description (max 5000 chars) |
| `prompt` | string | Yes | AI generation prompt |
| `type` | string | Yes | Product type: `hoodie`, `tee`, `poster`, `mug` |
| `base_cost` | float | Yes | Base cost in USD ($5-$500) |
| `inventory` | integer | Yes | Stock quantity (> 0) |

**Response** (Success):
```json
{
  "success": true,
  "result": {
    "sku": "SW-HOO-20240115120000",
    "printify_id": "printify_abc123",
    "shopify_id": "shopify_def456",
    "tiktok_id": "tiktok_ghi789",
    "timestamp": "2024-01-15T12:00:00.000000Z"
  }
}
```

**Response** (Error):
```json
{
  "success": false,
  "error": "Title too long: 75 chars (max 60)"
}
```

**Status Codes**:
- `200` - Success
- `400` - Validation error
- `403` - License error

**Pipeline Steps**:
1. Validate product data (TikTok compliance)
2. Calculate pricing (cost + margin)
3. Generate design (ComfyUI)
4. Create mockups (templates)
5. Upload to Printify
6. Publish to Shopify
7. Sync to TikTok Shop
8. Send alert notifications

---

## Queue Management

### `GET /queue`

Get queue status across all stages.

**Response**:
```json
{
  "pending": 5,
  "processing": 2,
  "done": 127,
  "failed": 3
}
```

---

### `GET /queue/<stage>`

Get items in a specific queue stage.

**Stages**: `pending`, `processing`, `done`, `failed`

**Example**: `GET /queue/pending`

**Response**:
```json
[
  {
    "title": "Neon Dreams Tee",
    "prompt": "neon cyberpunk cityscape",
    "type": "tee",
    "base_cost": 18.00,
    "inventory": 50
  },
  {
    "title": "Ocean Vibes Poster",
    "prompt": "ocean waves sunset peaceful",
    "type": "poster",
    "base_cost": 12.00,
    "inventory": 30
  }
]
```

**Status Codes**:
- `200` - Success
- `400` - Invalid stage
- `500` - Server error

---

### `POST /queue/add`

Add an item to the pending queue (for batch processing).

**Request Body**:
```json
{
  "title": "Mountain Sunset Hoodie",
  "prompt": "mountain peaks sunset golden hour",
  "type": "hoodie",
  "base_cost": 35.00,
  "inventory": 75,
  "description": "Majestic mountain landscape at sunset"
}
```

**Response**:
```json
{
  "success": true,
  "id": "20240115_120000_Mountain_Sunset_Hood"
}
```

**Status Codes**:
- `200` - Success
- `400` - Validation error
- `403` - License error

---

## Statistics

### `GET /stats`

Get system-wide statistics.

**Response**:
```json
{
  "designs": 132,
  "queue": {
    "pending": 5,
    "processing": 2,
    "done": 127,
    "failed": 3
  },
  "timestamp": "2024-01-15T12:00:00.000000Z"
}
```

---

## Validation Rules

The API enforces TikTok Shop compliance rules:

### Title Rules
- Required
- Max 60 characters
- No prohibited words: `free`, `giveaway`, `replica`, `fake`
- No trademark violations

### Description Rules
- Optional
- Max 5000 characters
- No prohibited content

### Inventory Rules
- Required
- Must be positive integer
- Cannot be zero

### Price Rules
- Minimum: $5.00
- Maximum: $500.00

### Product Types
Valid types:
- `hoodie`
- `tee`
- `poster`
- `mug`
- `tank`
- `sweatshirt`

---

## Error Codes

| Status | Meaning | Example |
|--------|---------|---------|
| `200` | Success | Request completed |
| `400` | Bad Request | Invalid product data |
| `403` | Forbidden | License expired |
| `404` | Not Found | Endpoint doesn't exist |
| `500` | Server Error | Internal error |

---

## Rate Limiting

Rate limits are enforced based on license tier:

| Tier | Requests/minute | SKUs/day |
|------|----------------|----------|
| Solo | 60 | 10 |
| Agency | 120 | 50 |
| Enterprise | 300 | 500 |
| Unlimited | ∞ | ∞ |

---

## Webhooks (Coming Soon)

Subscribe to events:
- `product.published`
- `product.failed`
- `queue.completed`
- `license.expiring`

---

## Python SDK Example

```python
import requests

API_BASE = "http://localhost:5000"

def publish_product(product_data):
    response = requests.post(
        f"{API_BASE}/publish",
        json=product_data
    )
    return response.json()

# Usage
result = publish_product({
    "title": "Cosmic Hoodie",
    "prompt": "cosmic nebula stars",
    "type": "hoodie",
    "base_cost": 35.00,
    "inventory": 100
})

print(result)
```

---

## cURL Examples

### Publish Product
```bash
curl -X POST http://localhost:5000/publish \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sunset Vibes Tee",
    "prompt": "sunset beach palm trees",
    "type": "tee",
    "base_cost": 18.00,
    "inventory": 50
  }'
```

### Add to Queue
```bash
curl -X POST http://localhost:5000/queue/add \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Forest Dreams Poster",
    "prompt": "forest mist morning light",
    "type": "poster",
    "base_cost": 12.00,
    "inventory": 30
  }'
```

### Check Status
```bash
curl http://localhost:5000/stats
```

---

## JavaScript/TypeScript Example

```typescript
const API_BASE = "http://localhost:5000";

interface ProductData {
  title: string;
  prompt: string;
  type: string;
  base_cost: number;
  inventory: number;
  description?: string;
}

async function publishProduct(data: ProductData) {
  const response = await fetch(`${API_BASE}/publish`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return await response.json();
}

// Usage
const result = await publishProduct({
  title: "Neon City Hoodie",
  prompt: "neon city cyberpunk futuristic",
  type: "hoodie",
  base_cost: 35.00,
  inventory: 100,
});

console.log(result);
```

---

## Support

For API issues or questions:
- [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- Email: ops@staticwaves.io
