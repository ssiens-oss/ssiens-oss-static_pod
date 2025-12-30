<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Engine

**Production-Grade AI-Powered Print-on-Demand Automation System**

Complete end-to-end POD stack with ComfyUI GPU workers, automated publishing to Printify/Shopify/TikTok Shop, and web dashboard.

[![Build Status](https://github.com/ssiens-oss/ssiens-oss-static_pod/workflows/Build%20&%20Release/badge.svg)](https://github.com/ssiens-oss/ssiens-oss-static_pod/actions)

---

## 🚀 Quick Start

### Production Installation (Linux)

```bash
# One-command install
curl -fsSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/install-master.sh | sudo bash
```

### Development (Web UI)

View your app in AI Studio: https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   ```bash
   npm install
   ```

2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key (optional)

3. Run the app:
   ```bash
   npm run dev
   ```

4. Open http://localhost:5173 in your browser

## Deploy to RunPod

This application can be deployed to RunPod for cloud hosting.

### Quick Deploy

```bash
# Build and deploy using the automated script
./deploy.sh

# Or manually build the Docker image
docker build -t staticwaves-pod-studio .
```

### Full Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions on:
- Building the Docker image
- Pushing to container registries (Docker Hub or GitHub Container Registry)
- Deploying to RunPod
- Configuration options
- Troubleshooting

## ⚡ What's Included

### Backend (Production)
- 🧠 **AI Art Engine** - ComfyUI GPU workers for design generation
- 🔄 **Queue System** - Managed pipeline (pending → processing → done/failed)
- 🖼️ **Auto Mockups** - Hoodie, tee, poster templates
- 💰 **Smart Pricing** - Cost + margin calculations
- 📤 **Auto Publishing** - Printify → Shopify → TikTok Shop
- ✅ **Validators** - TikTok compliance checks
- 🔔 **Alerts** - Discord & Telegram notifications
- 🔐 **License System** - Commercial SaaS controls
- 📦 **Debian Packages** - `.deb` installers with GPG signing
- 🏷️ **White-Label** - Client-specific branded installers
- ⚙️ **Systemd Services** - Auto-restart, always-on daemons

### Frontend (Development/Demo)
- **Batch Processing**: Process multiple drops in sequence
- **Real-time Logging**: See live updates as your POD automation runs
- **Interactive Editor**: Scale and transform designs in real-time
- **Product Mockup Preview**: View generated mockups instantly
- **Upload Queue Management**: Track Printify upload status

## 📁 Project Structure

```
.
├── api/                       # 🔥 Flask API (production backend)
│   ├── app.py                 # Control plane API server
│   ├── publish.py             # Publishing orchestrator
│   ├── pricing.py             # Cost + margin engine
│   ├── validators.py          # TikTok compliance
│   ├── alerts.py              # Discord/Telegram
│   └── license.py             # SaaS enforcement
├── workers/                   # 🔥 Background workers
│   ├── comfy_worker.py        # ComfyUI GPU integration
│   ├── mockup_worker.py       # Product mockup generator
│   └── uploader.py            # Printify uploader
├── systemd/                   # 🔥 System services
│   ├── staticwaves-pod-api.service
│   ├── staticwaves-pod-worker.service
│   └── staticwaves-comfyui.service
├── debian-pkg/                # 🔥 .deb packaging
│   └── DEBIAN/
│       ├── control
│       ├── postinst
│       ├── prerm
│       └── postrm
├── .github/workflows/         # 🔥 CI/CD
│   └── build-release.yml      # Auto-build & sign releases
├── config/                    # Configuration
│   ├── env.example
│   ├── pricing.json
│   └── products.json
├── App.tsx                    # Frontend: Main component
├── components/                # Frontend: UI components
│   ├── Terminal.tsx
│   └── EditorControls.tsx
├── services/
│   └── mockEngine.ts          # Frontend: Simulation engine
├── build-deb.sh               # 🔥 Build standard .deb
├── build-whitelabel.sh        # 🔥 Build client-specific .deb
├── install-master.sh          # 🔥 One-command installer
├── POD_STACK.md               # 🔥 Complete documentation
├── API.md                     # 🔥 API reference
├── APT_REPO.md                # 🔥 APT repository guide
└── README.md                  # This file
```

🔥 = **Production POD stack** (new!)
