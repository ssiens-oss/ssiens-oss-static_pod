#!/bin/bash
#
# RunPod Serverless ComfyUI Test Script (Async with Polling)
# Usage: ./test-runpod-async.sh
#

set -e

# Load environment variables
if [ -f .env ]; then
  set -a
  source <(cat .env | grep -v '^#' | grep -v '^$' | sed 's/ *#.*$//')
  set +a
fi

# Check credentials
if [ -z "$RUNPOD_API_KEY" ] || [ -z "$RUNPOD_ENDPOINT_ID" ]; then
  echo "❌ Missing credentials"
  exit 1
fi

echo "🚀 Testing RunPod Serverless (Async Mode with Polling)"
echo ""
echo "✓ Endpoint: $RUNPOD_ENDPOINT_ID"
echo ""

BASE_URL="https://api.runpod.ai/v2/$RUNPOD_ENDPOINT_ID"

# Build workflow
read -r -d '' WORKFLOW << 'EOF' || true
{
  "input": {
    "workflow": {
      "3": {
        "inputs": {
          "seed": 12345,
          "steps": 20,
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
        "inputs": { "width": 1024, "height": 1024, "batch_size": 1 },
        "class_type": "EmptyLatentImage"
      },
      "6": {
        "inputs": {
          "text": "a majestic dragon flying over a medieval castle, fantasy art, highly detailed, 4k",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": {
          "text": "text, watermark, low quality, worst quality, blurry",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "8": {
        "inputs": { "samples": ["3", 0], "vae": ["4", 2] },
        "class_type": "VAEDecode"
      },
      "9": {
        "inputs": { "filename_prefix": "dragon", "images": ["8", 0] },
        "class_type": "SaveImage"
      }
    }
  }
}
EOF

# Submit job
echo "🎨 Submitting generation job..."
echo "   Prompt: 'dragon flying over castle'"
echo "   Size: 1024x1024, Steps: 20"
echo ""

SUBMIT_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -d "$WORKFLOW" \
  "$BASE_URL/run")

HTTP_CODE=$(echo "$SUBMIT_RESPONSE" | tail -n1)
BODY=$(echo "$SUBMIT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ Submission failed (HTTP $HTTP_CODE)"
  echo "$BODY"
  exit 1
fi

JOB_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "✅ Job submitted!"
echo "   Job ID: $JOB_ID"
echo ""

# Poll for completion
echo "⏳ Polling for completion (max 2 minutes)..."
echo ""

MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  sleep 2
  ATTEMPT=$((ATTEMPT + 1))

  STATUS_RESPONSE=$(curl -s \
    -H "Authorization: Bearer $RUNPOD_API_KEY" \
    "$BASE_URL/status/$JOB_ID")

  STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

  printf "   [%2d] Status: %-15s" "$ATTEMPT" "$STATUS"

  if [ "$STATUS" = "COMPLETED" ]; then
    echo " ✅"
    echo ""
    echo "🎉 Generation completed!"
    echo ""
    echo "Full response:"
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
    echo ""

    # Extract images
    IMAGES=$(echo "$STATUS_RESPONSE" | grep -o 'https://[^"]*\.png' | head -5)
    if [ -n "$IMAGES" ]; then
      echo "🖼️  Generated Images:"
      echo "$IMAGES" | nl -w2 -s'. '
    fi

    exit 0
  elif [ "$STATUS" = "FAILED" ]; then
    echo " ❌"
    echo ""
    echo "Generation failed!"
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
    exit 1
  else
    echo ""
  fi
done

echo ""
echo "⏱️  Timeout: Job did not complete in 2 minutes"
echo "   Job ID: $JOB_ID"
echo "   Check manually: $BASE_URL/status/$JOB_ID"
