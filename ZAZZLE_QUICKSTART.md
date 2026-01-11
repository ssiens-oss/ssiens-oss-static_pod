# Zazzle Setup - 5 Minute Quick Start

## Step 1: Get Credentials (Choose One)

### Option A: Associate Program (Fastest)
1. Go to: https://www.zazzle.com/sell/associates
2. Sign up (free)
3. Get your Associate ID (example: `238123456789012345`)

### Option B: Full API
1. Go to: https://www.zazzle.com/sell/developers
2. Apply for API access (takes 3-7 days)
3. Get your API Key

### Get Store ID
- Your store URL: `https://www.zazzle.com/store/yourstore`
- Your Store ID: `yourstore`

## Step 2: Configure

```bash
# Edit configuration
nano /home/user/ssiens-oss-static_pod/antigravity/.env
```

**Find the Zazzle section (line ~95) and update:**

```bash
# Add ONE of these:
ZAZZLE_ASSOCIATE_ID=238123456789012345    # Your actual Associate ID
# OR
ZAZZLE_API_KEY=your_actual_api_key        # Your actual API Key

# Required:
ZAZZLE_STORE_ID=yourstore                 # Your store name
```

**Save:** `Ctrl+X` → `Y` → `Enter`

## Step 3: Validate

```bash
cd /home/user/ssiens-oss-static_pod/antigravity
./check_zazzle.sh
```

## Step 4: Test

```bash
# Test with dry run (safe, won't publish)
python3 -m antigravity.zazzle_cli design design.png --dry-run --product-type tshirt

# Expected: AI consultation, risk assessment, planning (no actual publishing)
```

## Done! ✅

### Next Steps:

**Create multiple products from one design:**
```bash
python3 -m antigravity.zazzle_cli multi design.png \
  --product-types tshirt,hoodie,mug,poster
```

**Watch directory for automatic processing:**
```bash
python3 -m antigravity.zazzle_cli watch \
  --watch-dir /data/comfyui/output \
  --product-type tshirt
```

**Run examples:**
```bash
python3 examples/zazzle_quickstart.py
```

## Troubleshooting

**Can't find credentials?**
- Run: `./check_zazzle.sh` to see what's configured

**Need more help?**
- Read: `cat antigravity/ZAZZLE_SETUP.md`
- Detailed guide: `cat antigravity/ZAZZLE_INTEGRATION.md`

**Not sure what to enter?**
- Associate ID looks like: `238123456789012345` (long number)
- Store ID is the last part of your store URL
- Example store URL: `https://www.zazzle.com/store/staticwaves`
- Example Store ID: `staticwaves`

## What You Get

✅ 10+ product types (tshirts, hoodies, posters, mugs, stickers, etc.)
✅ Multi-model AI decision-making (GPT + Claude)
✅ Risk assessment and safety checks
✅ A/B testing with multiple variants
✅ Playwright verification
✅ Complete audit trails

---

**Need help?** Run `./check_zazzle.sh` to validate your setup!
