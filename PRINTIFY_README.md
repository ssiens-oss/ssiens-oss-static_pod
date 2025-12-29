# StaticWaves Printify Auto-Publisher

**Production-grade POD automation with TikTok-safe validation**

---

## 🎯 Features

All 5 production features implemented:

1. **Auto-Pricing = Cost + Margin**
   - Dynamic pricing based on base cost + configurable margin
   - TikTok-safe rounding (always ends in .99)
   - Minimum price enforcement ($12.99)

2. **TikTok-Safe Validator**
   - Pre-publish validation against TikTok Shop rules
   - Variant limit enforcement (≤ 50)
   - Price minimum checking
   - Title length validation
   - Prevents silent TikTok rejections

3. **Multi-Platform Notifications**
   - Telegram bot integration
   - Discord webhooks
   - Slack webhooks (optional)
   - Success and failure alerts

4. **Multi-Product Templates**
   - One PNG → 4 SKUs automatically
   - Templates: Tee, Hoodie, Crewneck, Poster
   - Expandable to 8+ products (canvas, mug, phone case, tote bag)
   - Per-template margin configuration

5. **Immortal Daemon**
   - Never exits, auto-restarts
   - Heartbeat logging every 60s
   - Error recovery with exponential backoff
   - Queue-based processing

---

## 📁 Directory Structure

```
staticwaves_pod/
├── printify/
│   ├── __init__.py
│   ├── autopublish.py         # Main daemon
│   ├── templates.py            # Product templates
│   └── notifier.py             # Notification system
│
└── queue/
    ├── pending/                # Drop PNGs here
    ├── published/              # Successfully published
    └── failed/                 # Failed to publish
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
```

Edit `.env.local` with your credentials:

```bash
# Printify
PRINTIFY_API_KEY=pk_live_your_key_here
PRINTIFY_SHOP_ID=12345678

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Discord (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 3️⃣ Create Queue Directories

```bash
mkdir -p /opt/staticwaves_pod/queue/{pending,published,failed}
sudo chown -R $USER:$USER /opt/staticwaves_pod
```

### 4️⃣ Install systemd Service

```bash
sudo cp systemd/staticwaves-pod-engine.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable staticwaves-pod-engine
sudo systemctl start staticwaves-pod-engine
```

### 5️⃣ Watch Logs

```bash
journalctl -u staticwaves-pod-engine -f
```

---

## 📤 Publishing Products

### Drop a PNG into the Queue

```bash
cp my_design.png /opt/staticwaves_pod/queue/pending/
```

Within ~60 seconds:

- Image uploaded to Printify
- 4 products created (tee, hoodie, crewneck, poster)
- Auto-priced with margin
- TikTok-validated
- Notifications sent
- File moved to `published/`

---

## 🎨 Product Templates

### Default Templates

| Template | Blueprint | Base Cost | Margin | Sale Price |
|----------|-----------|-----------|--------|------------|
| Tee | 384 | $12.00 | 55% | $18.99 |
| Hoodie | 521 | $26.00 | 60% | $41.99 |
| Crewneck | 521 | $22.00 | 58% | $34.99 |
| Poster | 12 | $8.00 | 65% | $13.99 |

### Expandable Templates

Available in `templates.py`:

- Canvas
- Mug
- Phone Case
- Tote Bag
- Tank Top
- Sweatshirt
- Beanie
- Blanket

To add more templates, edit:

```python
# staticwaves_pod/printify/templates.py

PRODUCT_TEMPLATES = {
    "your_template": {
        "name": "Product Name",
        "blueprint_id": 123,
        "provider_id": 1,
        "variant_id": 1,
        "base_cost": 1500,  # $15.00
        "margin": 0.60  # 60%
    }
}
```

---

## 💰 Pricing Configuration

### How Auto-Pricing Works

```python
def calc_price(base_cost_cents: int, margin: float = 0.55) -> int:
    raw = base_cost_cents * (1 + margin)
    rounded = int((raw // 100) * 100 + 99)  # Round to X.99
    return max(1299, rounded)  # Minimum $12.99
```

### Per-Template Margins

Edit in `autopublish.py`:

```python
PRODUCT_TEMPLATES = {
    "hoodie": {
        "base_cost": 2600,  # $26.00
        "margin": 0.65      # 65% instead of 60%
    }
}
```

---

## 🛡️ TikTok Validation Rules

Before publishing, each product is validated:

| Rule | Enforcement |
|------|-------------|
| Variant limit | ≤ 50 variants |
| Price minimum | ≥ $5.00 |
| Title length | ≤ 120 characters |
| Visibility | Must be `true` |

Products failing validation:
- Move to `failed/` queue
- Send error notification
- Never reach Printify

---

## 🔔 Notifications

### Telegram Setup

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get bot token
3. Find your chat ID (use [@userinfobot](https://t.me/userinfobot))
4. Add to `.env.local`:

```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

### Discord Setup

1. Create webhook in Discord server settings
2. Copy webhook URL
3. Add to `.env.local`:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/abc...
```

### Notification Events

- ✅ Product published successfully
- ❌ Product failed to publish
- 🚀 Daemon started
- 🔥 Fatal errors

---

## 🔁 Daemon Management

### Check Status

```bash
sudo systemctl status staticwaves-pod-engine
```

### Restart

```bash
sudo systemctl restart staticwaves-pod-engine
```

### Stop

```bash
sudo systemctl stop staticwaves-pod-engine
```

### View Logs

```bash
# Live tail
journalctl -u staticwaves-pod-engine -f

# Last 100 lines
journalctl -u staticwaves-pod-engine -n 100

# Since yesterday
journalctl -u staticwaves-pod-engine --since yesterday
```

### Heartbeat Confirmation

Healthy daemon shows every 60 seconds:

```
❤️ heartbeat: alive, queue empty
```

Or when processing:

```
❤️ heartbeat: publish cycle complete
```

---

## 🧪 Testing

### Manual Test

```python
python3 - <<'PY'
from PIL import Image
from pathlib import Path

# Create test image
p = Path("/opt/staticwaves_pod/queue/pending")
p.mkdir(parents=True, exist_ok=True)

img = Image.new("RGBA", (4500, 5400), (255, 0, 0, 255))
img.save(p / "test_red.png")
print("✅ Test image created")
PY
```

Watch logs:

```bash
journalctl -u staticwaves-pod-engine -f
```

Expected output:

```
⬆️  Uploading image: test_red.png
📦 Publishing tee: Test Red – Unisex Heavy Cotton Tee
✅ Published tee: 12345678
📦 Publishing hoodie: Test Red – Unisex Heavy Blend Hoodie
✅ Published hoodie: 12345679
...
```

---

## 🔧 Troubleshooting

### No Heartbeat

1. Check service status:

```bash
sudo systemctl status staticwaves-pod-engine
```

2. Look for errors in logs:

```bash
journalctl -u staticwaves-pod-engine -n 50
```

3. Verify environment variables:

```bash
sudo systemctl cat staticwaves-pod-engine | grep EnvironmentFile
```

### Products Not Publishing

1. Check API credentials:

```bash
echo $PRINTIFY_API_KEY
echo $PRINTIFY_SHOP_ID
```

2. Verify queue permissions:

```bash
ls -ld /opt/staticwaves_pod/queue/pending
```

3. Check failed queue:

```bash
ls -la /opt/staticwaves_pod/queue/failed
```

### Notifications Not Sending

Test notification manually:

```python
from staticwaves_pod.printify.notifier import notify

notify("Test notification", level="info")
```

---

## 📊 Production Monitoring

### Key Metrics

- **Queue depth**: `ls /opt/staticwaves_pod/queue/pending | wc -l`
- **Success rate**: Compare `published/` vs `failed/` counts
- **Heartbeat interval**: Should be ~60s
- **Memory usage**: Check with `systemctl status`

### Automated Monitoring

Add to cron:

```bash
# Check heartbeat every 5 minutes
*/5 * * * * journalctl -u staticwaves-pod-engine -n 10 | grep -q "heartbeat" || /usr/bin/systemctl restart staticwaves-pod-engine
```

---

## 🚀 Advanced Usage

### Batch Upload

```bash
for img in designs/*.png; do
    cp "$img" /opt/staticwaves_pod/queue/pending/
done
```

### Retry Failed Products

```bash
mv /opt/staticwaves_pod/queue/failed/*.png /opt/staticwaves_pod/queue/pending/
```

### Custom Template Set

Create custom template configuration:

```python
# custom_templates.py
HOLIDAY_TEMPLATES = {
    "christmas_hoodie": {...},
    "christmas_mug": {...}
}
```

---

## 🔐 Security Notes

- Never commit `.env.local` with real credentials
- Rotate API keys periodically
- Use systemd sandboxing (already configured)
- Limit filesystem access with `ReadWritePaths`
- Monitor failed login attempts in Printify dashboard

---

## 📈 Next Upgrades

Choose one to add next:

1. **AI Design Generator** - Auto-create designs from prompts
2. **Auto-Kill Low ROI SKUs** - Remove underperformers
3. **Multi-Store Support** - Manage multiple shops
4. **Price A/B Testing** - Test price points automatically
5. **Revenue Dashboard** - Track profit per SKU

---

## 🔗 Integration with TikTok OAuth

This Printify engine works alongside the TikTok OAuth auto-refresh system:

- **Printify** handles product creation
- **TikTok OAuth** keeps shop connection alive
- **Analytics** tracks performance across both platforms

See `BACKEND_README.md` for TikTok integration details.

---

**Status: ✅ Production-Ready**

All 5 features implemented, tested, and daemon-safe.
