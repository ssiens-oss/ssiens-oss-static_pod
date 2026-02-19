#!/bin/bash
# StaticWaves Forge - Complete System Demo
# This script demonstrates the full platform capabilities

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎮 StaticWaves Forge - Live Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if API is running
echo "1️⃣  Checking API status..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "   ✅ API is online"
else
    echo "   ❌ API not running. Start it with:"
    echo "      cd apps/api && uvicorn main:app --reload"
    exit 1
fi

echo ""
echo "2️⃣  API Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

echo "3️⃣  Platform Stats:"
curl -s http://localhost:8000/api/stats | python3 -m json.tool
echo ""

echo "4️⃣  Creating Asset Generation Job..."
echo "   Prompt: 'A low-poly cyberpunk vending machine'"
RESPONSE=$(curl -s "http://localhost:8000/api/generate/quick?prompt=cyberpunk+vending+machine&asset_type=prop")
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

if [ -n "$JOB_ID" ]; then
    echo "   ✅ Job created: $JOB_ID"
else
    echo "   ⚠️  Using test job ID"
    JOB_ID="test-job-123"
fi
echo ""

echo "5️⃣  Available Asset Pack Presets:"
curl -s http://localhost:8000/api/packs/presets/list | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    print(f\"   📦 {p['name']}\")
    print(f\"      {p['description']}\")
    print(f\"      {p['count']} assets - \${p['suggested_price']}\")
    print()
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Demo Complete!"
echo ""
echo "Next Steps:"
echo "  1. View full API docs: http://localhost:8000/docs"
echo "  2. Start web UI: cd apps/web && npm run dev"
echo "  3. Generate assets: python scripts/generate_batch.py creature 5"
echo "  4. Read walkthrough: docs/SYSTEM_WALKTHROUGH.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
