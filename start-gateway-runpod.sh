#!/bin/bash
# Complete setup and start script for POD Gateway with RunPod serverless
# This script fixes any merge conflicts, configures .env, and starts the gateway

set -e

echo "🚀 POD Gateway - RunPod Serverless Setup"
echo "========================================"
echo ""

cd ~/ssiens-oss-static_pod

# Auto-detect current branch or use environment variable
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
GATEWAY_BRANCH="${GATEWAY_BRANCH:-$CURRENT_BRANCH}"

# Step 1: Fix any merge conflicts
echo "1️⃣  Fixing merge conflicts..."
echo "   Using branch: ${GATEWAY_BRANCH}"
git merge --abort 2>/dev/null || true
git reset --hard HEAD 2>/dev/null || true
git fetch origin "${GATEWAY_BRANCH}" 2>/dev/null || echo "   (Using local branch)"
git checkout "origin/${GATEWAY_BRANCH}" -- gateway/app/main.py 2>/dev/null || true
git checkout "origin/${GATEWAY_BRANCH}" -- gateway/app/runpod_adapter.py 2>/dev/null || true
git checkout "origin/${GATEWAY_BRANCH}" -- gateway/app/config.py 2>/dev/null || true
git checkout "origin/${GATEWAY_BRANCH}" -- gateway/templates/gallery.html 2>/dev/null || true
git checkout "origin/${GATEWAY_BRANCH}" -- RUNPOD_SETUP.md 2>/dev/null || true
echo "   ✅ Files cleaned"
echo ""

# Step 2: Verify Python syntax
echo "2️⃣  Verifying Python syntax..."
if python3 -m py_compile gateway/app/main.py 2>/dev/null; then
    echo "   ✅ main.py syntax OK"
else
    echo "   ❌ main.py has syntax errors"
    exit 1
fi

if python3 -m py_compile gateway/app/runpod_adapter.py 2>/dev/null; then
    echo "   ✅ runpod_adapter.py syntax OK"
else
    echo "   ❌ runpod_adapter.py has syntax errors"
    exit 1
fi
echo ""

# Step 3: Configure .env
echo "3️⃣  Configuring .env for RunPod serverless..."

if [ ! -f ".env.runpod-config" ]; then
    echo "   ❌ .env.runpod-config not found!"
    echo "   Please create this file with your RunPod credentials"
    echo "   See RUNPOD_SETUP.md for instructions"
    exit 1
fi

# Extract values from .env.runpod-config (they're in the comments/examples)
# For security, credentials should be in .env.runpod-config (gitignored)
# This is a placeholder - users should have their own .env.runpod-config
RUNPOD_URL=$(grep "^COMFYUI_API_URL=" .env.runpod-config | head -1 | cut -d= -f2)
RUNPOD_KEY=$(grep "^RUNPOD_API_KEY=" .env.runpod-config | head -1 | cut -d= -f2)

if [ -z "$RUNPOD_URL" ] || [ -z "$RUNPOD_KEY" ]; then
    echo "   ℹ️  .env.runpod-config exists but credentials not extracted"
    echo "   Using manual configuration..."
    echo ""
    echo "   Please configure .env manually with your RunPod credentials:"
    echo "   - COMFYUI_API_URL=https://api.runpod.ai/v2/{your-endpoint}/runsync"
    echo "   - RUNPOD_API_KEY={your-api-key}"
    echo "   - PRINTIFY_API_KEY= (leave empty)"
    echo "   - PRINTIFY_SHOP_ID= (leave empty)"
    echo ""
    read -p "Press Enter when done, or Ctrl+C to exit..."
else
    sed -i "s|^COMFYUI_API_URL=.*|COMFYUI_API_URL=$RUNPOD_URL|" .env
    sed -i "s|^RUNPOD_API_KEY=.*|RUNPOD_API_KEY=$RUNPOD_KEY|" .env
    sed -i 's|^PRINTIFY_API_KEY=.*|PRINTIFY_API_KEY=|' .env
    sed -i 's|^PRINTIFY_SHOP_ID=.*|PRINTIFY_SHOP_ID=|' .env
    echo "   ✅ .env configured from .env.runpod-config"
fi
echo ""

# Step 4: Install dependencies if needed
echo "4️⃣  Checking dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    echo "   ✅ Dependencies OK"
else
    echo "   📦 Installing dependencies..."
    cd gateway
    python3 -m pip install -q -r requirements.txt
    cd ..
    echo "   ✅ Dependencies installed"
fi
echo ""

# Step 5: Start gateway
echo "5️⃣  Starting POD Gateway..."
echo ""
# Extract endpoint ID from configured URL if possible
ENDPOINT_ID=$(echo "$RUNPOD_URL" | grep -oP 'v2/\K[^/]+' || echo "(configured in .env)")
echo "============================================================"
echo "🌐 Gateway will start on http://127.0.0.1:5000"
echo "🧠 Using RunPod Serverless: ${ENDPOINT_ID}"
echo "🎨 Model: Flux Dev FP8"
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd gateway
PYTHONPATH=$(pwd) python3 -m app.main
