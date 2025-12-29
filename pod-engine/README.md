# StaticWaves POD Engine v3.0

Enterprise-grade Print-on-Demand automation platform with AI generation, multi-platform publishing, and agency management.

## 🚀 Features

### Core Pipeline
- ✅ AI Image Generation (ComfyUI integration)
- ✅ Background Removal (RMBG)
- ✅ Printify Product Creation
- ✅ Shopify Store Publishing
- ✅ TikTok Shop Integration

### AI Features
- ✅ AI Content Generation (titles, descriptions, SEO)
- ✅ Dynamic Pricing Engine
- ✅ Trend Detection & Monitoring
- ✅ Multi-language Support

### Agency Features
- ✅ Multi-client Workspace Management
- ✅ Client Portal UI
- ✅ Usage-based Billing (Stripe)
- ✅ White-label Support

### Enterprise Features
- ✅ Automated Backups
- ✅ Role-based Access Control (RBAC)
- ✅ Compliance Reporting
- ✅ Multi-region Failover

## 📦 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- ComfyUI (for AI generation)
- API keys (Printify, Shopify, TikTok, etc.)

### Installation

```bash
# Clone repository
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod/pod-engine

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Run workers
python workers/printify_worker.py
python workers/shopify_worker.py
```

### Frontend Dashboard

```bash
cd ..
npm install
npm run dev  # Start development server
```

## 🔧 Configuration

### Environment Variables

```env
# Core
ENV=development
COMFY_API=http://127.0.0.1:8188

# Platforms
PRINTIFY_API_KEY=your_key
SHOPIFY_STORE=your_store
SHOPIFY_TOKEN=your_token
TIKTOK_ACCESS_TOKEN=your_token

# AI
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# Agency
MULTI_CLIENT=1
WHITE_LABEL=1
```

## 🏗️ Architecture

```
Pod Engine
├── comfy/          # ComfyUI client integration
├── workers/        # Queue workers (Printify, Shopify)
├── features/       # AI features (content, SEO, pricing)
├── engine/         # Core utilities (logger, retry)
├── tools/          # CLI tools (TikTok feed, etc.)
├── queues/         # Job queues
│   ├── incoming/   # Raw images
│   ├── done/       # Processed images
│   ├── failed/     # Failed jobs
│   └── published/  # Published products
└── clients/        # Multi-tenant workspaces
```

## 📊 Workflow

1. **Generate** - ComfyUI creates designs → `queues/incoming/`
2. **Process** - Remove background → `queues/done/`
3. **Upload** - Printify creates products → `queues/published/`
4. **Publish** - Shopify/TikTok publish products
5. **Monitor** - Dashboard shows analytics

## 🎯 Usage

### Generate TikTok Feed
```bash
python tools/tiktok_feed_generator.py
```

### Run Full Pipeline
```bash
# Start all workers
python workers/printify_worker.py &
python workers/shopify_worker.py &
```

### Create Client Workspace
```bash
python engine/create_client.py client_name plan_tier
```

## 🚢 Deployment

### RunPod (GPU Cloud)
```bash
# One-command install
bash <(curl -fsSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/pod-engine/runpod_install.sh)
```

### Docker
```bash
docker-compose up -d
```

### Systemd Services
```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl enable staticwaves-*
sudo systemctl start staticwaves-*
```

## 💰 Monetization

### Pricing Tiers
- **Starter**: $1,500/mo (shared infrastructure)
- **Pro**: $3,000/mo (dedicated GPU pod)
- **Enterprise**: $5,000+/mo (white-label + SLA)

### Revenue Streams
- Monthly retainers
- Usage-based overages
- White-label licenses
- Rev-share partnerships

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Client Onboarding](docs/onboarding.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🛡️ Security

- AES-256 encryption at rest
- Client-owned encryption keys (BYOK)
- Role-based access control
- SOC2-style audit logging
- Automated backup & DR

## 📈 Roadmap

- [ ] Mobile app
- [ ] Additional marketplaces (Etsy, Amazon)
- [ ] Advanced analytics dashboard
- [ ] AI video generation
- [ ] Voice command interface

## 📝 License

Enterprise License - Contact for pricing

## 🤝 Support

- Email: support@staticwaves.ai
- Discord: https://discord.gg/staticwaves
- Docs: https://docs.staticwaves.ai

---

**Built with ❤️ by the StaticWaves Team**
