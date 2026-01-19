#!/bin/bash
# Check available models on RunPod ComfyUI
set -e

ENDPOINT_ID="${1:-}"
API_KEY="${2:-}"

if [ -z "$ENDPOINT_ID" ]; then
    echo "Usage: $0 <endpoint-id> [api-key]"
    echo "Example: $0 gm6ofmy96f3htl rpa_YOUR_KEY"
    exit 1
fi

ENDPOINT_URL="https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync"

echo "🔍 Checking available models on RunPod ComfyUI"
echo "=============================================="
echo "Endpoint: $ENDPOINT_URL"
echo ""

# Minimal workflow to test model loading
PAYLOADS=(
  # Test 1: SDXL base model
  '{"input":{"workflow":{"4":{"inputs":{"ckpt_name":"sd_xl_base_1.0.safetensors"},"class_type":"CheckpointLoaderSimple"},"5":{"inputs":{"width":512,"height":512,"batch_size":1},"class_type":"EmptyLatentImage"}}}}'

  # Test 2: Alternative SDXL name
  '{"input":{"workflow":{"4":{"inputs":{"ckpt_name":"sd_xl_base.safetensors"},"class_type":"CheckpointLoaderSimple"},"5":{"inputs":{"width":512,"height":512,"batch_size":1},"class_type":"EmptyLatentImage"}}}}'

  # Test 3: Check if SD 1.5 is available
  '{"input":{"workflow":{"4":{"inputs":{"ckpt_name":"v1-5-pruned-emaonly.safetensors"},"class_type":"CheckpointLoaderSimple"},"5":{"inputs":{"width":512,"height":512,"batch_size":1},"class_type":"EmptyLatentImage"}}}}'
)

CURL_OPTS="-s -X POST '$ENDPOINT_URL' -H 'Content-Type: application/json'"
if [ -n "$API_KEY" ]; then
    CURL_OPTS="$CURL_OPTS -H 'Authorization: Bearer $API_KEY'"
fi
CURL_OPTS="$CURL_OPTS --max-time 120"

echo "Testing model: sd_xl_base_1.0.safetensors..."
RESPONSE=$(eval curl $CURL_OPTS -d "'${PAYLOADS[0]}'" 2>&1)
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20 || echo "$RESPONSE" | head -20
echo ""
