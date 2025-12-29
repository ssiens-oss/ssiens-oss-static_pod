#!/usr/bin/env bash
set -e

echo "🚀 StaticWaves POD Engine → RunPod Installer"

# System dependencies
apt update && apt install -y \
  git ffmpeg supervisor curl nginx \
  python3 python3-venv

# Directories
mkdir -p /workspace/{logs,queues/{incoming,done,failed,published},clients}
cd /workspace

# Clone or update POD Engine
if [ ! -d pod-engine ]; then
  git clone https://github.com/YOUR_REPO/ssiens-oss-static_pod.git
  mv ssiens-oss-static_pod/pod-engine pod-engine
fi

cd pod-engine

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Clone ComfyUI (if needed)
if [ ! -d /workspace/ComfyUI ]; then
  cd /workspace
  git clone https://github.com/comfyanonymous/ComfyUI.git
  cd ComfyUI
  pip install -r requirements.txt
fi

# Supervisor configuration
cat >/etc/supervisor/conf.d/staticwaves.conf <<'EOF'
[program:comfyui]
command=python3 main.py --listen 0.0.0.0 --port 8188
directory=/workspace/ComfyUI
autostart=true
autorestart=true
stdout_logfile=/workspace/logs/comfy.out.log
stderr_logfile=/workspace/logs/comfy.err.log

[program:printify-worker]
command=/workspace/pod-engine/venv/bin/python workers/printify_worker.py
directory=/workspace/pod-engine
autostart=true
autorestart=true
stdout_logfile=/workspace/logs/printify.out.log
stderr_logfile=/workspace/logs/printify.err.log

[program:shopify-worker]
command=/workspace/pod-engine/venv/bin/python workers/shopify_worker.py
directory=/workspace/pod-engine
autostart=true
autorestart=true
stdout_logfile=/workspace/logs/shopify.out.log
stderr_logfile=/workspace/logs/shopify.err.log
EOF

# Reload supervisor
supervisorctl reread
supervisorctl update

echo "✅ StaticWaves POD Engine installed!"
echo "⚠️ Next steps:"
echo "  1. Edit /workspace/pod-engine/.env with your API keys"
echo "  2. supervisorctl restart all"
echo "  3. Access at https://<pod>-8188.proxy.runpod.net (ComfyUI)"
