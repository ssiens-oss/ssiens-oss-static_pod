#!/bin/bash
###############################################################################
# Test RunPod Serverless Pipeline
# Tests the complete workflow: Generate → Download → Display → Approve → Publish
###############################################################################

set -e

GATEWAY_URL="http://localhost:5000"
IMAGE_DIR="$HOME/ssiens-oss-static_pod/gateway/data/images"

echo "════════════════════════════════════════════════════════════════════"
echo "  RunPod Serverless Pipeline Test"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Check if gateway is running
echo "1. Checking if POD Gateway is running..."
if curl -s "${GATEWAY_URL}/health" > /dev/null 2>&1; then
    echo "✓ Gateway is running at ${GATEWAY_URL}"
else
    echo "✗ Gateway is not running!"
    echo ""
    echo "Start the gateway first:"
    echo "  cd ~/ssiens-oss-static_pod/gateway"
    echo "  export PYTHONPATH=\$(pwd)"
    echo "  .venv/bin/python app/main.py"
    exit 1
fi

# Check current images
echo ""
echo "2. Checking current images in gallery..."
IMAGE_COUNT_BEFORE=$(ls -1 "$IMAGE_DIR"/*.png 2>/dev/null | wc -l)
echo "✓ Found ${IMAGE_COUNT_BEFORE} image(s) in gallery"

# Test generation
echo ""
echo "3. Testing image generation via RunPod serverless..."
echo "   Prompt: 'cyberpunk cat wearing sunglasses, neon lights'"
echo ""

RESPONSE=$(curl -s -X POST "${GATEWAY_URL}/api/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "cyberpunk cat wearing sunglasses, neon lights, futuristic city",
        "steps": 20,
        "width": 1024,
        "height": 1024
    }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check status
STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

if [ "$STATUS" = "completed" ]; then
    echo "✓ Workflow completed successfully!"

    # Check if images were downloaded
    echo ""
    echo "4. Checking if images were downloaded..."
    sleep 2  # Give it a moment

    IMAGE_COUNT_AFTER=$(ls -1 "$IMAGE_DIR"/*.png 2>/dev/null | wc -l)
    NEW_IMAGES=$((IMAGE_COUNT_AFTER - IMAGE_COUNT_BEFORE))

    if [ $NEW_IMAGES -gt 0 ]; then
        echo "✓ Downloaded ${NEW_IMAGES} new image(s)!"
        echo ""
        echo "Latest images:"
        ls -lt "$IMAGE_DIR"/*.png | head -n $NEW_IMAGES
    else
        echo "✗ No new images found"
        echo ""
        echo "Check the gateway terminal for error messages"
        exit 1
    fi

elif [ "$STATUS" = "IN_PROGRESS" ] || [ "$STATUS" = "IN_QUEUE" ]; then
    echo "⏳ Workflow is processing asynchronously..."
    PROMPT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt_id', ''))" 2>/dev/null || echo "")

    if [ -n "$PROMPT_ID" ]; then
        echo "   Prompt ID: $PROMPT_ID"
        echo ""
        echo "Check status with:"
        echo "   curl ${GATEWAY_URL}/api/generation_status?prompt_id=${PROMPT_ID}"
    fi

else
    echo "✗ Workflow failed or returned unknown status: $STATUS"
    exit 1
fi

# Test gallery API
echo ""
echo "5. Testing gallery API..."
GALLERY_RESPONSE=$(curl -s "${GATEWAY_URL}/api/images")
GALLERY_COUNT=$(echo "$GALLERY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo "0")
echo "✓ Gallery showing ${GALLERY_COUNT} image(s)"

# Test stats API
echo ""
echo "6. Testing stats API..."
STATS=$(curl -s "${GATEWAY_URL}/api/stats")
echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Test Complete!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Open ${GATEWAY_URL} in your browser"
echo "  2. View the generated image in the gallery"
echo "  3. Click 'Approve' on the image"
echo "  4. Click 'Publish' to send to Printify"
echo ""
echo "Full pipeline:"
echo "  Generate (RunPod) → Download → Gallery → Approve → Publish (Printify)"
echo ""
