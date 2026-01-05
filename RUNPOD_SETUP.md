# RunPod Static Forge Setup Guide

This guide will help you connect your local GUI to your RunPod ComfyUI instance.

## Quick Setup

### 1. Your RunPod Configuration

Your RunPod instance is already configured in `.env`:

```bash
COMFYUI_API_URL=https://8yulnm43rzjh7l-8188.proxy.runpod.net
RUNPOD_POD_ID=8yulnm43rzjh7l
```

### 2. Start the Development Server

The dev server is already running at:
- **Local**: http://localhost:3000
- **Network**: http://21.0.0.72:3000

### 3. Access the GUI

Open your browser and navigate to:
```
http://localhost:3000
```

### 4. Verify Connection

You should see a connection status indicator in the top-left sidebar:
- **Green dot + "Connected"** = RunPod is accessible
- **Red dot + "Disconnected"** = RunPod is not responding
- **Yellow dot + "Checking..."** = Health check in progress

## What's Been Set Up

### New Components

1. **Connection Status Component** (`components/ConnectionStatus.tsx`)
   - Real-time health checks every 30 seconds
   - Shows RunPod connection status
   - Manual retry button

2. **Config Service** (`services/config.ts`)
   - Centralizes environment variable access
   - Detects RunPod vs local setup

3. **Updated App.tsx**
   - Integrated ComfyUI service
   - Shows connection status in sidebar
   - Ready for AI generation

### Environment Variables

The GUI now reads from `.env`:
- `COMFYUI_API_URL` - Your RunPod URL
- `RUNPOD_POD_ID` - Your pod identifier
- `ANTHROPIC_API_KEY` - For Claude-powered prompt generation

## Testing the Connection

### From Browser DevTools

1. Open http://localhost:3000
2. Open Browser DevTools (F12)
3. Go to Console tab
4. Run:
   ```javascript
   fetch('https://8yulnm43rzjh7l-8188.proxy.runpod.net/system_stats')
     .then(r => r.json())
     .then(console.log)
   ```

If successful, you'll see ComfyUI system stats in the console.

### Common Issues

**Connection shows "Disconnected":**
- ✓ Check if your RunPod pod is running
- ✓ Verify port 8188 is exposed
- ✓ Ensure ComfyUI is running in the pod
- ✓ Check browser console for CORS errors

**CORS Errors:**
- ComfyUI needs to allow cross-origin requests
- Add `--enable-cors-header` flag when starting ComfyUI:
  ```bash
  python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
  ```

## SSH into Your RunPod Instance

To check if ComfyUI is running or to start it:

```bash
ssh 8yulnm43rzjh7l-64410f12@ssh.runpod.io -i ~/.ssh/id_ed25519
```

Once connected:

```bash
# Check if ComfyUI is running
ps aux | grep comfyui

# Start ComfyUI with CORS enabled
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```

## Next Steps

### 1. Configure Claude API

Update `.env` with your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### 2. Test AI Generation

Once connected, the "Run Single Drop" button will:
1. Generate a creative prompt using Claude
2. Send it to your RunPod ComfyUI instance
3. Display the generated image in the preview panel
4. Queue it for Printify product creation

### 3. Configure Printify (Optional)

To enable full POD automation:
```bash
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
```

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ──────> │   Vite Dev   │ ──────> │   RunPod    │
│ localhost:  │  HTTP   │   Server     │  HTTPS  │   ComfyUI   │
│   3000      │         │   Port 3000  │         │   Port 8188 │
└─────────────┘         └──────────────┘         └─────────────┘
      │                                                  │
      │                                                  │
      └──────── Direct HTTPS Connection ────────────────┘
               (for health checks & API calls)
```

The browser makes direct requests to RunPod, bypassing any local proxy issues.

## Support

If you encounter issues:
1. Check RunPod pod status in dashboard
2. Verify ComfyUI logs in the pod
3. Check browser console for errors
4. Ensure `.env` configuration is correct
