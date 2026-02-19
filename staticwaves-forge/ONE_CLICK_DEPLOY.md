# 🚀 StaticWaves Forge - One-Click Deployment Guide

Complete guide for deploying the entire StaticWaves Forge platform with a single command on RunPod.

---

## 📋 Table of Contents

- [Quick Start (30 seconds)](#quick-start-30-seconds)
- [What Gets Deployed](#what-gets-deployed)
- [Management Commands](#management-commands)
- [Accessing Services](#accessing-services)
- [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start (30 seconds)

### On Your RunPod Instance

```bash
# SSH into your RunPod pod
ssh YOUR-POD-ID@ssh.runpod.io -i ~/.ssh/id_ed25519

# One-click boot (that's it!)
bash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh
```

**That's literally it!** The script will:
- ✅ Clean up any existing processes
- ✅ Start Redis queue (if available)
- ✅ Start Forge API backend (port 8000)
- ✅ Start Forge Web GUI (port 3000)
- ✅ Run health checks on all services
- ✅ Display all service URLs

---

## 🎯 What Gets Deployed

### Services Started

| Service | Port | Description |
|---------|------|-------------|
| **Forge Web GUI** | 3000 | Next.js web interface with enhanced UI |
| **Forge API** | 8000 | FastAPI backend for asset generation |
| **Redis Queue** | 6379 | Job queue (optional) |

### Features Included

- ✨ AI-powered 3D asset generation
- 🎨 Interactive web GUI with 6 pages
- 📊 Analytics dashboard with charts
- 📦 Asset pack creation wizard
- 🔔 Toast notifications
- 🎭 Asset detail modals with 3D preview
- 📚 Complete asset library management
- ⚙️ Full settings interface

---

## 🛠 Management Commands

All commands use the same script:

```bash
# Navigate to script location
cd /workspace/staticwaves-forge/staticwaves-forge

# Start all services
./start-unified.sh start

# Stop all services
./start-unified.sh stop

# Restart all services
./start-unified.sh restart

# Check service status
./start-unified.sh status

# View live logs
./start-unified.sh logs
```

### Advanced Management

```bash
# View specific service logs
tail -f /tmp/staticwaves-logs/forge-web.log
tail -f /tmp/staticwaves-logs/forge-api.log
tail -f /tmp/staticwaves-logs/redis.log

# Check process IDs
ls -la /tmp/staticwaves-pids/

# Manual process control
kill $(cat /tmp/staticwaves-pids/forge-web.pid)  # Stop web only
kill $(cat /tmp/staticwaves-pids/forge-api.pid)  # Stop API only
```

---

## 🌐 Accessing Services

### Find Your RunPod URLs

1. Go to RunPod Dashboard
2. Click on your pod
3. Look for "TCP Port Mappings" or "Connect" section
4. Find ports 3000 and 8000

Your URLs will be:
```
Web GUI:  https://YOUR-POD-ID-3000.proxy.runpod.net
API:      https://YOUR-POD-ID-8000.proxy.runpod.net
API Docs: https://YOUR-POD-ID-8000.proxy.runpod.net/docs
```

### Quick Access Examples

**Web Interface:**
```bash
# From your local machine
open https://YOUR-POD-ID-3000.proxy.runpod.net
```

**API Testing:**
```bash
# Health check
curl https://YOUR-POD-ID-8000.proxy.runpod.net/

# API documentation
curl https://YOUR-POD-ID-8000.proxy.runpod.net/docs
```

---

## 📱 Using the Platform

### Home Page
- Landing page with animated hero
- Example carousel
- Feature overview

### Dashboard (`/dashboard`)
- Analytics charts (30-day activity)
- Quick stats cards
- Recent assets list
- Quick action buttons

### Generate (`/generate`)
- AI asset generator
- Example prompts dropdown (12 pre-made prompts)
- Real-time 3D preview
- Generation history sidebar
- Keyboard shortcuts

### Library (`/library`)
- Grid/list view toggle
- Search and filter
- Click assets to see detail modal
- Download in multiple formats
- Share and delete options

### Packs (`/packs`)
- Create asset packs
- Multi-step creation wizard
- Pre-configured templates
- Revenue tracking

### Settings (`/settings`)
- 5-tab configuration interface
- General, Generation, Export, API, Billing
- API key management

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check if processes are already running
ps aux | grep -E "(node|python|uvicorn)" | grep -v grep

# Kill existing processes
pkill -f "uvicorn"
pkill -f "next dev"

# Restart
./start-unified.sh restart
```

### Port Already in Use

```bash
# Check what's using ports
netstat -tulpn | grep -E ':(3000|8000|6379)'

# Kill specific port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Restart
./start-unified.sh start
```

### API Not Responding

```bash
# Check API logs
tail -50 /tmp/staticwaves-logs/forge-api.log

# Test API manually
curl http://localhost:8000/

# Restart just the API
kill $(cat /tmp/staticwaves-pids/forge-api.pid)
cd /workspace/staticwaves-forge/staticwaves-forge/apps/api
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Web GUI Not Loading

```bash
# Check web logs
tail -50 /tmp/staticwaves-logs/forge-web.log

# Test locally
curl http://localhost:3000/

# Restart just the web
kill $(cat /tmp/staticwaves-pids/forge-web.pid)
cd /workspace/staticwaves-forge/staticwaves-forge/apps/web
npm run dev
```

### Dependencies Missing

```bash
# Reinstall Node dependencies
cd /workspace/staticwaves-forge/staticwaves-forge/apps/web
rm -rf node_modules
npm install

# Reinstall Python dependencies
pip install fastapi uvicorn python-multipart aiofiles pydantic
```

### Health Check Failures

```bash
# The script waits 30 attempts (60 seconds total)
# If services are slow, just wait longer

# Or adjust wait time in start-unified.sh:
# Change: max_attempts=30
# To:     max_attempts=60
```

---

## 🚀 Auto-Start on Pod Boot

To make services start automatically when your RunPod pod boots:

### Method 1: RunPod Template

Use the `runpod-template.json` configuration when creating your pod.

### Method 2: Manual Setup

```bash
# Create startup script in workspace root
cat > /workspace/start.sh << 'EOF'
#!/bin/bash
sleep 10  # Wait for system to be ready
bash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh start
EOF

chmod +x /workspace/start.sh
```

Then configure RunPod to run `/workspace/start.sh` on boot.

### Method 3: Systemd Service (if available)

```bash
cat > /etc/systemd/system/staticwaves.service << 'EOF'
[Unit]
Description=StaticWaves Forge Platform
After=network.target

[Service]
Type=forking
ExecStart=/workspace/staticwaves-forge/staticwaves-forge/start-unified.sh start
ExecStop=/workspace/staticwaves-forge/staticwaves-forge/start-unified.sh stop
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl enable staticwaves
systemctl start staticwaves
```

---

## 📊 Performance Tips

### For Best Performance:

1. **Use GPU Instance** - Even though web/API don't need GPU, having one available for future worker processes is beneficial

2. **Persistent Storage** - Use RunPod network volumes to persist:
   - `/workspace` - All code and data
   - `/tmp/staticwaves-logs` - Logs
   - `/root/.npm` - Node cache
   - `/root/.cache/pip` - Python cache

3. **Memory Allocation**:
   - Minimum: 16GB RAM
   - Recommended: 32GB+ RAM
   - Disk: 50GB+ SSD

4. **Network**:
   - Expose ports 3000 and 8000
   - Use RunPod proxy URLs for public access
   - Configure firewall if needed

---

## 🔒 Security Considerations

### Environment Variables

Never commit secrets. Use environment files:

```bash
# Create .env file
cat > /workspace/staticwaves-forge/staticwaves-forge/.env << 'EOF'
DATABASE_URL=your-database-url
API_SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
EOF
```

### Access Control

```bash
# Restrict API access to specific IPs (in nginx or firewall)
# Use API keys for authentication
# Enable CORS only for trusted domains
```

---

## 📈 Monitoring

### View Service Status

```bash
# Quick status
./start-unified.sh status

# Detailed process info
ps aux | grep -E "(node|python|uvicorn)"

# Resource usage
htop  # or top
```

### Log Aggregation

```bash
# All logs in one view
tail -f /tmp/staticwaves-logs/*.log

# Just errors
grep -i error /tmp/staticwaves-logs/*.log

# Last 100 lines
tail -100 /tmp/staticwaves-logs/forge-api.log
```

---

## 🎉 Success Checklist

After running `./start-unified.sh start`, you should see:

- ✅ "Redis Queue started successfully"
- ✅ "Forge API Backend started successfully"
- ✅ "Forge Web GUI started successfully"
- ✅ Service URLs displayed
- ✅ All health checks passed

**You're ready to go!** Open the web URL and start generating 3D assets! 🚀

---

## 📞 Support

- **GitHub Issues**: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- **Documentation**: See other `.md` files in this repo
- **API Docs**: Access at `https://YOUR-POD-ID-8000.proxy.runpod.net/docs`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-01
**Tested On**: RunPod PyTorch 2.1.0 image
