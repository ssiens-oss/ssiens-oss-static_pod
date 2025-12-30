# AliExpress API Integration Guide

## Overview

The AliExpress API integration enables automated product sourcing and order fulfillment for your dropshipping business. Our implementation uses the **AliExpress Open Platform API** with OAuth 2.0 authentication.

## 🔑 Authentication Setup

### Step 1: Register as Developer

1. Visit [AliExpress Developer Portal](https://developers.aliexpress.com)
2. Sign in with your AliExpress account
3. Go to **App Management** → **Create App**
4. Select **Self Developer**
5. Fill in application details:
   - App Name: "Your Dropshipping Platform"
   - App Type: "Dropshipping"
   - Contact Info: Your email and phone
   - Business Description: "Automated dropshipping platform"

### Step 2: Get API Credentials

After approval (1-2 business days):

```env
ALIEXPRESS_APP_KEY=your_app_key_here
ALIEXPRESS_APP_SECRET=your_app_secret_here
```

Add these to your `.env` file.

### Step 3: OAuth 2.0 Authentication

#### Full Authentication Flow

```python
import requests
import hmac
import hashlib
import time

class AliExpressAuth:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api-sg.aliexpress.com/rest"

    def get_authorization_url(self, redirect_uri):
        """Step 1: Get authorization URL to redirect user"""
        auth_url = "https://oauth.aliexpress.com/authorize"

        params = {
            "response_type": "code",
            "client_id": self.app_key,
            "redirect_uri": redirect_uri,
            "state": "xyz123",  # CSRF token
            "view": "web",
            "sp": "ae"
        }

        # Build URL
        url = f"{auth_url}?response_type={params['response_type']}&client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&state={params['state']}&view={params['view']}&sp={params['sp']}"

        return url

    def _generate_signature(self, endpoint, params):
        """Generate HMAC-SHA256 signature"""
        sorted_keys = sorted(params.keys())
        concatenated = endpoint + "".join([f"{key}{params[key]}" for key in sorted_keys])

        sign = hmac.new(
            self.app_secret.encode('utf-8'),
            concatenated.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

        return sign

    def exchange_code_for_token(self, code):
        """Step 2: Exchange authorization code for access token"""
        endpoint = "/auth/token/create"
        timestamp = str(int(time.time() * 1000))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "sign_method": "sha256",
            "code": code
        }

        # Generate signature
        params["sign"] = self._generate_signature(endpoint, params)

        # Make request
        url = self.base_url + endpoint
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in"),
            "user_id": data.get("user_id")
        }

    def refresh_access_token(self, refresh_token):
        """Step 3: Refresh expired access token"""
        endpoint = "/auth/token/refresh"
        timestamp = str(int(time.time() * 1000))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "sign_method": "sha256",
            "refresh_token": refresh_token
        }

        params["sign"] = self._generate_signature(endpoint, params)

        url = self.base_url + endpoint
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in")
        }

# Usage example
auth = AliExpressAuth(
    app_key="your_app_key",
    app_secret="your_app_secret"
)

# 1. Get authorization URL
auth_url = auth.get_authorization_url("https://yourapp.com/callback")
print(f"Redirect user to: {auth_url}")

# 2. After user approves, exchange code for token
# (code received from callback URL parameter)
tokens = auth.exchange_code_for_token("authorization_code_from_callback")
print(f"Access Token: {tokens['access_token']}")

# Save tokens to .env
# ALIEXPRESS_ACCESS_TOKEN=...
# ALIEXPRESS_REFRESH_TOKEN=...

# 3. Refresh token when expired
new_tokens = auth.refresh_access_token(tokens['refresh_token'])
```

## 📡 API Endpoints

### 1. Product Search

Search for products to import into your store.

**Endpoint:** `POST /api/aliexpress/products/search`

```bash
curl -X POST http://localhost:8000/api/aliexpress/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "wireless earbuds",
    "min_price": 5,
    "max_price": 30,
    "min_orders": 100,
    "limit": 20
  }'
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "product_id": "1005001234567890",
      "product_title": "Wireless Bluetooth Earbuds",
      "target_sale_price": "19.99",
      "original_price": "39.99",
      "discount": "50%",
      "product_detail_url": "https://www.aliexpress.com/item/...",
      "product_main_image_url": "https://ae01.alicdn.com/...",
      "volume": 5000,
      "evaluation_rate": "98%",
      "ship_to_days": "3-7"
    }
  ],
  "count": 20
}
```

**Python Example:**
```python
from services.aliexpress_service import AliExpressService

ali_service = AliExpressService()

# Search for products
products = await ali_service.search_products(
    keywords="yoga mat",
    min_price=10,
    max_price=50,
    min_orders=500,
    limit=10
)

# Filter high-quality products
quality_products = [
    p for p in products
    if float(p.get('evaluation_rate', '0%').rstrip('%')) > 95
]

print(f"Found {len(quality_products)} high-quality products")
```

### 2. Get Product Details

Get detailed information about a specific product.

**Endpoint:** `GET /api/aliexpress/products/{product_id}`

```bash
curl http://localhost:8000/api/aliexpress/products/1005001234567890
```

**Response:**
```json
{
  "success": true,
  "data": {
    "product_id": "1005001234567890",
    "product_title": "Premium Yoga Mat",
    "description": "Eco-friendly, non-slip yoga mat...",
    "price": "24.99",
    "stock": 5000,
    "images": [
      "https://ae01.alicdn.com/image1.jpg",
      "https://ae01.alicdn.com/image2.jpg"
    ],
    "variants": [
      {
        "sku_id": "14:193#Blue",
        "color": "Blue",
        "price": "24.99",
        "stock": 2000
      }
    ],
    "shipping_info": {
      "country": "US",
      "shipping_fee": "0.00",
      "delivery_time": "3-7 days"
    }
  }
}
```

### 3. Place Order (Automated Fulfillment)

Automatically place an order with AliExpress when customer orders.

**Endpoint:** `POST /api/aliexpress/orders/place`

```bash
curl -X POST http://localhost:8000/api/aliexpress/orders/place \
  -H "Content-Type: application/json" \
  -d '{
    "shopify_order_id": "12345",
    "products": [
      {
        "product_id": "1005001234567890",
        "quantity": 1,
        "sku_attr": "14:193#Blue"
      }
    ],
    "shipping_address": {
      "name": "John Doe",
      "address1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "US",
      "phone": "1234567890"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Order placement initiated",
  "shopify_order_id": "12345"
}
```

### 4. Get Order Status

Track order status and get tracking information.

**Endpoint:** `GET /api/aliexpress/orders/{order_id}/status`

```bash
curl http://localhost:8000/api/aliexpress/orders/ABC123456/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order_id": "ABC123456",
    "order_status": "WAIT_SELLER_SEND_GOODS",
    "logistics_status": "PROCESSING",
    "tracking_number": "LP123456789CN",
    "carrier": "China Post",
    "estimated_delivery": "2025-01-15"
  }
}
```

### 5. Get Categories

List product categories for filtering.

**Endpoint:** `GET /api/aliexpress/categories`

```bash
curl http://localhost:8000/api/aliexpress/categories
```

## 🔄 Complete Workflow Example

### Automated Product Import and Fulfillment

```python
import asyncio
from services.aliexpress_service import AliExpressService
from services.shopify_service import ShopifyService

async def automate_dropshipping():
    """Complete dropshipping automation workflow"""

    ali_service = AliExpressService()
    shopify_service = ShopifyService()

    # 1. PRODUCT RESEARCH
    print("🔍 Searching for trending products...")
    products = await ali_service.search_products(
        keywords="eco-friendly water bottle",
        min_price=5,
        max_price=20,
        min_orders=1000,
        limit=10
    )

    # 2. QUALITY FILTER
    print("✅ Filtering quality products...")
    quality_products = [
        p for p in products
        if float(p.get('evaluation_rate', '0%').rstrip('%')) > 95
        and p.get('volume', 0) > 1000
    ]

    # 3. IMPORT TO SHOPIFY
    print(f"📦 Importing {len(quality_products)} products to Shopify...")
    for product in quality_products:
        # Get detailed info
        details = await ali_service.get_product_details(product['product_id'])

        # Calculate price with markup
        cost_price = float(details['price'])
        markup = 1.4  # 40% markup
        selling_price = round(cost_price * markup, 2)

        # Create in Shopify
        shopify_product = await shopify_service.create_product({
            "title": details['product_title'],
            "description": details['description'],
            "vendor": "AliExpress",
            "price": selling_price,
            "cost": cost_price,
            "images": details['images'],
            "variants": details.get('variants', []),
            "sku": product['product_id']
        })

        print(f"✓ Imported: {shopify_product['title']} (${selling_price})")

    # 4. MONITOR ORDERS
    print("👀 Monitoring for new orders...")
    # This would be triggered by Shopify webhooks

    # 5. AUTO-FULFILL
    # When order received, automatically place with AliExpress

    return {
        "imported": len(quality_products),
        "status": "success"
    }

# Run automation
asyncio.run(automate_dropshipping())
```

## 🛠️ Advanced Features

### 1. Batch Product Import

```python
async def batch_import_products(product_ids, markup_percentage=40):
    """Import multiple products at once"""

    ali_service = AliExpressService()
    shopify_service = ShopifyService()

    results = []

    for product_id in product_ids:
        try:
            # Get product details
            product = await ali_service.get_product_details(product_id)

            # Calculate pricing
            cost = float(product['price'])
            price = round(cost * (1 + markup_percentage/100), 2)

            # Create in Shopify
            shopify_product = await shopify_service.create_product({
                "title": product['product_title'],
                "description": product['description'],
                "price": price,
                "cost": cost,
                "images": product['images'],
                "sku": product_id
            })

            results.append({
                "product_id": product_id,
                "shopify_id": shopify_product['id'],
                "status": "success"
            })

        except Exception as e:
            results.append({
                "product_id": product_id,
                "status": "failed",
                "error": str(e)
            })

    return results
```

### 2. Inventory Sync

```python
async def sync_inventory_from_aliexpress():
    """Sync inventory levels from AliExpress"""

    ali_service = AliExpressService()
    shopify_service = ShopifyService()

    # Get all products from Shopify
    shopify_products = await shopify_service.list_products(limit=250)

    for product in shopify_products:
        # Get AliExpress product ID from SKU
        ali_product_id = product.get('sku')

        if ali_product_id:
            try:
                # Get current stock from AliExpress
                ali_product = await ali_service.get_product_details(ali_product_id)
                current_stock = ali_product.get('stock', 0)

                # Update Shopify
                await shopify_service.update_product(product['id'], {
                    "variants": [{
                        "inventory_quantity": current_stock
                    }]
                })

                print(f"✓ Synced {product['title']}: {current_stock} units")

            except Exception as e:
                print(f"✗ Error syncing {product['title']}: {e}")

        # Rate limiting
        await asyncio.sleep(0.5)
```

### 3. Price Monitoring

```python
async def monitor_and_adjust_prices():
    """Monitor AliExpress prices and adjust Shopify accordingly"""

    ali_service = AliExpressService()
    shopify_service = ShopifyService()

    shopify_products = await shopify_service.list_products()

    for product in shopify_products:
        ali_product_id = product.get('sku')

        if ali_product_id:
            # Get current AliExpress price
            ali_product = await ali_service.get_product_details(ali_product_id)
            new_cost = float(ali_product['price'])

            # Get current Shopify price
            current_price = float(product['variants'][0]['price'])
            current_cost = float(product.get('cost', 0))

            # Check if supplier price changed
            if new_cost != current_cost:
                # Maintain same margin
                margin_percentage = ((current_price - current_cost) / current_cost) * 100
                new_price = round(new_cost * (1 + margin_percentage/100), 2)

                # Update Shopify
                await shopify_service.update_product(product['id'], {
                    "variants": [{
                        "price": new_price,
                        "cost": new_cost
                    }]
                })

                print(f"💰 Price adjusted: {product['title']}")
                print(f"   Old: ${current_price} (cost: ${current_cost})")
                print(f"   New: ${new_price} (cost: ${new_cost})")
```

## 🚨 Error Handling

### Common Errors and Solutions

```python
class AliExpressAPIError(Exception):
    """Custom exception for AliExpress API errors"""
    pass

async def safe_api_call(func, *args, max_retries=3, **kwargs):
    """Wrapper for API calls with retry logic"""

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⏱️  Timeout. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise AliExpressAPIError("API timeout after retries")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                print("🚫 Rate limit hit. Waiting 60s...")
                await asyncio.sleep(60)
            elif e.response.status_code == 401:  # Auth error
                print("🔐 Token expired. Refreshing...")
                # Refresh token logic here
            else:
                raise AliExpressAPIError(f"HTTP error: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")
            raise

# Usage
result = await safe_api_call(
    ali_service.search_products,
    keywords="product",
    limit=10
)
```

## 📊 Rate Limits

AliExpress API rate limits:
- **Standard:** 100 requests/minute
- **Search API:** 50 requests/minute
- **Order API:** 30 requests/minute

**Best Practices:**
```python
import time
from functools import wraps

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    async def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls
            self.calls = [c for c in self.calls if c > now - self.period]

            # Check if limit exceeded
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                print(f"⏸️  Rate limit. Waiting {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
                self.calls = []

            # Make call
            self.calls.append(time.time())
            return await func(*args, **kwargs)

        return wrapper

# Apply rate limiter
search_limiter = RateLimiter(max_calls=50, period=60)

@search_limiter
async def search_with_limit(keywords):
    return await ali_service.search_products(keywords=keywords)
```

## 🔐 Security Best Practices

1. **Never commit credentials**
   ```bash
   # .gitignore
   .env
   .env.local
   *.key
   ```

2. **Encrypt tokens in database**
   ```python
   from cryptography.fernet import Fernet

   def encrypt_token(token, key):
       f = Fernet(key)
       return f.encrypt(token.encode()).decode()

   def decrypt_token(encrypted_token, key):
       f = Fernet(key)
       return f.decrypt(encrypted_token.encode()).decode()
   ```

3. **Rotate tokens regularly**
   ```python
   async def auto_refresh_token():
       """Automatically refresh token before expiry"""
       while True:
           await asyncio.sleep(3600)  # Check hourly
           # Refresh if expires in < 24 hours
           await ali_service.refresh_access_token()
   ```

## 📝 Testing

```python
import pytest
from services.aliexpress_service import AliExpressService

@pytest.mark.asyncio
async def test_product_search():
    """Test product search functionality"""
    service = AliExpressService()

    results = await service.search_products(
        keywords="test product",
        limit=5
    )

    assert len(results) <= 5
    assert all('product_id' in p for p in results)

@pytest.mark.asyncio
async def test_get_product_details():
    """Test getting product details"""
    service = AliExpressService()

    product = await service.get_product_details("1005001234567890")

    assert product['product_id'] == "1005001234567890"
    assert 'product_title' in product
    assert 'price' in product
```

## 📞 Support

If you encounter issues:

1. **Check API status:** https://status.aliexpress.com
2. **Review error codes:** See AliExpress Developer Docs
3. **Contact support:** developers@aliexpress.com
4. **Community:** AliExpress Developer Forum

## 🔗 Resources

- **Developer Portal:** https://developers.aliexpress.com
- **API Documentation:** https://developers.aliexpress.com/en/doc.htm
- **Dropshipping Guide:** See DROPSHIPPING_GUIDE.md
- **Code Examples:** backend/examples/aliexpress/

---

**Your AliExpress integration is ready! Start importing products and automating fulfillment.** 🚀
