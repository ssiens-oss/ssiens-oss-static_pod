# Zazzle API Setup - Step-by-Step Guide

Complete guide to setting up Zazzle API integration with Antigravity POD system.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Setup (5 Minutes)](#quick-setup-5-minutes)
- [Detailed Setup](#detailed-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Overview

Zazzle offers two integration methods:

### 1. Associate Program (Recommended for Starting)
- ✅ Free to join
- ✅ Earn commissions on sales
- ✅ Quick setup (5 minutes)
- ⚠️ Limited API access
- 👍 Best for: Testing, getting started

### 2. Full API Access
- ✅ Complete product management
- ✅ Direct store integration
- ✅ Full automation capabilities
- ⚠️ Requires application approval (3-7 days)
- 👍 Best for: Production, scale

**We recommend starting with the Associate Program, then upgrading to Full API when ready.**

## Prerequisites

Before starting:

1. ✅ Antigravity POD system installed
2. ✅ `.env` file created from `.env.example`
3. ✅ Zazzle account created (https://www.zazzle.com/sell)

## Quick Setup (5 Minutes)

### Step 1: Run Setup Script

```bash
cd antigravity
./setup_zazzle.sh
```

The script will guide you through:
- Choosing integration method (Associate or Full API)
- Entering credentials
- Configuring store ID
- Setting default template
- Testing connection

### Step 2: Validate Configuration

```bash
python validate_zazzle.py
```

This will verify:
- Environment variables are set
- Client initializes correctly
- Product types are available
- Templates are loaded
- Orchestrator works

### Step 3: Test with a Design

```bash
python -m antigravity.zazzle_cli design test.png --dry-run --product-type tshirt
```

**Done!** If all tests pass, you're ready to use Zazzle.

## Detailed Setup

### Option A: Associate Program (Quick Start)

#### 1. Sign Up for Associate Program

Go to: **https://www.zazzle.com/sell/associates**

- Click "Join Now"
- Fill out the application form
- Wait for approval (usually instant to 24 hours)

#### 2. Get Your Associate ID

Once approved:
1. Log in to your Zazzle Associate dashboard
2. Look for your **Associate ID**
3. It's a long number like: `238123456789012345`

#### 3. Configure Associate ID

**Automatic (using setup script):**
```bash
./setup_zazzle.sh
# Choose option 1 (Associate Program)
# Enter your Associate ID when prompted
```

**Manual (edit .env):**
```bash
nano .env
```

Add:
```bash
ZAZZLE_ASSOCIATE_ID=238123456789012345
ZAZZLE_STORE_ID=your_store_name
ZAZZLE_DEFAULT_TEMPLATE=tshirt_basic
ENABLE_ZAZZLE=true
```

#### 4. Get Your Store ID

Your Store ID is in your Zazzle store URL:

```
https://www.zazzle.com/store/staticwaves
                              ^^^^^^^^^^^^
                              This is your Store ID
```

### Option B: Full API Access

#### 1. Apply for API Access

Go to: **https://www.zazzle.com/sell/developers**

- Click "Apply for API Access"
- Fill out the developer application
- Describe your use case (POD automation, design management)
- Submit application

⏱️ **Wait for approval** (typically 3-7 business days)

#### 2. Generate API Key

Once approved:
1. Log in to Zazzle Developer Portal
2. Navigate to "API Keys"
3. Generate a new API key
4. **Save it immediately** (won't be shown again)

#### 3. Configure API Key

**Automatic (using setup script):**
```bash
./setup_zazzle.sh
# Choose option 2 (Full API)
# Enter your API Key when prompted
```

**Manual (edit .env):**
```bash
nano .env
```

Add:
```bash
ZAZZLE_API_KEY=your_api_key_here
ZAZZLE_STORE_ID=your_store_name
ZAZZLE_DEFAULT_TEMPLATE=tshirt_basic
ENABLE_ZAZZLE=true
```

### Option C: Both (Most Flexible)

You can configure both for maximum flexibility:

```bash
./setup_zazzle.sh
# Choose option 3 (Both)
```

This allows:
- Testing with Associate Program
- Production with Full API
- Fallback if one fails

## Verification

### 1. Validate Configuration

```bash
python validate_zazzle.py
```

**Expected output:**
```
======================================================================
  Zazzle API Validation
======================================================================

🔍 Checking Environment Variables...

  ✅ ZAZZLE_ASSOCIATE_ID: 23812345...
  ✅ ZAZZLE_STORE_ID: staticwaves
  ✅ ZAZZLE_DEFAULT_TEMPLATE: tshirt_basic
  ✅ ENABLE_ZAZZLE: true

🔧 Testing Zazzle Client Initialization...

  ✅ Zazzle client initialized successfully
  ✅ Store URL: https://www.zazzle.com/store/staticwaves
  ✅ Associate ID configured
  ✅ Store ID: staticwaves

📦 Checking Product Types...

  Available product types:
    • tshirt
    • hoodie
    • poster
    • mug
    • sticker
    • phone_case
    • tote_bag
    • pillow
    • mousepad
    • keychain

📋 Checking Templates...

  Available templates:
    • tshirt_basic
      Product: tshirt
      Price: $19.99
      Royalty: 10%
    • hoodie_premium
      Product: hoodie
      Price: $49.99
      Royalty: 15%
    [...]

🎨 Testing Zazzle POD Orchestrator...

  ✅ Zazzle POD Orchestrator initialized
  ✅ Antigravity core loaded
  ✅ Zazzle client available

✅ Testing Verification Functions...

  ✅ verify_zazzle_product() available
  ✅ verify_zazzle_store() available

======================================================================
  Validation Summary
======================================================================

  ✅ PASS: Environment Variables
  ✅ PASS: Client Initialization
  ✅ PASS: Product Types
  ✅ PASS: Templates
  ✅ PASS: Orchestrator
  ✅ PASS: Verification

  Total: 6/6 tests passed

✅ All tests passed! Zazzle integration is ready.
```

### 2. Test with Dry Run

```bash
# Create a test image (if you don't have one)
convert -size 4500x5400 xc:white -pointsize 200 -draw "text 1000,2700 'TEST DESIGN'" test.png

# Test Zazzle integration
python -m antigravity.zazzle_cli design test.png --dry-run \
  --product-type tshirt \
  --template tshirt_basic

# Expected: AI consultation, risk assessment, but no actual publishing
```

### 3. View Quick Start Examples

```bash
python examples/zazzle_quickstart.py
```

This will show:
- Available templates
- How to create products
- How to use the orchestrator
- How to verify products

## Configuration Options

### Environment Variables Reference

```bash
# Credentials (need at least one)
ZAZZLE_ASSOCIATE_ID=your_associate_id      # Associate program
ZAZZLE_API_KEY=your_api_key                # Full API

# Required
ZAZZLE_STORE_ID=your_store_name            # Your store name

# Optional
ZAZZLE_DEFAULT_TEMPLATE=tshirt_basic       # Default product template
ENABLE_ZAZZLE=true                         # Enable/disable Zazzle

# Behavioral (from main Antigravity config)
DRY_RUN=false                              # Test mode
REQUIRE_HUMAN=true                         # Require approval
ENABLE_AB_TESTING=true                     # Generate variants
```

### Template Options

Choose your default template based on product strategy:

| Template | Product | Price | Royalty | Best For |
|----------|---------|-------|---------|----------|
| `tshirt_basic` | T-Shirt | $19.99 | 10% | Volume, testing |
| `tshirt_premium` | T-Shirt | $24.99 | 15% | Quality, margins |
| `hoodie_basic` | Hoodie | $39.99 | 10% | Entry-level hoodies |
| `hoodie_premium` | Hoodie | $49.99 | 15% | Premium hoodies |
| `poster` | Poster | $14.99 | 20% | Art prints |
| `mug` | Mug | $12.99 | 15% | Gift items |

## Troubleshooting

### "No Zazzle credentials found"

**Problem:** Neither Associate ID nor API Key is configured.

**Solution:**
```bash
./setup_zazzle.sh
# OR
nano .env
# Add ZAZZLE_ASSOCIATE_ID or ZAZZLE_API_KEY
```

### "Zazzle client not available"

**Problem:** Credentials are configured but invalid.

**Solutions:**
1. Check credentials are correct in `.env`
2. Verify Associate ID format (long number)
3. Check API key hasn't expired
4. Make sure .env is in correct directory

### "Configuration incomplete"

**Problem:** Missing required fields.

**Solution:**
```bash
# Check what's missing
python validate_zazzle.py

# Configure missing fields
nano .env
```

### Associate Program Not Approved Yet

**Problem:** Applied but waiting for approval.

**Workaround:**
- Use dry-run mode while waiting: `--dry-run`
- Test the orchestration flow
- Set up other integrations (Printify, Shopify)
- Continue once approved

### API Application Rejected

**Problem:** API access application was denied.

**Solutions:**
1. Use Associate Program instead (works fine for most use cases)
2. Reapply with more details about your use case
3. Build portfolio with Associate Program first
4. Contact Zazzle support for guidance

### Import Errors

**Problem:** `ImportError: No module named 'antigravity'`

**Solution:**
```bash
# Ensure you're in the right directory
cd antigravity

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Verification Fails

**Problem:** Playwright verification doesn't work.

**Solution:**
```bash
# Install Playwright browsers
playwright install chromium

# Test Playwright
python -c "from playwright.sync_api import sync_playwright"
```

## Testing Your Setup

### Test 1: Simple Product Creation

```python
from antigravity.integrations.zazzle import create_zazzle_product

product = create_zazzle_product(
    image_path="test.png",
    title="Test Product",
    description="Testing Zazzle integration",
    product_type="tshirt",
    price=19.99,
    tags=["test"],
)

print(f"Product URL: {product['url']}")
```

### Test 2: Full AI Orchestration

```python
from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

orchestrator = ZazzlePODOrchestrator(dry_run=True)

result = orchestrator.process_design_for_zazzle(
    design_path="test.png",
    product_type="tshirt",
)

print(f"Result: {result}")
```

### Test 3: Multiple Product Types

```python
orchestrator = ZazzlePODOrchestrator(dry_run=True)

results = orchestrator.create_multiple_product_types(
    design_path="test.png",
    product_types=["tshirt", "hoodie", "mug"],
)

print(f"Created {len(results)} products")
```

## Next Steps After Setup

1. **Test with One Design**
   ```bash
   python -m antigravity.zazzle_cli design design.png --dry-run
   ```

2. **Enable Production Mode**
   ```bash
   # Edit .env
   DRY_RUN=false
   ```

3. **Start Autonomous Processing**
   ```bash
   python -m antigravity.zazzle_cli watch --watch-dir /data/comfyui/output
   ```

4. **Monitor via Slack**
   - Configure `SLACK_WEBHOOK_URL`
   - Get real-time notifications

5. **Review Decisions**
   ```bash
   cat provenance.jsonl | tail -10
   ```

## Support & Resources

### Documentation
- **Full Guide**: `ZAZZLE_INTEGRATION.md`
- **Main README**: `README.md`
- **Quick Start**: `QUICKSTART.md`

### Testing
- **Setup Script**: `./setup_zazzle.sh`
- **Validation**: `python validate_zazzle.py`
- **Examples**: `python examples/zazzle_quickstart.py`

### Zazzle Resources
- **Associate Program**: https://www.zazzle.com/sell/associates
- **API Docs**: https://www.zazzle.com/sell/developers
- **Seller Forum**: https://www.zazzle.com/forum/seller
- **Help Center**: https://help.zazzle.com

### Antigravity Support
- **Issues**: Check `provenance.jsonl` for decision history
- **Debugging**: Set `DEBUG=true` in `.env`
- **Verification**: Review Slack notifications
- **Memory**: Check vector memory count

## FAQ

**Q: Do I need both Associate ID and API Key?**
A: No, you only need one. Associate ID is easier to get. API Key provides more features.

**Q: How long does API approval take?**
A: Typically 3-7 business days. Use Associate Program while waiting.

**Q: Can I change templates later?**
A: Yes, you can specify template per product or change the default in `.env`.

**Q: Does this work with ComfyUI?**
A: Yes, just set `--watch-dir` to your ComfyUI output directory.

**Q: Is this production-ready?**
A: Yes, with proper testing. Start with `--dry-run` and `--require-human` flags.

**Q: How much does Zazzle take?**
A: Zazzle sets base prices. You earn royalties on top (10-99% configurable).

**Q: Can I sell on multiple platforms?**
A: Yes, Zazzle works alongside Printify, Shopify, and other integrations.

---

**Ready to start?** Run `./setup_zazzle.sh` now!
