# POD Pipeline Configuration Guide

Complete guide to configuring the POD Pipeline for RunPod serverless, Printify, and Claude API.

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)

Run the interactive configuration script:

```bash
./setup-pod-config.sh
```

This will guide you through configuring:
- RunPod Serverless (for image generation)
- Printify API (for product creation)
- Claude API (optional, for metadata generation)

### Option 2: Manual Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```bash
   nano .env
   ```

3. Validate your configuration:
   ```bash
   ./check-pod-config.sh
   ```

## 🔐 Required Credentials

### 1. RunPod Serverless

**What it's for**: AI image generation using serverless ComfyUI

**How to get credentials**:

1. **Create RunPod account**: https://www.runpod.io/console
2. **Get API key**:
   - Visit: https://www.runpod.io/console/user/settings
   - Click "API Keys" → "Create API Key"
   - Copy the key (starts with your RunPod username)

3. **Get Endpoint URL**:
   - Visit: https://www.runpod.io/console/serverless
   - Click on your ComfyUI endpoint
   - Copy the endpoint URL
   - Should look like: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync`

**Add to .env**:
```bash
RUNPOD_API_KEY=your-actual-api-key-here
COMFYUI_API_URL=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

**Common Issues**:
- ❌ **401 Unauthorized**: API key is missing or invalid
  - Fix: Double-check key from RunPod settings
  - Make sure there are no spaces or quotes in .env file
- ❌ **404 Not Found**: Endpoint ID is incorrect
  - Fix: Copy the full endpoint URL from RunPod console
- ⏱️ **Timeout**: Endpoint may be inactive
  - Fix: Visit RunPod console to wake up the endpoint

### 2. Printify API

**What it's for**: Product creation, image upload, and publishing

**How to get credentials**:

1. **Create Printify account**: https://printify.com/
2. **Get API key**:
   - Visit: https://printify.com/app/account/api
   - Click "Generate Token" or copy existing token
   - Save the token securely

3. **Get Shop ID**:
   - Visit: https://printify.com/app/stores
   - Your shop ID is visible in the store settings
   - Or find it in the API documentation section

4. **Connect Sales Channel** (IMPORTANT):
   - Visit: https://printify.com/app/stores
   - Click "Add Sales Channel"
   - Connect Shopify, Etsy, WooCommerce, etc.
   - **Required for publishing** - products can be created but not published without this

**Add to .env**:
```bash
PRINTIFY_API_KEY=your-printify-api-token
PRINTIFY_SHOP_ID=your-shop-id-number
PRINTIFY_BLUEPRINT_ID=77      # 77 = Gildan 18500 Hoodie
PRINTIFY_PROVIDER_ID=39       # 39 = SwiftPOD (recommended)
PRINTIFY_DEFAULT_PRICE_CENTS=3499  # $34.99
```

**Blueprint Options**:
- `77` = Gildan 18500 Heavy Blend Hoodie (recommended for POD)
- `3` = Gildan 5000 T-Shirt
- `380` = Gildan 64000 Softstyle T-Shirt
- See full list: https://developers.printify.com/docs/catalog.html

**Provider Options**:
- `39` = SwiftPOD (US-based, reliable, recommended)
- `99` = Printify Choice (global network)
- Full list: https://developers.printify.com/docs/providers.html

**Common Issues**:
- ❌ **401 Unauthorized**: API key is invalid
  - Fix: Regenerate token in Printify dashboard
- ❌ **Publishing fails**: "No sales channels connected"
  - Fix: Connect Shopify/Etsy in Printify dashboard
  - Publishing works without channels, but products won't appear in store
- ⚠️ **Product created but not published**: Expected if no sales channels
  - Product still exists in Printify catalog
  - Can manually publish later from dashboard

### 3. Claude API (Optional)

**What it's for**: Automated generation of product titles and descriptions

**How to get credentials**:

1. **Create Anthropic account**: https://console.anthropic.com/
2. **Get API key**:
   - Visit: https://console.anthropic.com/settings/keys
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-`)
3. **Add credits** (required):
   - Visit: https://console.anthropic.com/settings/billing
   - Add payment method and credits
   - ~$0.01 per metadata generation

**Add to .env**:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**Fallback Behavior**:
If Claude API is not configured, the pipeline will:
- Use simple timestamp-based titles: "POD Design - 20260121-103045"
- Use generic descriptions: "Unique AI-generated [theme] design for print-on-demand"
- Still work perfectly, just with less creative metadata

**Common Issues**:
- ❌ **401 Unauthorized**: API key is invalid
  - Fix: Check key from Anthropic console
- ❌ **403 Forbidden**: Insufficient credits
  - Fix: Add credits in billing settings
- ⚠️ **Fallback mode**: Expected if key not configured

## 🧪 Testing Your Configuration

### 1. Validate Configuration

Check all credentials and connectivity:

```bash
./check-pod-config.sh
```

This script will:
- ✅ Verify all API keys are set
- ✅ Test connectivity to RunPod
- ✅ Test Printify authentication
- ✅ Check shop access
- ✅ Verify Python dependencies
- ⚠️ Warn about optional missing configs

**Example Output**:
```
🔍 POD Pipeline - Configuration Checker
========================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣  RunPod Serverless Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ RUNPOD_API_KEY: Configured (username...xyz)
   Testing RunPod connection...
   ✅ Connection successful (HTTP 200)

✅ COMFYUI_API_URL: https://api.runpod.ai/v2/qm6ofmy96f3htl/runsync
   ℹ️  Using RunPod serverless

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2️⃣  Printify Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PRINTIFY_API_KEY: Configured (eyJhbGc...xyz)
   Testing Printify connection...
   ✅ Authentication successful

✅ PRINTIFY_SHOP_ID: 12345678
   Testing shop access...
   ✅ Shop access confirmed
```

### 2. Test Image Generation

Start the gateway and test generation:

```bash
# Terminal 1: Start gateway
./start-gateway-runpod.sh

# Terminal 2: Test generation
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "test generation",
    "width": 1024,
    "height": 1024,
    "steps": 20
  }'
```

**Expected Response**:
```json
{
  "prompt_id": "abc123-def456",
  "status": "COMPLETED",
  "images": [
    {
      "id": "generated_xyz789_0",
      "path": "/workspace/comfyui/output/generated_xyz789_0.png"
    }
  ],
  "source": "runpod"
}
```

### 3. Test Full Pipeline

Run proof-of-life to test end-to-end:

```bash
./run-pod-pipeline.sh --theme "test design" --no-publish
```

This tests:
1. ✅ Metadata generation (Claude API or fallback)
2. ✅ Image generation (RunPod)
3. ✅ Gateway integration
4. ⏭️ Publishing (skipped with --no-publish)

## 🔧 Advanced Configuration

### Custom ComfyUI Workflow

Edit `pod-pipeline.py` to customize the generation workflow:

```python
def build_pod_workflow(self, prompt: str, seed: Optional[int] = None) -> Dict[str, Any]:
    # Modify workflow here
    workflow = {
        # Your custom nodes
    }
    return workflow
```

### Custom Printify Settings

Override defaults per-request:

```python
# In pod-pipeline.py
response = requests.post(
    f"{self.gateway_url}/api/publish/{image_id}",
    json={
        "title": metadata["title"],
        "description": metadata.get("description", ""),
        "blueprint_id": 380,  # Softstyle T-Shirt instead of Hoodie
        "provider_id": 99,    # Printify Choice instead of SwiftPOD
        "price_cents": 1999,  # $19.99 for t-shirts
        "auto_approve": True
    }
)
```

### Multiple Printify Shops

To use different shops for different products:

1. Create multiple shop configurations in `.env`:
   ```bash
   PRINTIFY_SHOP_ID_HOODIES=12345
   PRINTIFY_SHOP_ID_TSHIRTS=67890
   ```

2. Modify gateway to select shop based on blueprint:
   ```python
   # In gateway/app/main.py
   shop_id = (
       config.PRINTIFY_SHOP_ID_HOODIES
       if blueprint_id == 77
       else config.PRINTIFY_SHOP_ID_TSHIRTS
   )
   ```

## 🐛 Troubleshooting

### RunPod Issues

**Problem**: 401 Unauthorized
```
❌ RunPod authentication failed (401 Unauthorized)
💡 Fix: Set RUNPOD_API_KEY in .env file
```

**Solution**:
1. Get fresh API key from RunPod console
2. Update `.env`:
   ```bash
   RUNPOD_API_KEY=your-new-key
   ```
3. Restart gateway

**Problem**: Timeout during generation
```
⏱️ RunPod request timeout after 300s
```

**Solution**:
1. Check endpoint status in RunPod console
2. Increase timeout in `pod-pipeline.py`:
   ```python
   timeout=600  # Increase to 10 minutes
   ```
3. Consider using a faster endpoint/GPU

### Printify Issues

**Problem**: Publishing fails - No sales channels
```
⚠️ Product created but not published: No sales channels connected
💡 Tip: Connect a sales channel in Printify dashboard
```

**Solution**:
1. Visit https://printify.com/app/stores
2. Click "Add Sales Channel"
3. Connect Shopify, Etsy, or other platform
4. Product will be in catalog, can publish manually

**Problem**: Image upload fails
```
❌ Failed to upload image
```

**Solution**:
1. Check image format (must be PNG, JPEG)
2. Check image size (recommended 4500x5400 for POD)
3. Verify file exists and is readable
4. Check Printify API limits (rate limiting)

### Claude API Issues

**Problem**: 401 Unauthorized
```
❌ Claude API authentication failed
```

**Solution**:
1. Verify key from https://console.anthropic.com/settings/keys
2. Check for spaces or quotes in `.env`
3. Regenerate key if needed

**Problem**: Fallback metadata used
```
⚠️ Claude API key not configured, using fallback metadata
```

**Solution**:
- This is expected behavior if `ANTHROPIC_API_KEY` is not set
- Pipeline still works, just with generic titles
- Set API key to enable AI-generated metadata

## 📊 Configuration Matrix

| Feature | Required? | Impact if Missing |
|---------|-----------|-------------------|
| RUNPOD_API_KEY | ✅ Required | Generation fails with 401 |
| COMFYUI_API_URL | ✅ Required | Generation endpoint not found |
| PRINTIFY_API_KEY | ✅ Required | Publishing fails |
| PRINTIFY_SHOP_ID | ✅ Required | Cannot create products |
| Sales Channel | ⚠️ Recommended | Products created but not published |
| ANTHROPIC_API_KEY | ⬜ Optional | Uses fallback metadata |
| PRINTIFY_BLUEPRINT_ID | ⬜ Optional | Defaults to 77 (Hoodie) |
| PRINTIFY_PROVIDER_ID | ⬜ Optional | Defaults to 39 (SwiftPOD) |

## 🔒 Security Best Practices

### Protect Your Credentials

1. **Never commit `.env` to git**:
   ```bash
   # Already in .gitignore
   .env
   .env.local
   .env.*.local
   ```

2. **Use environment variables in production**:
   ```bash
   export RUNPOD_API_KEY="your-key"
   export PRINTIFY_API_KEY="your-key"
   ./start-gateway-runpod.sh
   ```

3. **Rotate keys regularly**:
   - RunPod: Create new key, update `.env`, delete old key
   - Printify: Regenerate token in dashboard
   - Claude: Create new key in console

### Access Control

1. **Limit API key permissions**:
   - RunPod: Use endpoint-specific keys if available
   - Printify: Use shop-specific tokens
   - Claude: Use project-specific keys

2. **Monitor usage**:
   - RunPod: Check usage in console
   - Printify: Monitor API calls in dashboard
   - Claude: Track spend in billing

## 📚 Additional Resources

- [POD Pipeline Guide](./POD_PIPELINE_GUIDE.md) - Complete usage guide
- [Gateway Features](./GATEWAY_FEATURES.md) - Gateway capabilities
- [RunPod Setup](./RUNPOD_SETUP.md) - RunPod deployment guide
- [Printify API Docs](https://developers.printify.com/) - Official API reference
- [Claude API Docs](https://docs.anthropic.com/) - Anthropic documentation

## 🆘 Getting Help

1. **Check configuration**: `./check-pod-config.sh`
2. **View logs**: Check terminal where gateway is running
3. **Test individually**: Test RunPod, Printify, Claude separately
4. **GitHub Issues**: Report bugs at repository issues page

---

**Last Updated**: 2026-01-21
**Version**: 2.0
