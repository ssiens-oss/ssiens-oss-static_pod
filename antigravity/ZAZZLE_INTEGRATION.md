# Zazzle Integration Guide

Complete guide for integrating Zazzle into your Antigravity POD pipeline with multi-model AI orchestration.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [Product Types](#product-types)
- [Templates](#templates)
- [Verification](#verification)
- [Examples](#examples)
- [API Reference](#api-reference)

## Overview

Zazzle is a print-on-demand marketplace that allows you to create and sell custom products. This integration provides:

✅ **Full Antigravity Intelligence**
- Multi-model AI decision-making (GPT + Claude + Grok)
- Risk assessment and safety checks
- A/B testing with multiple variants
- Uncertainty detection and escalation

✅ **Zazzle-Specific Features**
- Support for 10+ product types (t-shirts, hoodies, posters, mugs, stickers, etc.)
- Pre-configured templates with optimized pricing
- Royalty percentage management
- Product verification with Playwright

✅ **Seamless Integration**
- Works with existing POD pipeline
- Same workflow as Printify/Shopify
- Slack notifications
- Memory and learning

## Setup

### 1. Get Zazzle Credentials

You need either:

**Option A: Associate ID (Recommended for starting)**
1. Go to https://www.zazzle.com/sell/associates
2. Sign up for Zazzle Associate program
3. Get your Associate ID

**Option B: API Key (For full API access)**
1. Go to https://www.zazzle.com/sell/developers
2. Apply for API access
3. Get your API key

### 2. Configure Environment

Edit your `.env` file:

```bash
# Zazzle credentials
ZAZZLE_ASSOCIATE_ID=your-associate-id
ZAZZLE_API_KEY=your-api-key
ZAZZLE_STORE_ID=your-store-id

# Default template
ZAZZLE_DEFAULT_TEMPLATE=tshirt_basic

# Enable Zazzle
ENABLE_ZAZZLE=true
```

### 3. Test Connection

```python
from antigravity.integrations.zazzle import ZazzleClient

client = ZazzleClient()
print(f"Zazzle store URL: {client.get_store_url()}")
```

## Usage

### Quick Start: Single Product

```python
from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

# Initialize orchestrator
orchestrator = ZazzlePODOrchestrator(
    dry_run=False,
    require_human=True,
    default_brand="StaticWaves",
)

# Process a design
result = orchestrator.process_design_for_zazzle(
    design_path="design.png",
    product_type="tshirt",
    brand="StaticWaves",
)

if result and result['ready_for_publish']:
    print(f"✅ Published to Zazzle!")
    print(f"URL: {result['zazzle_product']['url']}")
```

### Command Line

```bash
# Process single design for Zazzle
python -m antigravity.zazzle design.png --product-type tshirt

# Batch process
python -m antigravity.zazzle batch --directory /path/to/designs --product-type hoodie

# Watch directory
python -m antigravity.zazzle watch --watch-dir /data/comfyui/output
```

## Product Types

Zazzle supports many product types:

| Type | Description | Default Price | Royalty |
|------|-------------|---------------|---------|
| `tshirt` | Basic T-shirt | $19.99 | 10% |
| `hoodie` | Pullover Hoodie | $39.99 | 10% |
| `poster` | Poster Print | $14.99 | 20% |
| `mug` | Coffee Mug | $12.99 | 15% |
| `sticker` | Sticker | $3.99 | 25% |
| `phone_case` | Phone Case | $24.99 | 15% |
| `tote_bag` | Tote Bag | $16.99 | 15% |
| `pillow` | Throw Pillow | $29.99 | 15% |
| `mousepad` | Mouse Pad | $11.99 | 20% |
| `keychain` | Keychain | $5.99 | 20% |

### Using Different Product Types

```python
# Create multiple product types from same design
result = orchestrator.create_multiple_product_types(
    design_path="design.png",
    product_types=["tshirt", "hoodie", "poster", "mug"],
    brand="StaticWaves",
)

print(f"Created {len(result)} product types")
```

## Templates

Pre-configured templates optimize pricing and royalties:

### Available Templates

```python
from antigravity.integrations.zazzle import ZAZZLE_TEMPLATES

# List all templates
print(ZAZZLE_TEMPLATES.keys())
# Output: ['tshirt_basic', 'tshirt_premium', 'hoodie_basic',
#          'hoodie_premium', 'poster', 'mug']
```

### Template Specifications

**`tshirt_basic`**
- Product: T-shirt
- Price: $19.99
- Royalty: 10%

**`tshirt_premium`**
- Product: T-shirt
- Price: $24.99
- Royalty: 15%

**`hoodie_basic`**
- Product: Hoodie
- Price: $39.99
- Royalty: 10%

**`hoodie_premium`**
- Product: Hoodie
- Price: $49.99
- Royalty: 15%

**`poster`**
- Product: Poster
- Price: $14.99
- Royalty: 20%

**`mug`**
- Product: Mug
- Price: $12.99
- Royalty: 15%

### Using Templates

```python
# Use specific template
result = orchestrator.process_design_for_zazzle(
    design_path="design.png",
    product_type="tshirt",
    template="tshirt_premium",  # Higher price, higher royalty
)
```

## Verification

Zazzle products can be verified using Playwright:

### Verify Single Product

```python
from antigravity.verification import verify_zazzle_product

# Verify product is live
result = verify_zazzle_product(
    product_id="zazzle_product_123",
    expected_title="StaticWaves Hoodie",
    expected_price=44.99,
    store_id="your-store-id",
)

if result['success']:
    print("✅ Product verified")
else:
    print(f"❌ Verification failed: {result['checks_failed']}")
```

### Verify Store

```python
from antigravity.verification import verify_zazzle_store

result = verify_zazzle_store(
    store_id="your-store-id",
    screenshot_path="zazzle_store_screenshot.png",
)

if result['success']:
    print("✅ Store is accessible")
```

## Examples

### Example 1: Simple Zazzle Upload

```python
from antigravity.integrations.zazzle import create_zazzle_product

# Quick upload without AI orchestration
product = create_zazzle_product(
    image_path="design.png",
    title="StaticWaves T-Shirt",
    description="Limited edition AI-generated design",
    product_type="tshirt",
    price=24.99,
    tags=["streetwear", "ai", "limited"],
    royalty_percentage=15.0,
)

print(f"Product URL: {product['url']}")
```

### Example 2: Full AI Orchestration

```python
from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

orchestrator = ZazzlePODOrchestrator(
    dry_run=False,
    require_human=True,
    enable_ab_testing=True,
)

# This will:
# 1. Generate 3 offer variants
# 2. Run risk assessment
# 3. Consult GPT + Claude for decision
# 4. Require human approval
# 5. Publish to Zazzle
# 6. Verify it went live
# 7. Store in memory

result = orchestrator.process_design_for_zazzle(
    design_path="design.png",
    product_type="hoodie",
)
```

### Example 3: Batch Processing

```python
from pathlib import Path

# Find all designs
designs = list(Path("/data/designs").glob("*.png"))

# Batch process to Zazzle
results = orchestrator.batch_process_for_zazzle(
    design_paths=[str(d) for d in designs],
    product_type="tshirt",
    template="tshirt_basic",
)

print(f"Processed {len(results)}/{len(designs)} designs")
```

### Example 4: Multi-Product Line

```python
# Create a full product line from one design
results = orchestrator.create_multiple_product_types(
    design_path="hero_design.png",
    product_types=[
        "tshirt",
        "hoodie",
        "poster",
        "mug",
        "sticker",
    ],
    brand="StaticWaves",
)

for result in results:
    product_type = result['product_type']
    url = result.get('zazzle_product', {}).get('url', 'N/A')
    print(f"✅ {product_type}: {url}")
```

### Example 5: Watch Directory for Zazzle

```python
from antigravity.watcher import watch_and_process

def zazzle_callback(file_path: str):
    """Process each new design for Zazzle."""
    orchestrator = ZazzlePODOrchestrator()
    orchestrator.process_design_for_zazzle(
        design_path=file_path,
        product_type="tshirt",
    )

# Watch ComfyUI output and auto-publish to Zazzle
watch_and_process(
    watch_dir="/data/comfyui/output",
    callback=zazzle_callback,
)
```

## API Reference

### ZazzleClient

Main client for Zazzle API operations.

```python
from antigravity.integrations.zazzle import ZazzleClient

client = ZazzleClient(
    associate_id="your-id",
    api_key="your-key",
    store_id="your-store",
)
```

**Methods:**

- `upload_image(image_path, image_name)` - Upload design image
- `create_product(product_type, title, description, ...)` - Create product
- `publish_product(product_id)` - Make product live
- `unpublish_product(product_id)` - Make product inactive
- `get_product(product_id)` - Get product details
- `update_product(product_id, updates)` - Update product
- `list_products(status, limit)` - List your products
- `get_product_url(product_id)` - Get product URL
- `get_store_url()` - Get store URL

### ZazzlePODOrchestrator

Zazzle-specific orchestrator with full AI intelligence.

```python
from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

orchestrator = ZazzlePODOrchestrator(
    dry_run=False,
    require_human=True,
    enable_ab_testing=True,
    default_brand="StaticWaves",
    default_template="tshirt_basic",
)
```

**Methods:**

- `process_design_for_zazzle(design_path, product_type, brand, template)` - Process single design
- `batch_process_for_zazzle(design_paths, product_type, template)` - Process multiple designs
- `create_multiple_product_types(design_path, product_types, brand)` - Create multiple types

### Helper Functions

```python
# Quick product creation
from antigravity.integrations.zazzle import create_zazzle_product

product = create_zazzle_product(
    image_path="design.png",
    title="Product Title",
    description="Product description",
    product_type="tshirt",
    price=19.99,
    tags=["tag1", "tag2"],
    royalty_percentage=10.0,
)

# Get template
from antigravity.integrations.zazzle import get_zazzle_template

template = get_zazzle_template("hoodie_premium")
# Returns: {'product_type': 'hoodie', 'price': 49.99, 'royalty_percentage': 15.0}
```

## Integration Workflow

The complete Zazzle workflow with Antigravity:

```
┌─────────────────┐
│  ComfyUI Design │
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│  ZazzlePODOrchestrator   │
│                          │
│  Step 1: Offer Factory   │
│  • Generate 3 variants   │
│  • Different prices      │
│  • A/B testing ready     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Risk Assessment         │
│  • Copyright check       │
│  • Pricing validation    │
│  • Content safety        │
│  • Risk scoring 0-100    │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  AI Consultation         │
│  • GPT: Strategy         │
│  • Claude: Safety        │
│  • Grok: Adversarial     │
│  • Disagreement detect   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Human Approval          │
│  (if required/uncertain) │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Zazzle Publishing       │
│  • Upload image          │
│  • Create product        │
│  • Set price/royalty     │
│  • Publish to store      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Verification            │
│  • Playwright check      │
│  • Screenshot proof      │
│  • Title/price validate  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Memory & Learning       │
│  • Store in vector DB    │
│  • Log to provenance     │
│  • Slack notification    │
│  • Notion logging        │
└──────────────────────────┘
```

## Configuration Tips

### For Testing

```bash
DRY_RUN=true                 # Don't actually publish
REQUIRE_HUMAN=true           # Always ask for approval
ZAZZLE_DEFAULT_TEMPLATE=tshirt_basic  # Start simple
```

### For Production

```bash
DRY_RUN=false
REQUIRE_HUMAN=false          # Auto-publish if confident
CONFIDENCE_THRESHOLD=0.8     # High confidence required
DISAGREEMENT_THRESHOLD=0.03  # Low tolerance for disagreement
```

### For Maximum Revenue

```bash
ZAZZLE_DEFAULT_TEMPLATE=hoodie_premium  # Higher margins
ENABLE_AB_TESTING=true                   # Test variants
```

## Troubleshooting

### "Zazzle client not available"
- Check `ZAZZLE_ASSOCIATE_ID` or `ZAZZLE_API_KEY` in `.env`
- Verify credentials are correct

### "Product verification failed"
- Zazzle products may take time to become live
- Check product URL manually
- Verify store_id is correct

### "API rate limit"
- Zazzle may have rate limits
- Add delays between batch operations
- Consider using dry_run mode for testing

## Best Practices

1. **Start with Templates**
   - Use pre-configured templates for consistent pricing
   - Adjust royalty percentages based on market testing

2. **Use Risk Assessment**
   - Always run risk checks before publishing
   - Block high-risk designs automatically

3. **Enable Memory**
   - Let the system learn from past decisions
   - Review provenance logs regularly

4. **Test Before Scaling**
   - Use dry_run mode initially
   - Verify a few products manually
   - Then enable autonomous mode

5. **Monitor Performance**
   - Check Slack notifications
   - Review Notion logs
   - Analyze provenance data

6. **Optimize Pricing**
   - Use A/B testing with multiple variants
   - Track which price points convert best
   - Adjust templates based on data

## Next Steps

1. **Set up credentials** in `.env`
2. **Test with one design** in dry-run mode
3. **Verify the product** appears on Zazzle
4. **Enable autonomous mode** for scaling
5. **Create multiple product types** from top designs
6. **Monitor and optimize** based on sales data

---

**Questions?** Check the main README.md or provenance logs for decision history.

**Issues?** The Zazzle integration uses the same verification and memory systems as Printify/Shopify - if it works for one platform, it works for all.
