#!/bin/bash
# Get RunPod ComfyUI Endpoint URL
# This script queries the RunPod API to get your pod's correct endpoint URL

set -e

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# Check for required variables
if [ -z "$RUNPOD_POD_ID" ]; then
    echo "❌ Error: RUNPOD_POD_ID not set in .env"
    exit 1
fi

if [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ Error: RUNPOD_API_KEY not set in .env"
    exit 1
fi

echo "🔍 Fetching RunPod endpoint for pod: $RUNPOD_POD_ID"
echo ""

# Query RunPod API for pod details
RESPONSE=$(curl -s -X POST "https://api.runpod.io/graphql" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
    -d '{
        "query": "query Pod { pod(input: { podId: \"'"${RUNPOD_POD_ID}"'\" }) { id name runtime { ports { ip isIpPublic privatePort publicPort type } } } }"
    }')

echo "API Response:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Try to extract ComfyUI port (8188)
COMFYUI_URL=$(echo "$RESPONSE" | jq -r '.data.pod.runtime.ports[] | select(.privatePort == 8188) | "https://" + .publicPort + "-8188.proxy.runpod.net"' 2>/dev/null || echo "")

if [ -z "$COMFYUI_URL" ]; then
    echo "⚠️  Could not find port 8188 in pod configuration"
    echo ""
    echo "Available ports:"
    echo "$RESPONSE" | jq -r '.data.pod.runtime.ports[]?' 2>/dev/null || echo "No ports found"
    echo ""
    echo "📝 Manual URL Format:"
    echo "   https://${RUNPOD_POD_ID}-8188.proxy.runpod.net"
    echo "   or"
    echo "   https://${RUNPOD_POD_ID}.proxy.runpod.net:8188"
    echo ""
    COMFYUI_URL="https://${RUNPOD_POD_ID}-8188.proxy.runpod.net"
fi

echo "✅ ComfyUI Endpoint:"
echo "   $COMFYUI_URL"
echo ""

# Test connectivity
echo "🔌 Testing connectivity..."
if curl -s --max-time 10 "${COMFYUI_URL}/system_stats" > /dev/null 2>&1; then
    echo "✅ ComfyUI is reachable!"
else
    echo "⚠️  Cannot reach ComfyUI at ${COMFYUI_URL}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure your RunPod pod is running"
    echo "  2. Check that port 8188 is exposed in pod settings"
    echo "  3. Verify ComfyUI is running inside the pod"
    echo "  4. Try accessing the URL in a browser"
fi

echo ""
echo "📝 To update your configuration:"
echo "   Edit .env and set:"
echo "   COMFYUI_API_URL=${COMFYUI_URL}"
echo ""
