# 🚀 SaaS App Guide - Shopify & TikTok Shop Apps

Complete guide to deploying your DropCommerce-style SaaS apps on Shopify and TikTok Shop.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Shopify App Setup](#shopify-app-setup)
4. [TikTok Shop App Setup](#tiktok-shop-app-setup)
5. [Database Setup](#database-setup)
6. [Deployment](#deployment)
7. [Billing & Plans](#billing--plans)
8. [Product Catalog](#product-catalog)
9. [Embedded UI](#embedded-ui)

---

## 🎯 Overview

You now have a complete multi-tenant SaaS platform that allows merchants to:

✅ **Install your app** on Shopify or TikTok Shop
✅ **Browse curated products** (like DropCommerce)
✅ **One-click import** products to their store
✅ **Auto-fulfill orders** via AliExpress
✅ **Track usage** and enforce plan limits
✅ **Subscribe** via Shopify's native billing

---

## 🏗️ Architecture

### Multi-Tenant Structure

```
┌─────────────────────────────────────────┐
│         Your SaaS Platform              │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │     Shared Product Catalog       │  │
│  │  (curated dropshipping products) │  │
│  └─────────────────────────────────┘  │
│                  │                     │
│  ┌───────────────┴────────────────┐  │
│  │                                 │  │
│  ▼                                 ▼  │
│ Shop A                          Shop B │
│ (mystore.myshopify.com)  (tiktok123)   │
│ - Access token                         │
│ - Imported products                    │
│ - Usage limits                         │
│ - Billing status                       │
└─────────────────────────────────────────┘
```

### Database Models

- **Shop**: Each merchant installation
- **ImportedProduct**: Products imported by shops
- **ProductCatalog**: Shared product library
- **ShopOrder**: Orders tracked per shop
- **UsageLog**: Usage tracking for billing
- **PlanFeatures**: Subscription tiers

---

## 📦 Shopify App Setup

### 1. Create Shopify Partner Account

1. Go to [partners.shopify.com](https://partners.shopify.com)
2. Sign up for Partner account
3. Navigate to **Apps** → **Create app**

### 2. Configure App Settings

**App Info:**
- App name: "YourApp Dropshipping"
- App URL: `https://your-app.com/api/shopify-app/embedded?shop={{shop}}`
- Allowed redirection URLs:
  ```
  https://your-app.com/api/shopify-app/callback
  https://your-app.com/api/shopify-app/billing/confirm
  ```

**App Setup:**
- Embedded app: **Yes**
- App proxy: **Optional** (for storefront widgets)

### 3. Get API Credentials

From your app dashboard:

```env
SHOPIFY_API_KEY=abc123...
SHOPIFY_API_SECRET=xyz789...
```

### 4. Configure Scopes

Request these OAuth scopes:
```
read_products, write_products
read_orders, write_orders
read_inventory, write_inventory
read_fulfillments, write_fulfillments
read_shipping, write_shipping
```

### 5. Set App URLs

**Installation URL:**
```
https://your-app.com/api/shopify-app/install?shop={shop}
```

**Embedded App URL:**
```
https://your-app.com/api/shopify-app/embedded?shop={shop}
```

### 6. Test Installation

```bash
# Visit this URL to install on a development store
https://your-app.com/api/shopify-app/install?shop=dev-store.myshopify.com
```

---

## 🎵 TikTok Shop App Setup

### 1. Register TikTok Developer Account

1. Go to [partner.tiktokshop.com](https://partner.tiktokshop.com)
2. Register as developer
3. Create new app

### 2. App Configuration

**Basic Info:**
- App name: "YourApp Dropshipping"
- Redirect URI: `https://your-app.com/api/tiktok-app/callback`

**Permissions:**
```
product.list
product.write
order.list
order.fulfillment
shop.read
```

### 3. Get API Credentials

```env
TIKTOK_APP_KEY=your_app_key
TIKTOK_APP_SECRET=your_app_secret
```

### 4. Authorization Flow

Sellers authorize via:
```
https://your-app.com/api/tiktok-app/install
```

---

## 💾 Database Setup

### 1. Run Migrations

```bash
cd backend

# Create tables
python -c "from models.saas import init_saas_db; from sqlalchemy import create_engine; engine = create_engine('your_database_url'); init_saas_db(engine)"
```

### 2. Seed Product Catalog

```bash
# Import products into catalog
python scripts/seed_catalog.py
```

### 3. Create Plan Tiers

```sql
INSERT INTO plan_features (tier, name, monthly_price, max_products, max_orders_per_month, features)
VALUES
  ('free', 'Free', 0, 25, 100, '{"auto_fulfillment": false, "analytics": false}'),
  ('starter', 'Starter', 29.99, 500, 1000, '{"auto_fulfillment": true, "analytics": true}'),
  ('professional', 'Professional', 79.99, -1, -1, '{"auto_fulfillment": true, "analytics": true, "priority": true}'),
  ('enterprise', 'Enterprise', 199.99, -1, -1, '{"auto_fulfillment": true, "analytics": true, "priority": true, "white_label": true}');
```

---

## 🚀 Deployment

### 1. Environment Variables

Create `.env`:

```env
# App
APP_NAME=YourApp Dropshipping
APP_URL=https://your-app.com
SECRET_KEY=your_secret_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Shopify App
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_API_VERSION=2025-10

# TikTok Shop App
TIKTOK_APP_KEY=your_app_key
TIKTOK_APP_SECRET=your_app_secret

# Suppliers (for product import)
ALIEXPRESS_APP_KEY=...
ALIEXPRESS_APP_SECRET=...
PRINTIFY_API_TOKEN=...

# Celery
REDIS_URL=redis://localhost:6379/0
```

### 2. Deploy API Server

```bash
# Using Docker
docker-compose up -d

# Or systemd service
sudo systemctl start dropship-api
```

### 3. Deploy Celery Workers

```bash
celery -A celery_app worker --loglevel=info &
celery -A celery_app beat --loglevel=info &
```

### 4. Expose to Internet

Use ngrok for development:
```bash
ngrok http 8000
# Update APP_URL in .env to ngrok URL
```

For production, deploy to:
- **Heroku**: Easy Shopify app hosting
- **AWS**: Elastic Beanstalk or ECS
- **DigitalOcean**: App Platform
- **Vercel/Railway**: Simple deployment

---

## 💳 Billing & Plans

### Plan Tiers

| Plan | Price/mo | Products | Orders/mo | Features |
|------|----------|----------|-----------|----------|
| **Free** | $0 | 25 | 100 | Basic import |
| **Starter** | $29.99 | 500 | 1,000 | Auto-fulfillment, Analytics |
| **Professional** | $79.99 | Unlimited | Unlimited | Priority support |
| **Enterprise** | $199.99 | Unlimited | Unlimited | White-label, Dedicated manager |

### Shopify Billing Flow

1. **Merchant installs app** → Free tier activated
2. **Merchant upgrades** → `POST /api/shopify-app/billing/create?plan=starter`
3. **Redirect to Shopify** → Merchant approves charge
4. **Callback** → `GET /api/shopify-app/billing/confirm?charge_id=...`
5. **Activate charge** → Subscription active

### Enforce Limits

```python
# Check before import
if shop.products_imported >= shop.max_products:
    raise HTTPException(403, detail="Upgrade to import more products")

# Track usage
usage_log = UsageLog(
    shop_id=shop.id,
    action="import_product",
    quantity=1,
    billing_period="2025-01"
)
db.add(usage_log)
```

---

## 🛍️ Product Catalog

### Curate Products

```python
# Add product to catalog
catalog_product = ProductCatalog(
    supplier_product_id="1005001234567890",
    supplier="aliexpress",
    title="Wireless Earbuds Pro",
    cost=12.99,
    suggested_price=39.99,
    category="Electronics",
    rating=4.8,
    ships_from="CN",
    trending_score=8.5,
)
db.add(catalog_product)
db.commit()
```

### API Endpoints

```bash
# Browse catalog
GET /api/catalog/products?category=Electronics&min_rating=4.5

# One-click import
POST /api/catalog/import?shop_domain=mystore.myshopify.com&product_id=123

# Get my imports
GET /api/catalog/my-imports?shop_domain=mystore.myshopify.com
```

---

## 🎨 Embedded UI

### Shopify App Bridge

Create a React app embedded in Shopify admin:

```jsx
import { AppProvider } from '@shopify/polaris';
import { Provider as AppBridgeProvider } from '@shopify/app-bridge-react';

const config = {
  apiKey: 'YOUR_API_KEY',
  host: new URLSearchParams(window.location.search).get('host'),
  forceRedirect: true,
};

function App() {
  return (
    <AppBridgeProvider config={config}>
      <AppProvider>
        <ProductCatalog />
      </AppProvider>
    </AppBridgeProvider>
  );
}
```

### Product Catalog Component

```jsx
function ProductCatalog() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/api/catalog/products')
      .then(res => res.json())
      .then(data => setProducts(data.products));
  }, []);

  const handleImport = async (productId) => {
    const shop = new URLSearchParams(window.location.search).get('shop');

    await fetch(`/api/catalog/import?shop_domain=${shop}&product_id=${productId}`, {
      method: 'POST'
    });

    alert('Product import started!');
  };

  return (
    <Page title="Browse Products">
      <Card>
        <ResourceList
          items={products}
          renderItem={(product) => (
            <ResourceItem
              id={product.id}
              media={<Thumbnail source={product.featured_image} />}
            >
              <Stack alignment="center" distribution="equalSpacing">
                <Stack.Item fill>
                  <h3>{product.title}</h3>
                  <p>Cost: ${product.cost} → Sell: ${product.suggested_price}</p>
                </Stack.Item>
                <Button primary onClick={() => handleImport(product.id)}>
                  Import
                </Button>
              </Stack>
            </ResourceItem>
          )}
        />
      </Card>
    </Page>
  );
}
```

---

## 📊 Merchant Dashboard

Show merchants their stats:

```jsx
function Dashboard() {
  return (
    <Page title="Dashboard">
      <Layout>
        <Layout.Section>
          <Card title="Your Stats">
            <TextContainer>
              <p>Products Imported: <strong>12 / 500</strong></p>
              <p>Orders Fulfilled: <strong>45 / 1,000</strong></p>
              <p>Current Plan: <strong>Starter</strong></p>
            </TextContainer>
          </Card>
        </Layout.Section>

        <Layout.Section secondary>
          <Card title="Upgrade">
            <Button primary>Upgrade to Professional</Button>
          </Card>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
```

---

## 🔐 Security

### Verify HMAC

All Shopify callbacks include HMAC:

```python
def verify_hmac(params: Dict[str, str]) -> bool:
    hmac_to_verify = params.get("hmac")
    params_without_hmac = {k: v for k, v in params.items() if k != "hmac"}
    encoded_params = urlencode(sorted(params_without_hmac.items()))

    calculated_hmac = hmac.new(
        app_secret.encode("utf-8"),
        encoded_params.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(calculated_hmac, hmac_to_verify)
```

### Encrypt Access Tokens

```python
from cryptography.fernet import Fernet

cipher = Fernet(SECRET_KEY)

# Encrypt before saving
encrypted_token = cipher.encrypt(access_token.encode())

# Decrypt when using
decrypted_token = cipher.decrypt(encrypted_token).decode()
```

---

## 📈 Next Steps

1. **Build React UI** - Full embedded app experience
2. **Add analytics** - Track merchant performance
3. **Marketing site** - Landing page for app listing
4. **App Store listing** - Submit to Shopify App Store
5. **Customer support** - Help center and live chat
6. **Scale infrastructure** - Load balancers, CDN

---

## 🎯 Monetization

### Revenue Streams

1. **Subscription fees** - Monthly/annual plans
2. **Transaction fees** - % of fulfilled orders
3. **Premium products** - Higher-margin catalog items
4. **White-label** - Enterprise custom branding

### Example ARR Calculation

```
100 merchants × $29.99/mo × 12 = $35,988/year (Starter)
50 merchants × $79.99/mo × 12 = $47,994/year (Professional)
10 merchants × $199.99/mo × 12 = $23,999/year (Enterprise)

Total ARR: ~$108,000
```

---

## 🚨 Troubleshooting

### Installation Issues

**"Shop not found"**
- Verify shop domain format: `store.myshopify.com`
- Check HMAC signature

**"Invalid scope"**
- Update scopes in Partner Dashboard
- Merchants must reinstall

### Billing Issues

**"Charge not accepted"**
- Merchant declined
- Trial period expired
- Payment method invalid

### Import Failures

**"Product limit reached"**
- Upgrade plan
- Check `shop.products_imported`

---

**You now have a complete SaaS dropshipping platform! 🎉**

Similar to DropCommerce, but with full automation, multi-platform support, and enterprise features.