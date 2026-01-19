# RunPod Serverless - Quick Start Guide

## ⚡ One-Command Start

```bash
cd ~/ssiens-oss-static_pod
bash start-gateway-runpod.sh
```

This script will:
1. Fix any merge conflicts
2. Configure `.env` from `.env.runpod-config`
3. Verify Python syntax
4. Install dependencies if needed
5. Start the POD Gateway

---

## 🔧 If You Have Merge Conflicts

```bash
cd ~/ssiens-oss-static_pod
bash emergency-fix.sh
```

This will reset your repository to a clean state by checking out fresh files from the remote.

---

## 📝 Manual Setup

If you prefer to configure manually:

### 1. Fix merge conflicts (if any)
```bash
cd ~/ssiens-oss-static_pod
git merge --abort
git reset --hard HEAD
git fetch origin claude/review-changes-mkljilavyj0p92rc-yIHnQ
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/main.py
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/runpod_adapter.py
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/config.py
```

### 2. Configure `.env`

See `.env.runpod-config` for your specific credentials, then edit `.env`:

```bash
# Find lines and update:
COMFYUI_API_URL=https://api.runpod.ai/v2/{your-endpoint-id}/runsync
RUNPOD_API_KEY={your-runpod-api-key}
PRINTIFY_API_KEY=
PRINTIFY_SHOP_ID=
```

### 3. Start gateway
```bash
cd gateway
PYTHONPATH=$(pwd) python3 -m app.main
```

---

## ✅ Verify It's Working

### Health Check
```bash
curl http://127.0.0.1:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "image_dir": true,
  "printify": false
}
```

### Test Image Generation
```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "beautiful sunset", "width": 1024, "height": 1024}'
```

Expected response:
```json
{
  "prompt_id": "sync-...",
  "status": "COMPLETED",
  "prompt": "beautiful sunset"
}
```

---

## 📍 Access Points

- **Web UI:** http://127.0.0.1:5000
- **Health:** http://127.0.0.1:5000/health
- **API:** http://127.0.0.1:5000/api/*

---

## 🐛 Troubleshooting

### Python Syntax Error with ">>>>>>>"
This means you have merge conflict markers in your files.

**Fix:** Run `bash emergency-fix.sh`

### "RUNPOD_API_KEY is required"
Your `.env` is not configured with RunPod credentials.

**Fix:** Edit `.env` and add your credentials (see `.env.runpod-config`)

### "ModuleNotFoundError: No module named 'flask'"
Dependencies not installed.

**Fix:**
```bash
cd gateway
python3 -m pip install -r requirements.txt
```

### Gateway won't start
Check for merge conflicts or syntax errors.

**Fix:** Run `bash emergency-fix.sh` then restart

---

## 📚 More Info

- Full documentation: `RUNPOD_SETUP.md`
- Configuration details: `.env.runpod-config`
- Helper scripts: `emergency-fix.sh`, `start-gateway-runpod.sh`
