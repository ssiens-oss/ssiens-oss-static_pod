# 🎨 POD Dashboard

**Unified control center for Print-on-Demand automation**

Combines AI Prompter + Design Gallery + Overview into one beautiful interface.

---

## 🎯 What It Does

**One dashboard. All your POD tools.**

- **Overview** - Real-time stats from all systems
- **AI Prompter** - Generate creative prompts with Claude
- **Design Gallery** - Approve/reject/publish designs
- **Workflow Tracking** - Monitor entire pipeline

---

## 🚀 Quick Start

### Install
```bash
cd dashboard
./install_runpod.sh
```

### Configure
```bash
cp .env.example .env
# Add ANTHROPIC_API_KEY and PRINTIFY credentials
```

### Run
```bash
./start.sh
```

### Access
**Port 5000** - http://localhost:5000

---

## 🎨 Features

### **Dashboard Overview** (`/`)
- Live stats from all systems
- Service status indicators
- Quick action buttons
- Workflow visualization

### **AI Prompter** (`/prompter`)
- Generate creative POD prompts
- 6 quick presets
- Batch generation
- Export to JSON

### **Design Gallery** (`/gallery`)
- View all generated images
- Approve/reject designs
- One-click publish to Printify
- Status tracking

---

## 📊 Dashboard Features

### Real-Time Stats
- **Prompts Generated** - Total prompt count
- **Pending Review** - Images awaiting approval
- **Approved** - Designs ready to publish
- **Published** - Live on Printify

### Service Status
- ✅ Claude API (online/offline)
- ✅ Printify API (online/offline)
- ✅ State Manager (active/inactive)

### Workflow Visualization
```
Generate → Create → Approve → Publish
  (AI)   (ComfyUI) (Gallery) (Printify)
```

---

## 🔧 Configuration

All services configured in one `.env` file:

```env
# APIs
ANTHROPIC_API_KEY=sk-ant-...
PRINTIFY_API_KEY=...
PRINTIFY_SHOP_ID=...

# Paths
POD_IMAGE_DIR=/workspace/comfyui/output
POD_STATE_FILE=/workspace/dashboard/state.json
PROMPTER_OUTPUT_DIR=/workspace/prompts
```

---

## 🎯 Complete Workflow

### 1. Generate Prompts
- Open Dashboard → Click "AI Prompter"
- Choose preset or custom input
- Generate 5-10 prompts
- Copy best prompt

### 2. Create Images
- Paste prompt into ComfyUI
- Generate images
- Images auto-appear in Gallery

### 3. Review Designs
- Open Dashboard → Click "Gallery"
- View all generated images
- Approve good ones, reject bad ones

### 4. Publish
- Click "Publish" on approved designs
- Automatic upload to Printify
- Products go live

### 5. Monitor
- Return to Dashboard overview
- Check stats
- Repeat!

---

## 📁 Directory Structure

```
dashboard/
├── app/
│   ├── main.py        # Flask app (all services)
│   └── config.py      # Unified configuration
├── templates/
│   ├── dashboard.html # Overview page
│   ├── prompter.html  # Prompter interface
│   └── gallery.html   # Gallery interface
├── requirements.txt
├── install_runpod.sh
├── start.sh
└── .env.example
```

---

## 🔌 API Endpoints

### Overview
- `GET /` - Dashboard home
- `GET /api/overview` - Stats from all systems

### Prompter
- `GET /prompter` - Prompter UI
- `POST /api/generate-prompts` - Generate prompts
- `GET /api/presets` - Get presets

### Gallery
- `GET /gallery` - Gallery UI
- `GET /api/images` - List images
- `POST /api/approve/<id>` - Approve image
- `POST /api/reject/<id>` - Reject image
- `POST /api/publish/<id>` - Publish to Printify

### System
- `GET /health` - Health check
- `GET /api/gateway-stats` - Gateway stats

---

## 🎨 UI Design

### Color Scheme
- Primary: Purple gradient (#667eea → #764ba2)
- Background: White cards on gradient
- Accents: Green (approve), Red (reject), Blue (info)

### Navigation
- Top bar with logo + links
- Active page highlighted
- Responsive mobile design

### Cards
- Overview stats (4 cards)
- Tool cards (2 cards)
- Status cards (2 cards)
- Workflow visualization

---

## 🚀 Deployment

### RunPod
```bash
cd /workspace/ssiens-oss-static_pod
git pull origin claude/review-pod-code-SUPJU
cd dashboard
./install_runpod.sh
cp .env.example .env
# Edit .env
./start.sh
```

Expose port **5000**

### Local
```bash
cd dashboard
./install_runpod.sh
cp .env.example .env
# Edit .env
./start.sh
```

Access: http://localhost:5000

---

## 🎯 Advantages

### Before (Separate Tools)
- Gateway on port 5000
- Prompter on port 5001
- Switch between tabs
- No unified view

### After (Dashboard)
- ✅ Everything on port 5000
- ✅ Single interface
- ✅ Unified navigation
- ✅ Real-time overview
- ✅ One configuration file

---

## 🎉 Summary

**One dashboard to rule them all!**

- ✅ Unified interface for all POD tools
- ✅ Real-time stats and monitoring
- ✅ Beautiful, responsive design
- ✅ Single port, single config
- ✅ Complete workflow in one place

**Perfect for:** POD creators who want efficiency and simplicity

**Next:** Install → Configure → Generate → Approve → Publish → Profit! 🚀
