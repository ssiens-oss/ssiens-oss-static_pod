#!/bin/bash
#
# RunPod Serverless ComfyUI Test Script
# Usage: ./test-runpod.sh
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
  echo "❌ Missing credentials in .env file"
  echo "   RUNPOD_API_KEY: ${RUNPOD_API_KEY:+✓ Set}${RUNPOD_API_KEY:-✗ Missing}"
  echo "   RUNPOD_ENDPOINT_ID: ${RUNPOD_ENDPOINT_ID:+✓ Set}${RUNPOD_ENDPOINT_ID:-✗ Missing}"
  exit 1
fi

echo "🚀 Testing RunPod Serverless ComfyUI"
echo ""
echo "✓ Credentials loaded:"
echo "  Endpoint ID: $RUNPOD_ENDPOINT_ID"
echo "  API Key: ${RUNPOD_API_KEY:0:20}..."
echo ""

BASE_URL="https://api.runpod.ai/v2/$RUNPOD_ENDPOINT_ID"

# Test 1: Health Check
echo "🏥 Test 1: Health Check"
echo "   GET $BASE_URL/health"
echo ""

HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $RUNPOD_API_KEY" "$BASE_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Health check passed!"
  echo "   Response: $BODY"
else
  echo "⚠️  Health check returned HTTP $HTTP_CODE"
  echo "   Response: $BODY"
fi

echo ""
echo ""

# Test 2: Image Generation with /runsync
echo "🎨 Test 2: Image Generation (Synchronous)"
echo "   POST $BASE_URL/runsync"
echo "   Generating: 'cyberpunk city at night, neon lights'"
echo "   Size: 512x512, Steps: 15"
echo "   This may take 30-60 seconds..."
echo ""

# Build ComfyUI workflow JSON
read -r -d '' WORKFLOW << 'EOF' || true
{
  "input": {
    "workflow": {
      "3": {
        "inputs": {
          "seed": 42,
          "steps": 15,
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
        "inputs": {
          "ckpt_name": "sd_xl_base_1.0.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
      },
      "5": {
        "inputs": {
          "width": 512,
          "height": 512,
          "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
      },
      "6": {
        "inputs": {
          "text": "cyberpunk city at night, neon lights, highly detailed digital art",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": {
          "text": "text, watermark, low quality, worst quality",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "8": {
        "inputs": {
          "samples": ["3", 0],
          "vae": ["4", 2]
        },
        "class_type": "VAEDecode"
      },
      "9": {
        "inputs": {
          "filename_prefix": "test",
          "images": ["8", 0]
        },
        "class_type": "SaveImage"
      }
    },
    "images": []
  }
}
EOF

# Make the request
GEN_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -d "$WORKFLOW" \
  "$BASE_URL/runsync")

HTTP_CODE=$(echo "$GEN_RESPONSE" | tail -n1)
BODY=$(echo "$GEN_RESPONSE" | sed '$d')

echo "📥 Response received!"
echo "   HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Generation successful!"
  echo ""
  echo "Response:"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
  echo ""

  # Extract image URLs
  IMAGES=$(echo "$BODY" | grep -o '"https://[^"]*\.png"' | tr -d '"' || echo "")

  if [ -n "$IMAGES" ]; then
    echo ""
    echo "🖼️  Generated Images:"
    echo "$IMAGES" | nl -w2 -s'. '
  fi
else
  echo "❌ Generation failed!"
  echo "   Response: $BODY"
fi

echo ""
echo "✅ Test completed!"
