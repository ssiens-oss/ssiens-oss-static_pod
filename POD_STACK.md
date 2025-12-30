# StaticWaves POD Stack

**Complete AI-Powered Print-on-Demand Automation System**

[![Build Status](https://github.com/ssiens-oss/ssiens-oss-static_pod/workflows/Build%20&%20Release/badge.svg)](https://github.com/ssiens-oss/ssiens-oss-static_pod/actions)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)

---

## 🚀 What You Get

This is a production-ready, end-to-end POD automation system:

### Core Capabilities

- 🧠 **AI Art Engine** - ComfyUI GPU workers for batch design generation
- 🧾 **Design Queue** - Managed pipeline (pending → processing → done/failed)
- 🧵 **Auto Mockups** - Hoodie, tee, poster templates with design compositing
- 🏷️ **Auto Pricing** - Configurable cost + margin rules
- 🛒 **Auto Publish** - Printify → Shopify → TikTok Shop orchestration
- 🧪 **Pre-Publish Validator** - TikTok-safe compliance checks
- 🔔 **Alerts** - Discord & Telegram notifications per SKU
- 🖥️ **Web Dashboard** - Status, logs, manual controls (integrates with existing UI)
- 🧰 **Systemd Services** - Always-on, auto-restart daemons
- 🔐 **License Enforcement** - Commercial SaaS controls with usage limits
- 📦 **Debian Packaging** - One-command install via `.deb`
- 🏷️ **White-Label Support** - Client-specific branded installers

---

## 📦 Installation

### Option 1: One-Command Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/install-master.sh | sudo bash
```

### Option 2: APT Repository (Coming Soon)

```bash
# Add StaticWaves APT repo
curl -fsSL https://apt.staticwaves.io/staticwaves-pod.gpg | sudo gpg --dearmor -o /usr/share/keyrings/staticwaves-pod.gpg

echo "deb [signed-by=/usr/share/keyrings/staticwaves-pod.gpg] https://apt.staticwaves.io stable main" | sudo tee /etc/apt/sources.list.d/staticwaves-pod.list

# Install
sudo apt update
sudo apt install staticwaves-pod
```

### Option 3: Manual .deb Install

```bash
# Download latest release
wget https://github.com/ssiens-oss/ssiens-oss-static_pod/releases/latest/download/staticwaves-pod_1.0.0_amd64.deb

# Install
sudo dpkg -i staticwaves-pod_1.0.0_amd64.deb
sudo apt --fix-broken install
```

---

## ⚙️ Configuration

### 1. API Keys Setup

```bash
sudo nano /opt/staticwaves-pod/config/.env
```

Required variables:

```bash
# Printify
PRINTIFY_API_KEY=sk_live_***
PRINTIFY_SHOP_ID=******

# Shopify
SHOPIFY_API_KEY=***
SHOPIFY_STORE=your-store.myshopify.com

# TikTok Shop
TIKTOK_SHOP_ID=***
TIKTOK_ACCESS_TOKEN=***

# ComfyUI
COMFYUI_API=http://localhost:8188

# Alerts (optional)
DISCORD_WEBHOOK=https://discord.com/api/webhooks/***
TELEGRAM_BOT_TOKEN=***
TELEGRAM_CHAT_ID=***
```

### 2. Start Services

```bash
# Start worker
sudo systemctl start staticwaves-pod-worker

# Check status
sudo systemctl status staticwaves-pod-api
sudo systemctl status staticwaves-pod-worker

# View logs
sudo journalctl -u staticwaves-pod-api -f
```

### 3. Test Installation

```bash
# Health check
curl http://localhost:5000/health

# Queue status
curl http://localhost:5000/queue
```

---

## 🔥 Usage

### Daily Workflow (Fully Autonomous)

1. **Drop prompts** → `data/queue/pending/`
2. **ComfyUI generates** art
3. **Mockups auto-render**
4. **Validator checks** TikTok rules
5. **Printify upload**
6. **Shopify publish**
7. **TikTok Shop sync**
8. **Alert fired** ✅

**Zero clicks. Fully autonomous.**

### API Usage

#### Publish a Product

```bash
curl -X POST http://localhost:5000/publish \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cosmic Waves Hoodie",
    "description": "AI-generated cosmic design",
    "prompt": "cosmic waves nebula stars",
    "type": "hoodie",
    "base_cost": 35.00,
    "inventory": 100
  }'
```

#### Add to Queue

```bash
curl -X POST http://localhost:5000/queue/add \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Neon Dreams Tee",
    "prompt": "neon cyberpunk cityscape",
    "type": "tee",
    "base_cost": 18.00,
    "inventory": 50
  }'
```

#### Check Queue Status

```bash
curl http://localhost:5000/queue
```

#### Get Statistics

```bash
curl http://localhost:5000/stats
```

---

## 📁 Directory Structure

```
/opt/staticwaves-pod/
├── api/
│   ├── app.py                 # Flask API (control plane)
│   ├── publish.py             # Unified publish orchestrator
│   ├── pricing.py             # Cost + margin logic
│   ├── validators.py          # TikTok / Shopify safety checks
│   ├── alerts.py              # Discord / Telegram
│   └── license.py             # License enforcement
├── workers/
│   ├── comfy_worker.py        # GPU image generation
│   ├── mockup_worker.py       # Hoodie/tee mockups
│   └── uploader.py            # Printify image upload
├── config/
│   ├── .env                   # Your API keys (SECRET)
│   ├── pricing.json           # Margin rules
│   └── products.json          # Product templates
├── data/
│   ├── queue/
│   │   ├── pending/
│   │   ├── processing/
│   │   ├── done/
│   │   └── failed/
│   ├── designs/
│   └── logs/
└── systemd/
    ├── staticwaves-pod-api.service
    ├── staticwaves-pod-worker.service
    └── staticwaves-comfyui.service
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React)                      │
│              (existing components + UI)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                  Flask API Server                       │
│            (port 5000, systemd managed)                 │
│  Routes: /health, /publish, /queue, /stats             │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌────────▼────────┐
│  ComfyUI Worker│          │ Mockup Worker   │
│   (GPU-based)  │          │ (PIL/Pillow)    │
└───────┬────────┘          └────────┬────────┘
        │                            │
        └──────────┬─────────────────┘
                   │
         ┌─────────▼──────────┐
         │  Uploader Worker   │
         │  (Printify API)    │
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌─────▼─────┐  ┌────▼─────┐
│Printify│  │  Shopify  │  │ TikTok   │
└────────┘  └───────────┘  └──────────┘
```

---

## 🔐 License System

StaticWaves POD includes commercial license enforcement:

### License Tiers

| Tier       | SKUs/Day | Price      |
|------------|----------|------------|
| Solo       | 10       | $49/mo     |
| Agency     | 50       | $149/mo    |
| Enterprise | 500      | $499/mo    |
| Unlimited  | ∞        | Custom     |

### License File Format

```json
{
  "client_id": "acme",
  "tier": "agency",
  "max_skus_per_day": 50,
  "expires": "2025-12-31",
  "signature": "..."
}
```

Located at: `/opt/staticwaves/license.json`

### Development Mode

Bypass license checks during development:

```bash
export STATICWAVES_DEV_MODE=true
```

---

## 🏷️ White-Label Distribution

Build client-specific branded installers:

```bash
./build-whitelabel.sh <client_id> <tier> <expires>

# Example
./build-whitelabel.sh acme agency 2025-12-31
```

This creates:
- Custom package name: `staticwaves-pod-client-acme`
- Embedded license
- Client-specific systemd services
- Isolated installation

---

## 🚢 Building from Source

### Build Standard .deb

```bash
./build-deb.sh
```

Output: `staticwaves-pod_1.0.0_amd64.deb`

### Build with GPG Signing

```bash
# First time: Generate GPG key
gpg --full-generate-key

# Sign package
dpkg-sig --sign builder staticwaves-pod_1.0.0_amd64.deb

# Verify
dpkg-sig --verify staticwaves-pod_1.0.0_amd64.deb
```

---

## 🔄 CI/CD Pipeline

GitHub Actions automatically:

1. **Builds** `.deb` on every tag push
2. **Signs** with GPG (if configured)
3. **Creates** GitHub Release
4. **Uploads** to APT repository (if configured)
5. **Builds** white-label variants (on dispatch)

### Setup Secrets

In GitHub repository settings → Secrets:

```
GPG_PRIVATE_KEY          # Your GPG private key
GPG_PASSPHRASE           # GPG key passphrase
APT_REPO_SSH_KEY         # SSH key for APT server
APT_REPO_HOST            # APT server hostname
APT_REPO_USER            # APT server username
```

### Trigger Release

```bash
git tag v1.0.1
git push origin v1.0.1
```

---

## 📊 Monitoring & Logs

### Service Status

```bash
systemctl status staticwaves-pod-api
systemctl status staticwaves-pod-worker
```

### Live Logs

```bash
# API logs
sudo journalctl -u staticwaves-pod-api -f

# Worker logs
sudo journalctl -u staticwaves-pod-worker -f

# All POD services
sudo journalctl -u "staticwaves-pod-*" -f
```

### Queue Inspection

```bash
# Count items
ls /opt/staticwaves-pod/data/queue/pending/ | wc -l

# View pending items
cat /opt/staticwaves-pod/data/queue/pending/*.json

# Check failures
cat /opt/staticwaves-pod/data/queue/failed/*.json
```

---

## 🛠️ Troubleshooting

### API Not Starting

```bash
# Check logs
sudo journalctl -u staticwaves-pod-api -n 50

# Verify port
sudo lsof -i :5000

# Check config
cat /opt/staticwaves-pod/config/.env
```

### Worker Stuck

```bash
# Restart worker
sudo systemctl restart staticwaves-pod-worker

# Check queue
ls /opt/staticwaves-pod/data/queue/processing/

# Clear stuck items
sudo mv /opt/staticwaves-pod/data/queue/processing/* \
        /opt/staticwaves-pod/data/queue/pending/
```

### ComfyUI Issues

```bash
# Check ComfyUI status
curl http://localhost:8188/system_stats

# Restart ComfyUI
sudo systemctl restart staticwaves-comfyui

# Check GPU
nvidia-smi
```

### License Errors

```bash
# Check license
cat /opt/staticwaves/license.json

# Enable dev mode
echo "STATICWAVES_DEV_MODE=true" | sudo tee -a /opt/staticwaves-pod/config/.env
sudo systemctl restart staticwaves-pod-api
```

---

## 🚀 Next-Level Upgrades

### Recommended Enhancements

- 🔁 **Usage-based billing** (Stripe integration)
- 🧠 **Prompt A/B testing** (conversion-driven optimization)
- 🧾 **SKU bundler** (product packs for higher AOV)
- 🖼️ **Video mockups** (TikTok-first media)
- 📦 **White-label SaaS** edition
- 🌐 **APT auto-update** repository
- 🔐 **Multi-tenant** isolation
- 📊 **Analytics dashboard** (real-time metrics)

---

## 📚 Additional Documentation

- [API Reference](API.md)
- [Configuration Guide](CONFIGURATION.md)
- [APT Repository Setup](APT_REPO.md)
- [White-Label Guide](WHITELABEL.md)

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ssiens-oss/ssiens-oss-static_pod/discussions)
- **Email**: ops@staticwaves.io

---

## 📄 License

Proprietary - StaticWaves © 2024

For licensing inquiries: ops@staticwaves.io

---

**Built with ⚡ by the StaticWaves team**
