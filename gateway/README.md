# 🎨 POD Gateway

**Human-in-the-loop approval system for Print-on-Demand designs**

The POD Gateway sits between ComfyUI output and Printify publishing, giving you manual control over which designs go live.

---

## 🎯 What It Does

```
ComfyUI → POD Gateway → Printify → Shopify
         (YOU APPROVE)
```

1. **Scans** ComfyUI output directory for generated images
2. **Displays** them in a web gallery
3. **Lets you** approve, reject, or reset each design
4. **Publishes** approved designs to Printify automatically
5. **Tracks** status (pending → approved → published)

---

## 🚀 Quick Start (RunPod)

### 1. Install
```bash
cd gateway
chmod +x install_runpod.sh
./install_runpod.sh
```

### 2. Configure
```bash
cp .env.example .env
nano .env  # Add your Printify API key and shop ID
```

### 3. Run
```bash
source .venv/bin/activate
python app/main.py
```

### 4. Expose Port
- Go to RunPod UI → HTTP Ports
- Expose port **5000**
- Access via provided URL

---

## 📁 Directory Structure

```
gateway/
├── app/
│   ├── main.py              # Flask entrypoint
│   ├── config.py            # Environment configuration
│   ├── state.py             # Status tracking (JSON)
│   └── printify_client.py   # Printify API wrapper
├── templates/
│   └── gallery.html         # Web UI
├── requirements.txt
├── install_runpod.sh
├── .env.example
└── README.md
```

---

## 🔧 Configuration

### Required
- `PRINTIFY_API_KEY` - Your Printify API key
- `PRINTIFY_SHOP_ID` - Your Printify shop ID

### Optional
- `POD_IMAGE_DIR` - Where ComfyUI outputs images (default: `/workspace/comfyui/output`)
- `POD_STATE_FILE` - Where to store approval state (default: `/workspace/gateway/state.json`)
- `PRINTIFY_BLUEPRINT_ID` - Product type (default: `3` = T-shirt)
- `PRINTIFY_PROVIDER_ID` - Print provider (default: `99` = SwiftPOD)

---

## 🎨 Web Interface

### Gallery View
- **Grid layout** showing all generated images
- **Status badges**: Pending, Approved, Rejected, Published, Failed
- **Filter buttons**: View by status
- **Live stats**: Counts by status

### Actions
- **Approve** → Mark ready for publishing
- **Reject** → Hide from publishing queue
- **Publish** → Send to Printify (approved images only)
- **Reset** → Return to pending status

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Gallery UI |
| `/api/images` | GET | List all images with status |
| `/api/image/<id>` | GET | Serve image file |
| `/api/approve/<id>` | POST | Approve image |
| `/api/reject/<id>` | POST | Reject image |
| `/api/publish/<id>` | POST | Publish to Printify |
| `/api/reset/<id>` | POST | Reset to pending |
| `/api/stats` | GET | Get statistics |
| `/health` | GET | Health check |

---

## 🛠️ Workflow Integration

### With ComfyUI
1. ComfyUI saves images to `POD_IMAGE_DIR`
2. Gateway auto-discovers new images
3. Images appear in gallery as "Pending"

### With Printify
1. You approve a design in the gallery
2. Click "Publish"
3. Gateway uploads image to Printify
4. Creates product (T-shirt by default)
5. Publishes to connected sales channels
6. Status updates to "Published"

### With Shopify (Future)
- Automatic webhook on Printify publish
- Sync status back to gateway
- Auto-collection assignment

---

## 🔒 State Management

State is stored in `state.json`:

```json
{
  "images": {
    "img_12345": {
      "filename": "img_12345.png",
      "path": "/workspace/comfyui/output/img_12345.png",
      "status": "published",
      "product_id": "printify_abc123",
      "title": "Cool Design"
    }
  }
}
```

**Status Lifecycle:**
```
pending → approved → publishing → published
                    ↓
                  failed (can retry)
```

**Thread-safe** with atomic writes (temp file + rename).

---

## 🐛 Troubleshooting

### Images not showing up
- Check `POD_IMAGE_DIR` path is correct
- Ensure images are `.png` files
- Check permissions on directory

### Printify publish fails
- Verify `PRINTIFY_API_KEY` and `PRINTIFY_SHOP_ID`
- Check Printify API status
- Look for error in terminal logs

### Port already in use
- Change `FLASK_PORT` in `.env`
- Or kill existing process: `pkill -f "python app/main.py"`

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│  ComfyUI Output                                 │
│  /workspace/comfyui/output/*.png                │
└───────────────────┬─────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────┐
│  POD Gateway (Flask)                            │
│  - Gallery UI (Port 5000)                       │
│  - State Manager (state.json)                   │
│  - Printify Client (API wrapper)                │
└───────────────────┬─────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────┐
│  Printify API                                   │
│  - Upload image                                 │
│  - Create product                               │
│  - Publish to sales channels                    │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

### 1. Quality Control
Review AI-generated designs before they go live to avoid low-quality or inappropriate content.

### 2. Brand Consistency
Ensure all designs match your brand aesthetic before publishing.

### 3. Batch Processing
Generate 100 designs overnight, approve 20 in the morning, publish in bulk.

### 4. A/B Testing
Approve designs in waves, track which ones sell best.

---

## 🤖 AIM Proofing Engine

**NEW:** Automated Image Manipulation (AIM) Proofing Engine for automatic quality validation and approval.

### Features
- ✅ **Automated quality checks** - Resolution, file size, format validation
- 🤖 **AI-powered analysis** - Claude Vision evaluates commercial suitability
- ⚡ **Auto-approval** - High-quality images bypass manual review
- 📁 **Directory monitoring** - Real-time processing of new images
- 🔗 **Gateway integration** - Works seamlessly with approval workflow

### Quick Start

```bash
# Configure directories and settings
nano aim_config.json

# Add API key for AI analysis
echo "ANTHROPIC_API_KEY=your_key" >> .env

# Start monitoring
./start_aim_monitor.sh
```

**See [AIM_README.md](AIM_README.md) for complete documentation.**

---

## 🚀 Next Steps

- [x] ~~Create rules engine (auto-approve based on criteria)~~ - **✅ AIM Engine Complete**
- [ ] Add Shopify webhook listener
- [ ] Implement auto-archive for published designs
- [ ] Add bulk approval/rejection
- [ ] Add OBS overlay feed (`/status.json`)

---

## 📄 License

Part of the StaticWaves POD automation system.
