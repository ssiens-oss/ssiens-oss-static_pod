# Antigravity - Quick Start Guide

Get up and running with Antigravity in 5 minutes.

## Prerequisites

- Python 3.10+
- OpenAI API key
- Anthropic Claude API key
- (Optional) Slack webhook for notifications

## Installation

```bash
cd antigravity

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

## Configuration

Edit `.env` and add your API keys:

```bash
nano .env
```

**Minimum required:**
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...  # Recommended
```

## Test It Out

### 1. Test with Dry Run (Safe)

```bash
# Process a single design (no actual publishing)
python -m antigravity.main design /path/to/design.png --dry-run

# Expected: AI models consulted, risk assessed, but nothing published
```

### 2. Process Single Design

```bash
# Process with human approval
python -m antigravity.main design design.png

# You'll see:
# - Offer variants generated
# - Risk assessment
# - AI model consultation
# - Approval prompt
```

### 3. Watch Directory (Autonomous)

```bash
# Watch ComfyUI output directory
python -m antigravity.main watch --watch-dir /data/comfyui/output

# Now whenever a new design appears, it will be automatically processed
```

### 4. Integrate with Gateway

```bash
# Process pending designs in your POD Gateway
python -m antigravity.main gateway

# Or continuous mode
python -m antigravity.main gateway --watch
```

## What You'll See

When processing a design:

```
======================================================================
🎨 POD DESIGN PROCESSING
======================================================================
Design: /path/to/design.png
Product: hoodie
Brand: StaticWaves
ID: a3f2b1c4
======================================================================

📋 Step 1: Generating offer variants...
   Generated 3 variants
   Price range: $39.99 - $54.99

📌 Selected offer:
   Title: StaticWaves Hoodie
   Price: $44.99
   Tags: staticwaves, hoodie, streetwear

🔍 Step 2: Risk assessment...
   Risk Level: LOW
   Risk Score: 15/100

🧠 Step 3: Consulting AI models...
🤖 Consulting gpt for analysis...
   ✓ gpt: 85% confidence
🤖 Consulting claude for safety...
   ✓ claude: 92% confidence

📊 Consensus (confidence: 88.5%)
   Proceed with launch. Design is safe, pricing is competitive...

📦 Step 4: Preparing for publish...

✅ Processing complete!
   Design ID: a3f2b1c4
   Ready for publish: True
```

## Common Commands

```bash
# Single design
python -m antigravity.main design <file> [options]

# Batch directory
python -m antigravity.main batch --directory <dir>

# Watch mode (autonomous)
python -m antigravity.main watch --watch-dir <dir>

# Gateway integration
python -m antigravity.main gateway [--watch]

# Options
--dry-run           # Plan but don't execute
--auto-approve      # Skip human approval
--product-type      # tshirt or hoodie
--brand            # Brand name
--ab-testing       # Generate variants
```

## How It Helps Your POD Workflow

### Before Antigravity
1. Generate design in ComfyUI
2. Manually check if it looks good
3. Guess a price
4. Upload to Printify
5. Hope it sells

### With Antigravity
1. Generate design in ComfyUI
2. **Antigravity automatically:**
   - Generates 3 price/copy variants
   - Checks for copyright/safety issues
   - Consults GPT for strategy
   - Consults Claude for safety
   - Calculates risk score
   - Decides if safe to proceed
   - Logs decision with proof
   - Notifies you on Slack
3. Approve and publish
4. **Antigravity verifies** product went live correctly
5. **Antigravity remembers** what worked

### Key Advantages

✅ **Safety**: Catches problems before they happen
✅ **Intelligence**: Multiple AI models, not just one
✅ **Verification**: Proof that things actually work
✅ **Memory**: Learns from past decisions
✅ **Automation**: Can run autonomously with safeguards
✅ **Visibility**: Slack notifications keep you informed

## Troubleshooting

### Issue: "Module not found"
**Solution:** Activate virtual environment
```bash
source venv/bin/activate
```

### Issue: "API key not set"
**Solution:** Check `.env` file has correct keys
```bash
cat .env | grep API_KEY
```

### Issue: "Playwright not available"
**Solution:** Install Playwright browsers
```bash
playwright install
```

### Issue: "No Slack notifications"
**Solution:** Add `SLACK_WEBHOOK_URL` to `.env`

### Issue: "Memory errors"
**Solution:** Install optional dependencies
```bash
pip install chromadb sentence-transformers
```

## Next Steps

1. **Read the full README**: `cat README.md`
2. **Configure thresholds**: Edit `.env` to tune behavior
3. **Set up Notion**: For human-readable logs
4. **Enable verification**: Set `ENABLE_VERIFICATION=true`
5. **Production deploy**: Integrate with your existing pipeline

## Integration Patterns

### Pattern 1: Standalone Watcher

Run Antigravity as a separate process watching ComfyUI output:

```bash
# In a tmux/screen session
python -m antigravity.main watch --watch-dir /data/comfyui/output
```

### Pattern 2: Gateway Enhancement

Use Antigravity to enhance your existing POD Gateway:

```python
from antigravity.gateway_bridge import GatewayBridge

bridge = GatewayBridge()
bridge.process_pending_designs()
```

### Pattern 3: Direct Integration

Call Antigravity from your existing code:

```python
from antigravity.pod.orchestrator import PODOrchestrator

orchestrator = PODOrchestrator()
result = orchestrator.process_design("design.png", "hoodie")
```

## Configuration Tips

### Conservative (Safer)
```bash
REQUIRE_HUMAN=true
DISAGREEMENT_THRESHOLD=0.03
CONFIDENCE_THRESHOLD=0.8
RISK_SCORE_THRESHOLD=30
```

### Balanced (Recommended)
```bash
REQUIRE_HUMAN=true
DISAGREEMENT_THRESHOLD=0.05
CONFIDENCE_THRESHOLD=0.7
RISK_SCORE_THRESHOLD=50
```

### Aggressive (Autonomous)
```bash
REQUIRE_HUMAN=false  # Use with caution!
DISAGREEMENT_THRESHOLD=0.1
CONFIDENCE_THRESHOLD=0.6
RISK_SCORE_THRESHOLD=70
```

## Monitoring

### Check Decision History
```bash
# View recent decisions
cat provenance.jsonl | tail -5

# Analyze performance
python -c "from antigravity.memory.provenance import analyze_provenance; import json; print(json.dumps(analyze_provenance(), indent=2))"
```

### Check Memory
```python
from antigravity.memory.vector import VectorMemory

memory = VectorMemory()
print(f"Stored memories: {memory.count()}")
```

## Support

If you run into issues:

1. Check `provenance.jsonl` for decision history
2. Review Slack notifications
3. Enable `DEBUG=true` in `.env`
4. Check API rate limits

## What's Next?

- Enable TikTok Shop verification
- Add profit tracking per SKU
- Set up competitive price monitoring
- Configure multiple brands
- Implement automatic rollback

Read the full README for advanced features!

---

**You're ready to go! Start with a test design in `--dry-run` mode.**
