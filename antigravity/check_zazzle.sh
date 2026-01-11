#!/bin/bash
# Quick Zazzle validation - run this after editing .env

cd /home/user/ssiens-oss-static_pod/antigravity

echo "======================================"
echo "  Zazzle Configuration Check"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Source .env
source .env 2>/dev/null

echo "Checking credentials..."
echo ""

# Check for credentials
HAS_CRED=0

if [ -n "$ZAZZLE_ASSOCIATE_ID" ] && [ "$ZAZZLE_ASSOCIATE_ID" != "your-associate-id" ]; then
    echo "✅ Associate ID configured: ${ZAZZLE_ASSOCIATE_ID:0:12}..."
    HAS_CRED=1
fi

if [ -n "$ZAZZLE_API_KEY" ] && [ "$ZAZZLE_API_KEY" != "your-api-key" ]; then
    echo "✅ API Key configured: ${ZAZZLE_API_KEY:0:12}..."
    HAS_CRED=1
fi

if [ $HAS_CRED -eq 0 ]; then
    echo "❌ No Zazzle credentials configured!"
    echo ""
    echo "Edit .env and set either:"
    echo "  - ZAZZLE_ASSOCIATE_ID"
    echo "  - ZAZZLE_API_KEY"
    echo ""
    echo "Run: nano /home/user/ssiens-oss-static_pod/antigravity/.env"
    exit 1
fi

if [ -n "$ZAZZLE_STORE_ID" ] && [ "$ZAZZLE_STORE_ID" != "your-store-id" ]; then
    echo "✅ Store ID configured: $ZAZZLE_STORE_ID"
else
    echo "⚠️  Store ID not configured (optional)"
fi

echo ""
echo "======================================"
echo "  Running Full Validation"
echo "======================================"
echo ""

python3 validate_zazzle.py
