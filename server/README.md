# TikTok Seller Webhook Server

A robust Node.js/Express backend server for ingesting TikTok Seller webhooks and processing orders in real-time.

## Features

- **Secure Webhook Processing**: HMAC-SHA256 signature verification for all TikTok webhook events
- **Real-time Order Ingestion**: Capture and process TikTok orders as they happen
- **PostgreSQL Storage**: Persistent storage with optimized indexes for fast queries
- **Idempotency**: Prevent duplicate event processing with event deduplication
- **Replay Attack Prevention**: Timestamp validation to reject old webhook requests
- **Comprehensive Logging**: Full audit trail of all webhook events
- **RESTful API**: Query orders, view statistics, and monitor processing status
- **Type Safety**: Full TypeScript implementation with Zod schema validation
- **Security Hardened**: Helmet, CORS, rate limiting, and input validation
- **Production Ready**: Graceful shutdown, error handling, and database connection pooling

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌──────────────┐
│  TikTok     │ Webhook │  Express Server  │  Store  │  PostgreSQL  │
│  Seller API │────────>│  (This Service)  │────────>│   Database   │
└─────────────┘         └──────────────────┘         └──────────────┘
                               │
                               │ Process
                               ▼
                        ┌──────────────┐
                        │  Your Logic  │
                        │  (Printify,  │
                        │   Email,     │
                        │   etc.)      │
                        └──────────────┘
```

## Prerequisites

- **Node.js**: 18.x or higher
- **PostgreSQL**: 12.x or higher
- **TikTok Seller Account**: With API access
- **TikTok App**: Registered on TikTok Developer Portal

## Quick Start

### 1. Installation

```bash
cd server
npm install
```

### 2. Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Server
PORT=3001
NODE_ENV=development

# TikTok API Credentials
TIKTOK_APP_KEY=your_app_key_here
TIKTOK_APP_SECRET=your_app_secret_here

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tiktok_orders
DB_USER=postgres
DB_PASSWORD=your_password_here

# Security
WEBHOOK_SECRET=your_webhook_secret_here

# CORS
FRONTEND_URL=http://localhost:3000
```

### 3. Database Setup

Create the PostgreSQL database:

```bash
createdb tiktok_orders
```

Initialize the schema:

```bash
npm run db:init
```

Or use the automated setup script:

```bash
npm run setup
```

### 4. Start Development Server

```bash
npm run dev
```

The server will start on `http://localhost:3001`

## API Endpoints

### Webhook Endpoints

#### POST /webhook/tiktok
Receives TikTok webhook events

**Headers:**
- `x-tiktok-shop-signature`: HMAC-SHA256 signature
- `x-tiktok-shop-timestamp`: Unix timestamp

**Response:**
```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "order_id": "123456789"
}
```

#### GET /webhook/health
Health check for webhook service

### Order Management API

#### GET /api/orders/:orderId
Get a specific order by ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "order_id": "123456789",
    "shop_id": "shop_123",
    "event_type": "order_created",
    "order_status": "AWAITING_SHIPMENT",
    "order_data": { ... },
    "processed": true,
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z"
  }
}
```

#### GET /api/orders/shop/:shopId?limit=100&offset=0
Get orders for a specific shop (paginated)

#### GET /api/orders/queue/unprocessed?limit=100
Get unprocessed orders for manual retry

#### GET /api/orders/stats/webhooks?shopId=xxx
Get webhook processing statistics

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "event_type": "order_created",
      "total": 150,
      "successful": 148,
      "failed": 2,
      "last_received": "2025-12-28T10:00:00Z"
    }
  ]
}
```

#### GET /api/orders/stats/orders
Get order statistics by shop and status

### General

#### GET /health
Server health check

## TikTok Webhook Configuration

### 1. Register Your Webhook URL

In the TikTok Seller Partner Center:

1. Go to **App Management** → **Your App**
2. Navigate to **Webhooks** section
3. Enter your webhook URL: `https://your-domain.com/webhook/tiktok`
4. Select events to subscribe to:
   - Order Status Change
   - Order Created
   - Package Shipped
   - Package Delivered

### 2. Verify Webhook Endpoint

TikTok will send a verification request. The server automatically handles this.

### 3. Supported Events

- `order_created` - New order placed
- `order_status_change` - Order status updated
- `order_cancelled` - Order cancelled
- `package_shipped` - Package shipped
- `package_delivered` - Package delivered

## Database Schema

### tiktok_orders

Stores all order data from webhooks.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| order_id | VARCHAR(255) | TikTok order ID (unique) |
| shop_id | VARCHAR(255) | TikTok shop ID |
| event_type | VARCHAR(100) | Webhook event type |
| order_status | VARCHAR(100) | Current order status |
| order_data | JSONB | Complete order payload |
| processed | BOOLEAN | Processing status |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |
| error_message | TEXT | Error details (if failed) |

### webhook_events

Audit log of all webhook requests.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| event_id | VARCHAR(255) | Unique event identifier |
| shop_id | VARCHAR(255) | TikTok shop ID |
| event_type | VARCHAR(100) | Event type |
| payload | JSONB | Raw webhook payload |
| signature | VARCHAR(512) | Webhook signature |
| timestamp | BIGINT | Request timestamp |
| received_at | TIMESTAMP | Server receive time |
| processed | BOOLEAN | Processing status |
| success | BOOLEAN | Success status |
| error_message | TEXT | Error details |

## Security Features

### 1. Webhook Signature Verification

All webhooks are verified using HMAC-SHA256:

```typescript
signature = HMAC-SHA256(app_secret, timestamp + request_body)
```

Invalid signatures are rejected with 401 Unauthorized.

### 2. Replay Attack Prevention

Webhooks older than 5 minutes are rejected to prevent replay attacks.

### 3. Rate Limiting

- 100 requests per 15 minutes per IP
- Configurable via environment variables

### 4. Input Validation

All payloads are validated using Zod schemas before processing.

### 5. SQL Injection Protection

Parameterized queries prevent SQL injection attacks.

## Custom Order Processing

Implement your business logic in `src/services/orderService.ts`:

```typescript
export async function processOrder(orderData: TikTokOrder): Promise<void> {
  // Example: Send to Printify
  await printifyAPI.createOrder({
    items: orderData.items.map(item => ({
      sku: item.seller_sku,
      quantity: item.quantity,
    })),
    shipping_address: orderData.shipping_address,
  });

  // Example: Send confirmation email
  await emailService.sendOrderConfirmation(orderData.buyer_email, orderData);

  // Example: Update analytics
  await analytics.trackOrder(orderData);
}
```

## Monitoring & Debugging

### View Logs

The server uses Morgan for request logging:

```bash
npm run dev
```

### Check Unprocessed Orders

```bash
curl http://localhost:3001/api/orders/queue/unprocessed
```

### View Webhook Stats

```bash
curl http://localhost:3001/api/orders/stats/webhooks
```

### Database Queries

```sql
-- View recent orders
SELECT * FROM order_processing_queue LIMIT 10;

-- Check failed orders
SELECT * FROM tiktok_orders WHERE processed = false;

-- View statistics
SELECT * FROM order_statistics;
```

## Deployment

### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Use strong `WEBHOOK_SECRET`
- [ ] Configure SSL/TLS certificate
- [ ] Set up database backups
- [ ] Configure monitoring (e.g., PM2, Datadog)
- [ ] Set up log aggregation
- [ ] Configure firewall rules
- [ ] Use environment secrets manager (e.g., AWS Secrets Manager)
- [ ] Set up alerting for failed webhooks

### Deploy with PM2

```bash
npm run build
pm2 start dist/index.js --name tiktok-webhook
pm2 save
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3001
CMD ["node", "dist/index.js"]
```

Build and run:

```bash
docker build -t tiktok-webhook-server .
docker run -p 3001:3001 --env-file .env tiktok-webhook-server
```

## Troubleshooting

### Webhook signature verification fails

1. Check that `TIKTOK_APP_SECRET` matches your TikTok app secret
2. Ensure webhook payload is not modified (no middleware parsing body before verification)
3. Verify timestamp is within 5-minute window

### Database connection errors

1. Check PostgreSQL is running: `pg_isready`
2. Verify database credentials in `.env`
3. Ensure database exists: `psql -l | grep tiktok_orders`

### Orders not processing

1. Check unprocessed orders: `GET /api/orders/queue/unprocessed`
2. Review error logs
3. Verify `processOrder()` function in `orderService.ts`

## Development

### Project Structure

```
server/
├── src/
│   ├── config/
│   │   └── database.ts          # Database configuration
│   ├── database/
│   │   ├── schema.sql            # Database schema
│   │   └── init.ts               # Initialization script
│   ├── middleware/
│   │   ├── errorHandler.ts      # Error handling
│   │   └── validation.ts        # Input validation
│   ├── routes/
│   │   ├── webhook.ts            # Webhook endpoints
│   │   └── orders.ts             # Order API endpoints
│   ├── services/
│   │   ├── orderService.ts      # Order business logic
│   │   └── webhookService.ts    # Webhook processing
│   ├── types/
│   │   └── tiktok.ts             # TypeScript types
│   ├── utils/
│   │   └── webhookVerification.ts # Security utils
│   └── index.ts                  # Server entry point
├── scripts/
│   └── setup.sh                  # Setup automation
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

### Running Tests

```bash
npm test
```

### Linting

```bash
npm run lint
```

## Support

For issues and questions:
- Review TikTok API documentation: https://partner.tiktokshop.com/doc
- Check server logs for error details
- Review webhook event logs in database

## License

MIT
