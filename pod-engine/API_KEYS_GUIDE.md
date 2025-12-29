# API Keys Configuration Guide

Complete guide to obtaining and configuring all API keys for StaticWaves POD Engine.

## 🔑 Required Keys (Core Functionality)

### 1. Printify API Key

**Purpose**: Create and manage print-on-demand products

**How to Get**:
1. Go to https://printify.com
2. Sign up for a Printify account
3. Navigate to **My Account** → **Connections** → **API**
4. Click **Generate API Token**
5. Copy the token

**Add to .env**:
```env
PRINTIFY_API_KEY=your_token_here
PRINTIFY_SHOP_ID=your_shop_id
```

**Finding Shop ID**:
- In Printify dashboard, go to **My Stores**
- Click on your store
- Shop ID is in the URL: `printify.com/app/stores/{SHOP_ID}/products`

**Cost**: Free tier available (5 products/month), paid plans start at $29/month

---

### 2. Shopify Credentials

**Purpose**: Publish products to Shopify store

**How to Get**:
1. Go to https://shopify.com and create a store
2. In your Shopify admin, go to **Apps** → **Develop apps**
3. Click **Create an app**
4. Name it "StaticWaves POD Engine"
5. Under **API Credentials**, click **Configure Admin API scopes**
6. Enable these scopes:
   - `read_products`
   - `write_products`
   - `read_inventory`
   - `write_inventory`
   - `read_files`
   - `write_files`
7. Click **Install app**
8. Copy the **Admin API access token**

**Add to .env**:
```env
SHOPIFY_STORE=yourstore
SHOPIFY_TOKEN=shpat_xxxxxxxxxxxxx
```

**Note**: `SHOPIFY_STORE` is just the store name (e.g., `mystore` from `mystore.myshopify.com`)

**Cost**: Shopify Basic plan starts at $29/month

---

### 3. ComfyUI (Local/RunPod)

**Purpose**: AI image generation

**Local Setup**:
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py --listen 0.0.0.0 --port 8188
```

**Add to .env**:
```env
COMFY_API=http://127.0.0.1:8188
```

**RunPod Setup**:
- Automatically configured by `runpod_install.sh`
- Uses RunPod proxy URL: `https://{POD_ID}-8188.proxy.runpod.net`

**Cost**: Free (local) or RunPod GPU pricing ($0.44-$1.89/hour)

---

## 🎯 Optional Keys (Enhanced Features)

### 4. TikTok Shop API

**Purpose**: Publish products to TikTok Shop

**How to Get**:
1. Go to https://seller-us.tiktok.com
2. Create a TikTok Seller account
3. Apply for **TikTok Shop API** access:
   - Go to **Partner Center** → **API Access**
   - Submit application (requires business verification)
4. Once approved:
   - Go to **Developer Portal**
   - Create an app
   - Copy App Key, App Secret
   - Generate access token

**Add to .env**:
```env
TIKTOK_ACCESS_TOKEN=your_access_token
TIKTOK_REFRESH_TOKEN=your_refresh_token
TIKTOK_SELLER_ID=your_seller_id
TIKTOK_APP_KEY=your_app_key
TIKTOK_APP_SECRET=your_app_secret
TIKTOK_REGION=US
```

**Cost**: Free (TikTok takes 5% commission on sales)

**Alternative (CSV Upload)**:
- If API access is pending, use `tools/tiktok_feed_generator.py`
- Generates XLSX/CSV files for manual upload
- No API keys needed

---

### 5. Anthropic Claude API

**Purpose**: AI-powered product descriptions, SEO, content generation

**How to Get**:
1. Go to https://console.anthropic.com
2. Sign up for an account
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-`)

**Add to .env**:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Cost**: Pay-as-you-go (~$0.50 per 100 products for descriptions)

---

### 6. OpenAI API

**Purpose**: Alternative AI content generation, DALL-E image generation

**How to Get**:
1. Go to https://platform.openai.com
2. Sign up and add payment method
3. Navigate to **API Keys**
4. Click **Create new secret key**
5. Copy the key (starts with `sk-`)

**Add to .env**:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

**Cost**: GPT-4: ~$0.03 per 1K tokens, GPT-3.5: ~$0.002 per 1K tokens

---

### 7. Stripe (Billing & Payments)

**Purpose**: Usage-based billing for multi-client agency setup

**How to Get**:
1. Go to https://stripe.com
2. Create an account
3. Navigate to **Developers** → **API Keys**
4. Copy both:
   - Publishable key (starts with `pk_`)
   - Secret key (starts with `sk_`)

**Add to .env**:
```env
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
```

**Note**: Use test keys (`pk_test_`, `sk_test_`) during development

**Cost**: Free (2.9% + $0.30 per transaction)

---

## 🔒 Optional Keys (Advanced)

### 8. AWS S3 (Backups & Storage)

**Purpose**: Backup queues, outputs, and client data

**How to Get**:
1. Go to https://aws.amazon.com/console
2. Navigate to **IAM** → **Users** → **Add User**
3. Enable **Programmatic access**
4. Attach policy: `AmazonS3FullAccess`
5. Copy Access Key ID and Secret Access Key

**Add to .env**:
```env
S3_BUCKET=staticwaves-backup
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

**Cost**: ~$0.023/GB/month storage, minimal for backups

---

### 9. RunPod API

**Purpose**: Programmatic pod management, scaling

**How to Get**:
1. Go to https://www.runpod.io/console
2. Click your profile → **Settings**
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Copy the key

**Add to .env**:
```env
RUNPOD_API_KEY=your_api_key
RUNPOD_TEMPLATE_ID=your_template_id
RUNPOD_GPU_TYPE=RTX_4090
```

**Cost**: Free (for API access, you pay for GPU usage)

---

### 10. Twilio (SMS Notifications)

**Purpose**: Alert clients when products are published

**How to Get**:
1. Go to https://www.twilio.com
2. Sign up and verify your phone
3. Get $15 free trial credit
4. Navigate to **Console**
5. Copy Account SID and Auth Token
6. Get a Twilio phone number

**Add to .env**:
```env
TWILIO_SID=ACxxxxxxxxxxxxx
TWILIO_TOKEN=your_auth_token
TWILIO_FROM=+1234567890
```

**Cost**: ~$0.0075 per SMS

---

### 11. SendGrid (Email Notifications)

**Purpose**: Send email alerts, reports, invoices

**How to Get**:
1. Go to https://sendgrid.com
2. Sign up (free tier: 100 emails/day)
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Select **Full Access**
6. Copy the key

**Add to .env**:
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
```

**Cost**: Free tier (100 emails/day), paid plans from $15/month

---

### 12. DeepL (Translation)

**Purpose**: Multi-language product descriptions

**How to Get**:
1. Go to https://www.deepl.com/pro-api
2. Sign up for API account
3. Navigate to **Account** → **API Keys**
4. Copy your authentication key

**Add to .env**:
```env
DEEPL_API_KEY=your_api_key
```

**Cost**: Free tier (500,000 characters/month), Pro starts at $5.49/month

---

## 🚀 Quick Setup Guide

### Minimum Viable Setup (Core Features)

**Required** for basic POD automation:
```env
# Essential
PRINTIFY_API_KEY=your_key
PRINTIFY_SHOP_ID=your_shop_id
SHOPIFY_STORE=yourstore
SHOPIFY_TOKEN=your_token
COMFY_API=http://127.0.0.1:8188
```

**Cost**: ~$58/month (Printify + Shopify)

---

### Recommended Setup (Full Features)

**For AI-powered content + publishing**:
```env
# Core
PRINTIFY_API_KEY=your_key
PRINTIFY_SHOP_ID=your_shop_id
SHOPIFY_STORE=yourstore
SHOPIFY_TOKEN=your_token
COMFY_API=http://127.0.0.1:8188

# AI Content
ANTHROPIC_API_KEY=sk-ant-xxxxx

# TikTok (manual CSV upload)
TIKTOK_SAFE_MODE=1
```

**Cost**: ~$60/month + pay-as-you-go AI costs

---

### Enterprise Setup (Agency/White-Label)

**For multi-client SaaS deployment**:
```env
# All core + AI keys
# Plus:
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
TWILIO_SID=AC...
SENDGRID_API_KEY=SG...

# Agency features
MULTI_CLIENT=1
WHITE_LABEL=1
```

**Cost**: ~$150/month + usage-based AI/notification costs

---

## 🔧 Configuration Steps

### 1. Copy Template

```bash
cd /home/user/ssiens-oss-static_pod/pod-engine
cp .env.example .env
```

### 2. Edit File

```bash
nano .env
```

### 3. Add Your Keys

Replace empty values with your API keys:
```env
PRINTIFY_API_KEY=     # ← Add your key here
```

Becomes:
```env
PRINTIFY_API_KEY=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Save and Exit

- Press `Ctrl+O` to save
- Press `Ctrl+X` to exit

### 5. Restart Services

```bash
# If using supervisor (RunPod)
supervisorctl restart staticwaves:*

# If running manually
python workers/printify_worker.py
python workers/shopify_worker.py
```

---

## 🔒 Security Best Practices

1. **Never commit .env files to git**
   - Already in `.gitignore`
   - Use `.env.example` for templates

2. **Use environment-specific keys**
   - Development: Test/sandbox keys
   - Production: Live keys with restricted scopes

3. **Rotate keys regularly**
   - Monthly rotation recommended
   - Immediately rotate if compromised

4. **Restrict API scopes**
   - Only enable necessary permissions
   - Use read-only keys where possible

5. **Backup .env securely**
   - Store in password manager (1Password, LastPass)
   - Encrypt backups if storing in S3

---

## 📊 Cost Summary

| Service | Free Tier | Paid Plan | Required? |
|---------|-----------|-----------|-----------|
| Printify | 5 products/mo | $29/mo | ✅ Yes |
| Shopify | None | $29/mo | ✅ Yes |
| ComfyUI | Free (local) | GPU costs | ✅ Yes |
| TikTok Shop | Free | 5% commission | ⚠️ Optional |
| Anthropic | $5 credit | Pay-as-you-go | ⚠️ Optional |
| OpenAI | $5 credit | Pay-as-you-go | ⚠️ Optional |
| Stripe | Free | 2.9% + $0.30 | ⚠️ Optional |
| AWS S3 | 5GB | $0.023/GB | ⚠️ Optional |
| Twilio | $15 credit | $0.0075/SMS | ⚠️ Optional |
| SendGrid | 100/day | $15/mo | ⚠️ Optional |

**Minimum Cost**: ~$58/month (Printify + Shopify)
**Recommended**: ~$60/month + AI usage
**Enterprise**: ~$150/month + usage

---

## 🆘 Troubleshooting

### API Key Not Working

**Printify**:
- Check key hasn't expired
- Verify shop ID matches your store
- Ensure you have an active Printify plan

**Shopify**:
- Verify all required API scopes are enabled
- Check token hasn't been revoked
- Ensure store name is correct (without `.myshopify.com`)

**TikTok**:
- Most common issue: API access not approved yet
- Use CSV export method while waiting for approval
- Check token hasn't expired (refresh tokens valid for 90 days)

### Services Not Starting

```bash
# Check if .env is loaded
source .env
echo $PRINTIFY_API_KEY  # Should print your key

# Check for syntax errors
cat .env | grep -v '^#' | grep '='
```

### Testing API Keys

```bash
# Test Printify
curl -H "Authorization: Bearer $PRINTIFY_API_KEY" \
     https://api.printify.com/v1/shops.json

# Test Shopify
curl -H "X-Shopify-Access-Token: $SHOPIFY_TOKEN" \
     https://$SHOPIFY_STORE.myshopify.com/admin/api/2024-01/products.json

# Test ComfyUI
curl http://127.0.0.1:8188/system_stats
```

---

## 📞 Support

**Need help getting API keys?**
- Printify Support: https://help.printify.com
- Shopify Support: https://help.shopify.com
- TikTok Seller Support: https://seller-us-support.tiktok.com

**Issues with this guide?**
- GitHub Issues: https://github.com/YOUR_ORG/ssiens-oss-static_pod/issues
- Email: support@staticwaves.ai

---

## ✅ Verification Checklist

Before running the POD Engine, verify:

- [ ] Copied `.env.example` to `.env`
- [ ] Added Printify API key and shop ID
- [ ] Added Shopify store name and token
- [ ] Configured ComfyUI API URL
- [ ] Added AI API keys (if using AI features)
- [ ] Verified all keys with test curl commands
- [ ] `.env` file is in `.gitignore`
- [ ] Restarted all services after configuration

**You're ready to automate! 🚀**
