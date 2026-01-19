#!/bin/bash
# Quick Fix: Update .env with RunPod ComfyUI URL
# This script automatically updates COMFYUI_API_URL to use your RunPod endpoint

set -e

echo "🔧 Fixing RunPod ComfyUI URL in .env"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Read current RunPod Pod ID
RUNPOD_POD_ID=$(grep "^RUNPOD_POD_ID=" .env | cut -d'=' -f2)

if [ -z "$RUNPOD_POD_ID" ]; then
    echo "❌ Error: RUNPOD_POD_ID not set in .env"
    echo ""
    echo "Please set your RunPod Pod ID in .env:"
    echo "  RUNPOD_POD_ID=your-pod-id-here"
    exit 1
fi

echo "📋 Found Pod ID: $RUNPOD_POD_ID"
echo ""

# Construct RunPod URL
# RunPod proxy format: https://{POD_ID}-{PORT}.proxy.runpod.net
RUNPOD_URL="https://${RUNPOD_POD_ID}-8188.proxy.runpod.net"

echo "🔗 New ComfyUI URL: $RUNPOD_URL"
echo ""

# Backup .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "💾 Backed up .env"

# Update COMFYUI_API_URL
if grep -q "^COMFYUI_API_URL=" .env; then
    # Replace existing line
    sed -i "s|^COMFYUI_API_URL=.*|COMFYUI_API_URL=${RUNPOD_URL}|" .env
    echo "✅ Updated COMFYUI_API_URL in .env"
else
    # Add new line
    echo "COMFYUI_API_URL=${RUNPOD_URL}" >> .env
    echo "✅ Added COMFYUI_API_URL to .env"
fi

echo ""
echo "📝 Updated Configuration:"
grep "^COMFYUI_API_URL=" .env
echo ""

# Test connectivity
echo "🔌 Testing connection to RunPod ComfyUI..."
if curl -s --max-time 10 "${RUNPOD_URL}/system_stats" > /dev/null 2>&1; then
    echo "✅ SUCCESS! ComfyUI is reachable at RunPod"
    echo ""
    echo "🎉 You're all set! Generation should now work."
else
    echo "⚠️  WARNING: Cannot connect to ${RUNPOD_URL}"
    echo ""
    echo "This could mean:"
    echo "  1. Your RunPod pod is stopped (start it in RunPod dashboard)"
    echo "  2. ComfyUI is not running inside the pod"
    echo "  3. Port 8188 is not exposed"
    echo "  4. The URL format is different for your pod"
    echo ""
    echo "🔍 To diagnose:"
    echo "  1. Check RunPod dashboard: https://www.runpod.io/console/pods"
    echo "  2. Ensure your pod is running"
    echo "  3. Check pod logs for ComfyUI errors"
    echo "  4. Try accessing $RUNPOD_URL in your browser"
    echo ""
    echo "📞 Alternative URL formats to try:"
    echo "  - https://${RUNPOD_POD_ID}.proxy.runpod.net:8188"
    echo "  - Check RunPod dashboard for the exact HTTP endpoint"
fi

echo ""
echo "💡 Next steps:"
echo "  1. Verify your RunPod pod is running"
echo "  2. Restart the gateway: cd gateway && python app/main.py"
echo "  3. Try generating an image"
echo ""
