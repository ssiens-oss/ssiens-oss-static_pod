# POD Pipeline - Production Run Guide

Complete step-by-step guide for running the POD pipeline in production and creating real products.

---

## 📋 Prerequisites Checklist

Before you start, make sure you have:

- [x] **API Keys Configured** - Run `npm run test:config` to verify
- [ ] **ComfyUI Running** - Either locally or on RunPod
- [ ] **Storage Directory** - `./designs/` should exist
- [ ] **Printify Shop** - Active shop with API access

---

## 🚀 Step-by-Step Production Run

### **Step 1: Start ComfyUI** 🎨

ComfyUI must be running before you can generate designs.

#### **Option A: Local ComfyUI**

```bash
# Navigate to your ComfyUI directory
cd /path/to/ComfyUI

# Start ComfyUI
python main.py

# ComfyUI should be accessible at http://localhost:8188
```

Test it:
```bash
curl http://localhost:8188/system_stats
```

#### **Option B: RunPod ComfyUI**

1. Go to RunPod dashboard
2. Deploy a ComfyUI pod (GPU recommended: RTX 3090 or A4000)
3. Note your pod URL (e.g., `https://xxx-xxx.proxy.runpod.net`)
4. Update `.env`:
   ```env
   COMFYUI_API_URL=https://your-pod-id.proxy.runpod.net
   ```

Test it:
```bash
curl https://your-pod-id.proxy.runpod.net/system_stats
```

---

### **Step 2: Verify Configuration** ✅

```bash
npm run test:config
```

**Expected output:**
```
✅ Configuration loaded successfully!

🎨 ComfyUI:
   URL: http://localhost:8188
   ✅ ComfyUI is reachable

🤖 Claude AI:
   API Key: ✓ sk-ant-********

✅ Printify:
   API Key: ✓ eyJ0********
   Shop ID: 25860767

✅ All checks passed!
```

If you see errors, fix them before proceeding.

---

### **Step 3: Choose Your Settings** ⚙️

Edit `.env` to configure pipeline behavior:

#### **Safe Test Mode** (Recommended First)
```env
AUTO_PUBLISH=false
ENABLE_PLATFORMS=printify
BATCH_SIZE=1
```

This will:
- Create designs and products
- NOT auto-publish to your store
- Only use Printify
- Process 1 design at a time

#### **Production Mode**
```env
AUTO_PUBLISH=true
ENABLE_PLATFORMS=printify,shopify
BATCH_SIZE=5
```

This will:
- Auto-publish products
- Can publish to multiple platforms
- Process multiple designs

---

### **Step 4: Run Production Test** 🚀

```bash
npm run test:production
```

**What happens:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀 POD Pipeline Production Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Step 1: Loading configuration...
✅ Configuration loaded successfully
   Enabled Platforms: printify
   Auto-Publish: No

🔧 Step 2: Initializing orchestrator...
✅ Orchestrator initialized

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎨 Running POD Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️ 🚀 Starting POD automation pipeline...
ℹ️ 📝 Generating creative prompts with Claude...
✅ ✓ Generated 1 creative prompts
ℹ️ 🎨 Generating AI images with ComfyUI...
✅ ✓ Generated 1 images
ℹ️ 💾 Saving images to storage...
✅ ✓ Saved 1 images
ℹ️ 📦 Creating tshirt products for: Cyberpunk Neon City
✅ ✓ Created 1 products
✅ ✅ Pipeline complete! Created 1 products in 45.23s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 Pipeline Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: ✅ SUCCESS
Total Time: 45.23s

🎨 Generated Images:
   1. img_1704096123_abc123
      URL: file:///home/user/ssiens-oss-static_pod/designs/img_1704096123_abc123.png
      Prompt: A futuristic cyberpunk cityscape with neon lights...

📦 Created Products:
   1. PRINTIFY - tshirt
      Product ID: 12345678
      URL: https://printify.com/app/products/12345678
```

---

### **Step 5: Verify Results** 📊

#### **Check Generated Images**
```bash
ls -lh ./designs/
```

You should see:
```
img_1704096123_abc123.png
img_1704096123_abc123.metadata.json
```

View the image:
```bash
# On Linux
xdg-open ./designs/img_*.png

# On macOS
open ./designs/img_*.png

# Or just navigate to the folder
```

#### **Check Printify Dashboard**

1. Go to https://printify.com
2. Navigate to "My Products"
3. You should see your new product
4. Status will be "Draft" if `AUTO_PUBLISH=false`

#### **Check Product Details**

The product should have:
- ✅ Your generated design image
- ✅ Title from Claude's prompt
- ✅ Description
- ✅ Multiple sizes (S-3XL)
- ✅ Pricing ($19.99 for T-shirt by default)

---

### **Step 6: Publish Product** 📢

If you ran in test mode (`AUTO_PUBLISH=false`), you need to manually publish:

#### **Option A: Publish via Printify Dashboard**

1. Go to Printify → My Products
2. Find your product
3. Click "Publish to Store"
4. Select your connected sales channel

#### **Option B: Enable Auto-Publish**

Edit `.env`:
```env
AUTO_PUBLISH=true
```

Run again:
```bash
npm run test:production
```

---

## 🔄 Production Workflow

### **Single Design**

```bash
npm run test:production
```

- Creates 1 design
- Theme: "cyberpunk neon city"
- Product: T-shirt

### **Custom Design via Web UI**

```bash
npm run dev
```

Then:
1. Open http://localhost:5173
2. Enter your theme/niche
3. Choose product types
4. Click "Run Single Drop"
5. Watch live preview

### **Batch Processing**

Edit `run-production-test.ts`:
```typescript
const result = await orchestrator.run({
  theme: 'minimalist nature',
  style: 'clean, simple, modern',
  niche: 'eco-conscious buyers',
  productTypes: ['tshirt', 'hoodie'],
  count: 5,  // Generate 5 designs
  autoPublish: true
})
```

Run:
```bash
npm run test:production
```

---

## 📈 Monitoring & Analytics

### **View Logs**

Logs are printed to console in real-time:

```
ℹ️ Starting POD automation pipeline...
✅ Generated 3 creative prompts
⚠️ Retrying ComfyUI prompt submission (attempt 1)
❌ Failed to create tshirt: Printify API error
```

### **Check Pipeline Stats**

Add to your script:
```typescript
const stats = await orchestrator.getStats()
console.log('Pipeline Stats:', stats)
```

### **Export Results**

Results are saved to:
- **Images:** `./designs/*.png`
- **Metadata:** `./designs/*.metadata.json`
- **Logs:** Console output (redirect to file if needed)

---

## 💰 Cost Estimation

Per design generation:

| Service | Cost | Notes |
|---------|------|-------|
| Claude API | ~$0.01 | Prompt generation |
| ComfyUI (Local) | $0.00 | Free if running locally |
| ComfyUI (RunPod) | ~$0.05 | GPU rental (RTX 3090) |
| Printify | $0.00 | Free until sold |
| Storage (Local) | $0.00 | Free |
| Storage (S3) | ~$0.001 | Per GB stored |
| **Total (Local)** | **~$0.01** | |
| **Total (RunPod)** | **~$0.06** | |

### **Batch Cost Example**

10 designs with local ComfyUI:
- 10 × $0.01 = **$0.10**

50 designs with RunPod:
- 50 × $0.06 = **$3.00**

---

## 🐛 Troubleshooting

### **ComfyUI Not Responding**

**Symptom:**
```
❌ Cannot reach ComfyUI
   Error: fetch failed
```

**Solutions:**
1. Check ComfyUI is running: `curl http://localhost:8188/system_stats`
2. Verify port 8188 is open: `netstat -an | grep 8188`
3. Check firewall settings
4. Try restarting ComfyUI

### **Claude API Errors**

**Symptom:**
```
❌ Claude API error: 401 Unauthorized
```

**Solutions:**
1. Verify API key: `npm run test:config`
2. Check account has credits: https://console.anthropic.com
3. Ensure key hasn't expired

### **Printify Creation Failed**

**Symptom:**
```
❌ Failed to create tshirt: Printify API error
```

**Solutions:**
1. Check API key is valid
2. Verify shop ID is correct
3. Ensure shop is active (not suspended)
4. Check image URL is accessible
5. Verify product blueprint (3 for T-shirts)

### **Image Generation Timeout**

**Symptom:**
```
❌ ComfyUI generation timed out
```

**Solutions:**
1. Increase timeout in `.env`: `COMFYUI_TIMEOUT=600000` (10 minutes)
2. Use faster GPU
3. Reduce image size (512x512 instead of 1024x1024)
4. Reduce steps (15 instead of 20)

### **Rate Limits**

**Symptom:**
```
⚠️ Rate limit exceeded for Claude API
```

**Solutions:**
- Pipeline automatically retries with backoff
- Reduce batch size
- Add delays between requests

---

## 🎯 Best Practices

### **1. Start Small**
- Run 1 design first
- Verify it works end-to-end
- Then scale up

### **2. Test Mode First**
```env
AUTO_PUBLISH=false
```
- Review products before publishing
- Avoid mistakes in live store

### **3. Monitor Costs**
- Track ComfyUI GPU time
- Monitor Claude API usage
- Set daily budgets

### **4. Quality Control**
- Review generated images
- Check product mockups
- Verify descriptions and tags

### **5. Backup Configuration**
```bash
cp .env .env.backup.$(date +%s)
```

### **6. Version Control**
- Commit code changes
- Don't commit `.env`
- Track successful prompts

---

## 📊 Success Metrics

Track these metrics:

- ✅ **Generation Success Rate:** % of successful generations
- ✅ **Average Time:** Time per design
- ✅ **Product Creation Rate:** % of products successfully created
- ✅ **Publishing Success:** % of products published
- ✅ **Cost Per Design:** Total cost / number of designs

---

## 🔒 Security Checklist

Before production:

- [ ] `.env` is in `.gitignore`
- [ ] API keys are not in code
- [ ] No keys in git history
- [ ] Using HTTPS for RunPod
- [ ] Regular key rotation schedule
- [ ] Different keys for dev/prod

---

## 🎉 Ready for Production!

You're now ready to run the POD pipeline in production!

**Quick Command Reference:**

```bash
# Test configuration
npm run test:config

# Run production test
npm run test:production

# Start web UI
npm run dev

# Setup new API keys
npm run setup:keys
```

**Need Help?**
- [Quick Start Guide](docs/QUICK_START.md)
- [API Keys Setup](API_KEYS_SETUP.md)
- [Full Documentation](docs/POD_PIPELINE_GUIDE.md)

---

Happy selling! 🎨💰
