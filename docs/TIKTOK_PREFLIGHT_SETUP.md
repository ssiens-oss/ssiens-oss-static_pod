# TikTok Storefront Preflight System - Setup Guide

## 🎯 What This Does

Automatically validates products before publishing to TikTok to prevent:
- ❌ Silent storefront blocks
- ❌ LIVE-only products
- ❌ Price floor violations
- ❌ Inventory issues
- ❌ Image policy violations

## 📦 Installation on RunPod

### Step 1: Copy Preflight Script

```bash
# On RunPod - create the preflight checker
cat > /workspace/ssiens-oss-static_pod/scripts/tiktok-preflight.cjs << 'EOF'
[CONTENT FROM PREVIOUS FILE]
EOF
```

### Step 2: Integrate with Pipeline

Update your `pipeline/stages/publish.cjs` to include preflight checks:

```javascript
const TikTokPreflight = require('../../scripts/tiktok-preflight.cjs')
const preflight = new TikTokPreflight()

// Before creating products:
const productData = {
  id: job.id,
  title: `Static Waves Drop #${dropNum} - Tee (Black)`,
  price: 19.99,
  variants: [...],
  images: [imagePath]
}

const result = preflight.check(productData)

if (!result.pass) {
  ctx.log.warn(`⚠️  Storefront blocked - switching to LIVE-only`)
  ctx.log.warn(`Blockers: ${JSON.stringify(result.blockers)}`)

  // Auto-fix
  if (preflight.autoFix(productData)) {
    ctx.log.info(`✓ Applied ${preflight.fixes.length} fixes`)
  }
}

// Continue with product creation
```

### Step 3: Enable LIVE-Only Fallback

Add to your `.env`:

```bash
TIKTOK_LIVE_FALLBACK=true
TIKTOK_ALERT_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK
```

### Step 4: Test

```bash
# Test the preflight checker
node scripts/tiktok-preflight-test.cjs

# Run pipeline with preflight enabled
node pipeline/runner.cjs --count 1
```

## 🔧 Features

### Auto-Fix Engine

Automatically fixes:
- ✅ Low inventory (sets to 10)
- ✅ Price below floor (raises to minimum)
- ✅ Missing variant data (fills defaults)

### LIVE-Only Fallback

If storefront blocks:
- ✅ Product still published to LIVE
- ✅ Tagged as `LIVE_ONLY`
- ✅ Alert sent to Discord/Telegram

### Blocker Detection

Catches:
- 🔴 Price too low
- 🔴 Images missing/small
- 🔴 Variants incomplete
- 🟡 Low inventory (warning)
- 🟡 Suspicious text in images

## 📊 Reports

Check logs:
```bash
tail -f /var/log/tiktok_preflight.log
```

View latest report:
```bash
cat /tmp/tiktok_preflight_latest.json
```

## 🚨 Alerts

### Discord Webhook

Set in `.env`:
```bash
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

### Telegram Bot

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 📈 Next Steps

Once working, you can add:
1. Supabase dashboard integration
2. OCR watermark detection
3. CSV compliance reports
4. Auto-retry logic
5. TikTok API eligibility checks

---

**Status**: Ready for production
**Last Updated**: 2025-12-30
