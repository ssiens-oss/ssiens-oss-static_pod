# StaticWaves POD Engine - Fresh RunPod Deployment

## 🚀 Quick Deploy (New RunPod Instance)

This guide covers deploying the POD Engine on a fresh RunPod instance from scratch.

---

## Prerequisites

- RunPod account with an active pod
- Pod template: **runpod/stable-diffusion:comfy-ui-5.0.0** (or similar)
- SSH access to your pod
- GitHub repository: https://github.com/ssiens-oss/ssiens-oss-static_pod

---

## Step 1: SSH into Your RunPod Instance

```bash
ssh <pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519
```

Example:
```bash
ssh ckgp3l49rwtvjr-644113a3@ssh.runpod.io -i ~/.ssh/id_ed25519
```

---

## Step 2: Clone the Repository

```bash
cd ~
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod
```

---

## Step 3: Checkout the Deployment Branch

```bash
git checkout claude/push-images-printify-JLjuQ
```

---

## Step 4: Run the Deployment Script

```bash
./deploy-runpod.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies (FastAPI, SQLAlchemy, etc.)
- ✅ Install Node.js dependencies (React, Vite, etc.)
- ✅ Build production frontend
- ✅ Initialize SQLite database
- ✅ Start backend on port 8188
- ✅ Start frontend on port 5174
- ✅ Verify services are healthy

**Expected output:**
```
🎉 Ready to create POD products! Happy designing!
```

---

## Step 5: Access Your POD Engine

### Via RunPod Dashboard

1. Open your **RunPod Dashboard**
2. Find your pod (e.g., `ckgp3l49rwtvjr`)
3. Look for **HTTP services** section
4. Click: **Port 5174 → HTTP Service** (Main App) 🎨
5. Click: **Port 8188 → HTTP Service** (API Docs) 📚

### Via Direct URLs (if available)

The script will show you the URLs. Format usually:
- Frontend: `https://<pod-id>-5174.proxy.runpod.net`
- Backend: `https://<pod-id>-8188.proxy.runpod.net`

---

## Step 6: First Time Setup

Once you access the app:

1. **Register** - Create your account
2. **Login** - Sign in
3. **Settings Tab** - Add your API keys:
   - Printify API Key
   - Printify Shop ID (e.g., 25860767)
   - Optional: Shopify credentials

---

## Troubleshooting

### Services Not Starting

**Check logs:**
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

**Restart services:**
```bash
./stop-pod-engine.sh
./deploy-runpod.sh
```

### Port Already in Use

```bash
# Kill existing processes
pkill -f "python.*main.py"
pkill -f "vite"

# Restart
./deploy-runpod.sh
```

### Python Environment Issues

```bash
# Remove virtual environment and recreate
rm -rf venv
./deploy-runpod.sh
```

### Database Issues

```bash
# Reset database
rm backend/staticwaves_pod.db
cd backend
python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
cd ..
```

---

## Management Commands

### View Logs
```bash
tail -f logs/backend.log   # Backend logs
tail -f logs/frontend.log  # Frontend logs
tail -f logs/*.log         # Both logs
```

### Check Service Status
```bash
curl http://localhost:8188/api/health  # Backend health
curl -I http://localhost:5174          # Frontend status
lsof -i :5174 -i :8188 | grep LISTEN   # Check ports
```

### Stop Services
```bash
./stop-pod-engine.sh
```

### Quick Restart
```bash
./test-run.sh
```

---

## Environment Configuration

### Required Environment Variables

Create `.env` file in the project root:

```env
# API Configuration
DATABASE_URL=sqlite:///./backend/staticwaves_pod.db
SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-random

# Optional: External Services
COMFY_OUTPUT_DIR=/workspace/ComfyUI/output
COMFYUI_URL=http://127.0.0.1:8188
```

### Recommended Secret Key Generation

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Pod Configuration

### Recommended Pod Specs

- **GPU:** RTX 3090 or better (for AI image generation)
- **RAM:** 16GB minimum
- **Storage:** 50GB+ (for models and outputs)
- **Template:** ComfyUI 5.0.0

### Required Ports

| Port | Service | Purpose |
|------|---------|---------|
| 5174 | Frontend | React web interface |
| 8188 | Backend | FastAPI REST API |
| 8188 | ComfyUI | AI image generation (if using) |

**Note:** Backend and ComfyUI can share port 8188 if ComfyUI is not used.

---

## Features Available

### ✅ AI Image Generation
- 9 genre categories
- 24+ quick-start templates
- Batch processing (1, 2, 4, 8 images)
- Real-time job queue
- Progress tracking

### ✅ Design Management
- Upload custom designs
- Advanced search & filtering
- Multi-select bulk operations
- Grid/List view modes
- Status tracking

### ✅ POD Integration
- Printify API support
- Auto-publish to products
- Shopify integration ready
- TikTok Shop compatible

### ✅ User System
- JWT authentication
- Per-user API keys
- Encrypted credentials
- Role-based access (future)

---

## Production Deployment Checklist

- [ ] Clone repository
- [ ] Checkout deployment branch
- [ ] Run `./deploy-runpod.sh`
- [ ] Verify both services are running
- [ ] Access via RunPod HTTP Service
- [ ] Create user account
- [ ] Add Printify API credentials
- [ ] Test image generation
- [ ] Test product creation
- [ ] Verify database persistence

---

## Backup & Restore

### Backup Database
```bash
cp backend/staticwaves_pod.db backend/staticwaves_pod.db.backup
```

### Backup Configuration
```bash
cp .env .env.backup
```

### Restore Database
```bash
cp backend/staticwaves_pod.db.backup backend/staticwaves_pod.db
```

---

## Updating to Latest Version

```bash
cd ~/ssiens-oss-static_pod
git pull origin claude/push-images-printify-JLjuQ
./stop-pod-engine.sh
./deploy-runpod.sh
```

---

## Support & Documentation

- **Full Guide:** [README_FULLSTACK_APP.md](README_FULLSTACK_APP.md)
- **Deployment:** [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)
- **AI Features:** [AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md)
- **Compilation:** [COMPILATION_SUMMARY.txt](COMPILATION_SUMMARY.txt)

---

## Quick Reference Commands

```bash
# Deploy
./deploy-runpod.sh

# Stop
./stop-pod-engine.sh

# Quick start
./test-run.sh

# View logs
tail -f logs/*.log

# Check health
curl http://localhost:8188/api/health

# Access frontend
# Click: Port 5174 → HTTP Service in RunPod Dashboard
```

---

## Security Notes

- Change `SECRET_KEY` in `.env` before production use
- Never commit `.env` to git (already in .gitignore)
- Keep Printify API keys secure
- Use HTTPS for all external access
- Regularly backup the database

---

## Performance Tips

1. **Use GPU pods** for AI generation
2. **Enable caching** for frequently used models
3. **Monitor logs** for errors
4. **Clean up old designs** to save space
5. **Use batch operations** for efficiency

---

🎉 **Happy POD Creating!**

For issues or questions, check the logs first, then consult the documentation.
