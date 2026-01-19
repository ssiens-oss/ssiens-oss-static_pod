#!/bin/bash
# Quick setup for RunPod Serverless ComfyUI
set -e

echo "🚀 RunPod Serverless Setup"
echo "=========================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Ask for endpoint ID
read -p "Enter your RunPod Serverless Endpoint ID (e.g., gm6ofmy96f3htl): " ENDPOINT_ID
if [ -z "$ENDPOINT_ID" ]; then
    echo "❌ Endpoint ID is required"
    exit 1
fi

# Ask for API key (optional but recommended)
read -p "Enter your RunPod API Key (optional, press Enter to skip): " API_KEY

# Construct endpoint URL
ENDPOINT_URL="https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync"

echo ""
echo "📝 Configuration:"
echo "  Endpoint ID: $ENDPOINT_ID"
echo "  Endpoint URL: $ENDPOINT_URL"
if [ -n "$API_KEY" ]; then
    echo "  API Key: ${API_KEY:0:10}..."
fi
echo ""

# Backup .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "💾 Backed up .env"

# Update COMFYUI_API_URL
if grep -q "^COMFYUI_API_URL=" .env; then
    sed -i "s|^COMFYUI_API_URL=.*|COMFYUI_API_URL=${ENDPOINT_URL}|" .env
    echo "✅ Updated COMFYUI_API_URL"
else
    echo "COMFYUI_API_URL=${ENDPOINT_URL}" >> .env
    echo "✅ Added COMFYUI_API_URL"
fi

# Update RUNPOD_ENDPOINT_ID
if grep -q "^RUNPOD_ENDPOINT_ID=" .env; then
    sed -i "s|^RUNPOD_ENDPOINT_ID=.*|RUNPOD_ENDPOINT_ID=${ENDPOINT_ID}|" .env
    echo "✅ Updated RUNPOD_ENDPOINT_ID"
else
    echo "RUNPOD_ENDPOINT_ID=${ENDPOINT_ID}" >> .env
    echo "✅ Added RUNPOD_ENDPOINT_ID"
fi

# Update RUNPOD_API_KEY if provided
if [ -n "$API_KEY" ]; then
    if grep -q "^RUNPOD_API_KEY=" .env; then
        sed -i "s|^RUNPOD_API_KEY=.*|RUNPOD_API_KEY=${API_KEY}|" .env
        echo "✅ Updated RUNPOD_API_KEY"
    else
        echo "RUNPOD_API_KEY=${API_KEY}" >> .env
        echo "✅ Added RUNPOD_API_KEY"
    fi
fi

echo ""
echo "📋 Current configuration:"
grep -E "COMFYUI_API_URL|RUNPOD_ENDPOINT_ID|RUNPOD_API_KEY" .env
echo ""

# Test connectivity
echo "🔌 Testing connection to RunPod Serverless..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${ENDPOINT_URL}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${API_KEY}" \
    -d '{"input":{"workflow":{"prompt":"test"}}}' \
    --max-time 10 || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ SUCCESS! RunPod Serverless is reachable"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "⚠️  WARNING: Authentication failed (check API key)"
    echo "   But endpoint is reachable"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "⚠️  WARNING: Connection timeout"
    echo "   Endpoint might be cold starting or unreachable"
else
    echo "⚠️  WARNING: HTTP $HTTP_CODE"
    echo "   Check endpoint ID and try again"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "💡 Next steps:"
echo "  1. cd gateway"
echo "  2. PYTHONPATH=. python3 app/main.py"
echo "  3. Open http://localhost:5000 in your browser"
echo "  4. Try generating an image!"
echo ""
