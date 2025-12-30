# AliExpress Integration Examples

Practical examples for using the AliExpress API in your dropshipping business.

## 📋 Examples

### 1. Product Research (`product_research.py`)

Find winning products across multiple niches.

```bash
python examples/aliexpress/product_research.py
```

**Features:**
- Search multiple niches automatically
- Filter by quality (rating > 95%, orders > 1000)
- Calculate profit margins
- Display top winners
- Estimate monthly revenue

**Output:**
```
🔍 Researching: eco-friendly yoga mat
✅ Found 10 products

📊 Top 3 Winners in 'eco-friendly yoga mat':

1. Premium TPE Yoga Mat Eco-Friendly Non-Slip...
   💰 Cost: $12.99 → Sell: $18.19 (Profit: $5.20)
   📦 Orders: 5,234 | ⭐ Rating: 98.5%
   🔗 https://www.aliexpress.com/item/...
```

### 2. Auto Fulfillment (`auto_fulfillment.py`)

Automatically fulfill Shopify orders via AliExpress.

```bash
# Fulfill all pending orders
python examples/aliexpress/auto_fulfillment.py

# Check specific order status
python examples/aliexpress/auto_fulfillment.py --check-status ORDER123
```

**Workflow:**
1. Fetch unfulfilled orders from Shopify
2. Extract AliExpress product IDs from SKUs
3. Place orders on AliExpress
4. Update Shopify with tracking info
5. Notify customers

## 🔧 Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure .env:**
   ```env
   ALIEXPRESS_APP_KEY=your_key
   ALIEXPRESS_APP_SECRET=your_secret
   ALIEXPRESS_ACCESS_TOKEN=your_token
   SHOPIFY_ACCESS_TOKEN=your_token
   SHOPIFY_SHOP_URL=yourstore.myshopify.com
   ```

3. **Run authentication:**
   ```bash
   python utils/aliexpress_auth.py
   ```

## 💡 Usage Tips

### Finding Profitable Products

1. **Target metrics:**
   - Orders: > 1,000 (proven demand)
   - Rating: > 95% (quality)
   - Price: $5-50 (sweet spot)
   - Margin: 30-50%

2. **Best niches:**
   - Eco-friendly products
   - Fitness accessories
   - Phone accessories
   - Home organization
   - Pet supplies

3. **Avoid:**
   - Fragile items
   - Seasonal products (unless planned)
   - Copyrighted/branded items
   - Very cheap items (< $5)

### Automation Best Practices

1. **Order fulfillment:**
   - Run hourly via cron
   - Monitor failed orders
   - Set up alerts for issues
   - Keep backup suppliers

2. **Inventory sync:**
   - Sync every 4-6 hours
   - Set low-stock alerts at 10 units
   - Auto-pause out-of-stock items

3. **Error handling:**
   - Retry failed orders (max 3 times)
   - Log all errors
   - Manual review for exceptions

## 🤖 Scheduled Automation

### Cron Jobs

Add to your crontab:

```bash
# Fulfill orders every hour
0 * * * * cd /path/to/backend && python examples/aliexpress/auto_fulfillment.py

# Research new products daily
0 9 * * * cd /path/to/backend && python examples/aliexpress/product_research.py

# Sync inventory every 4 hours
0 */4 * * * cd /path/to/backend && python -c "from services.shopify_service import ShopifyService; import asyncio; asyncio.run(ShopifyService().sync_inventory())"
```

### Systemd Service

Create `/etc/systemd/system/aliexpress-fulfillment.service`:

```ini
[Unit]
Description=AliExpress Auto Fulfillment
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/python examples/aliexpress/auto_fulfillment.py
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable aliexpress-fulfillment
sudo systemctl start aliexpress-fulfillment
```

## 📊 Monitoring

Track these metrics:

- **Fulfillment rate:** > 95%
- **Average fulfillment time:** < 24 hours
- **Failed orders:** < 2%
- **Customer satisfaction:** > 90%

## 🚨 Troubleshooting

### Common Issues

**"Invalid signature"**
- Check app secret is correct
- Verify timestamp format
- Ensure parameters are sorted

**"Token expired"**
```bash
python utils/aliexpress_auth.py
```

**"Rate limit exceeded"**
- Reduce request frequency
- Implement exponential backoff
- Upgrade API tier

**"Order placement failed"**
- Verify shipping address format
- Check product availability
- Ensure sufficient account balance

## 🔗 Resources

- [AliExpress API Docs](https://developers.aliexpress.com)
- [Dropshipping Guide](../../DROPSHIPPING_GUIDE.md)
- [API Guide](../ALIEXPRESS_API_GUIDE.md)
