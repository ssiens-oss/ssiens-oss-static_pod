#!/bin/bash

# Start POD Pipeline GUI
# This script launches the multi-platform POD pipeline web interface

echo "🚀 Starting POD Pipeline Studio..."
echo ""
echo "POD Pipeline GUI will be available at: http://localhost:5174"
echo ""
echo "Features:"
echo "  ✓ Multi-platform distribution (Shopify, TikTok, Etsy, Instagram, Facebook)"
echo "  ✓ AI-powered design generation with ComfyUI"
echo "  ✓ Claude prompt generation"
echo "  ✓ Real-time analytics dashboard"
echo "  ✓ Automated product creation"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev:pod
