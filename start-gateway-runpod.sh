#!/bin/bash
# Complete setup and start script for POD Gateway with RunPod serverless
# This script fixes any merge conflicts, configures .env, and starts the gateway

set -e

# User-specific RunPod credentials
# TODO: After git pull, replace these placeholders with your actual RunPod values
# (I'll provide them separately - they can't be committed to git for security)
RUNPOD_ENDPOINT_ID="YOUR_ENDPOINT_ID_HERE"
RUNPOD_API_KEY="YOUR_API_KEY_HERE"

echo "🚀 POD Gateway - RunPod Serverless Setup"
echo "========================================"
echo ""

# Check if credentials are configured
if [ "$RUNPOD_ENDPOINT_ID" = "YOUR_ENDPOINT_ID_HERE" ] || [ "$RUNPOD_API_KEY" = "YOUR_API_KEY_HERE" ]; then
    echo "❌ ERROR: RunPod credentials not configured!"
    echo ""
    echo "Please edit this script (start-gateway-runpod.sh) at lines 11-12"
    echo "Replace the placeholder values with your actual RunPod credentials"
    echo "(See the comments on lines 9-10 for your specific values)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

cd ~/ssiens-oss-static_pod

# Step 1: Fix any merge conflicts
echo "1️⃣  Fixing merge conflicts..."
git merge --abort 2>/dev/null || true
git reset --hard HEAD 2>/dev/null || true
git fetch origin claude/review-changes-mkljilavyj0p92rc-yIHnQ
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/main.py 2>/dev/null || true
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/runpod_adapter.py 2>/dev/null || true
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/config.py 2>/dev/null || true
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- RUNPOD_SETUP.md 2>/dev/null || true
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
    echo "   ⚠️  .env.runpod-config not found!"
    echo ""
    echo "   Creating it now with configured credentials..."
    echo ""

    # Check if template exists
    if [ ! -f ".env.runpod-config.example" ]; then
        echo "   ❌ .env.runpod-config.example not found!"
        echo "   Please run: git pull origin claude/review-changes-mkljilavyj0p92rc-yIHnQ"
        exit 1
    fi

    # Copy template and fill in credentials from variables
    cp .env.runpod-config.example .env.runpod-config
    sed -i "s|YOUR_ENDPOINT_ID|${RUNPOD_ENDPOINT_ID}|g" .env.runpod-config
    sed -i "s|YOUR_RUNPOD_API_KEY|${RUNPOD_API_KEY}|g" .env.runpod-config

    echo "   ✅ .env.runpod-config created successfully"
    echo ""
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
echo "============================================================"
echo "🌐 Gateway will start on http://127.0.0.1:5000"
echo "🧠 Using RunPod Serverless: qm6ofmy96f3htl"
echo "🎨 Model: Flux Dev FP8"
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd gateway
PYTHONPATH=$(pwd) python3 -m app.main
