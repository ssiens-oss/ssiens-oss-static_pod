#!/bin/bash
set -e

RUNPOD_HOST="nfre49elqpt6su-64411157@ssh.runpod.io"
RUNPOD_KEY="$HOME/.ssh/id_ed25519"

echo "╔════════════════════════════════════════════════════╗"
echo "║  Deploying to RunPod...                           ║"
echo "╚════════════════════════════════════════════════════╝"

echo "📦 Creating archive..."
tar czf /tmp/pod-deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='dist' \
  .

echo "📁 Creating remote directory..."
ssh -i "$RUNPOD_KEY" "$RUNPOD_HOST" "mkdir -p /workspace/app"

echo "📤 Transferring files..."
scp -i "$RUNPOD_KEY" /tmp/pod-deploy.tar.gz "$RUNPOD_HOST:/tmp/"

echo "📂 Extracting on RunPod..."
ssh -i "$RUNPOD_KEY" "$RUNPOD_HOST" "cd /workspace/app && tar xzf /tmp/pod-deploy.tar.gz"

echo "🔐 Creating .env file..."
ssh -i "$RUNPOD_KEY" "$RUNPOD_HOST" "cat > /workspace/app/.env" << 'EOF'
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output
ANTHROPIC_API_KEY=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
CLAUDE_MODEL=claude-3-5-sonnet-20241022
STORAGE_TYPE=local
STORAGE_PATH=/data/designs
PRINTIFY_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjkwMTBmZSIsImp0aSI6IjBiOTg1ZDk1OWU4YmY5MGEzNzg3ZWY3MzMxNTdlMmU5OWFiOWQ3NjI3MjM2NTI1MTM0YTQyYzIyYmYzOGZjMzQ5M2Y5ZDVkOWI5YjQ5OWUzIiwiaWF0IjoxNzM1Mzk1MDk4LjM2MjUzNSwibmJmIjoxNzM1Mzk1MDk4LjM2MjUzOCwiZXhwIjoxNzY2OTMxMDk4LjM0MTE3MSwic3ViIjoiMjA1NTQ3ODciLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwicHJvZHVjdHMudGVtcGxhdGVzLnJlYWQiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.Bkf3Tn_zf0EiD1hUahkL9wOT3_hKLPAg1Oi-uL0Br_6w5LdOhV99p_ZSGQ8ewjPIbpyj4lHZRQxIBkqCQZ9zyMY0AMrbU3FaMGWsN0N9t88WVlVALCX9e8HU9fQx1SbHwEOKsYWBsqxJDpGrHHgvbCT1ghiP51RsVtLEX0OkIOBDXIbTMl5exPj14m13Qv9TjNfD5iBGgf5KBVpgZb1HZDVU_0r5HVa9QQZ8d83RQ1SL_7_1VZzww8YeIZ0Nl7qc0SKmvqfaHVCJCdYYdFuWx_sWOTGq2lO_lzKCqW0tqkHFACy-RnO_MjdHvgBlmz8NdEEqAw6PKDjz4D7aUXMmrw
PRINTIFY_SHOP_ID=25860767
AUTO_PUBLISH=true
ENABLE_PLATFORMS=printify
EOF

echo "📦 Installing dependencies..."
ssh -i "$RUNPOD_KEY" "$RUNPOD_HOST" "cd /workspace/app && npm install"

rm /tmp/pod-deploy.tar.gz

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  ✅ Deployment Complete!                          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next: SSH to RunPod and test:"
echo "  ssh -i ~/.ssh/id_ed25519 $RUNPOD_HOST"
echo "  cd /workspace/app"
echo "  npm run pipeline:single -- --help"
