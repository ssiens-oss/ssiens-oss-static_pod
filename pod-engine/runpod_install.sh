#!/usr/bin/env bash
###############################################################################
# StaticWaves POD Engine - RunPod Optimized Installer
# Designed for RunPod GPU pods with persistent storage
###############################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🚀 StaticWaves POD Engine - RunPod Installation             ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Detect RunPod environment
if [ -d "/workspace" ]; then
    WORKSPACE="/workspace"
    echo "✅ RunPod environment detected"
else
    WORKSPACE="$HOME/staticwaves"
    echo "⚠️  Non-RunPod environment, using $WORKSPACE"
    mkdir -p "$WORKSPACE"
fi

cd "$WORKSPACE"

# System dependencies
echo "📦 Installing system dependencies..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    ffmpeg \
    libsm6 \
    libxext6 \
    supervisor \
    nginx \
    htop \
    > /dev/null 2>&1

echo "✅ System dependencies installed"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p {logs,queues/{incoming,done,failed,published},clients,exports,models}

# Clone or update repository
echo "📥 Setting up POD Engine..."
if [ ! -d "pod-engine" ]; then
    if [ -n "$REPO_URL" ]; then
        git clone "$REPO_URL" pod-engine
    else
        # Create minimal structure if no repo
        mkdir -p pod-engine
        cd pod-engine
        mkdir -p {workers,features,engine,comfy,tools}
        cd ..
    fi
fi

cd pod-engine

# Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip -q

# Install Python dependencies
echo "📦 Installing Python packages (this may take a few minutes)..."
cat > requirements.txt <<'EOF'
flask==3.0.0
flask-cors==4.0.0
fastapi==0.109.0
uvicorn[standard]==0.27.0
requests==2.31.0
python-dotenv==1.0.0
rembg==2.0.50
pillow==10.2.0
onnxruntime-gpu==1.16.3
tenacity==8.2.3
pydantic==2.5.3
websockets==12.0
pandas==2.1.4
openpyxl==3.1.2
aiohttp==3.9.1
psutil==5.9.7
EOF

pip install -r requirements.txt -q

# Install ComfyUI
echo "🎨 Installing ComfyUI..."
cd "$WORKSPACE"
if [ ! -d "ComfyUI" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
    pip install -r requirements.txt -q

    # Download models (optional - comment out if you want to add manually)
    echo "📥 Downloading default checkpoint (this takes time)..."
    mkdir -p models/checkpoints
    # Uncomment to auto-download a model:
    # wget -q -O models/checkpoints/v1-5-pruned.safetensors \
    #   "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors"

    cd "$WORKSPACE"
fi

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > "$WORKSPACE/pod-engine/.env" <<'EOF'
# Environment
ENV=production
WORKSPACE=/workspace

# ComfyUI
COMFY_API=http://127.0.0.1:8188

# Printify
PRINTIFY_API_KEY=
PRINTIFY_SHOP_ID=

# Shopify
SHOPIFY_STORE=
SHOPIFY_TOKEN=

# TikTok
TIKTOK_ACCESS_TOKEN=
TIKTOK_REFRESH_TOKEN=
TIKTOK_SELLER_ID=

# AI APIs
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# RunPod specific
RUNPOD_POD_ID=${RUNPOD_POD_ID}
RUNPOD_GPU_COUNT=${RUNPOD_GPU_COUNT:-1}
EOF

echo "✅ Environment file created at $WORKSPACE/pod-engine/.env"

# Supervisor configuration
echo "🔧 Configuring Supervisor..."
cat > /etc/supervisor/conf.d/staticwaves.conf <<EOF
[program:comfyui]
command=python3 main.py --listen 0.0.0.0 --port 8188
directory=$WORKSPACE/ComfyUI
autostart=true
autorestart=true
startsecs=10
user=root
stdout_logfile=$WORKSPACE/logs/comfyui.log
stderr_logfile=$WORKSPACE/logs/comfyui.err.log
environment=HOME="$WORKSPACE",USER="root"

[program:pod-api]
command=$WORKSPACE/pod-engine/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
directory=$WORKSPACE/pod-engine
autostart=true
autorestart=true
startsecs=10
user=root
stdout_logfile=$WORKSPACE/logs/pod-api.log
stderr_logfile=$WORKSPACE/logs/pod-api.err.log

[program:printify-worker]
command=$WORKSPACE/pod-engine/venv/bin/python workers/printify_worker.py
directory=$WORKSPACE/pod-engine
autostart=true
autorestart=true
startsecs=10
user=root
stdout_logfile=$WORKSPACE/logs/printify.log
stderr_logfile=$WORKSPACE/logs/printify.err.log

[program:shopify-worker]
command=$WORKSPACE/pod-engine/venv/bin/python workers/shopify_worker.py
directory=$WORKSPACE/pod-engine
autostart=true
autorestart=true
startsecs=10
user=root
stdout_logfile=$WORKSPACE/logs/shopify.log
stderr_logfile=$WORKSPACE/logs/shopify.err.log

[group:staticwaves]
programs=comfyui,pod-api,printify-worker,shopify-worker
EOF

# Create simple API server for health checks
echo "🌐 Creating API server..."
cat > "$WORKSPACE/pod-engine/api.py" <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import psutil
import requests
from pathlib import Path

app = FastAPI(title="StaticWaves POD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "StaticWaves POD Engine"}

@app.get("/health")
def health():
    """Health check endpoint"""
    comfy_status = "unknown"
    try:
        r = requests.get("http://127.0.0.1:8188/system_stats", timeout=2)
        comfy_status = "running" if r.status_code == 200 else "error"
    except:
        comfy_status = "offline"

    return {
        "status": "healthy",
        "comfyui": comfy_status,
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/workspace').percent if Path('/workspace').exists() else 0
    }

@app.get("/queues")
def queue_status():
    """Check queue status"""
    workspace = Path(os.getenv("WORKSPACE", "/workspace"))
    queues = {
        "incoming": len(list((workspace / "queues/incoming").glob("*.*"))),
        "done": len(list((workspace / "queues/done").glob("*.*"))),
        "failed": len(list((workspace / "queues/failed").glob("*.*"))),
        "published": len(list((workspace / "queues/published").glob("*.*")))
    }
    return queues

@app.get("/stats")
def stats():
    """Overall statistics"""
    return {
        "total_processed": 0,  # TODO: Track from database
        "success_rate": 0.0,
        "avg_processing_time": 0.0
    }
EOF

# Start supervisor
echo "🚀 Starting services..."
supervisorctl reread
supervisorctl update
supervisorctl start staticwaves:*

# Wait a moment for services to start
sleep 5

# Check status
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📊 Service Status:"
supervisorctl status

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Installation Complete!"
echo ""
echo "📍 Access Points (RunPod Proxy):"
echo "   • ComfyUI:  https://\${RUNPOD_POD_ID}-8188.proxy.runpod.net"
echo "   • API:      https://\${RUNPOD_POD_ID}-8000.proxy.runpod.net"
echo "   • Health:   https://\${RUNPOD_POD_ID}-8000.proxy.runpod.net/health"
echo ""
echo "📁 Important Paths:"
echo "   • Workspace:    $WORKSPACE"
echo "   • POD Engine:   $WORKSPACE/pod-engine"
echo "   • ComfyUI:      $WORKSPACE/ComfyUI"
echo "   • Queues:       $WORKSPACE/queues"
echo "   • Logs:         $WORKSPACE/logs"
echo ""
echo "⚙️  Next Steps:"
echo "   1. Edit API keys: nano $WORKSPACE/pod-engine/.env"
echo "   2. Add ComfyUI models to: $WORKSPACE/ComfyUI/models/checkpoints/"
echo "   3. Restart services: supervisorctl restart staticwaves:*"
echo "   4. Check logs: tail -f $WORKSPACE/logs/*.log"
echo ""
echo "═══════════════════════════════════════════════════════════════"
