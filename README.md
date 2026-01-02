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

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Up ComfyUI (for AI image generation)
```bash
./scripts/setup-comfyui.sh
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys (Claude, Printify, Shopify, etc.)
```

### 4. Start Services
```bash
# Terminal 1: Start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188

# Terminal 2: Start Web UI
npm run dev
```

### 5. Access Pipeline
Open http://localhost:5173 in your browser

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete installation instructions.**

## Deploy to RunPod

### Automated Deployment
```bash
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key
./scripts/deploy-runpod.sh
```

### What You Get on RunPod
- ⚡ GPU-accelerated AI image generation (NVIDIA RTX A4000+)
- 🌐 Public URL for accessing your pipeline
- 💰 Pay-per-use pricing (only when generating)
- 📦 Pre-configured ComfyUI + all integrations
- 🔐 Secure environment variable management

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed deployment instructions.**

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

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation and setup instructions
- **[MUSIC_GUIDE.md](MUSIC_GUIDE.md)** - AI music generation guide and API reference
- **[PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md)** - Technical architecture and flow
- **[SYSTEM_WALKTHROUGH.md](SYSTEM_WALKTHROUGH.md)** - Original POD studio documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Legacy deployment guide

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

## AI Code Review & Automation

**New: GitHub Actions automation with GPT↔Claude collaboration**

### Features
- 🤖 Auto code review on every PR
- ✅ Auto-merge safe changes
- 🧠 Multi-agent reasoning (Plan → Execute → Critique)
- 💰 Budget guards ($5-10/day default)
- 📊 Web dashboard for AI control
- 🔄 Local code review scripts

### Quick Start

```bash
# Install AI agent
cd ai-agent
npm install

# Set API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Start agent
npm start
```

**See [ai-agent/README.md](ai-agent/README.md) and [SETUP.md](SETUP.md) for details.**

### GitHub Actions

Add to repo secrets:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

Workflows auto-run on PRs:
- `.github/workflows/ai-review.yml` - Code review
- `.github/workflows/ai-auto-merge.yml` - Safe auto-merge

### Local Usage

```bash
# Code review
node scripts/claude-review.js backend/src

# GPT↔Claude bridge
node scripts/ai-bridge.js arbiter "Review this design"
```

## Cost Estimates

**Per Design (1 T-shirt + 1 Hoodie):**
- Claude API: ~$0.01
- ComfyUI (RunPod): ~$0.05
- Total: **~$0.06 per design**

**100 Designs: ~$6.00**

**AI Code Review:**
- ~$0.01 per single review
- ~$0.06 per multi-agent review
- Budget guard enforced (default $5-10/day)

---

**Need help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md), [SETUP.md](SETUP.md), or open an issue.
