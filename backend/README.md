# Automated Dropshipping Platform - Backend

A comprehensive dropshipping automation platform with multi-platform integration (Shopify, AliExpress, TikTok Shop, Printify, Instagram, Facebook, YouTube).

## Features

### 🛍️ **Multi-Platform Integration**
- **Shopify**: Full product and order management
- **AliExpress**: Product sourcing and automated fulfillment
- **TikTok Shop**: Product sync, order management, and ad campaigns
- **Printify**: Print-on-demand product creation
- **Meta (Facebook & Instagram)**: Shop integration and advertising
- **YouTube Shopping**: Product tagging and monetization

### 🤖 **Automation**
- Automated order fulfillment from suppliers
- Real-time inventory synchronization
- Price optimization with AI
- Automated product research and niche analysis
- Marketing campaign automation
- Smart reordering based on stock levels

### 📊 **Analytics & Intelligence**
- Real-time dashboard with sales metrics
- ROI and ROAS tracking
- Trending product identification
- Customer lifetime value analysis
- Platform performance comparison

### 🔄 **Workflow Automation**
- Custom automation rules (triggers + actions)
- Background task processing
- Webhook handling for real-time updates
- Batch operations for efficiency

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for frontend)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb dropshipping

   # Run migrations
   alembic upgrade head
   ```

6. **Start Redis**
   ```bash
   redis-server
   ```

7. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Docker Setup (Recommended)

```bash
docker-compose up -d
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Shopify Integration
- `GET /api/shopify/products` - List Shopify products
- `POST /api/shopify/products/import` - Import products from suppliers
- `POST /api/shopify/products/publish` - Publish to other platforms
- `GET /api/shopify/orders` - List orders
- `POST /api/shopify/orders/sync` - Sync orders
- `POST /api/shopify/orders/{order_id}/fulfill` - Fulfill order

### AliExpress Integration
- `POST /api/aliexpress/products/search` - Search products
- `GET /api/aliexpress/products/{product_id}` - Get product details
- `POST /api/aliexpress/orders/place` - Place order for fulfillment
- `GET /api/aliexpress/orders/{order_id}/status` - Get order status
- `GET /api/aliexpress/categories` - List categories

### TikTok Shop Integration
- `POST /api/tiktok/products/sync` - Sync products to TikTok
- `GET /api/tiktok/products` - List TikTok products
- `GET /api/tiktok/orders` - List TikTok orders
- `POST /api/tiktok/campaigns/create` - Create ad campaign
- `GET /api/tiktok/analytics` - Get analytics data

### Printify Integration
- `POST /api/printify/products/create` - Create POD product
- `GET /api/printify/products` - List products
- `POST /api/printify/orders/create` - Create order
- `GET /api/printify/catalog/blueprints` - Get product blueprints

### Products Management
- `GET /api/products` - List all products
- `GET /api/products/{product_id}` - Get product details
- `POST /api/products/research` - AI-powered product research

### Orders Management
- `GET /api/orders` - List all orders
- `GET /api/orders/{order_id}` - Get order details
- `POST /api/orders/{order_id}/fulfill` - Trigger fulfillment

### Automation
- `POST /api/automation/rules/create` - Create automation rule
- `GET /api/automation/rules` - List automation rules
- `POST /api/automation/inventory/sync` - Sync inventory
- `POST /api/automation/price/optimize` - Optimize pricing

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/sales` - Sales data for charts
- `GET /api/analytics/performance` - Performance metrics
- `GET /api/analytics/products/trending` - Trending products

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dropshipping

# Shopify
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
SHOPIFY_SHOP_URL=yourstore.myshopify.com

# AliExpress
ALIEXPRESS_APP_KEY=your_aliexpress_app_key
ALIEXPRESS_APP_SECRET=your_aliexpress_app_secret
ALIEXPRESS_ACCESS_TOKEN=your_aliexpress_access_token

# TikTok Shop
TIKTOK_APP_KEY=your_tiktok_app_key
TIKTOK_APP_SECRET=your_tiktok_app_secret
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
TIKTOK_SHOP_ID=your_tiktok_shop_id

# Printify
PRINTIFY_API_TOKEN=your_printify_api_token

# Redis
REDIS_URL=redis://localhost:6379/0

# App
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### API Credentials Setup

#### Shopify
1. Go to Shopify Partners Dashboard
2. Create a custom app
3. Enable required scopes: `read_products`, `write_products`, `read_orders`, `write_orders`
4. Copy API key, secret, and access token

#### AliExpress
1. Register at AliExpress Developer Portal
2. Create an app (Self Developer)
3. Complete business verification
4. Copy App Key and Secret
5. Implement OAuth flow to get access token

#### TikTok Shop
1. Register at TikTok Shop Seller Center
2. Create app in Developer Portal
3. Link Shopify store
4. Copy App Key, Secret, and Shop ID

#### Printify
1. Go to Printify Dashboard > API
2. Generate Personal Access Token
3. Copy token to `.env`

## Development

### Project Structure

```
backend/
├── api/                    # API routers
│   ├── shopify_router.py
│   ├── aliexpress_router.py
│   ├── tiktok_router.py
│   ├── printify_router.py
│   ├── products_router.py
│   ├── orders_router.py
│   ├── automation_router.py
│   └── analytics_router.py
├── services/              # Business logic
│   ├── shopify_service.py
│   ├── aliexpress_service.py
│   ├── tiktok_service.py
│   └── printify_service.py
├── models/                # Database models
│   └── database.py
├── config/                # Configuration
│   └── settings.py
├── utils/                 # Utilities
├── main.py               # FastAPI application
└── requirements.txt       # Dependencies
```

### Running Tests

```bash
pytest
```

### Code Style

```bash
# Format code
black .

# Lint
flake8
```

## Deployment

### Production Setup

1. Set `DEBUG=False` in `.env`
2. Configure production database
3. Set up proper CORS origins
4. Use gunicorn for production server:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment

```bash
# Build image
docker build -t dropshipping-backend .

# Run container
docker run -p 8000:8000 --env-file .env dropshipping-backend
```

## Automation Workflows

### Example: Auto-Fulfill Orders

1. Customer places order on Shopify
2. Webhook triggers order processing
3. System identifies supplier (AliExpress/Printify)
4. Automatically places order with supplier
5. Tracking number synced back to Shopify
6. Customer receives shipping notification

### Example: Inventory Sync

1. Scheduled task runs every hour
2. Fetches inventory from all suppliers
3. Updates Shopify product quantities
4. Triggers low-stock alerts if needed
5. Optionally auto-reorders popular items

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection string in .env
```

**API Rate Limits**
- Implement exponential backoff
- Monitor rate limit headers
- Use batch operations where possible

**Webhook Failures**
- Ensure webhook URL is publicly accessible
- Verify signature validation
- Check endpoint returns 200 OK

## Support

For issues and questions:
- Create an issue on GitHub
- Check documentation at `/docs`
- Review example workflows in `examples/`

## License

Proprietary - All rights reserved

## Security

- Never commit `.env` files
- Rotate API keys regularly
- Use HTTPS in production
- Implement proper authentication
- Monitor for suspicious activity
