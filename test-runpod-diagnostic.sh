#!/bin/bash
#
# RunPod Serverless Diagnostic Test
# Shows full API responses for debugging
#

set -e

# Load .env
if [ -f .env ]; then
  set -a
  source <(cat .env | grep -v '^#' | grep -v '^$' | sed 's/ *#.*$//')
  set +a
fi

echo "🔍 RunPod Serverless Diagnostic Test"
echo "===================================="
echo ""
echo "Endpoint: $RUNPOD_ENDPOINT_ID"
echo ""

BASE_URL="https://api.runpod.ai/v2/$RUNPOD_ENDPOINT_ID"

# Minimal workflow for testing
read -r -d '' WORKFLOW << 'EOF' || true
{
  "input": {
    "workflow": {
      "3": {
        "inputs": {
          "seed": 999,
          "steps": 10,
          "cfg": 7,
          "sampler_name": "euler",
          "scheduler": "normal",
          "denoise": 1,
          "model": ["4", 0],
          "positive": ["6", 0],
          "negative": ["7", 0],
          "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
      },
      "4": {
        "inputs": { "ckpt_name": "sd_xl_base_1.0.safetensors" },
        "class_type": "CheckpointLoaderSimple"
      },
      "5": {
        "inputs": { "width": 512, "height": 512, "batch_size": 1 },
        "class_type": "EmptyLatentImage"
      },
      "6": {
        "inputs": { "text": "a red apple on white background", "clip": ["4", 1] },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": { "text": "bad quality", "clip": ["4", 1] },
        "class_type": "CLIPTextEncode"
      },
      "8": {
        "inputs": { "samples": ["3", 0], "vae": ["4", 2] },
        "class_type": "VAEDecode"
      },
      "9": {
        "inputs": { "filename_prefix": "test", "images": ["8", 0] },
        "class_type": "SaveImage"
      }
    }
  }
}
EOF

echo "📤 Submitting test job..."
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -d "$WORKFLOW" \
  "$BASE_URL/run")

echo "Response from /run:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

JOB_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Job ID: $JOB_ID"
echo ""

# Wait a bit
echo "⏳ Waiting 5 seconds..."
sleep 5
echo ""

# Check status
echo "📥 Checking status..."
STATUS_RESPONSE=$(curl -s \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  "$BASE_URL/status/$JOB_ID")

echo "Full status response:"
echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
echo ""

# Parse status
STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Status: $STATUS"
echo ""

# Check if output field exists
HAS_OUTPUT=$(echo "$STATUS_RESPONSE" | grep -c '"output"' || true)
echo "Has 'output' field: $HAS_OUTPUT"
echo ""

if [ "$HAS_OUTPUT" -gt 0 ]; then
  echo "Output field content:"
  echo "$STATUS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('output'), indent=2))" 2>/dev/null || echo "Could not parse output"
else
  echo "⚠️  No 'output' field in response"
  echo ""
  echo "This suggests your RunPod Serverless handler needs to return output."
  echo "Check your handler code to ensure it returns:"
  echo '  return {"images": ["url1", "url2", ...]}'
fi
