# 🧠 StaticWaves POD → TikTok Engine v3

**Enterprise-grade TikTok Shop automation for Print-on-Demand**

This is revenue-grade infrastructure — not theory. Built for TikTok longevity + Gumroad resale.

---

## ✅ Features (ALL 5 Implemented)

1. **🔁 TikTok OAuth Auto-Refresh** - Zero downtime, automatic token renewal
2. **🧠 Auto-Kill Losing Price Buckets** - Automatically removes underperforming prices
3. **📈 SKU-Level Analytics** - Track impressions, clicks, orders, and CVR per price
4. **📦 White-Label SaaS Packaging** - License validation + branding customization
5. **🧾 Appeal-Safe Listing Generator** - Policy-compliant descriptions that survive audits

---

## 📁 Project Structure

```
staticwaves_pod/
├── core/
│   ├── __init__.py
│   └── logger.py                  # Logging utility
│
├── tiktok/
│   ├── __init__.py
│   ├── oauth.py                   # OAuth auto-refresh
│   ├── analytics.py               # SKU analytics engine
│   ├── price_optimizer.py         # Auto-kill losing prices
│   ├── appeal_safe_copy.py        # Policy-safe copy generator
│   └── uploader.py                # Main product uploader
│
├── saas/
│   ├── __init__.py
│   ├── license.py                 # License key validation
│   ├── branding.py                # White-label branding
│   └── bootstrap.py               # SaaS initialization
│
└── data/
    ├── oauth.json                 # OAuth state (auto-generated)
    └── tiktok_metrics.json        # Analytics data (auto-generated)
```

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local with your credentials
```

Required variables:
- `TIKTOK_CLIENT_ID` - Your TikTok app client ID
- `TIKTOK_CLIENT_SECRET` - Your TikTok app secret
- `LICENSE_KEY` - Generate with: `python -m staticwaves_pod.saas.license generate`

### 3️⃣ Initialize OAuth State

After completing TikTok OAuth flow, initialize state:

```python
from staticwaves_pod.tiktok.oauth import initialize_oauth_state

initialize_oauth_state(
    access_token="your_access_token",
    refresh_token="your_refresh_token",
    expires_in=86400  # seconds
)
```

### 4️⃣ Upload Products

```python
from staticwaves_pod.tiktok.uploader import TikTokUploader

uploader = TikTokUploader()

uploader.upload_product(
    sku="HOODIE-001",
    name="Midnight Waves Hoodie",
    price=29.99,
    images=["https://example.com/image.jpg"],
    product_type="hoodie",
    features=["premium cotton", "unique design"]
)
```

---

## 🔁 OAuth Auto-Refresh

**Location:** `staticwaves_pod/tiktok/oauth.py`

### How It Works

- Automatically refreshes tokens 5 minutes before expiry
- Zero manual intervention required
- Prevents failed uploads due to expired tokens

### Usage

```python
from staticwaves_pod.tiktok.oauth import get_token

# Always returns a valid token
token = get_token()  # Auto-refreshes if needed
```

---

## 🧠 Auto-Kill Losing Price Buckets

**Location:** `staticwaves_pod/tiktok/price_optimizer.py`

### How It Works

- Tracks performance per price point
- Removes prices with:
  - `impressions >= 500` AND
  - `CVR < 1%`
- Stops wasting impressions on non-converters

### Usage

```python
from staticwaves_pod.tiktok.price_optimizer import prune_prices, lock_winning_price

# Remove underperforming prices
removed = prune_prices()

# Lock winning price for a SKU
winning_price = lock_winning_price("HOODIE-001", min_orders=10)
```

---

## 📈 SKU Analytics

**Location:** `staticwaves_pod/tiktok/analytics.py`

### Track Events

```python
from staticwaves_pod.tiktok.analytics import record_event, compute_cvr

# Track events
record_event("HOODIE-001", 29.99, "impressions")
record_event("HOODIE-001", 29.99, "clicks")
record_event("HOODIE-001", 29.99, "orders")

# Compute conversion rates
compute_cvr()
```

### Get Best Price

```python
from staticwaves_pod.tiktok.analytics import get_best_price

price, metrics = get_best_price("HOODIE-001")
print(f"Best price: ${price} (CVR: {metrics['cvr']:.2%})")
```

---

## 🧾 Appeal-Safe Copy

**Location:** `staticwaves_pod/tiktok/appeal_safe_copy.py`

### Generate Safe Descriptions

```python
from staticwaves_pod.tiktok.appeal_safe_copy import generate, validate_copy

# Generate policy-compliant copy
desc = generate(
    "Midnight Waves Hoodie",
    product_type="hoodie",
    features=["premium cotton", "unique design"]
)

# Validate existing copy
is_safe, violations = validate_copy("Your copy here")
```

### Banned Phrases

Automatically removes:
- "guaranteed", "viral", "best seller"
- "limited time only", "act now"
- All urgency/hype language

---

## 📦 White-Label SaaS

**Location:** `staticwaves_pod/saas/`

### Generate License Key

```bash
python -m staticwaves_pod.saas.license generate
```

### Customize Branding

Set in `.env.local`:

```bash
SAAS_BRAND=YourBrand
SAAS_COLOR=#FF5733
SAAS_LOGO=/your-logo.png
```

### Initialize SaaS

```python
from staticwaves_pod.saas.bootstrap import init, health_check

# Initialize and validate
init()

# Check health
status = health_check()
```

---

## ⚙️ Automation with systemd

Create `/etc/systemd/system/staticwaves-upload.service`:

```ini
[Unit]
Description=StaticWaves TikTok Uploader
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/staticwaves_pod
ExecStart=/usr/bin/python3 /opt/staticwaves_pod/staticwaves_pod/tiktok/uploader.py
ExecStartPost=/usr/bin/python3 /opt/staticwaves_pod/staticwaves_pod/tiktok/price_optimizer.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable staticwaves-upload
sudo systemctl start staticwaves-upload
```

---

## 💰 Gumroad SaaS Packaging

### Recommended SKUs

| SKU                      | Price | Features                                      |
|--------------------------|-------|-----------------------------------------------|
| TikTok POD Engine        | $79   | Core features, single store                   |
| TikTok POD Engine PRO    | $149  | + Analytics dashboard, 3 stores               |
| White-Label SaaS         | $399  | + Custom branding, unlimited stores           |
| Agency Unlimited         | $999  | + Multi-client tenancy, priority support      |

### What's Included

✅ Full source code
✅ Documentation
✅ License key generation
✅ White-label branding
✅ Updates for 1 year

---

## 🎯 Next Steps

Choose one to implement next:

1. **TikTok Seller webhook ingestion** - Real-time order/event processing
2. **Auto-pause SKUs on shadowban signals** - Detect and pause flagged products
3. **Winning price lock-in logic** - Automatically lock best performers
4. **Multi-store / multi-client tenancy** - Manage multiple TikTok shops
5. **Investor-ready metrics** - Dashboard with KPIs and growth metrics

---

## 📞 Support

- **Docs:** Check inline comments in each module
- **Issues:** File issues in your repository
- **License:** Commercial use allowed with valid license key

---

## 🔐 Security Notes

- Never commit `.env.local` or `data/oauth.json`
- Rotate `LICENSE_SALT` in production
- Use HTTPS for all API endpoints
- Regularly audit banned phrase list

---

**Built for scale. Designed for revenue. Ready to ship.** 🚀
