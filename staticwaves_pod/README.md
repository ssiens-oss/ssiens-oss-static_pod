# StaticWaves POD - Automated Print-on-Demand Pipeline

Production-ready POD automation system for design intake, processing, and multi-platform publishing.

## Features

✅ **Design Intake** - Queue-based design processing
✅ **Background Removal** - Automatic RMBG processing
✅ **Mockup Generation** - Automated product mockups
✅ **Printify Upload** - Direct API integration
✅ **Shopify Publishing** - Auto-publish to store
✅ **TikTok Shop Feeds** - XLSX export generator
✅ **systemd Ready** - Production deployment

## Installation

```bash
cd staticwaves_pod
chmod +x install.sh
./install.sh
```

## Configuration

Edit `.env` with your credentials:

```env
PRINTIFY_API_KEY=your_api_key
PRINTIFY_SHOP_ID=your_shop_id
SHOPIFY_STORE=your_store_name
SHOPIFY_TOKEN=your_access_token
TIKTOK_MODE=guard
LOG_LEVEL=INFO
```

## Directory Structure

```
staticwaves_pod/
├── api/              # Flask API endpoints
├── workers/          # Background processing workers
├── core/             # Shared utilities
├── queues/           # Processing queues
│   ├── incoming/     # New designs
│   ├── processed/    # RMBG complete
│   ├── published/    # Ready for upload
│   └── failed/       # Error handling
├── tools/            # TikTok feed generator
└── systemd/          # Service files
```

## Usage

### Manual Mode

```bash
# Start workers individually
python3 workers/rmbg_worker.py
python3 workers/mockup_worker.py
python3 workers/printify_worker.py
python3 workers/shopify_worker.py

# Start API
python3 api/app.py
```

### Production Mode (systemd)

```bash
# Install services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable staticwaves-*.service
sudo systemctl start staticwaves-*.service

# Check status
sudo systemctl status staticwaves-rmbg
```

## API Endpoints

**Health Check**
```bash
GET /api/health
```

**Upload Design**
```bash
POST /api/upload
Content-Type: multipart/form-data
file: design.png
```

**Queue Status**
```bash
GET /api/queue/status
```

## TikTok Shop Feed

Generate XLSX feed for TikTok Shop:

```bash
python3 tools/tiktok_feed_generator.py
```

Output: `exports/tiktok_shop_feed.xlsx`

## Workflow

1. **Upload** → Design lands in `queues/incoming/`
2. **RMBG** → Background removed → `queues/processed/`
3. **Mockup** → Applied to template → `queues/published/`
4. **Upload** → Sent to Printify
5. **Publish** → Created in Shopify
6. **Export** → TikTok feed generated

## Requirements

- Python 3.8+
- Linux (Ubuntu/Debian recommended)
- API credentials for Printify & Shopify
- Base mockup image (`assets/hoodie_base.png`)

## Monetization Ready

This system is designed for:
- 🎯 SaaS products
- 💰 Gumroad/digital products
- 🏢 Agency automation
- 🔁 White-label licensing

## Next Steps

1. Add base mockup image to `assets/hoodie_base.png`
2. Configure API credentials in `.env`
3. Test with sample design
4. Deploy systemd services
5. Monitor logs

## License

Production-ready POD automation toolkit.
