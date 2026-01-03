# API Keys Setup Guide

This guide will help you securely configure all API keys needed for the POD Pipeline.

## Quick Setup

### Option 1: Interactive Setup Script (Recommended)

Run the interactive setup script:

```bash
npm run setup:keys
# or
./setup-keys.sh
```

This will guide you through setting up:
- ✅ ComfyUI connection
- ✅ Claude API key
- ✅ Storage configuration
- ✅ Platform integrations (Printify, Shopify, Etsy, TikTok, etc.)
- ✅ Pipeline options

### Option 2: Manual Setup

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your favorite editor:
```bash
nano .env
# or
vim .env
# or
code .env
```

3. Fill in the values (see sections below)

## Required Configuration

These settings are **required** for the pipeline to work:

### 1. ComfyUI

```env
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/data/comfyui/output
```

**Where to get it:**
- If running locally: `http://localhost:8188`
- If using RunPod: `https://your-pod-id.proxy.runpod.net`

**Test it:**
```bash
curl http://localhost:8188/system_stats
```

### 2. Claude API (Anthropic)

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**Where to get it:**
1. Go to https://console.anthropic.com
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new key
5. Copy the key (starts with `sk-ant-`)

**Important:** Keep this key secret! Never commit it to git.

### 3. Storage

```env
STORAGE_TYPE=local
STORAGE_PATH=./designs
```

**Options:**
- `local` - Save to local disk (easiest for testing)
- `s3` - Use AWS S3 (requires AWS credentials)
- `gcs` - Use Google Cloud Storage (requires GCS credentials)

## Optional Platform Integrations

Enable only the platforms you want to use:

```env
ENABLE_PLATFORMS=printify,shopify,etsy
```

### Printify

```env
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
```

**Setup steps:**
1. Go to https://printify.com
2. Create an account or log in
3. Navigate to Settings → Connections
4. Generate API token
5. Copy API token and Shop ID from the URL

**Documentation:** https://developers.printify.com

### Shopify

```env
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your-access-token
SHOPIFY_API_VERSION=2024-01
```

**Setup steps:**
1. Go to your Shopify admin
2. Apps → Develop apps
3. Create an app
4. Configure Admin API scopes:
   - `write_products`
   - `read_products`
   - `write_inventory`
5. Install app and copy access token

**Documentation:** https://shopify.dev/docs/api/admin-rest

### Etsy

```env
ETSY_API_KEY=your-api-key
ETSY_SHOP_ID=your-shop-id
ETSY_ACCESS_TOKEN=your-oauth-token
```

**Setup steps:**
1. Go to https://www.etsy.com/developers
2. Register your application
3. Get API Key
4. Complete OAuth flow for access token
5. Find Shop ID in your shop URL

**Documentation:** https://developers.etsy.com

### TikTok Shop

```env
TIKTOK_APP_KEY=your-app-key
TIKTOK_APP_SECRET=your-app-secret
TIKTOK_SHOP_ID=your-shop-id
TIKTOK_ACCESS_TOKEN=your-access-token
```

**Setup steps:**
1. Apply for TikTok Shop Seller account
2. Go to TikTok Shop Partner Center
3. Create developer app
4. Complete OAuth flow
5. Get credentials

**Documentation:** https://partner.tiktokshop.com/doc

### Instagram Shopping

```env
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id
```

**Setup steps:**
1. Convert to Instagram Business Account
2. Connect to Facebook Page
3. Set up Meta Business Suite
4. Generate long-lived access token
5. Get Business Account ID

**Documentation:** https://developers.facebook.com/docs/instagram-api

### Facebook Commerce

```env
FACEBOOK_PAGE_ID=your-page-id
FACEBOOK_ACCESS_TOKEN=your-access-token
FACEBOOK_CATALOG_ID=your-catalog-id
```

**Setup steps:**
1. Create Facebook Page
2. Set up Commerce Manager
3. Create product catalog
4. Generate access token
5. Note Page ID and Catalog ID

**Documentation:** https://developers.facebook.com/docs/commerce-platform

## Cloud Storage (Optional)

### AWS S3

```env
STORAGE_TYPE=s3
AWS_S3_BUCKET=my-pod-designs
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key
```

**Setup steps:**
1. Go to AWS Console → S3
2. Create a new bucket
3. Go to IAM → Users
4. Create user with S3 permissions
5. Generate access key
6. Install SDK: `npm install @aws-sdk/client-s3`

### Google Cloud Storage

```env
STORAGE_TYPE=gcs
GCS_BUCKET=my-pod-designs
GCS_PROJECT_ID=my-project-id
GCS_KEY_FILENAME=/path/to/service-account-key.json
```

**Setup steps:**
1. Go to Google Cloud Console
2. Create project
3. Enable Cloud Storage API
4. Create bucket
5. Create service account
6. Download JSON key file
7. Install SDK: `npm install @google-cloud/storage`

## Pipeline Options

```env
# Auto-publish products (set false for testing)
AUTO_PUBLISH=false

# Batch size
BATCH_SIZE=5

# Pricing
DEFAULT_TSHIRT_PRICE=19.99
DEFAULT_HOODIE_PRICE=34.99
```

## Test Your Configuration

After setting up your keys, test the configuration:

```bash
npm run test:config
```

This will:
- ✅ Validate all required settings
- ✅ Check API key formats
- ✅ Test ComfyUI connection
- ✅ Display configured platforms
- ✅ Show validation summary

**Expected output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  POD Pipeline Configuration Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Loading configuration...
✅ Configuration loaded successfully!

🎨 ComfyUI:
   URL: http://localhost:8188
   ✅ Connection successful

🤖 Claude AI:
   API Key: ✓ sk-ant-********
   Model: claude-3-5-sonnet-20241022

✅ All checks passed!
```

## Security Best Practices

### 1. Never Commit `.env` to Git

The `.env` file is already in `.gitignore`. Make sure it stays there!

```bash
# Check it's ignored
git status  # .env should NOT appear
```

### 2. Use Environment Variables in Production

For production deployments, use your platform's environment variable system:

- **Vercel:** Environment Variables in dashboard
- **Heroku:** `heroku config:set`
- **Docker:** `-e` flag or `docker-compose.yml`
- **AWS:** Systems Manager Parameter Store

### 3. Rotate Keys Regularly

Change your API keys periodically, especially if:
- A team member leaves
- You suspect a key was compromised
- Moving from development to production

### 4. Use Different Keys for Different Environments

```bash
# Development
.env.development

# Production
.env.production

# Testing
.env.test
```

### 5. Limit API Key Permissions

Only grant the minimum permissions needed:
- Printify: Product creation only
- Shopify: Products and inventory (not orders)
- AWS: S3 bucket access only

## Troubleshooting

### "Configuration error: XXXX is required"

**Problem:** Missing required environment variable

**Solution:**
```bash
# Run setup script
npm run setup:keys

# Or manually edit .env
nano .env
```

### "API Key is a placeholder"

**Problem:** You haven't replaced the example value

**Solution:**
Replace `your-api-key-here` with your actual API key

### "Cannot reach ComfyUI"

**Problem:** ComfyUI is not running or URL is wrong

**Solution:**
```bash
# Test ComfyUI
curl http://localhost:8188/system_stats

# If using RunPod, check pod is running
# Update COMFYUI_API_URL in .env
```

### "Invalid API key format"

**Problem:** API key doesn't match expected format

**Solution:**
- Claude keys start with `sk-ant-`
- Shopify tokens start with `shpat_`
- Check for extra spaces or quotes

## Getting Help

If you're stuck:

1. **Run the test:** `npm run test:config`
2. **Check logs:** Look for specific error messages
3. **Verify platform docs:** Each platform has different requirements
4. **Read the guide:** [docs/QUICK_START.md](docs/QUICK_START.md)

## Quick Reference

| Service | Key Format | Where to Get |
|---------|-----------|--------------|
| Claude | `sk-ant-...` | https://console.anthropic.com |
| Printify | Various | https://printify.com → Settings → Connections |
| Shopify | `shpat_...` | Store Admin → Apps → Develop apps |
| Etsy | Various | https://www.etsy.com/developers |
| TikTok | Various | https://partner.tiktokshop.com |
| AWS | `AKIA...` | AWS Console → IAM |
| GCS | JSON file | GCP Console → Service Accounts |

---

**Next Steps:**

Once your API keys are configured:

1. Test configuration: `npm run test:config`
2. Start the pipeline: `npm run dev`
3. Read the docs: [docs/QUICK_START.md](docs/QUICK_START.md)

Happy designing! 🎨
