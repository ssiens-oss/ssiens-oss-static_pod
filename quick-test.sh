#!/bin/bash
###############################################################################
# Quick Gateway Test - Run this after starting the gateway
###############################################################################

echo "Testing POD Gateway..."
echo ""

# Test 1: Health check
echo "1. Health check..."
curl -s http://localhost:5000/health && echo " ✓" || echo " ✗"
echo ""

# Test 2: Generate image
echo "2. Submitting generation request..."
echo "   Prompt: 'cyberpunk cat wearing sunglasses'"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cat wearing sunglasses, neon lights",
    "steps": 20,
    "width": 1024,
    "height": 1024
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if completed
if echo "$RESPONSE" | grep -q '"status": "completed"'; then
    echo "✅ SUCCESS! Image generated and downloaded!"
    echo ""
    echo "Generated images:"
    echo "$RESPONSE" | python3 -c "import sys, json; print('\n'.join(json.load(sys.stdin).get('images', [])))" 2>/dev/null
    echo ""
    echo "View at: http://localhost:5000"
elif echo "$RESPONSE" | grep -q "prompt_id"; then
    echo "⏳ Generation submitted to RunPod"
    echo "   Check RunPod dashboard for progress"
else
    echo "⚠️  Check response above"
fi
echo ""
