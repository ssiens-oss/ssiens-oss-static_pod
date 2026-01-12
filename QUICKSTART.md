# ⚡ StaticWaves POD Engine - Quick Start

## 🚀 New RunPod Deployment (3 Commands)

```bash
# 1. SSH into your RunPod instance
ssh <your-pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519

# 2. Run the one-command installer
curl -sSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/claude/push-images-printify-JLjuQ/fresh-deploy.sh | bash

# 3. Access via RunPod Dashboard
# Click: Port 5174 → HTTP Service
```

---

## 📋 Manual Deployment

```bash
cd ~
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod
git checkout claude/push-images-printify-JLjuQ
./deploy-runpod.sh
```

---

## 🌐 Access Points

| Service | Port | Access Method |
|---------|------|---------------|
| **Main App** | 5174 | RunPod Dashboard → Port 5174 → HTTP Service |
| **API Docs** | 8188 | RunPod Dashboard → Port 8188 → HTTP Service |

---

## 🎯 First Steps After Deployment

1. **Register Account** → Create your user
2. **Login** → Sign in
3. **Settings** → Add Printify API Key
4. **AI Generate** → Create your first design
5. **Designs** → View and manage creations

---

## 🛠️ Common Commands

```bash
# Start services
./deploy-runpod.sh

# Quick restart
./test-run.sh

# Stop services
./stop-pod-engine.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check health
curl http://localhost:8188/api/health
```

---

## 🔧 Troubleshooting

### Services won't start
```bash
./stop-pod-engine.sh
rm -rf venv
./deploy-runpod.sh
```

### Can't access via browser
1. Verify services are running: `curl http://localhost:5174`
2. Check RunPod dashboard for HTTP Service buttons
3. Make sure you're clicking Port 5174, not 3000 or 8000

### Database errors
```bash
rm backend/staticwaves_pod.db
cd backend && python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## 📦 What Gets Installed

- ✅ Python virtual environment
- ✅ FastAPI backend (24 API endpoints)
- ✅ React frontend (TypeScript)
- ✅ SQLite database
- ✅ 9 genre categories for AI generation
- ✅ 24+ quick-start templates
- ✅ Printify & Shopify integration

---

## 🎨 Features

- **AI Image Generation** - 9 genres, batch processing
- **Design Management** - Search, filter, bulk operations
- **POD Integration** - Printify auto-publish
- **User System** - JWT auth, per-user API keys
- **Real-time Queue** - Job tracking and monitoring

---

## 📚 Full Documentation

- **Fresh Deploy:** [RUNPOD_FRESH_DEPLOY.md](RUNPOD_FRESH_DEPLOY.md)
- **Complete Guide:** [README_FULLSTACK_APP.md](README_FULLSTACK_APP.md)
- **AI Features:** [AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md)
- **Compilation:** [COMPILATION_SUMMARY.txt](COMPILATION_SUMMARY.txt)

---

## 🔑 Environment Setup

Optional - create `.env` file:

```env
DATABASE_URL=sqlite:///./backend/staticwaves_pod.db
SECRET_KEY=your-secret-key-here
COMFYUI_URL=http://127.0.0.1:8188
```

Generate secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 💾 Repository

**GitHub:** https://github.com/ssiens-oss/ssiens-oss-static_pod
**Branch:** `claude/push-images-printify-JLjuQ`

---

## 🎉 You're Ready!

After deployment, click **Port 5174 → HTTP Service** in your RunPod dashboard to start creating POD products!
