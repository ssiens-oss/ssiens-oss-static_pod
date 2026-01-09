#!/bin/bash
# Quick POD Pipeline verification test

echo "🧪 Testing POD Pipeline..."
echo ""

# Test 1: Gallery API
echo -n "1. Gallery API (port 8099)... "
if curl -s -f http://localhost:8099/ > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAILED"
    exit 1
fi

# Test 2: Designs endpoint
echo -n "2. Designs endpoint... "
DESIGN_COUNT=$(curl -s http://localhost:8099/designs | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ -n "$DESIGN_COUNT" ]; then
    echo "✅ WORKING ($DESIGN_COUNT designs)"
else
    echo "❌ FAILED"
    exit 1
fi

# Test 3: Web UI
echo -n "3. Web UI (port 8088)... "
if curl -s -f http://localhost:8088/view-gallery.html > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAILED"
    exit 1
fi

# Test 4: Static image serving
echo -n "4. Image serving... "
if curl -s -f http://localhost:8099/images/ComfyUI_00001_.png > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAILED"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ ALL TESTS PASSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Access points:"
echo "  • Gallery: http://localhost:8088/view-gallery.html"
echo "  • API:     http://localhost:8099"
echo ""
