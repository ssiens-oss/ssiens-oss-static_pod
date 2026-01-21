#!/bin/bash
# Direct gateway start with all environment variables
# Use this if start-gateway-runpod.sh has issues

# Load credentials from .env.runpod-config if it exists
if [ -f "../.env.runpod-config" ]; then
    source "../.env.runpod-config"
elif [ -f ".env.runpod-config" ]; then
    source ".env.runpod-config"
fi

# Require RUNPOD_API_KEY
if [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ RUNPOD_API_KEY not set!"
    echo "   Please set it in .env.runpod-config or export it"
    exit 1
fi

# Require COMFYUI_API_URL
if [ -z "$COMFYUI_API_URL" ]; then
    COMFYUI_API_URL="https://api.runpod.ai/v2/qm6ofmy96f3htl/runsync"
    echo "⚠️  Using default COMFYUI_API_URL: $COMFYUI_API_URL"
fi

# Detect home directory dynamically
USER_HOME=$(eval echo ~$USER)
PROJECT_DIR="$USER_HOME/ssiens-oss-static_pod"

cd "$PROJECT_DIR/gateway" && \
RUNPOD_API_KEY="$RUNPOD_API_KEY" \
COMFYUI_API_URL="$COMFYUI_API_URL" \
POD_IMAGE_DIR="$PROJECT_DIR/output" \
POD_STATE_FILE="$PROJECT_DIR/gateway/data/state.json" \
POD_ARCHIVE_DIR="$PROJECT_DIR/gateway/data/archive" \
PYTHONPATH=$(pwd) \
python3 -m app.main
