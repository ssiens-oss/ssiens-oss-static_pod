#!/bin/bash
# Complete setup and start script for POD Gateway with RunPod serverless
# This script fixes any merge conflicts, configures .env, and starts the gateway

set -e

echo "🚀 POD Gateway - RunPod Serverless Setup"
echo "========================================"
echo ""

cd ~/ssiens-oss-static_pod

# Get current branch or use environment variable
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
GATEWAY_BRANCH="${GATEWAY_BRANCH:-$CURRENT_BRANCH}"

# Step 1: Fix any merge conflicts
echo "1️⃣  Fixing merge conflicts..."
git merge --abort 2>/dev/null || true
git reset --hard HEAD 2>/dev/null || true
git fetch origin "${GATEWAY_BRANCH}"
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
POD_IMG_DIR=$(grep "^POD_IMAGE_DIR=" .env.runpod-config | head -1 | cut -d= -f2)
POD_STATE=$(grep "^POD_STATE_FILE=" .env.runpod-config | head -1 | cut -d= -f2)
POD_ARCHIVE=$(grep "^POD_ARCHIVE_DIR=" .env.runpod-config | head -1 | cut -d= -f2)

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

    # Apply local paths from .env.runpod-config (avoid /workspace permission errors)
    if [ -n "$POD_IMG_DIR" ]; then
        if grep -q "^POD_IMAGE_DIR=" .env; then
            sed -i "s|^POD_IMAGE_DIR=.*|POD_IMAGE_DIR=$POD_IMG_DIR|" .env
        else
            echo "POD_IMAGE_DIR=$POD_IMG_DIR" >> .env
        fi
    fi
    if [ -n "$POD_STATE" ]; then
        if grep -q "^POD_STATE_FILE=" .env; then
            sed -i "s|^POD_STATE_FILE=.*|POD_STATE_FILE=$POD_STATE|" .env
        else
            echo "POD_STATE_FILE=$POD_STATE" >> .env
        fi
    fi
    if [ -n "$POD_ARCHIVE" ]; then
        if grep -q "^POD_ARCHIVE_DIR=" .env; then
            sed -i "s|^POD_ARCHIVE_DIR=.*|POD_ARCHIVE_DIR=$POD_ARCHIVE|" .env
        else
            echo "POD_ARCHIVE_DIR=$POD_ARCHIVE" >> .env
        fi
    fi

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

# CRITICAL FIX: Ensure POD paths are set before starting (avoid /workspace error)
# Detect home directory dynamically
USER_HOME=$(eval echo ~$USER)
PROJECT_DIR="$USER_HOME/ssiens-oss-static_pod"

# Force-set POD paths if they're missing or still point to /workspace
grep -q "^POD_IMAGE_DIR=" .env || echo "POD_IMAGE_DIR=$PROJECT_DIR/output" >> .env
grep -q "^POD_STATE_FILE=" .env || echo "POD_STATE_FILE=$PROJECT_DIR/gateway/data/state.json" >> .env
grep -q "^POD_ARCHIVE_DIR=" .env || echo "POD_ARCHIVE_DIR=$PROJECT_DIR/gateway/data/archive" >> .env

# Update if they still point to /workspace
sed -i "s|^POD_IMAGE_DIR=/workspace.*|POD_IMAGE_DIR=$PROJECT_DIR/output|" .env
sed -i "s|^POD_STATE_FILE=/workspace.*|POD_STATE_FILE=$PROJECT_DIR/gateway/data/state.json|" .env
sed -i "s|^POD_ARCHIVE_DIR=/workspace.*|POD_ARCHIVE_DIR=$PROJECT_DIR/gateway/data/archive|" .env

# Create directories
mkdir -p "$PROJECT_DIR/output" "$PROJECT_DIR/gateway/data"

echo "============================================================"
echo "🌐 Gateway will start on http://127.0.0.1:5000"
echo "🧠 Using RunPod Serverless: qm6ofmy96f3htl"
echo "🎨 Model: Flux Dev FP8"
echo "🔧 POD Pipeline: Available at /pod-pipeline.py"
echo "📁 Output dir: $PROJECT_DIR/output"
echo "============================================================"
echo ""

# Optional: Run POD proof-of-life on startup if PROOF_OF_LIFE=true
if [ "${PROOF_OF_LIFE:-false}" = "true" ]; then
    echo "🚀 Running POD Proof of Life on startup..."
    (
        sleep 10  # Wait for gateway to be ready
        python3 ../pod-pipeline.py --theme "vibrant abstract art" --output /tmp/pod-proof-of-life.json &
    )
fi

echo "Press Ctrl+C to stop"
echo ""
echo "💡 Tip: Run POD pipeline manually with:"
echo "   python3 pod-pipeline.py --theme 'your theme here'"
echo ""

cd gateway
PYTHONPATH=$(pwd) python3 -m app.main
