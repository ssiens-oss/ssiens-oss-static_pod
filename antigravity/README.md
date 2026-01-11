# Antigravity - Multi-Model AI POD Orchestration System

Antigravity is an intelligent control plane that combines multiple AI models (GPT, Claude, Grok) with Playwright automation, memory systems, and human-in-the-loop controls to create a safe, verified, and learning-enabled POD (Print-on-Demand) operation system.

## What This Does (ELI5)

Instead of manually uploading POD designs and hoping they work, Antigravity:

1. **Thinks before acting** - Consults multiple AI models for different perspectives
2. **Checks its work** - Uses Playwright to verify products actually went live correctly
3. **Remembers what works** - Builds semantic memory of successful decisions
4. **Stops bad ideas** - Blocks risky launches before they happen
5. **Alerts when needed** - Notifies you only when human attention is required
6. **Scales intelligently** - Tests multiple variants and keeps what works

Think of it as turning POD from "upload and hope" into "test, verify, and scale what makes money."

## Architecture

```
┌─────────────┐
│   ComfyUI   │  ← AI image generation
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│  Antigravity Orchestrator   │
│  (Multi-Model Decision AI)  │
│                              │
│  • GPT (strategy, copy)     │
│  • Claude (safety checks)   │
│  • Grok (adversarial)       │
└──────┬──────────────────────┘
       │
┌──────▼───────┐  ┌──────────────┐
│ Offer Factory│  │ Risk Firewall│
└──────┬───────┘  └──────┬───────┘
       │                 │
┌──────▼─────────────────▼────┐
│   Existing POD Pipeline     │
│   (Printify → Shopify)      │
└──────┬──────────────────────┘
       │
┌──────▼────────────────┐
│ Playwright Verifier   │
│ (Proof of execution)  │
└───────────────────────┘
```

## Key Features

### 1. Multi-Model Arbitration
- **GPT**: Strategic analysis, copywriting, pricing
- **Claude**: Safety checking, policy compliance, risk assessment
- **Grok**: Adversarial thinking, edge case detection (mock for now)

Each model specializes in what it's best at. The system detects disagreement and escalates when confidence is low.

### 2. Uncertainty & Disagreement Detection
- Measures confidence variance across models
- Escalates to humans when disagreement is high
- Prevents acting on uncertain decisions

### 3. Verification & Proof
- Playwright verifies products actually went live
- Screenshots prove execution
- Catches silent failures

### 4. Memory & Learning
- **Vector memory**: Semantic search of past decisions
- **Provenance logs**: Complete audit trail of all decisions
- **Notion integration**: Human-readable decision logs

### 5. Safety & Risk Assessment
- Checks for copyright/trademark issues
- Validates pricing strategy
- Blocks problematic content
- Pre-mortem failure simulation

### 6. Offer Factory & A/B Testing
- Generates multiple product variants (price, copy, positioning)
- Tests different strategies
- Scales what works, kills what doesn't

### 7. Notifications & Escalation
- **Slack**: Real-time alerts, rich formatting
- **Email**: High-stakes escalations
- **Webhooks**: Custom integrations

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ (for existing POD pipeline)
- API keys for OpenAI and Anthropic

### Step 1: Install Dependencies

```bash
cd antigravity
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required configurations:**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `SLACK_WEBHOOK_URL` - Slack webhook (highly recommended)

### Step 3: Test Installation

```bash
# Test single design processing (dry run)
python -m antigravity.main design /path/to/design.png --dry-run

# Expected output: AI consultation, risk assessment, but no actual publishing
```

## Usage

### Process Single Design

```bash
python -m antigravity.main design design.png \
  --product-type hoodie \
  --brand StaticWaves \
  --ab-testing
```

### Batch Process Directory

```bash
python -m antigravity.main batch \
  --directory /data/comfyui/output \
  --product-type hoodie
```

### Watch Directory (Autonomous)

```bash
python -m antigravity.main watch \
  --watch-dir /data/comfyui/output \
  --product-type hoodie
```

This will automatically process any new designs that appear in the directory.

### Integrate with Existing Gateway

```bash
# Process pending designs in POD Gateway
python -m antigravity.main gateway

# Continuous gateway integration
python -m antigravity.main gateway --watch
```

### Command Line Options

```
--dry-run           Plan but don't execute
--auto-approve      Skip human approval (use with caution)
--brand NAME        Brand name (default: StaticWaves)
--product-type      tshirt or hoodie (default: hoodie)
--ab-testing        Generate A/B test variants
```

## Configuration

### Environment Variables

See `.env.example` for all available configurations.

**Key settings:**

```bash
# Behavioral
REQUIRE_HUMAN=true              # Always require approval
DRY_RUN=false                   # Actually execute
ENABLE_AB_TESTING=true          # Generate variants

# Thresholds
DISAGREEMENT_THRESHOLD=0.05     # Escalate if variance > 5%
CONFIDENCE_THRESHOLD=0.7        # Escalate if confidence < 70%
RISK_SCORE_THRESHOLD=50         # Block if risk > 50/100

# Directories
COMFYUI_OUTPUT_DIR=/data/comfyui/output
VECTOR_MEMORY_DIR=/data/antigravity/memory
SCREENSHOT_DIR=/data/antigravity/screenshots
```

## Integration with Existing Pipeline

Antigravity integrates cleanly with your existing setup:

### With POD Gateway (Flask)

```python
from antigravity.gateway_bridge import GatewayBridge

bridge = GatewayBridge()
bridge.process_pending_designs()
```

The bridge reads the Gateway's `state.json`, processes pending designs through Antigravity, and updates their status.

### With TypeScript Orchestrator

Your existing `services/orchestrator.ts` can call Antigravity:

```typescript
import { exec } from 'child_process';

// Process design through Antigravity
exec(`python -m antigravity.main design ${designPath}`, (error, stdout) => {
  if (!error) {
    // Proceed with Printify/Shopify publishing
  }
});
```

### Direct Python Integration

```python
from antigravity.pod.orchestrator import PODOrchestrator

orchestrator = PODOrchestrator(
    dry_run=False,
    require_human=True,
)

result = orchestrator.process_design(
    design_path="design.png",
    product_type="hoodie",
)

if result and result["ready_for_publish"]:
    # Publish to Printify/Shopify
    pass
```

## How It Works (Technical)

### Decision Flow

1. **Design Detection**
   - Watcher detects new file in ComfyUI output
   - Or: Manual/batch processing triggered

2. **Offer Generation**
   - Creates 3 variants (different prices, copy)
   - Generates tags, descriptions

3. **Risk Assessment**
   - Checks file validity
   - Scans for copyright/trademark issues
   - Validates pricing psychology
   - Calculates risk score (0-100)

4. **AI Consultation**
   - Task decomposed into subtasks
   - Routed to appropriate models:
     - GPT: Analysis, copywriting
     - Claude: Safety, policy
     - (Grok: Adversarial thinking - mock)
   - Responses collected and confidence scored

5. **Uncertainty Analysis**
   - Calculates disagreement (variance)
   - Checks average confidence
   - Escalates if thresholds exceeded

6. **Synthesis**
   - Weighted consensus from model responses
   - Human approval if required/escalated
   - Execution plan generated

7. **Provenance Recording**
   - Full decision logged to JSONL
   - Stored in vector memory
   - Logged to Notion (if configured)

8. **Ready for Publishing**
   - Result passed to Printify/Shopify
   - Or: Updated in Gateway state

9. **Verification** (after publishing)
   - Playwright navigates to product URL
   - Verifies title, price, availability
   - Takes screenshot proof
   - Reports success/failure

### Memory & Learning

- **Vector Memory**: Uses ChromaDB + sentence-transformers
  - Semantic search: "Have we seen this before?"
  - Similarity threshold: 0.85
  - Helps avoid repeating mistakes

- **Provenance Logs**: JSONL format
  - Every decision recorded with full context
  - Queryable by decision ID
  - Analysis: success rate, model usage, confidence trends

- **Notion Logs**: Human-readable
  - Decision summaries
  - Risk levels, confidence scores
  - Shared organizational memory

## Safety & Control

### Human-in-the-Loop

- Default: `REQUIRE_HUMAN=true`
- System presents decision, confidence, warnings
- Human approves or rejects
- Can be disabled with `--auto-approve` (use carefully)

### Escalation Triggers

System escalates if:
- Disagreement variance > threshold
- Average confidence < threshold
- Safety model blocks (BLOCK in response)
- Conflicting recommendations

### Risk Firewall

Blocks if:
- Design file missing or invalid
- Test/debug path detected
- Trademark/copyright concerns
- Blocked content terms detected

### Reversibility

- `--dry-run`: Plan without execution
- Verification catches failures
- Provenance allows auditing

## Monitoring & Observability

### Slack Notifications

```
🚀 Antigravity Orchestrator
Task: Evaluate POD product launch...
✅ AI decision: Approved for launch

✅ POD Design Approved
Product: hoodie
Price: $44.99
Risk: low
AI Confidence: 85.3%
```

### Provenance Analysis

```bash
python -c "from antigravity.memory.provenance import analyze_provenance; print(analyze_provenance())"
```

Output:
```json
{
  "total_decisions": 47,
  "successful": 42,
  "failed": 5,
  "success_rate": 0.894,
  "avg_confidence": 0.823,
  "model_usage": {
    "gpt": 94,
    "claude": 47,
    "grok": 47
  }
}
```

### Memory Queries

```python
from antigravity.memory.vector import VectorMemory

memory = VectorMemory()
results = memory.recall("hoodie design with cryptid theme", n_results=3)

for doc, distance in zip(results['documents'], results['distances']):
    print(f"{doc} (distance: {distance})")
```

## Troubleshooting

### "No model responses received"
- Check API keys in `.env`
- Verify internet connectivity
- Check API rate limits

### "SLACK_WEBHOOK_URL not configured"
- Add Slack webhook to `.env`
- Or: System will print warnings but continue

### "Playwright not available"
- Run: `playwright install`
- Ensure chromium browser installed

### "Vector memory requires chromadb"
- Run: `pip install chromadb sentence-transformers`
- Or: Memory will be disabled but system continues

### Gateway state not updating
- Check `POD_STATE_FILE` path in `.env`
- Verify file permissions
- Ensure not running in `--dry-run` mode

## Advanced Usage

### Custom Brand Configuration

```python
from antigravity.pod.offers import OfferFactory

factory = OfferFactory(
    default_brand="CryptidCore",
    enable_ab_testing=True,
)

offers = factory.generate_variants(
    product_type="hoodie",
    count=5,
    brand="CryptidCore",
)
```

### Custom Risk Assessment

```python
from antigravity.pod.risk import calculate_risk_score

risk = calculate_risk_score(
    design_path="design.png",
    offer=offer,
)

if risk['level'] == 'low':
    # Proceed
    pass
```

### Direct LLM Access

```python
from antigravity.llms.gpt import call as call_gpt
from antigravity.llms.claude import call as call_claude

gpt_response, confidence = call_gpt("Analyze this POD strategy...")
claude_response, confidence = call_claude("Check safety of this design...")
```

## Roadmap

### Phase 1 (Current)
- ✅ Multi-model orchestration
- ✅ POD offer factory
- ✅ Risk assessment
- ✅ Playwright verification
- ✅ Vector memory
- ✅ Gateway integration

### Phase 2 (Next)
- [ ] Real Grok API integration
- [ ] Dynamic pricing optimization
- [ ] Automatic rollback on failure
- [ ] Profitability tracking per SKU
- [ ] TikTok Shop verification
- [ ] Multi-brand routing logic

### Phase 3 (Future)
- [ ] Self-improving prompts (outcome-based)
- [ ] Competitive intelligence (price monitoring)
- [ ] Trend detection & auto-adaptation
- [ ] DAG-based decision graphs
- [ ] Distributed worker execution

## Contributing

This is an internal tool, but improvements welcome:

1. Test thoroughly in `--dry-run` mode
2. Add provenance logging to new features
3. Maintain human escalation paths
4. Document configuration changes in `.env.example`

## License

Internal use - StaticWaves POD Operations

## Support

- Check `provenance.jsonl` for decision history
- Review Slack notifications for real-time status
- Enable `DEBUG=true` for verbose logging
- Check memory count: `memory.count()`

---

**Built with:** OpenAI GPT, Anthropic Claude, Playwright, ChromaDB, Watchdog

**Architecture:** Multi-model control plane with verification, memory, and human governance
