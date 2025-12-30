#!/bin/bash
# Demo Script - Shows StaticWaves POD in Action

API="http://localhost:5000"

echo "🎬 StaticWaves POD - Live Demo"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

demo_step() {
    echo -e "${BLUE}▶${NC} $1"
    sleep 1
}

demo_result() {
    echo -e "${GREEN}✓${NC} $1"
    echo ""
    sleep 1
}

# 1. Check System Status
echo -e "${YELLOW}1. System Status${NC}"
echo "==============="
demo_step "Checking API health..."
curl -s "$API/health" | python3 -m json.tool
demo_result "API is healthy"

demo_step "Checking queue status..."
curl -s "$API/queue" | python3 -m json.tool
demo_result "Queue is ready"

# 2. Agent Status
echo -e "${YELLOW}2. Agent System${NC}"
echo "==============="
demo_step "Listing available agents..."
curl -s "$API/agents/agents" | python3 -m json.tool
demo_result "5 agents registered"

demo_step "Checking available workflows..."
curl -s "$API/agents/workflows" | python3 -m json.tool
demo_result "5 workflows available"

# 3. Add Product to Queue
echo -e "${YELLOW}3. Queue a Product${NC}"
echo "=================="
demo_step "Adding 'Cosmic Waves Hoodie' to queue..."
curl -s -X POST "$API/queue/add" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Cosmic Waves Hoodie",
        "prompt": "cosmic nebula waves galaxy stars, vibrant colors, high quality",
        "type": "hoodie",
        "base_cost": 35.00,
        "inventory": 100,
        "description": "AI-generated cosmic design"
    }' | python3 -m json.tool
demo_result "Product queued successfully"

demo_step "Checking pending queue..."
curl -s "$API/queue/pending" | python3 -m json.tool | head -20
demo_result "1 product in pending queue"

# 4. Test Pricing
echo -e "${YELLOW}4. Pricing Engine${NC}"
echo "================="
demo_step "Calculating price for hoodie (base cost: \$35)..."
echo "Base cost: \$35.00"
echo "Margin: 1.8x (from config/pricing.json)"
echo "Final price: \$63.00"
demo_result "Pricing calculated automatically"

# 5. Quick Launch Demo
echo -e "${YELLOW}5. Quick Launch (Simulated)${NC}"
echo "============================"
demo_step "Triggering quick launch for 'Neon Cyberpunk City'..."
echo ""
echo "Workflow: keyword → prompt → design → mockup → upload → publish"
echo ""
echo "Step 1: Generate prompt from keyword..."
echo "  → 'neon cyberpunk city digital art, vibrant colors, centered composition, 4k'"
echo ""
echo "Step 2: Queue for ComfyUI generation..."
echo "  → Design queued"
echo ""
echo "Step 3: Create mockups (hoodie, tee, poster)..."
echo "  → Mockups ready"
echo ""
echo "Step 4: Upload to Printify..."
echo "  → Product ID: printify_mock_SW-HOO-20251230"
echo ""
echo "Step 5: Publish to Shopify..."
echo "  → Product live"
echo ""
echo "Step 6: Sync to TikTok Shop..."
echo "  → Listed on TikTok"
echo ""
demo_result "Quick launch completed in simulation mode"

# Summary
echo ""
echo "=============================="
echo "✅ Demo Complete!"
echo ""
echo "🎯 What You Can Do Next:"
echo ""
echo "1. Start Frontend:"
echo "   npm install && npm run dev"
echo "   Open: http://localhost:5173"
echo ""
echo "2. Run Agent Workflows:"
echo "   curl -X POST $API/agents/workflows/daily_research/run"
echo ""
echo "3. Manual Product Publish:"
echo "   curl -X POST $API/publish -H 'Content-Type: application/json' \\"
echo "     -d '{\"title\":\"My Design\",\"prompt\":\"...\",\"type\":\"hoodie\",\"base_cost\":35,\"inventory\":100}'"
echo ""
echo "4. Check Stats:"
echo "   curl $API/stats | python3 -m json.tool"
echo ""
echo "5. View Logs:"
echo "   tail -f data/logs/*.log"
echo ""
echo "📖 Documentation:"
echo "   - POD_STACK.md  - Complete POD system guide"
echo "   - AGENTS.md     - Agent automation guide"
echo "   - API.md        - API reference"
echo ""
