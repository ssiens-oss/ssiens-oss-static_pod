#!/bin/bash
# Quick Printify setup script

echo "🖨️  Printify Setup"
echo "=================="
echo ""
echo "You need two things from Printify:"
echo ""
echo "1. API Key"
echo "   📍 Get it here: https://printify.com/app/account/api"
echo "   - Log in to Printify"
echo "   - Go to My Account → Connections → API"
echo "   - Click 'Generate Token'"
echo "   - Copy the token"
echo ""
echo "2. Shop ID"
echo "   📍 Get it here: https://printify.com/app/account/api"
echo "   - Same page as API key"
echo "   - Look for 'Shop ID' (numeric value)"
echo "   - Copy the number"
echo ""

read -p "Do you have your Printify API key and Shop ID? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "ℹ️  Get your credentials first, then run this script again:"
    echo "   ./setup-printify.sh"
    exit 0
fi

echo ""
read -p "Enter your Printify API Key: " API_KEY
read -p "Enter your Printify Shop ID: " SHOP_ID

if [ -z "$API_KEY" ] || [ -z "$SHOP_ID" ]; then
    echo "❌ Both API Key and Shop ID are required"
    exit 1
fi

# Update .env.runpod-config
CONFIG_FILE=".env.runpod-config"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ $CONFIG_FILE not found"
    exit 1
fi

# Use sed to update the values
sed -i "s|^PRINTIFY_API_KEY=.*|PRINTIFY_API_KEY=$API_KEY|" "$CONFIG_FILE"
sed -i "s|^PRINTIFY_SHOP_ID=.*|PRINTIFY_SHOP_ID=$SHOP_ID|" "$CONFIG_FILE"

echo ""
echo "✅ Printify credentials saved to $CONFIG_FILE"
echo ""
echo "📊 Configuration:"
echo "   API Key: ${API_KEY:0:20}..."
echo "   Shop ID: $SHOP_ID"
echo ""
echo "🚀 Next steps:"
echo "   1. Restart gateway: ./start-gateway-direct.sh"
echo "   2. Test publishing to Printify"
echo ""
