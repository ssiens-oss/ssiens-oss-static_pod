# 🚀 Quick Start Guide

**Get StaticWaves POD running in 60 seconds!**

---

## ⚡ Super Quick Start (One Command)

```bash
./start.sh
```

**That's it!** The API server will start on `http://localhost:5000`

---

## 🧪 Test It's Working

```bash
./test.sh
```

You should see all tests pass with green ✓ marks.

---

## 🎬 See It In Action

```bash
./demo.sh
```

This runs through all the key features.

---

## 📋 Manual Steps (If You Want Details)

### 1. Install Dependencies

```bash
pip3 install flask flask-cors requests pillow python-dotenv
```

For browser automation (optional):
```bash
pip3 install playwright
playwright install
```

### 2. Create Directories

```bash
mkdir -p data/{queue/{pending,processing,done,failed},designs,logs,agents}
mkdir -p config
```

### 3. Configure (Optional)

Copy example config:
```bash
cp config/env.example config/.env
```

Edit `config/.env` to add your API keys (Printify, Shopify, TikTok).

For development, it works without any keys (dev mode enabled by default).

### 4. Start Server

```bash
python3 api/app.py
```

Server starts on `http://localhost:5000`

---

## 🎯 What You Can Do

### Check Health
```bash
curl http://localhost:5000/health
```

### Add Product to Queue
```bash
curl -X POST http://localhost:5000/queue/add \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cosmic Waves Hoodie",
    "prompt": "cosmic nebula galaxy stars",
    "type": "hoodie",
    "base_cost": 35.00,
    "inventory": 100
  }'
```

### Check Queue Status
```bash
curl http://localhost:5000/queue
```

### View Stats
```bash
curl http://localhost:5000/stats
```

### List Agents
```bash
curl http://localhost:5000/agents/agents
```

### Run Workflow
```bash
curl -X POST http://localhost:5000/agents/workflows/daily_research/run
```

### Quick Launch
```bash
curl -X POST http://localhost:5000/agents/quick-launch \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "neon cyberpunk",
    "product_type": "hoodie",
    "auto_publish": false
  }'
```

---

## 🌐 Start the Frontend (React UI)

In a new terminal:

```bash
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## 🐛 Troubleshooting

### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
pip3 install --break-system-packages flask flask-cors requests pillow python-dotenv
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use a different port
PORT=5001 python3 api/app.py
```

### Permission Errors

**Solution**:
```bash
chmod -R 755 data/
```

### Agent Errors

**Problem**: Playwright not installed

**Solution**:
```bash
pip3 install playwright
playwright install
```

---

## 📚 Next Steps

1. **Read the Docs**
   - [POD_STACK.md](POD_STACK.md) - Complete system guide
   - [AGENTS.md](AGENTS.md) - Agent automation
   - [API.md](API.md) - API reference

2. **Configure API Keys**
   - Edit `config/.env`
   - Add Printify, Shopify, TikTok credentials

3. **Test Full Pipeline**
   - Add product to queue
   - Run ComfyUI worker (if installed)
   - Check mockup generation
   - Test upload to Printify

4. **Run Automation**
   - Start agent daemon: `python3 agents/agent_daemon.py`
   - Or use systemd: `sudo systemctl start staticwaves-agents`

5. **Deploy to Production**
   - Build .deb: `./build-deb.sh`
   - Install: `sudo dpkg -i staticwaves-pod_*.deb`
   - Or use installer: `./install-master.sh`

---

## 🆘 Getting Help

- **Issues**: [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- **Docs**: See `POD_STACK.md`, `AGENTS.md`, `API.md`

---

## ✅ Quick Check

Everything working? You should be able to:

- ✓ Access `http://localhost:5000/health` (returns JSON)
- ✓ View queue status
- ✓ Add products to queue
- ✓ List agents
- ✓ Run workflows

If all these work, you're good to go! 🎉

---

**Built with ⚡ by the StaticWaves team**
