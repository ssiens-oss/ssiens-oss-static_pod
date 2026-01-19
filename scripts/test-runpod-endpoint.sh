#!/bin/bash
# Test RunPod Serverless endpoint and show detailed response
set -e

ENDPOINT_ID="${1:-}"
API_KEY="${2:-}"

if [ -z "$ENDPOINT_ID" ]; then
    echo "Usage: $0 <endpoint-id> [api-key]"
    echo "Example: $0 gm6ofmy96f3htl rpa_YOUR_KEY"
    exit 1
fi

ENDPOINT_URL="https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync"

echo "🧪 Testing RunPod Serverless Endpoint"
echo "====================================="
echo "Endpoint: $ENDPOINT_URL"
echo ""

# Simple test payload
PAYLOAD='{
  "input": {
    "prompt": {
      "3": {
        "inputs": {
          "seed": 42,
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
          "text": "test image",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": {
          "text": "blurry",
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
          "filename_prefix": "ComfyUI",
          "images": ["8", 0]
        },
        "class_type": "SaveImage"
      }
    }
  }
}'

echo "📤 Sending test workflow..."
echo ""

# Build curl command
CURL_CMD="curl -s -X POST '$ENDPOINT_URL'"
CURL_CMD="$CURL_CMD -H 'Content-Type: application/json'"

if [ -n "$API_KEY" ]; then
    CURL_CMD="$CURL_CMD -H 'Authorization: Bearer $API_KEY'"
fi

CURL_CMD="$CURL_CMD -d '$PAYLOAD'"
CURL_CMD="$CURL_CMD --max-time 120"

# Execute and capture response
RESPONSE=$(eval $CURL_CMD)

echo "📥 Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check status
STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")

if [ "$STATUS" = "COMPLETED" ]; then
    echo "✅ Success! Endpoint is working"
elif [ "$STATUS" = "FAILED" ]; then
    echo "❌ Failed! Check error message above"
    ERROR=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "Unknown")
    echo "Error: $ERROR"
else
    echo "⚠️  Status: $STATUS"
fi
