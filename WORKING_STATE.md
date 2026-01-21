# ✅ WORKING STATE - POD Pipeline v1.0

**Date**: 2026-01-21
**Git Commit**: 7454ce0
**Branch**: claude/rebuild-pod-pipeline-gateway-Xf829
**Status**: FULLY FUNCTIONAL

---

## 🎯 What's Working

### ✅ Gateway Authentication
- RunPod API authentication successful
- No more 401 Unauthorized errors
- Environment variables loading correctly

### ✅ Image Generation
- **Flux-dev-fp8** model optimized
- Sharp, clear, professional-quality images
- POD-ready output (1024x1024)

**Working Settings:**
- Steps: 25 (higher quality)
- CFG: 3.5 (Flux-optimized, prevents blur)
- Scheduler: "simple" (Flux-optimized)
- Negative prompt: empty (Flux handles differently)

### ✅ File Paths
- Local paths working (/home/static/ssiens-oss-static_pod/output)
- No /workspace permission errors
- Directories auto-created

### ✅ Startup
- Gateway starts successfully with `./start-gateway-direct.sh`
- All environment variables loaded
- Listens on 0.0.0.0:5000

---

## 🚀 How to Start (Fresh Environment)

### 1. Pull Latest Code
```bash
cd /home/static/ssiens-oss-static_pod
git pull origin claude/rebuild-pod-pipeline-gateway-Xf829
```

### 2. Start Gateway
```bash
./start-gateway-direct.sh
```

**Expected Output:**
```
🚀 POD Gateway starting...
📁 Image directory: /home/static/ssiens-oss-static_pod/output
💾 State file: /home/static/ssiens-oss-static_pod/gateway/data/state.json
🔌 Printify: enabled
✓ RunPod serverless client initialized
🌐 Listening on 0.0.0.0:5000
```

### 3. Test Generation
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "vibrant abstract geometric art", "width": 1024, "height": 1024}'
```

---

## 📦 Backup Information

### Git Tag
```bash
# Tagged locally as: v1.0-working-pod-pipeline
git tag -l | grep working
```

### Tarball Backup
**Location**: `/home/user/ssiens-oss-static_pod-backup-20260121-194059.tar.gz`
**Size**: 90MB
**Excludes**: .git, __pycache__, output/, gateway/data/, .env files

**To Restore from Backup:**
```bash
cd /home/user
tar -xzf ssiens-oss-static_pod-backup-20260121-194059.tar.gz
cd ssiens-oss-static_pod
# Configure .env with your credentials
./start-gateway-direct.sh
```

---

## 🔑 Required Credentials

Create `.env.runpod-config` with:
```bash
RUNPOD_API_KEY=your-runpod-api-key
COMFYUI_API_URL=https://api.runpod.ai/v2/your-endpoint-id/runsync
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
CLAUDE_API_KEY=your-claude-api-key
```

**Note**: `start-gateway-direct.sh` loads from `.env.runpod-config`

---

## 📝 Key Commits

| Commit | Fix |
|--------|-----|
| 7454ce0 | Optimize Flux workflow - fixes blurry images |
| 83ecb76 | Add direct gateway start script with all env vars |
| fd2191a | Force-set local POD paths before gateway starts |
| c6493c4 | Load .env from correct directory |
| dc87c7c | Rebuild POD pipeline with serverless optimization |

---

## 🔧 Critical Files

### Start Script
- **start-gateway-direct.sh**: Loads all env vars from .env.runpod-config

### Gateway Core
- **gateway/app/main.py**: Flux-optimized workflow (CFG 3.5, steps 25)
- **gateway/app/runpod_adapter.py**: RunPod integration with 300s timeout
- **gateway/app/config.py**: Configuration management

### Pipeline
- **pod-pipeline.py**: Automated POD pipeline with proof-of-life
- **run-pod-pipeline.sh**: CLI wrapper for pipeline operations

### Documentation
- **POD_PIPELINE_GUIDE.md**: Complete usage guide
- **CONFIGURATION_GUIDE.md**: Credential setup instructions
- **QUICK_SETUP.md**: Quick reference for fresh environments

---

## ⚠️ Don't Change

These settings are optimized and working - **DO NOT modify** without testing:

1. **Flux CFG**: Must stay at 3.5 (7.0 causes blur!)
2. **Steps**: 25 minimum for quality
3. **Scheduler**: "simple" for Flux
4. **Negative prompt**: Empty for Flux
5. **Paths**: Local paths in start-gateway-direct.sh

---

## 🧪 Testing Checklist

After any changes, verify:

- [ ] Gateway starts without errors
- [ ] No 401 authentication errors
- [ ] No /workspace permission errors
- [ ] Image generation completes
- [ ] Images are sharp and clear (not blurry)
- [ ] Images are 1024x1024
- [ ] Printify upload works

---

## 📊 Performance

- **Generation time**: ~60-90 seconds (RunPod serverless)
- **Timeout**: 300 seconds (5 minutes)
- **Auto-polling**: Every 2 seconds
- **Image quality**: POD-ready (sharp, 1024x1024)

---

## 🆘 Troubleshooting

### Gateway won't start
```bash
# Pull latest code
git pull origin claude/rebuild-pod-pipeline-gateway-Xf829

# Check credentials exist
cat .env.runpod-config

# Start with direct script
./start-gateway-direct.sh
```

### 401 Errors
```bash
# Verify RUNPOD_API_KEY is set in .env.runpod-config
grep RUNPOD_API_KEY .env.runpod-config

# Restart gateway
./start-gateway-direct.sh
```

### Blurry Images
```bash
# Verify Flux settings in gateway/app/main.py
# Should be: steps=25, cfg_scale=3.5, scheduler="simple"
grep -A2 "def build_comfyui_workflow" gateway/app/main.py
```

---

**Last Updated**: 2026-01-21 19:40 UTC
**Maintained by**: Claude (ssiens-oss)
