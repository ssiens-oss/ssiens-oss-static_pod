# API Integration Guide

This guide explains how to replace the mock POD simulation with real Printify API integration.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [API Configuration](#api-configuration)
- [Replacing Mock Engine](#replacing-mock-engine)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Best Practices](#best-practices)

## Prerequisites

1. **Printify Account**: Sign up at [printify.com](https://printify.com)
2. **API Token**: Generate token in account settings
3. **Shop Connected**: Connect your e-commerce shop (Shopify, Etsy, etc.)
4. **Blueprint Access**: Know your product blueprint IDs

## Setup

### 1. Install Dependencies

```bash
npm install axios
```

### 2. Environment Variables

Create a `.env.local` file:

```env
VITE_PRINTIFY_API_KEY=your_api_token_here
VITE_PRINTIFY_SHOP_ID=your_shop_id_here
VITE_API_BASE_URL=https://api.printify.com/v1
```

### 3. API Configuration File

Create `services/printifyApi.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.printify.com/v1';
const API_KEY = import.meta.env.VITE_PRINTIFY_API_KEY;
const SHOP_ID = import.meta.env.VITE_PRINTIFY_SHOP_ID;

export const printifyApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  }
});

// Rate limiting helper
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 100; // 100ms between requests

export const rateLimitedRequest = async <T>(
  requestFn: () => Promise<T>
): Promise<T> => {
  const now = Date.now();
  const timeSinceLastRequest = now - lastRequestTime;

  if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
    await new Promise(resolve =>
      setTimeout(resolve, MIN_REQUEST_INTERVAL - timeSinceLastRequest)
    );
  }

  lastRequestTime = Date.now();
  return requestFn();
};

export { SHOP_ID };
```

## Replacing Mock Engine

### Original Mock Engine

The current `services/mockEngine.ts` simulates the workflow:

```typescript
export const runSimulation = async (
  dropName: string,
  isBatch: boolean,
  // callbacks...
) => {
  // Simulated workflow
};
```

### Real API Engine

Create `services/printifyEngine.ts`:

```typescript
import { printifyApi, rateLimitedRequest, SHOP_ID } from './printifyApi';
import { LogType, LogEntry, QueueItem } from '../types';
import { createLogEntry, sleep } from '../utils/podUtils';

interface PrintifyProduct {
  id: string;
  title: string;
  description: string;
  blueprint_id: number;
  print_provider_id: number;
  variants: Array<{
    id: number;
    price: number;
    is_enabled: boolean;
  }>;
  images: Array<{
    src: string;
    position: string;
    is_default: boolean;
  }>;
}

type LogCallback = (entry: LogEntry) => void;
type ProgressCallback = (val: number) => void;
type QueueCallback = (item: QueueItem) => void;
type ImageCallback = (type: 'design' | 'mockup', url: string) => void;

export const runPrintifyWorkflow = async (
  dropName: string,
  config: {
    designCount: number;
    blueprintId: number;
    providerId: number;
  },
  onLog: LogCallback,
  onProgress: ProgressCallback,
  onQueue: QueueCallback,
  onImage: ImageCallback,
  shouldStop: () => boolean
) => {
  const addLog = (msg: string, type: LogType = LogType.INFO) => {
    onLog(createLogEntry(msg, type));
  };

  try {
    if (shouldStop()) return;

    addLog(`🚀 Starting Printify workflow for: ${dropName}`, LogType.INFO);
    onProgress(5);

    // Step 1: Upload Design Image
    addLog(`Uploading design image to Printify...`, LogType.INFO);

    const designFile = await uploadDesignImage(dropName);
    onImage('design', designFile.url);
    addLog(`Design uploaded: ${designFile.file_name}`, LogType.SUCCESS);
    onProgress(25);

    if (shouldStop()) return;

    // Step 2: Create Product
    addLog(`Creating product on Printify...`, LogType.INFO);

    const product = await createProduct({
      title: `${dropName} - T-Shirt`,
      description: `Product from ${dropName} collection`,
      blueprint_id: config.blueprintId,
      print_provider_id: config.providerId,
      design_image_id: designFile.id
    });

    addLog(`Product created: ID ${product.id}`, LogType.SUCCESS);
    onImage('mockup', product.images[0].src);
    onProgress(50);

    if (shouldStop()) return;

    // Step 3: Publish to Shop
    addLog(`Publishing product to shop...`, LogType.INFO);

    const queueId = product.id;
    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'uploading' });

    await publishProduct(product.id);

    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'completed' });
    addLog(`✅ Product published successfully`, LogType.SUCCESS);
    onProgress(100);

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    addLog(`❌ Error: ${errorMsg}`, LogType.ERROR);
    throw error;
  }
};

// Helper Functions

async function uploadDesignImage(dropName: string): Promise<any> {
  // In real implementation, you would:
  // 1. Generate or load your design image
  // 2. Upload to Printify's image upload endpoint

  const response = await rateLimitedRequest(() =>
    printifyApi.post('/uploads/images.json', {
      file_name: `${dropName}_design.png`,
      url: 'YOUR_IMAGE_URL_HERE' // Your design image URL
    })
  );

  return response.data;
}

async function createProduct(productData: any): Promise<PrintifyProduct> {
  const response = await rateLimitedRequest(() =>
    printifyApi.post(`/shops/${SHOP_ID}/products.json`, {
      title: productData.title,
      description: productData.description,
      blueprint_id: productData.blueprint_id,
      print_provider_id: productData.print_provider_id,
      variants: [
        {
          id: 12345, // Variant ID from blueprint
          price: 2500, // Price in cents
          is_enabled: true
        }
      ],
      print_areas: [
        {
          variant_ids: [12345],
          placeholders: [
            {
              position: 'front',
              images: [
                {
                  id: productData.design_image_id,
                  x: 0.5,
                  y: 0.5,
                  scale: 1,
                  angle: 0
                }
              ]
            }
          ]
        }
      ]
    })
  );

  return response.data;
}

async function publishProduct(productId: string): Promise<void> {
  await rateLimitedRequest(() =>
    printifyApi.post(
      `/shops/${SHOP_ID}/products/${productId}/publish.json`,
      { title: true, description: true, images: true, variants: true, tags: true }
    )
  );
}
```

## API Endpoints

### Key Printify Endpoints

#### 1. Upload Image
```
POST /v1/uploads/images.json
```

**Request:**
```json
{
  "file_name": "design.png",
  "url": "https://your-cdn.com/design.png"
}
```

**Response:**
```json
{
  "id": "5d39b159749d0a000000000",
  "file_name": "design.png",
  "height": 1000,
  "width": 1000,
  "size": 50000,
  "mime_type": "image/png",
  "preview_url": "https://printify.com/preview.png",
  "upload_time": "2023-01-01 12:00:00"
}
```

#### 2. Create Product
```
POST /v1/shops/{shop_id}/products.json
```

#### 3. Publish Product
```
POST /v1/shops/{shop_id}/products/{product_id}/publish.json
```

#### 4. Get Blueprints
```
GET /v1/catalog/blueprints.json
```

## Authentication

### API Token

Generate your API token from Printify dashboard:

1. Go to **Settings** → **API**
2. Click **Generate Token**
3. Copy and store securely
4. Add to `.env.local`

### Security Best Practices

```typescript
// ❌ Bad: Exposing API key in frontend
const API_KEY = 'abc123';

// ✅ Good: Using environment variables
const API_KEY = import.meta.env.VITE_PRINTIFY_API_KEY;

// ✅ Better: Using backend proxy
const response = await fetch('/api/printify/products', {
  method: 'POST',
  body: JSON.stringify(productData)
});
```

## Error Handling

### Retry Logic

```typescript
async function retryRequest<T>(
  requestFn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error as Error;

      // Don't retry on client errors (4xx)
      if (axios.isAxiosError(error) && error.response?.status < 500) {
        throw error;
      }

      // Exponential backoff
      if (i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
      }
    }
  }

  throw lastError!;
}
```

### Common Errors

| Status | Error | Solution |
|--------|-------|----------|
| 401 | Unauthorized | Check API token |
| 403 | Forbidden | Verify shop access |
| 404 | Not Found | Check resource IDs |
| 422 | Validation Error | Review request payload |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry with backoff |

## Rate Limiting

Printify limits:
- **10 requests per second** per shop
- **600 requests per minute** per shop

### Implementation

```typescript
class RateLimiter {
  private queue: Array<() => Promise<any>> = [];
  private processing = false;
  private lastRequestTime = 0;
  private readonly minInterval = 100; // 100ms = 10 req/sec

  async enqueue<T>(fn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await fn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });

      this.processQueue();
    });
  }

  private async processQueue() {
    if (this.processing || this.queue.length === 0) return;

    this.processing = true;

    while (this.queue.length > 0) {
      const now = Date.now();
      const elapsed = now - this.lastRequestTime;

      if (elapsed < this.minInterval) {
        await sleep(this.minInterval - elapsed);
      }

      const fn = this.queue.shift()!;
      this.lastRequestTime = Date.now();
      await fn();
    }

    this.processing = false;
  }
}

export const rateLimiter = new RateLimiter();
```

## Best Practices

### 1. Use Backend Proxy

**Never** expose API keys in frontend code. Use a backend proxy:

```typescript
// Backend (Node.js/Express)
app.post('/api/printify/products', async (req, res) => {
  const response = await axios.post(
    `https://api.printify.com/v1/shops/${SHOP_ID}/products.json`,
    req.body,
    {
      headers: {
        'Authorization': `Bearer ${process.env.PRINTIFY_API_KEY}`
      }
    }
  );

  res.json(response.data);
});

// Frontend
const response = await fetch('/api/printify/products', {
  method: 'POST',
  body: JSON.stringify(productData)
});
```

### 2. Caching

Cache blueprint and provider data:

```typescript
const blueprintCache = new Map<number, any>();

async function getBlueprint(id: number): Promise<any> {
  if (blueprintCache.has(id)) {
    return blueprintCache.get(id);
  }

  const response = await printifyApi.get(`/catalog/blueprints/${id}.json`);
  blueprintCache.set(id, response.data);

  return response.data;
}
```

### 3. Webhooks

Listen for Printify events:

```typescript
// Backend webhook endpoint
app.post('/webhooks/printify', (req, res) => {
  const event = req.body;

  switch (event.type) {
    case 'order:created':
      handleOrderCreated(event.data);
      break;
    case 'order:sent-to-production':
      handleOrderProduction(event.data);
      break;
    case 'order:shipment:created':
      handleShipmentCreated(event.data);
      break;
  }

  res.status(200).send('OK');
});
```

## Testing

### Mock Responses

```typescript
// __mocks__/printifyApi.ts
export const printifyApi = {
  post: vi.fn((url, data) => {
    if (url.includes('/products.json')) {
      return Promise.resolve({
        data: {
          id: 'prod_123',
          title: data.title,
          images: [{ src: 'https://example.com/mock.png' }]
        }
      });
    }
  })
};
```

## Migration Checklist

- [ ] Sign up for Printify account
- [ ] Generate API token
- [ ] Connect e-commerce shop
- [ ] Install axios dependency
- [ ] Create `.env.local` with credentials
- [ ] Implement `printifyApi.ts`
- [ ] Replace `mockEngine.ts` with `printifyEngine.ts`
- [ ] Update `App.tsx` import
- [ ] Implement rate limiting
- [ ] Add error handling
- [ ] Set up backend proxy (recommended)
- [ ] Test with sandbox/test products
- [ ] Configure webhooks
- [ ] Deploy to production

## Resources

- [Printify API Documentation](https://developers.printify.com/)
- [Printify Dashboard](https://printify.com/app/dashboard)
- [API Reference](https://developers.printify.com/#introduction)
- [Webhook Events](https://developers.printify.com/#webhooks)

---

**Need Help?** Contact support@staticwaves.io
