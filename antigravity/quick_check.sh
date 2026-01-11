#!/bin/bash

echo "=================================================="
echo "  ZAZZLE CONFIGURATION VERIFICATION"
echo "=================================================="
echo ""

# Source .env file
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found"
    exit 1
fi

echo "📋 Credentials Status:"
echo ""

# Check Associate ID
if [ -n "$ZAZZLE_ASSOCIATE_ID" ] && [ "$ZAZZLE_ASSOCIATE_ID" != "your-associate-id" ]; then
    echo "  ✅ Ambassador ID: $ZAZZLE_ASSOCIATE_ID"
else
    echo "  ❌ Ambassador ID: Not configured"
fi

# Check Store ID
if [ -n "$ZAZZLE_STORE_ID" ] && [ "$ZAZZLE_STORE_ID" != "your-store-id" ]; then
    echo "  ✅ Store ID: $ZAZZLE_STORE_ID"
else
    echo "  ❌ Store ID: Not configured"
fi

# Check API Key (optional)
if [ -n "$ZAZZLE_API_KEY" ] && [ "$ZAZZLE_API_KEY" != "your-api-key" ]; then
    echo "  ⚠️  API Key: ${ZAZZLE_API_KEY:0:12}... (optional)"
else
    echo "  ⚠️  API Key: Not configured (optional for most operations)"
fi

echo ""
echo "⚙️  Configuration:"
echo "  • Default Template: ${ZAZZLE_DEFAULT_TEMPLATE:-tshirt_basic}"
echo "  • Zazzle Enabled: ${ENABLE_ZAZZLE:-true}"
echo ""

# Generate store URL
if [ -n "$ZAZZLE_STORE_ID" ] && [ "$ZAZZLE_STORE_ID" != "your-store-id" ]; then
    echo "🔗 Your Zazzle Store:"
    echo "  https://www.zazzle.com/store/$ZAZZLE_STORE_ID"
    echo ""
fi

# Check AI API keys
echo "🤖 AI Model APIs (required for orchestration):"
echo ""

if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "sk-..." ]; then
    echo "  ✅ OpenAI API Key: Configured"
else
    echo "  ❌ OpenAI API Key: Not configured"
fi

if [ -n "$ANTHROPIC_API_KEY" ] && [ "$ANTHROPIC_API_KEY" != "sk-ant-..." ]; then
    echo "  ✅ Anthropic API Key: Configured"
else
    echo "  ❌ Anthropic API Key: Not configured"
fi

if [ -n "$GROK_API_KEY" ]; then
    echo "  ⚠️  Grok API Key: Configured (currently using mock)"
else
    echo "  ⚠️  Grok API Key: Not configured (optional, using mock)"
fi

echo ""
echo "=================================================="

# Provide next steps
if [ -n "$ZAZZLE_ASSOCIATE_ID" ] && [ "$ZAZZLE_ASSOCIATE_ID" != "your-associate-id" ] && [ -n "$ZAZZLE_STORE_ID" ] && [ "$ZAZZLE_STORE_ID" != "your-store-id" ]; then
    echo "✅ ZAZZLE CREDENTIALS CONFIGURED!"
    echo ""
    echo "Next steps:"
    echo "  1. Wait for 'pip install' to complete (installing PyTorch...)"
    echo ""
    echo "  2. Install Playwright browsers:"
    echo "     python3 -m playwright install"
    echo ""
    echo "  3. Test with dry run:"
    echo "     python3 -m antigravity.zazzle_cli design your_design.png --dry-run --product-type tshirt"
    echo ""
else
    echo "⚠️  Please configure your Zazzle credentials in .env"
    echo "   See ../ZAZZLE_QUICKSTART.md for instructions"
fi

echo "=================================================="
