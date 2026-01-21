# Quick Setup for Fresh Environment

This guide is for environments that pull fresh code each time (like RunPod, cloud instances, etc.)

## 🚀 One-Time Setup (Run in Fresh Environment)

### Step 1: Pull Latest Code

```bash
cd ~/ssiens-oss-static_pod
git fetch origin claude/rebuild-pod-pipeline-gateway-Xf829
git checkout claude/rebuild-pod-pipeline-gateway-Xf829
git pull origin claude/rebuild-pod-pipeline-gateway-Xf829
```

### Step 2: Configure Credentials

**IMPORTANT**: Your `.env` file needs your actual API keys. Choose one method:

#### Method A: Quick Edit (Fastest)

```bash
nano .env
```

Update these lines with your actual credentials:
```bash
# Line 2: RunPod endpoint URL
COMFYUI_API_URL=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync

# Line 74: Your RunPod API key (get from https://www.runpod.io/console/user/settings)
RUNPOD_API_KEY=your-runpod-api-key-here

# Optional: Printify credentials for publishing
PRINTIFY_API_KEY=your-printify-api-key-here
PRINTIFY_SHOP_ID=your-shop-id-here

# Optional: Claude API for metadata generation
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

#### Method B: One-Liner (Replace with your actual credentials)

```bash
# Replace YOUR_KEY and YOUR_ENDPOINT_ID with actual values
sed -i 's|^RUNPOD_API_KEY=.*|RUNPOD_API_KEY=your-actual-key-here|' .env
sed -i 's|^COMFYUI_API_URL=.*|COMFYUI_API_URL=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync|' .env
```

#### Method C: Interactive Setup

```bash
./setup-pod-config.sh
```

### Step 3: Install Dependencies

```bash
cd gateway
pip install -r requirements.txt
cd ..
```

### Step 4: Verify Configuration

```bash
./check-pod-config.sh
```

You should see:
- ✅ RUNPOD_API_KEY: Configured
- ✅ COMFYUI_API_URL: Set to RunPod serverless

### Step 5: Start Gateway

```bash
./start-gateway-runpod.sh
```

The gateway will automatically:
- Fetch latest code from your branch
- Check out updated files (runpod_adapter.py with new error handling)
- Load your `.env` credentials
- Start on http://0.0.0.0:5000

### Step 6: Test Generation

Open another terminal and test:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test cat", "width": 1024, "height": 1024}'
```

**Expected**: No more 401 errors! Should see generation succeed or timeout (endpoint warming up).

## 🔧 What's New in This Branch

### Fixed Issues:
1. ✅ **RunPod 401 Error** - Better error messages with fix instructions
2. ✅ **Printify Publishing** - Graceful handling when no sales channels
3. ✅ **Config Checker** - Handles .env comments properly

### New Tools:
1. **./setup-pod-config.sh** - Interactive credential setup
2. **./check-pod-config.sh** - Configuration validator
3. **./run-pod-pipeline.sh** - Proof-of-life pipeline runner
4. **pod-pipeline.py** - Complete automation script

### Enhanced Files:
- `gateway/app/runpod_adapter.py` - Extended timeout (300s), auto-polling, better errors
- `gateway/app/printify_client.py` - Graceful publishing failure handling
- `start-gateway-runpod.sh` - Auto-detects current branch, optional proof-of-life

## 📋 Quick Reference Commands

```bash
# Check configuration
./check-pod-config.sh

# Start gateway
./start-gateway-runpod.sh

# Run proof of life (in another terminal after gateway starts)
./run-pod-pipeline.sh --theme "vibrant abstract art"

# Generate without publishing
./run-pod-pipeline.sh --theme "test design" --no-publish

# View logs
# (logs appear in terminal where gateway is running)
```

## 🆘 Troubleshooting

### Still getting 401 errors?

1. **Check credentials are set**:
   ```bash
   grep RUNPOD_API_KEY .env
   ```
   Should show: `RUNPOD_API_KEY=your-actual-key-here` (with your real key)

2. **Restart gateway** to load new credentials:
   ```bash
   # Press Ctrl+C in gateway terminal
   ./start-gateway-runpod.sh
   ```

3. **Check if new error handling is loaded**:
   When gateway starts, you should see in logs:
   ```
   ✓ Using RunPod serverless client
   ```

### Endpoint timeout (503)?

This is normal when RunPod endpoint is cold. It will warm up on first request.
Just retry the generation request.

### Printify publishing fails?

Expected if you haven't connected a sales channel. Product is still created in Printify catalog.
To fix: Connect Shopify/Etsy in https://printify.com/app/stores

## 📚 Documentation

- **Configuration Guide**: [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)
- **Pipeline Guide**: [POD_PIPELINE_GUIDE.md](./POD_PIPELINE_GUIDE.md)
- **Gateway Features**: [GATEWAY_FEATURES.md](./GATEWAY_FEATURES.md)

---

**Branch**: `claude/rebuild-pod-pipeline-gateway-Xf829`
**Last Updated**: 2026-01-21
