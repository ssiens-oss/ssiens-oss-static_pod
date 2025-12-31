#!/bin/bash

# Quick test script for music generation
# Tests the API without requiring GPU

set -e

echo "🧪 StaticWaves Music Engine - Quick Test"
echo "========================================"
echo ""

API_URL="${1:-http://localhost:8000}"

echo "Testing API at: $API_URL"
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s "$API_URL/health" || echo "")

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "Make sure services are running: cd music-engine && docker-compose up"
    exit 1
fi

# Test 2: Generate music
echo ""
echo "2️⃣ Generating test music..."

SPEC='{
  "bpm": 120,
  "key": "C minor",
  "duration": 10,
  "vibe": {
    "energy": 0.7,
    "dark": 0.5,
    "dreamy": 0.3,
    "aggressive": 0.2
  },
  "genre_mix": {
    "synthwave": 0.6,
    "lofi": 0.4
  },
  "instruments": {
    "bass": "analog_mono",
    "lead": "supersaw",
    "pad": "granular_pad",
    "drums": "808"
  },
  "stems": false
}'

RESPONSE=$(curl -s -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d "$SPEC")

JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to generate music"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Job created: $JOB_ID"

# Test 3: Poll status
echo ""
echo "3️⃣ Waiting for completion..."

MAX_WAIT=60
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS=$(curl -s "$API_URL/status/$JOB_ID")
    STATE=$(echo "$STATUS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    PROGRESS=$(echo "$STATUS" | grep -o '"progress":[0-9.]*' | cut -d':' -f2)

    echo "Status: $STATE ($PROGRESS%)"

    if [ "$STATE" = "completed" ]; then
        echo "✅ Music generation completed!"
        echo ""
        echo "Download URL: $API_URL/download/$JOB_ID/mix"
        echo ""
        echo "🎉 All tests passed!"
        exit 0
    elif [ "$STATE" = "failed" ]; then
        echo "❌ Music generation failed"
        echo "Response: $STATUS"
        exit 1
    fi

    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

echo "⚠️  Timeout waiting for completion"
echo "Job may still be processing. Check: $API_URL/status/$JOB_ID"
exit 1
