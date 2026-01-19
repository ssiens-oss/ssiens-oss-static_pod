# RunPod ComfyUI Configuration Guide

## Problem: Image Generation Failing

If you're seeing **generation failed** errors, it's likely because your `.env` file is configured for **local ComfyUI** (`localhost:8188`) but your ComfyUI is actually running on **RunPod** (remote).

## Quick Fix

Run this script to automatically fix your configuration:

```bash
cd ~/ssiens-oss-static_pod
./scripts/fix-runpod-url.sh
```

This will:
1. Read your `RUNPOD_POD_ID` from `.env`
2. Construct the correct RunPod URL
3. Update `COMFYUI_API_URL` in `.env`
4. Test the connection
5. Show you the results

## Manual Fix

If you prefer to update manually:

### 1. Find Your Pod ID

Check your `.env` file:
```bash
cat .env | grep RUNPOD_POD_ID
```

Example output:
```
RUNPOD_POD_ID=qm6ofmy96f3htl
```

### 2. Construct the RunPod URL

RunPod exposes services using this format:
```
https://{POD_ID}-{PORT}.proxy.runpod.net
```

For ComfyUI (port 8188), it becomes:
```
https://qm6ofmy96f3htl-8188.proxy.runpod.net
```

### 3. Update .env

Edit your `.env` file:
```bash
nano .env
```

Change this line:
```bash
COMFYUI_API_URL=http://localhost:8188
```

To this (replace with YOUR pod ID):
```bash
COMFYUI_API_URL=https://qm6ofmy96f3htl-8188.proxy.runpod.net
```

### 4. Test the Connection

```bash
curl https://qm6ofmy96f3htl-8188.proxy.runpod.net/system_stats
```

If successful, you'll see JSON with system stats.

## Troubleshooting

### Connection Fails

If you can't connect to the RunPod URL:

**1. Check if your pod is running:**
- Go to https://www.runpod.io/console/pods
- Ensure your pod status is "Running"
- If stopped, click "Start" to resume it

**2. Verify port 8188 is exposed:**
- In RunPod dashboard, check your pod's ports
- You should see port 8188 exposed as HTTP
- The dashboard will show you the exact URL to use

**3. Check if ComfyUI is running inside the pod:**
- Click "Connect" on your pod
- Open a terminal
- Run: `ps aux | grep comfyui` or `ps aux | grep main.py`
- If not running, start it: `cd /workspace/ComfyUI && python main.py --listen`

**4. Alternative URL formats:**

Some RunPod configurations use different URL formats:
```
https://{POD_ID}.proxy.runpod.net:8188
https://{POD_ID}-8188.proxy.runpod.io
```

Check your RunPod dashboard for the exact HTTP endpoint URL.

### Still Not Working?

Use the diagnostic script:
```bash
cd ~/ssiens-oss-static_pod
./scripts/get-runpod-endpoint.sh
```

This will:
- Query the RunPod API
- Show you all exposed ports
- Suggest the correct URL
- Test connectivity

## Verifying the Fix

After updating your configuration:

### 1. Restart the Gateway

```bash
cd ~/ssiens-oss-static_pod/gateway
python app/main.py
```

### 2. Test Image Generation

Open your browser to `http://localhost:5000` and try generating an image through the gateway.

Or use the API directly:
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful landscape"}'
```

### 3. Check Logs

If generation fails, check the gateway logs for the exact error:
```bash
tail -f /tmp/pod-gateway.log
```

Look for lines mentioning ComfyUI or connection errors.

## Configuration Reference

Your `.env` should have these RunPod settings:

```bash
# ComfyUI Configuration (IMPORTANT!)
COMFYUI_API_URL=https://your-pod-id-8188.proxy.runpod.net  # ← RunPod URL, not localhost!
COMFYUI_OUTPUT_DIR=/workspace/comfyui/output               # Path inside RunPod pod

# RunPod Credentials
RUNPOD_POD_ID=your-pod-id-here                             # Your pod ID
RUNPOD_API_KEY=your-api-key-here                           # Your RunPod API key
```

## Local vs RunPod

### Local ComfyUI (on your machine)
```bash
COMFYUI_API_URL=http://localhost:8188
```

### RunPod ComfyUI (remote)
```bash
COMFYUI_API_URL=https://your-pod-id-8188.proxy.runpod.net
```

**You cannot use both simultaneously.** Choose one based on where your ComfyUI is actually running.

## Performance Notes

### RunPod (Remote)
- ✅ GPU acceleration (if you have a GPU pod)
- ✅ No local resource usage
- ✅ Scales independently
- ⚠️ Network latency (1-3 seconds per request)
- ⚠️ Requires internet connection
- ⚠️ Costs per hour when running

### Local ComfyUI
- ✅ No network latency
- ✅ Free (after initial setup)
- ✅ Works offline
- ⚠️ Requires local GPU or slow CPU generation
- ⚠️ Uses local resources
- ⚠️ Limited by your hardware

## Common Issues

### Issue: "Connection refused"
**Cause:** Pod is stopped or ComfyUI not running
**Fix:** Start pod in RunPod dashboard

### Issue: "404 Not Found"
**Cause:** Wrong URL or port not exposed
**Fix:** Check RunPod dashboard for correct endpoint

### Issue: "Timeout"
**Cause:** Pod is busy or unresponsive
**Fix:** Check pod logs, restart if needed

### Issue: "SSL certificate error"
**Cause:** Using `http://` instead of `https://`
**Fix:** Use `https://` for RunPod URLs

## Need Help?

1. Run diagnostics: `./scripts/get-runpod-endpoint.sh`
2. Check RunPod dashboard: https://www.runpod.io/console/pods
3. Review gateway logs: `tail -f /tmp/pod-gateway.log`
4. Test direct access in browser: `https://your-pod-id-8188.proxy.runpod.net`

## Summary

**If generation is failing:**
1. Your ComfyUI is on RunPod (remote)
2. But your config points to localhost (local)
3. Run `./scripts/fix-runpod-url.sh` to fix it
4. Restart the gateway
5. Try generating again

That's it! 🚀
