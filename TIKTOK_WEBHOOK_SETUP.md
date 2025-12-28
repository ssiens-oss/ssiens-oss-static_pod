# TikTok Webhook Integration Guide

Complete guide for setting up TikTok Seller webhook integration for real-time order processing.

## Overview

This implementation provides:
- **Backend Server**: Express.js server with TypeScript
- **Secure Webhooks**: HMAC-SHA256 signature verification
- **Order Storage**: PostgreSQL database with audit logging
- **RESTful API**: Query and manage orders
- **Production Ready**: Rate limiting, error handling, monitoring

## System Architecture

```
┌──────────────────┐
│  TikTok Seller   │
│     Platform     │
└────────┬─────────┘
         │ Webhook Events
         │ (HTTPS POST)
         ▼
┌──────────────────┐
│  Your Server     │
│  (This Backend)  │
│                  │
│  • Verify Sig    │
│  • Store Order   │
│  • Process       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   PostgreSQL     │
│    Database      │
└──────────────────┘
```

## Prerequisites

### 1. TikTok Seller Account Setup

You need:
- Active TikTok Seller account
- TikTok Developer account
- Registered TikTok App

### 2. Get TikTok API Credentials

1. Go to [TikTok Seller Partner Center](https://partner.tiktokshop.com/)
2. Navigate to **Development** → **Apps**
3. Click **Create App**
4. Fill in app details:
   - App Name: "Order Processing"
   - Redirect URI: Your domain
5. Note down:
   - `App Key` (TIKTOK_APP_KEY)
   - `App Secret` (TIKTOK_APP_SECRET)

### 3. System Requirements

- **Node.js**: 18.x or higher
- **PostgreSQL**: 12.x or higher
- **Public Domain**: With SSL/TLS certificate
- **Port**: 3001 (or configure as needed)

## Installation Steps

### Step 1: Server Setup

```bash
# Navigate to server directory
cd server

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment

Edit `.env` file:

```env
# Server Configuration
PORT=3001
NODE_ENV=production

# TikTok API Credentials (from Partner Center)
TIKTOK_APP_KEY=your_app_key_from_tiktok
TIKTOK_APP_SECRET=your_app_secret_from_tiktok

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tiktok_orders
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Security
WEBHOOK_SECRET=generate_random_secure_string

# CORS (your frontend URL)
FRONTEND_URL=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### Step 3: Database Setup

```bash
# Create database
createdb tiktok_orders

# Or using psql
psql -U postgres -c "CREATE DATABASE tiktok_orders;"

# Initialize schema
npm run db:init
```

### Step 4: Start Server

```bash
# Development
npm run dev

# Production
npm run build
npm start
```

Verify server is running:
```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-12-28T10:00:00.000Z",
  "uptime": 123.456,
  "environment": "production"
}
```

## TikTok Webhook Configuration

### Step 1: Configure Public URL

Your webhook endpoint must be:
- **Publicly accessible** over internet
- **HTTPS enabled** (TikTok requires SSL)
- **Port 443 or 80** (or proxied via nginx)

Example: `https://yourdomain.com/webhook/tiktok`

### Step 2: Set Up Webhook in TikTok

1. Go to **TikTok Seller Partner Center**
2. Navigate to **Development** → **Your App** → **Webhooks**
3. Click **Add Webhook**
4. Configure webhook:
   - **URL**: `https://yourdomain.com/webhook/tiktok`
   - **Events to subscribe**:
     - ✅ Order Status Change
     - ✅ Order Created
     - ✅ Package Shipped
     - ✅ Package Delivered
     - ✅ Order Cancelled
5. Click **Save**

### Step 3: Verify Webhook

TikTok will send a verification request. Check server logs:

```bash
# View logs
npm run dev

# You should see:
# "Webhook received and verified"
```

### Step 4: Test Webhook

1. Create a test order in TikTok Seller Center
2. Check server logs for incoming webhook
3. Query database:

```bash
# Check if order was received
curl http://localhost:3001/api/orders/shop/YOUR_SHOP_ID
```

## Webhook Events

### Supported Event Types

| Event Type | Description | Triggered When |
|------------|-------------|----------------|
| `order_created` | New order placed | Customer completes purchase |
| `order_status_change` | Order status updated | Status changes (paid, shipped, etc.) |
| `order_cancelled` | Order cancelled | Customer or seller cancels |
| `package_shipped` | Package shipped | Tracking number added |
| `package_delivered` | Package delivered | Delivery confirmed |

### Event Payload Example

```json
{
  "timestamp": 1735380000,
  "type": "order_created",
  "shop_id": "shop_123456",
  "data": {
    "order_id": "987654321",
    "order_status": "AWAITING_SHIPMENT",
    "create_time": 1735380000,
    "update_time": 1735380000,
    "items": [
      {
        "id": "item_1",
        "product_id": "prod_123",
        "product_name": "Custom T-Shirt",
        "sku_id": "sku_456",
        "sku_name": "Size M, Color Blue",
        "quantity": 2,
        "original_price": 29.99,
        "sale_price": 24.99,
        "seller_sku": "TSHIRT-M-BLUE",
        "image_url": "https://..."
      }
    ],
    "shipping_address": {
      "full_address": "123 Main St, Apt 4B",
      "name": "John Doe",
      "phone": "+1234567890",
      "region_code": "US",
      "postal_code": "12345",
      "city": "New York",
      "state": "NY"
    },
    "total_amount": 49.98,
    "shipping_fee": 5.00,
    "buyer_email": "customer@example.com"
  }
}
```

## Custom Processing Logic

### Implement Your Business Logic

Edit `server/src/services/orderService.ts`:

```typescript
export async function processOrder(orderData: TikTokOrder): Promise<void> {
  console.log(`Processing order ${orderData.order_id}`);

  // 1. Send to Printify (or your POD provider)
  if (orderData.order_status === 'AWAITING_SHIPMENT') {
    await sendToPrintify(orderData);
  }

  // 2. Send confirmation email
  if (orderData.buyer_email) {
    await sendConfirmationEmail(orderData);
  }

  // 3. Update inventory
  await updateInventory(orderData.items);

  // 4. Trigger other automations
  await notifySlack(`New order: ${orderData.order_id}`);
}

async function sendToPrintify(orderData: TikTokOrder) {
  // Your Printify integration
  const printifyOrder = {
    line_items: orderData.items.map(item => ({
      product_id: item.seller_sku,
      variant_id: item.sku_id,
      quantity: item.quantity,
    })),
    shipping_address: {
      first_name: orderData.shipping_address.name.split(' ')[0],
      last_name: orderData.shipping_address.name.split(' ')[1] || '',
      address1: orderData.shipping_address.full_address,
      city: orderData.shipping_address.city,
      zip: orderData.shipping_address.postal_code,
      country: orderData.shipping_address.region_code,
    },
  };

  // await printifyAPI.createOrder(printifyOrder);
}
```

## API Usage Examples

### Get Order by ID

```bash
curl http://localhost:3001/api/orders/987654321
```

### Get All Orders for Shop

```bash
curl "http://localhost:3001/api/orders/shop/shop_123456?limit=50&offset=0"
```

### Get Unprocessed Orders

```bash
curl http://localhost:3001/api/orders/queue/unprocessed
```

### View Webhook Statistics

```bash
curl "http://localhost:3001/api/orders/stats/webhooks?shopId=shop_123456"
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "event_type": "order_created",
      "total": 450,
      "successful": 448,
      "failed": 2,
      "last_received": "2025-12-28T10:00:00Z"
    }
  ]
}
```

## Production Deployment

### 1. Security Checklist

- [ ] SSL/TLS certificate installed
- [ ] `NODE_ENV=production` set
- [ ] Strong database password
- [ ] `WEBHOOK_SECRET` configured
- [ ] Rate limiting enabled
- [ ] Firewall configured
- [ ] CORS properly set

### 2. Nginx Reverse Proxy

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
    }
}
```

### 3. Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start server
pm2 start dist/index.js --name tiktok-webhook

# Auto-restart on reboot
pm2 startup
pm2 save

# Monitor
pm2 monit
```

### 4. Database Backups

```bash
# Backup script
pg_dump -U postgres tiktok_orders > backup_$(date +%Y%m%d).sql

# Schedule daily backups (crontab)
0 2 * * * pg_dump -U postgres tiktok_orders > /backups/tiktok_orders_$(date +\%Y\%m\%d).sql
```

## Monitoring & Debugging

### View Server Logs

```bash
# Real-time logs
pm2 logs tiktok-webhook

# Or if running directly
npm run dev
```

### Check Database

```sql
-- Recent orders
SELECT * FROM order_processing_queue LIMIT 20;

-- Failed orders
SELECT order_id, error_message, created_at
FROM tiktok_orders
WHERE processed = false;

-- Statistics
SELECT * FROM order_statistics;

-- Webhook audit
SELECT event_type, COUNT(*), SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
FROM webhook_events
GROUP BY event_type;
```

### Common Issues

**1. Webhook signature verification fails**
- Verify `TIKTOK_APP_SECRET` is correct
- Check TikTok app credentials in Partner Center
- Ensure no middleware modifies request body

**2. Webhooks not received**
- Verify public URL is accessible: `curl https://yourdomain.com/webhook/health`
- Check firewall rules
- Verify SSL certificate is valid
- Check TikTok webhook configuration

**3. Database errors**
- Verify PostgreSQL is running: `pg_isready`
- Check database credentials
- Ensure database exists: `psql -l | grep tiktok_orders`

## Testing

### Local Testing with ngrok

For local development:

```bash
# Install ngrok
npm install -g ngrok

# Expose local server
ngrok http 3001

# Use ngrok URL in TikTok webhook config
# Example: https://abc123.ngrok.io/webhook/tiktok
```

### Test Webhook Manually

```bash
# Simulate TikTok webhook (requires valid signature)
curl -X POST http://localhost:3001/webhook/tiktok \
  -H "Content-Type: application/json" \
  -H "x-tiktok-shop-signature: YOUR_SIGNATURE" \
  -H "x-tiktok-shop-timestamp: $(date +%s)" \
  -d '{
    "timestamp": 1735380000,
    "type": "order_created",
    "shop_id": "test_shop",
    "data": {
      "order_id": "test_order_123",
      "order_status": "AWAITING_SHIPMENT",
      "create_time": 1735380000,
      "update_time": 1735380000,
      "items": [],
      "total_amount": 100.00
    }
  }'
```

## Next Steps

1. ✅ Server setup complete
2. ✅ Database initialized
3. ✅ TikTok webhooks configured
4. 🔄 Implement custom order processing logic
5. 🔄 Set up production deployment
6. 🔄 Configure monitoring and alerts
7. 🔄 Test with real orders

## Support & Resources

- **TikTok API Docs**: https://partner.tiktokshop.com/doc
- **Webhook Events**: https://partner.tiktokshop.com/doc/page/webhook
- **Server README**: See `server/README.md` for detailed API documentation

## License

MIT
