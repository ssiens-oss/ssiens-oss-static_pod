#!/bin/bash

###############################################################################
# RunPod Deployment Guide - Step by Step
###############################################################################

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            🚀 POD Engine RunPod Deployment                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

STEP 1: CREATE RUNPOD POD
═══════════════════════════════════════════════════════════════

1. Go to https://www.runpod.io/console/pods
2. Click "Deploy"
3. Choose template:
   - Select "RunPod Pytorch" or "RunPod Stable Diffusion"
   - GPU: RTX A4000 or better (recommended)
   - Storage: 50GB+ persistent volume

4. Configure ports to expose:
   - 5000 (POD Gateway)
   - 8188 (ComfyUI)
   - 5173 (Web UI - optional)

5. Click "Deploy On-Demand"

═══════════════════════════════════════════════════════════════

STEP 2: CONNECT TO YOUR POD
═══════════════════════════════════════════════════════════════

Once deployed, click "Connect" and choose:
- Option A: SSH Terminal (direct)
- Option B: Web Terminal

Copy your connection command, it looks like:
  ssh root@your-pod-id.runpod.io -p PORT -i ~/.ssh/id_rsa

═══════════════════════════════════════════════════════════════

STEP 3: SETUP ON RUNPOD
═══════════════════════════════════════════════════════════════

Run these commands on your RunPod instance:

# Navigate to workspace (persistent storage)
cd /workspace

# Clone repository
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod

# Checkout deployment branch
git checkout claude/summarize-recent-changes-gmY14

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Deploy
./deploy-pod-engine.sh runpod

# Start services
./start-pod-engine.sh

═══════════════════════════════════════════════════════════════

STEP 4: ACCESS YOUR SERVICES
═══════════════════════════════════════════════════════════════

RunPod will provide public URLs for your exposed ports:

POD Gateway:  https://your-pod-id-5000.proxy.runpod.net
ComfyUI:      https://your-pod-id-8188.proxy.runpod.net
Web UI:       https://your-pod-id-5173.proxy.runpod.net

Find these URLs in your RunPod dashboard under "Connect" → "TCP Port Mappings"

═══════════════════════════════════════════════════════════════

STEP 5: VERIFY DEPLOYMENT
═══════════════════════════════════════════════════════════════

Test your services:

# Check health
curl http://localhost:5000/health

# View logs
tail -f logs/*.log

# Check running processes
ps aux | grep -E "(gateway|comfyui|vite)"

═══════════════════════════════════════════════════════════════

QUICK COMMANDS
═══════════════════════════════════════════════════════════════

Start services:    ./start-pod-engine.sh
Stop services:     ./stop-pod-engine.sh
View logs:         tail -f logs/*.log
Check status:      curl http://localhost:5000/health
Update code:       git pull origin claude/summarize-recent-changes-gmY14

═══════════════════════════════════════════════════════════════

COST OPTIMIZATION
═══════════════════════════════════════════════════════════════

- Use Spot Instances: 70% cheaper
- Stop pod when not in use
- Use persistent volume for designs
- Generate in batches to maximize GPU utilization

Estimated costs:
- RTX A4000: $0.34/hour on-demand, $0.10/hour spot
- 100 designs in 1 hour: ~$0.34 ($0.003 per design)

═══════════════════════════════════════════════════════════════

TROUBLESHOOTING
═══════════════════════════════════════════════════════════════

If services won't start:
1. Check logs: tail -f logs/*.log
2. Verify ports: netstat -tulpn | grep -E "(5000|8188)"
3. Check GPU: nvidia-smi
4. Restart: ./stop-pod-engine.sh && ./start-pod-engine.sh

If can't access from browser:
1. Verify ports are exposed in RunPod settings
2. Check firewall rules
3. Use RunPod's provided proxy URLs

═══════════════════════════════════════════════════════════════

NEED HELP?

Documentation:
- POD_ENGINE_DEPLOYMENT.md
- QUICKSTART_POD_ENGINE.md
- POD_GATEWAY_INTEGRATION.md

Support:
- GitHub Issues: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- RunPod Docs: https://docs.runpod.io/

═══════════════════════════════════════════════════════════════

EOF
