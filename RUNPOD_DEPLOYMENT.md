# StaticWaves POD Engine - RunPod Deployment Guide

## 🚀 Quick Start

The POD Engine is pre-configured for RunPod's ComfyUI template with optimized port mappings.

### One-Command Deployment

```bash
./deploy-runpod.sh
```

This will:
- Install all dependencies
- Build the production frontend
- Initialize the database
- Start backend on port 8188
- Start frontend on port 5174
- Verify all services are healthy

---

## 🌐 Accessing Your POD Engine

### From RunPod Dashboard

1. Go to your RunPod dashboard
2. Find your pod: **ckgp3l49rwtvjr**
3. Look for **HTTP services** section
4. Click: **Port 5174 → HTTP Service** (Opens Main App)
5. Click: **Port 8188 → HTTP Service** (Opens API Docs)

### Port Configuration

| Service | Port | RunPod Status | Purpose |
|---------|------|---------------|---------|
| Frontend | 5174 | ✅ Ready | Main web interface |
| Backend API | 8188 | ✅ Ready | REST API + Docs |

---

## 📋 Management Commands

### Start Services
```bash
./deploy-runpod.sh
```

### Stop Services
```bash
./stop-pod-engine.sh
```

### Check Status
```bash
# Backend health
curl http://localhost:8188/api/health

# Frontend access
curl -I http://localhost:5174

# View running processes
lsof -i :5174 -i :8188 | grep LISTEN
```

### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Both logs simultaneously
tail -f logs/*.log
```

---

## 🔧 Service Architecture

```
┌─────────────────────────────────────────┐
│         RunPod HTTP Proxy               │
│   (port-5174.proxy.runpod.net)         │
└─────────────────┬───────────────────────┘
                  │
         ┌────────▼────────┐
         │  Port 5174      │
         │  Vite Frontend  │
         │  (React + TS)   │
         └────────┬────────┘
                  │ API Calls
                  │ (localhost:8188)
         ┌────────▼────────┐
         │  Port 8188      │
         │  FastAPI Backend│
         │  (Python)       │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  SQLite DB      │
         │  staticwaves.db │
         └─────────────────┘
```

---

## 🎨 Features

### AI Image Generation
- 9 genre categories (Fantasy, Sci-Fi, Nature, etc.)
- 24+ quick-start templates
- Batch generation (1, 2, 4, 8 images)
- 14 art style presets
- Real-time job queue monitoring

### Design Management
- Advanced search & filters
- Multi-select bulk operations
- Grid/List view modes
- Status tracking (draft, processing, published)

### POD Integration
- Printify API integration
- Auto-publish to products
- Shopify connection
- TikTok Shop ready

---

## 🐛 Troubleshooting

### "Bad Gateway" Error
- **Cause**: RunPod proxy not routing correctly
- **Solution**: Use ports 5174 and 8188 (pre-configured)
- **Verify**: Check HTTP Service shows "Ready" in dashboard

### Services Not Starting
```bash
# Stop all services
./stop-pod-engine.sh

# Redeploy from scratch
./deploy-runpod.sh
```

### Database Issues
```bash
# Reset database
cd backend
rm -f staticwaves_pod.db
python3 -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
cd ..
```

### Port Already in Use
```bash
# Find and kill process
lsof -ti:5174 | xargs kill -9
lsof -ti:8188 | xargs kill -9

# Restart
./deploy-runpod.sh
```

---

## 📁 Directory Structure

```
ssiens-oss-static_pod/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── comfyui_service.py      # ComfyUI integration
│   ├── requirements.txt        # Python dependencies
│   └── staticwaves_pod.db      # SQLite database
├── src/
│   ├── Dashboard.tsx           # Main dashboard
│   ├── ImageGenerator.tsx      # AI generation UI
│   ├── EnhancedDesigns.tsx     # Design management
│   ├── Settings.tsx            # API keys & config
│   └── ...                     # Other components
├── dist/                       # Production build (auto-generated)
├── logs/                       # Service logs
│   ├── backend.log
│   └── frontend.log
├── deploy-runpod.sh           # 🚀 Main deployment script
├── stop-pod-engine.sh         # 🛑 Stop all services
├── test-run.sh                # Quick test runner
└── README_FULLSTACK_APP.md    # Complete documentation
```

---

## 🔐 Security Notes

- API keys stored per-user in database
- JWT authentication for all endpoints
- Passwords hashed with bcrypt
- CORS configured for RunPod domains
- No keys committed to git (.gitignore configured)

---

## 📚 Additional Documentation

- **Full Application Guide**: [README_FULLSTACK_APP.md](README_FULLSTACK_APP.md)
- **AI Generation Tutorial**: [AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md)
- **API Documentation**: http://localhost:8188/docs (after deployment)

---

## 🎉 Success Indicators

After running `./deploy-runpod.sh`, you should see:

```
✓ Python dependencies installed
✓ Node dependencies installed
✓ Frontend built successfully
✓ Database initialized
✓ Backend started (PID: XXXX)
✓ Backend is ready!
✓ Frontend started (PID: XXXX)
✓ Frontend is ready!

✨ POD Engine Deployed Successfully!
```

Then access via RunPod's **Port 5174 → HTTP Service** button! 🚀

---

## 💡 Tips

1. **First Time Setup**: Use `./deploy-runpod.sh` for complete deployment
2. **Quick Restart**: Use `./test-run.sh` if services are already configured
3. **Clean Slate**: Run `./stop-pod-engine.sh` then `./deploy-runpod.sh`
4. **Monitor Health**: Check logs regularly during development
5. **RunPod Proxy**: Always use HTTP Service buttons, not direct TCP ports

---

## 🆘 Support

If you encounter issues:
1. Check `logs/backend.log` and `logs/frontend.log`
2. Verify ports 5174 and 8188 show "Ready" in RunPod
3. Ensure you're using RunPod's HTTP Service buttons
4. Try a clean redeployment with stop + deploy scripts

Happy POD creating! 🎨✨
