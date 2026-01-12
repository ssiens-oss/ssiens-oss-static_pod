<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Automation Pipeline

Complete end-to-end Print-on-Demand automation using AI image generation, multi-platform publishing, and intelligent product creation.

**🚀 Full Pipeline Features:**
- 🎨 **AI Image Generation** with Claude + ComfyUI
- 🎵 **AI Music Generation** with user-controlled synths, vibe mixing & stems
- 💾 **Auto-save** to local/cloud storage
- 👕 **Product Creation** on Printify (T-shirts & Hoodies)
- 🛍️ **Multi-Platform Publishing** to Shopify, TikTok, Etsy, Instagram, Facebook
- 📊 **Real-time Monitoring** with web UI
- ☁️ **RunPod Deployment** for scalable cloud execution

## Quick Start

### Option 1: One-Command Deployment (Recommended)

```bash
# Configure API keys
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY and PRINTIFY_API_KEY

# Deploy complete POD engine
./deploy-pod-engine.sh local

# Start all services
./start-pod-engine.sh
```

**Access your services:**
- POD Gateway: http://localhost:5000 (Approve designs)
- ComfyUI: http://localhost:8188 (Generate AI images)
- Web UI: http://localhost:5173 (Manage pipeline)

**See [QUICKSTART_POD_ENGINE.md](QUICKSTART_POD_ENGINE.md) for 10-minute setup guide.**

### Option 2: Manual Setup

```bash
# 1. Install Dependencies
npm install

# 2. Set Up ComfyUI
./scripts/setup-comfyui.sh

# 3. Configure Environment
cp .env.example .env
# Edit .env with your API keys (Claude, Printify, Shopify, etc.)

# 4. Start Services Manually
cd ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188 &
cd gateway && source .venv/bin/activate && python app/main.py &
npm run dev
```

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed manual setup.**

## Deploy to RunPod

### Quick Deploy to Cloud

```bash
# One-command cloud deployment with GPU
./deploy-pod-engine.sh runpod
```

**Or using existing script:**
```bash
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key
./scripts/deploy-runpod.sh
```

### What You Get on RunPod
- ⚡ GPU-accelerated AI image generation (NVIDIA RTX A4000+)
- 🌐 Public URL for accessing your pipeline
- 💰 Pay-per-use pricing (~$0.06 per design)
- 📦 Pre-configured ComfyUI + POD Gateway + all integrations
- 🔐 Secure environment variable management
- 🔄 Auto-scaling and persistent storage

**See [POD_ENGINE_DEPLOYMENT.md](POD_ENGINE_DEPLOYMENT.md) for complete cloud deployment guide.**

## Pipeline Features

### AI Image Generation
- **Claude Prompting**: Generate creative, commercially-viable prompts automatically
- **ComfyUI Integration**: Professional-grade AI image generation with SDXL
- **Batch Processing**: Generate multiple unique designs in one run
- **Custom Workflows**: Customize generation parameters and styles

### Product Management
- **Printify Integration**: Automatic product creation for T-shirts and Hoodies
- **Multi-variant Support**: All sizes and colors configured automatically
- **Smart Pricing**: Configurable base prices with automatic markup
- **Auto-publish**: Products go live immediately or saved as drafts

### Multi-Platform Distribution
- **Shopify**: Full product sync with SEO optimization
- **TikTok Shop**: Direct integration with TikTok commerce
- **Etsy**: Automated listing creation with proper taxonomy
- **Instagram Shopping**: Product catalog sync and post tagging
- **Facebook Shop**: Commerce Manager integration

### Monitoring & Management
- **Real-time Logging**: Watch every step of the pipeline
- **Progress Tracking**: Visual progress bars and status updates
- **Error Handling**: Automatic retries and detailed error messages
- **Storage Management**: Local or cloud storage with deduplication

## Project Structure

```
.
├── App.tsx                      # Main web UI
├── components/
│   ├── Terminal.tsx             # Real-time log viewer
│   └── EditorControls.tsx       # Design editor controls
├── services/
│   ├── comfyui.ts               # ComfyUI API integration
│   ├── claudePrompting.ts       # Claude AI prompt generation
│   ├── storage.ts               # Image storage service
│   ├── printify.ts              # Printify POD integration
│   ├── shopify.ts               # Shopify store integration
│   ├── orchestrator.ts          # Pipeline orchestration engine
│   └── platforms/
│       ├── tiktok.ts            # TikTok Shop integration
│       ├── etsy.ts              # Etsy marketplace integration
│       ├── instagram.ts         # Instagram Shopping integration
│       └── facebook.ts          # Facebook Shop integration
├── scripts/
│   ├── setup-comfyui.sh         # ComfyUI setup automation
│   └── deploy-runpod.sh         # RunPod deployment script
├── Dockerfile.runpod            # RunPod container config
├── .env.example                 # Environment configuration template
├── SETUP_GUIDE.md               # Complete setup instructions
├── PIPELINE_ARCHITECTURE.md     # Technical architecture docs
└── SYSTEM_WALKTHROUGH.md        # Original system documentation
```

## Documentation

### Getting Started
- **[QUICKSTART_POD_ENGINE.md](QUICKSTART_POD_ENGINE.md)** - 10-minute quick start guide ⚡
- **[POD_ENGINE_DEPLOYMENT.md](POD_ENGINE_DEPLOYMENT.md)** - Complete deployment guide 🚀
- **[POD_GATEWAY_INTEGRATION.md](POD_GATEWAY_INTEGRATION.md)** - Human approval system ✋

### Technical Reference
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed manual setup instructions
- **[PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md)** - Technical architecture and flow
- **[MUSIC_GUIDE.md](MUSIC_GUIDE.md)** - AI music generation guide and API reference
- **[SYSTEM_WALKTHROUGH.md](SYSTEM_WALKTHROUGH.md)** - Original POD studio documentation

## Platform Requirements

### Essential
- **Anthropic Claude API** - [Get API Key](https://console.anthropic.com/)
- **Printify Account** - [Sign Up](https://printify.com/)

### Optional
- **Shopify Store** - [Start Free Trial](https://www.shopify.com/)
- **TikTok Shop** - [Apply](https://seller.tiktokshop.com/)
- **Etsy Shop** - [Open Shop](https://www.etsy.com/sell)
- **Instagram Business** - [Setup](https://business.instagram.com/)
- **Facebook Page** - [Create](https://www.facebook.com/pages/create)

## Cost Estimates

**Per Design (1 T-shirt + 1 Hoodie):**
- Claude API: ~$0.01
- ComfyUI (RunPod): ~$0.05
- Total: **~$0.06 per design**

**100 Designs: ~$6.00**

---

**Need help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) or open an issue.
