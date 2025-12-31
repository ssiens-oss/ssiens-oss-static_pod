#!/bin/bash
set -e

RUNPOD_HOST="nfre49elqpt6su-64411157@ssh.runpod.io"
RUNPOD_KEY="$HOME/.ssh/id_ed25519"

echo "╔════════════════════════════════════════════════════╗"
echo "║  Deploying to RunPod (tar over SSH)               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Create remote directory
echo "📁 Creating remote directory..."
ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "mkdir -p /workspace/ssiens-oss-static_pod" 2>&1 | grep -v "RUNPOD" || true

echo "📦 Transferring files via tar over SSH..."
tar czf - \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='dist' \
  --exclude='*.log' \
  . | ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "cd /workspace/ssiens-oss-static_pod && tar xzf -" 2>&1 | grep -v "RUNPOD" || true

echo "✓ Files transferred!"
echo ""

# Create .env file
echo "🔐 Creating .env file..."
cat << 'ENVEOF' | ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "cat > /workspace/ssiens-oss-static_pod/.env" 2>&1 | grep -v "RUNPOD" || true
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
ENVEOF

echo "✓ .env created!"
echo ""

# Create pipeline/.env file with TikTok shop settings
echo "🔐 Creating pipeline/.env file..."
cat << 'PIPELINEENVEOF' | ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "cat > /workspace/ssiens-oss-static_pod/pipeline/.env" 2>&1 | grep -v "RUNPOD" || true
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output
STORAGE_TYPE=local
STORAGE_PATH=/data/designs
PRINTIFY_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjkwMTBmZSIsImp0aSI6IjBiOTg1ZDk1OWU4YmY5MGEzNzg3ZWY3MzMxNTdlMmU5OWFiOWQ3NjI3MjM2NTI1MTM0YTQyYzIyYmYzOGZjMzQ5M2Y5ZDVkOWI5YjQ5OWUzIiwiaWF0IjoxNzM1Mzk1MDk4LjM2MjUzNSwibmJmIjoxNzM1Mzk1MDk4LjM2MjUzOCwiZXhwIjoxNzY2OTMxMDk4LjM0MTE3MSwic3ViIjoiMjA1NTQ3ODciLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwicHJvZHVjdHMudGVtcGxhdGVzLnJlYWQiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.Bkf3Tn_zf0EiD1hUahkL9wOT3_hKLPAg1Oi-uL0Br_6w5LdOhV99p_ZSGQ8ewjPIbpyj4lHZRQxIBkqCQZ9zyMY0AMrbU3FaMGWsN0N9t88WVlVALCX9e8HU9fQx1SbHwEOKsYWBsqxJDpGrHHgvbCT1ghiP51RsVtLEX0OkIOBDXIbTMl5exPj14m13Qv9TjNfD5iBGgf5KBVpgZb1HZDVU_0r5HVa9QQZ8d83RQ1SL_7_1VZzww8YeIZ0Nl7qc0SKmvqfaHVCJCdYYdFuWx_sWOTGq2lO_lzKCqW0tqkHFACy-RnO_MjdHvgBlmz8NdEEqAw6PKDjz4D7aUXMmrw
PRINTIFY_SHOP_ID=25864831
PIPELINEENVEOF

echo "✓ pipeline/.env created!"
echo ""

# Install dependencies
echo "📦 Installing dependencies (this may take a minute)..."
ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "cd /workspace/ssiens-oss-static_pod && npm install" 2>&1 | grep -v "RUNPOD" || true

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  ✅ Deployment Complete!                          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. SSH: ssh -i ~/.ssh/id_ed25519 $RUNPOD_HOST"
echo "  2. Test: cd /workspace/ssiens-oss-static_pod && node scripts/tiktok-preflight-test.cjs"
echo ""
