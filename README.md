<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Automation Pipeline

Complete end-to-end Print-on-Demand automation using AI image generation, multi-platform publishing, and intelligent product creation.

**🚀 Full Pipeline Features:**
- 🎨 **AI Image Generation** with Claude + ComfyUI
- 🎵 **AI Music Generation** with user-controlled synths, vibe mixing & stems
- 🚀 **Pod Engine Pipeline** - Complete ComfyUI + RunPod + Proofing + Publishing automation
- 💾 **Auto-save** to local/cloud storage with RunPod sync
- 🔍 **Proofing System** - Review and approve before publishing
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

**Option A: Pod Engine Pipeline (Recommended)**
```bash
# Terminal 1: Start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188

# Terminal 2: Start Pod Engine
npm run pod-engine
```
Access at http://localhost:5174

**Option B: Original POD Studio**
```bash
# Terminal 1: Start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188

# Terminal 2: Start Web UI
npm run dev
```
Access at http://localhost:5173

**Option C: Music Studio**
```bash
npm run dev:music
```
Access at http://localhost:5173

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete installation instructions.**
**See [POD_ENGINE_GUIDE.md](POD_ENGINE_GUIDE.md) for Pod Engine documentation.**

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

### Pod Engine Pipeline (NEW!)
- **Complete Automation**: Generate → Proof → Publish in one workflow
- **ComfyUI + RunPod**: Local or cloud GPU-accelerated generation
- **Local Save from RunPod**: Automatically sync outputs to local storage
- **Proofing System**: Manual or auto-approval before publishing
- **Multi-Platform Publishing**: One-click publish to all platforms
- **Real-time Monitoring**: Live logs, progress, and statistics
- **Batch Processing**: Process multiple designs efficiently

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
├── App.tsx                      # Main web UI (Original POD Studio)
├── PodEngineApp.tsx             # Pod Engine Pipeline UI
├── MusicApp.tsx                 # Music Studio UI
├── components/
│   ├── PodEngineGUI.tsx         # Complete pipeline interface
│   ├── Terminal.tsx             # Real-time log viewer
│   ├── EditorControls.tsx       # Design editor controls
│   └── MusicStudio.tsx          # Music generation interface
├── services/
│   ├── podEngine.ts             # Pod Engine orchestrator (NEW!)
│   ├── proofing.ts              # Proofing workflow (NEW!)
│   ├── runpod.ts                # RunPod integration (NEW!)
│   ├── comfyui.ts               # ComfyUI API integration
│   ├── claudePrompting.ts       # Claude AI prompt generation
│   ├── storage.ts               # Storage with RunPod sync (ENHANCED!)
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
├── POD_ENGINE_GUIDE.md          # Pod Engine documentation (NEW!)
├── SETUP_GUIDE.md               # Complete setup instructions
├── MUSIC_GUIDE.md               # Music generation guide
├── PIPELINE_ARCHITECTURE.md     # Technical architecture docs
└── SYSTEM_WALKTHROUGH.md        # Original system documentation
```

## Documentation

- **[POD_ENGINE_GUIDE.md](POD_ENGINE_GUIDE.md)** - Complete Pod Engine Pipeline documentation
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

## Cost Estimates

**Per Design (1 T-shirt + 1 Hoodie):**
- Claude API: ~$0.01
- ComfyUI (RunPod): ~$0.05
- Total: **~$0.06 per design**

**100 Designs: ~$6.00**

---

**Need help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) or open an issue.
