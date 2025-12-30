# 🤖 Automation Guide - StaticWaves Dropshipping Platform

Complete guide to automated workflows, background tasks, and hands-free operation.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Automated Workflows](#automated-workflows)
3. [Background Workers](#background-workers)
4. [Scheduled Tasks](#scheduled-tasks)
5. [Webhooks](#webhooks)
6. [Monitoring & Control](#monitoring--control)
7. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install celery redis
```

### 2. Start Redis (Required for Celery)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally
sudo apt-get install redis-server
redis-server
```

### 3. Start Celery Workers

```bash
# Terminal 1: Main worker
celery -A celery_app worker --loglevel=info

# Terminal 2: Beat scheduler (for cron jobs)
celery -A celery_app beat --loglevel=info
```

### 4. Start API Server

```bash
uvicorn main:app --reload
```

✅ **You're now running fully automated dropshipping!**

---

## 🔄 Automated Workflows

### Product Import Pipeline
**AliExpress → Shopify → TikTok Shop**

#### Automatic Daily Research
Runs every day at 9 AM UTC:
- Searches trending niches
- Filters for quality (95%+ rating, 1000+ orders)
- Auto-imports top 10 winners
- Applies 40% markup
- Normalizes inventory for all platforms

#### Manual Import (via API)

```bash
# Import single product
curl -X POST "http://localhost:8000/api/monitor/tasks/import" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "1005001234567890", "markup": 40.0}'

# Bulk import
curl -X POST "http://localhost:8000/api/monitor/tasks/import-bulk" \
  -H "Content-Type: application/json" \
  -d '{"product_ids": ["1005001234567890", "1005009876543210"], "markup": 40.0}'
```

#### What Gets Automated
- ✅ Product fetching from AliExpress
- ✅ Price calculation (cost + markup)
- ✅ Image optimization
- ✅ Inventory normalization (999999999 → 9,999)
- ✅ Shopify product creation
- ✅ TikTok Shop sync
- ✅ Error retry (3 attempts with backoff)

---

### Order Fulfillment Pipeline
**Shopify Orders → AliExpress → Tracking**

#### Automatic Processing
Runs every 30 minutes:
- Checks for unfulfilled Shopify orders
- Identifies AliExpress products (SKU starts with "ALI-")
- Places orders on AliExpress
- Updates Shopify with tracking
- Sends customer notifications

#### Manual Fulfillment

```bash
# Trigger immediate processing
curl -X POST "http://localhost:8000/api/monitor/tasks/fulfill-orders"
```

#### What Gets Automated
- ✅ Order detection
- ✅ Address formatting
- ✅ AliExpress order placement
- ✅ Tracking number sync
- ✅ Shopify fulfillment update
- ✅ Customer email notification
- ✅ Failure retry (5 attempts with 5min+ backoff)

---

### Inventory Sync
**Keep Stock Accurate Across All Platforms**

#### Automatic Sync
Runs every 4 hours:
- Shopify inventory normalization
- Printify stock check
- AliExpress supplier stock verification
- TikTok Shop sync
- Low stock alerts (< 10 units)
- Auto-pause out-of-stock products

#### Manual Sync

```bash
# Trigger inventory sync
curl -X POST "http://localhost:8000/api/monitor/tasks/sync-inventory"

# Check for low stock
curl -X POST "http://localhost:8000/api/monitor/tasks/check-low-stock"
```

#### What Gets Automated
- ✅ Inventory normalization (handles Printify's 999999999)
- ✅ Supplier stock checks
- ✅ Platform-specific limits (TikTok: 9,999)
- ✅ Low stock warnings
- ✅ Out-of-stock pausing

---

## ⚙️ Background Workers

### Worker Types

#### 1. Product Import Worker
**File:** `workers/product_import.py`

**Tasks:**
- `import_product_by_id` - Import single product
- `import_products_bulk` - Batch import
- `research_trending_products` - Daily research
- `cleanup_failed_imports` - Retry failed syncs

#### 2. Order Fulfillment Worker
**File:** `workers/order_fulfillment.py`

**Tasks:**
- `fulfill_order` - Process single order
- `process_pending_orders` - Batch fulfillment
- `update_tracking_numbers` - Sync tracking
- `retry_failed_fulfillments` - Retry failures

#### 3. Inventory Sync Worker
**File:** `workers/inventory_sync.py`

**Tasks:**
- `sync_all_suppliers` - Multi-platform sync
- `alert_low_stock` - Stock warnings
- `pause_out_of_stock_products` - Auto-pause

#### 4. Analytics Worker
**File:** `workers/analytics.py`

**Tasks:**
- `generate_daily_report` - Performance summary
- `health_check` - System status
- `calculate_profit_margins` - Profitability analysis
- `identify_best_sellers` - Sales leaders

---

## 📅 Scheduled Tasks

### Cron Schedule (Celery Beat)

| Task | Schedule | Purpose |
|------|----------|---------|
| `sync_all_suppliers` | Every 4 hours | Keep inventory accurate |
| `process_pending_orders` | Every 30 minutes | Auto-fulfill orders |
| `research_trending_products` | Daily at 9 AM UTC | Find winning products |
| `generate_daily_report` | Daily at midnight UTC | Performance metrics |
| `health_check` | Every 5 minutes | System monitoring |

### View Scheduled Tasks

```bash
# Check what's scheduled
celery -A celery_app inspect scheduled
```

### Modify Schedule

Edit `celery_app.py`:

```python
app.conf.beat_schedule = {
    "sync-inventory-hourly": {  # Changed from 4h to 1h
        "task": "workers.inventory_sync.sync_all_suppliers",
        "schedule": crontab(hour="*/1"),  # Every hour
    },
}
```

---

## 🔗 Webhooks

Real-time event processing from platforms.

### Shopify Webhooks

#### Setup in Shopify Admin
1. Go to **Settings → Notifications → Webhooks**
2. Create webhooks pointing to your server:

```
https://your-domain.com/api/webhooks/shopify/orders/create
https://your-domain.com/api/webhooks/shopify/orders/paid
https://your-domain.com/api/webhooks/shopify/products/update
https://your-domain.com/api/webhooks/shopify/inventory/update
```

3. Set webhook format to **JSON**
4. Add webhook secret to `.env`:

```env
SHOPIFY_WEBHOOK_SECRET=your_secret_here
```

#### What Happens

**Order Created:**
- ✅ Automatically triggers fulfillment
- ✅ Only processes AliExpress products
- ✅ Queues background task

**Order Paid:**
- ✅ Can trigger priority processing
- ✅ Logs payment confirmation

**Product Updated:**
- ✅ Syncs changes to TikTok Shop

**Inventory Updated:**
- ✅ Triggers low stock checks

### TikTok Shop Webhooks

```
https://your-domain.com/api/webhooks/tiktok/orders
```

**Order Created:**
- ✅ Creates order in Shopify
- ✅ Triggers fulfillment

### Stripe Webhooks

```
https://your-domain.com/api/webhooks/stripe/webhook
```

Add secret to `.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Events:**
- `payment_intent.succeeded` - Payment successful
- `payment_intent.payment_failed` - Payment failed
- `customer.subscription.deleted` - Subscription cancelled

---

## 📊 Monitoring & Control

### Dashboard API Endpoints

#### System Status

```bash
# Overall health
GET /api/monitor/health

# System status
GET /api/monitor/status

# Quick stats
GET /api/monitor/stats/overview
```

#### Metrics

```bash
# Full metrics dashboard
GET /api/monitor/metrics
```

**Response:**
```json
{
  "daily_report": {
    "orders": {"total": 45, "fulfilled": 40, "fulfillment_rate": 88.9},
    "revenue": {"total": 1234.56, "average_order_value": 27.43},
    "products": {"total": 150, "active": 142, "low_stock": 5}
  },
  "profit_margins": {
    "top_5": [...],
    "average_margin": 35.2
  },
  "best_sellers": [...]
}
```

#### Active Tasks

```bash
# See what's running
GET /api/monitor/tasks

# Check specific task
GET /api/monitor/tasks/{task_id}
```

#### Manual Triggers

```bash
# Import products
POST /api/monitor/tasks/import
POST /api/monitor/tasks/import-bulk

# Fulfill orders
POST /api/monitor/tasks/fulfill-orders

# Sync inventory
POST /api/monitor/tasks/sync-inventory

# Check low stock
POST /api/monitor/tasks/check-low-stock
```

### Celery Flower (Optional Web UI)

```bash
# Install Flower
pip install flower

# Start web dashboard
celery -A celery_app flower

# Access at http://localhost:5555
```

---

## 💡 Best Practices

### 1. Monitoring

✅ **Set up alerts:**
```python
# In production, send alerts to Discord/Telegram/Slack
# when critical tasks fail or inventory is low
```

✅ **Check logs regularly:**
```bash
tail -f logs/celery.log
```

✅ **Monitor queue depth:**
```bash
celery -A celery_app inspect stats
```

### 2. Scaling

✅ **Multiple workers for heavy load:**
```bash
# Worker 1: Product imports
celery -A celery_app worker -Q product_imports --concurrency=4

# Worker 2: Order fulfillment
celery -A celery_app worker -Q fulfillment --concurrency=2
```

✅ **Distributed workers:**
```bash
# Run workers on different servers
# They all connect to same Redis instance
```

### 3. Error Handling

✅ **All tasks have retry logic:**
- Product import: 3 retries with exponential backoff
- Order fulfillment: 5 retries (5min, 10min, 20min, 40min, 80min)
- Inventory sync: No retry (runs every 4h anyway)

✅ **Failed tasks are logged:**
- Check Celery logs
- Monitor `/api/monitor/tasks`

### 4. Rate Limiting

✅ **Respect platform limits:**
- AliExpress: 2-second delays between requests
- TikTok: 1-second delays
- Shopify: 2 calls per second (handled by library)

✅ **Adjust concurrency:**
```python
# In celery_app.py
worker_prefetch_multiplier=1  # One task at a time
```

### 5. Testing

✅ **Test webhooks locally:**
```bash
# Use ngrok for Shopify testing
ngrok http 8000

# Update webhook URL in Shopify
https://abc123.ngrok.io/api/webhooks/shopify/orders/create
```

✅ **Dry run mode:**
```python
# In workers, set DRY_RUN = True to test without actual API calls
```

### 6. Production Deployment

✅ **Use supervisor or systemd:**

```ini
# /etc/supervisor/conf.d/celery.conf
[program:celery-worker]
command=/path/to/venv/bin/celery -A celery_app worker --loglevel=info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
```

✅ **Environment variables:**
```bash
# Use .env file, never commit secrets
cp .env.example .env
```

✅ **Monitor with CloudWatch/Datadog:**
- Track task success/failure rates
- Alert on queue backlog
- Monitor worker health

---

## 🎯 Common Workflows

### Daily Operations

**Morning (Automatic):**
- 9 AM: Product research runs
- Top 10 winners imported
- Inventory synced

**Throughout Day (Automatic):**
- Every 30 min: Orders fulfilled
- Every 4 hours: Inventory updated
- Every 5 min: Health checks

**Evening (Automatic):**
- Midnight: Daily report generated
- Metrics calculated
- Best sellers identified

### Weekly Tasks

```bash
# Monday: Analyze performance
GET /api/monitor/metrics

# Wednesday: Check profit margins
GET /api/monitor/metrics | jq '.profit_margins'

# Friday: Review best sellers
GET /api/monitor/metrics | jq '.best_sellers'
```

### Manual Overrides

```bash
# Import specific hot product
POST /api/monitor/tasks/import
{"product_id": "1005001234567890", "markup": 50.0}

# Force inventory sync
POST /api/monitor/tasks/sync-inventory

# Process stuck order manually
POST /api/monitor/tasks/fulfill-orders
```

---

## 🚨 Troubleshooting

### Workers Not Starting

```bash
# Check Redis connection
redis-cli ping

# Check Celery can connect
celery -A celery_app inspect ping
```

### Tasks Not Running

```bash
# Verify beat scheduler is running
celery -A celery_app inspect scheduled

# Check for errors
tail -f logs/celery.log
```

### Webhook Failures

```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/api/webhooks/test

# Check signature verification
# Make sure SHOPIFY_WEBHOOK_SECRET is set
```

### High Queue Depth

```bash
# Check queue status
celery -A celery_app inspect stats

# Purge stuck tasks (USE WITH CAUTION)
celery -A celery_app purge

# Add more workers
celery -A celery_app worker --concurrency=8
```

---

## 📚 Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Shopify Webhooks Guide](https://shopify.dev/docs/api/admin-rest/2024-01/resources/webhook)
- [TikTok Shop API Docs](https://partner.tiktokshop.com/doc)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)

---

**You now have a fully automated dropshipping platform! 🎉**

All workflows run in the background, orders fulfill automatically, and inventory stays synced. Just monitor the dashboard and let the system do the work.
