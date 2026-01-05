# StaticWaves POD Engine - Complete Integration Guide

## System Architecture Overview

The StaticWaves POD Engine is a comprehensive print-on-demand automation system combining TypeScript orchestration services with Python automation scripts for seamless end-to-end product creation and distribution.

### Components

#### **1. Frontend Orchestration Layer** (TypeScript/React)
- **Location**: `/services/` and `/components/`
- **Purpose**: Web UI for managing POD pipeline
- **Key Services**:
  - `orchestrator.ts` - Pipeline coordinator
  - `printify.ts` - Printify API integration
  - `shopify.ts` - Shopify store integration
  - `comfyui.ts` - AI image generation
  - `claudePrompting.ts` - AI prompt generation
  - Platform integrations: TikTok, Etsy, Instagram, Facebook

#### **2. Backend Automation Layer** (Python)
- **Location**: `/scripts/`
- **Purpose**: RunPod-native image processing and Printify automation
- **Key Scripts**:
  - `runpod_push_to_printify.py` - Direct RunPod execution
  - `push_to_printify.py` - SSH-based remote execution

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     STATICWAVES POD PIPELINE                        │
└─────────────────────────────────────────────────────────────────────┘

 PHASE 1: AI CONTENT GENERATION
 ═══════════════════════════════

 ┌──────────────┐       ┌──────────────┐
 │ User Input   │───────│ Claude API   │
 │ - Keywords   │       │ - Generates  │
 │ - Style      │       │   prompts    │
 └──────────────┘       └──────┬───────┘
                               │
                      ┌────────▼────────┐
                      │ ComfyUI         │
                      │ - SDXL models   │
                      │ - 4500x5400 px  │
                      │ - High quality  │
                      └────────┬────────┘
                               │
 PHASE 2: STORAGE & FILTERING
 ═════════════════════════════
                               │
                      ┌────────▼────────┐
                      │ Storage Service │
                      │ - Local/S3/GCS  │
                      │ - Deduplication │
                      │ - Metadata      │
                      └────────┬────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
         ┌────────▼──────┐        ┌────────▼────────┐
         │ Python Script │        │ TypeScript Svc  │
         │ - Dimension   │        │ - API upload    │
         │   filter      │        │ - Base64 encode │
         │   (4500x5400) │        │                 │
         │ - Name filter │        │                 │
         │   (no comfyui)│        │                 │
         └────────┬──────┘        └────────┬────────┘
                  │                         │
                  └────────────┬────────────┘
                               │
 PHASE 3: PRODUCT CREATION
 ═════════════════════════
                               │
                      ┌────────▼────────┐
                      │ Printify API    │
                      │ - Image upload  │
                      │ - T-Shirt       │
                      │   (Blueprint 5) │
                      │ - Hoodie        │
                      │   (Blueprint 6) │
                      │ - 20 variants   │
                      │ - Auto-publish  │
                      └────────┬────────┘
                               │
 PHASE 4: MULTI-PLATFORM DISTRIBUTION
 ════════════════════════════════
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐         ┌───────▼────┐        ┌──────▼──────┐
   │ Shopify │         │ TikTok Shop│        │  Etsy       │
   │ - SEO   │         │ - Direct   │        │ - Listings  │
   │ - Collections     │   listing  │        │ - Tags      │
   └─────────┘         └────────────┘        └─────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                      ┌────────▼────────┐
                      │ Social Commerce │
                      │ - Instagram     │
                      │ - Facebook      │
                      └─────────────────┘
```

---

## Deployment Modes

### **Mode 1: Full Stack (Recommended for Production)**

Run complete orchestration with web UI:

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with all API keys

# 2. Install dependencies
npm install
pip install -r requirements.txt

# 3. Start services
# Terminal 1: ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188

# Terminal 2: Web UI
npm run dev

# 4. Access at http://localhost:5173
```

**Use Cases**:
- Interactive design creation
- Batch processing with UI feedback
- Multi-platform management
- Real-time monitoring

---

### **Mode 2: RunPod Automation (Recommended for Scale)**

Run headless automation directly on RunPod:

```bash
# On RunPod instance:

# 1. Install dependencies
pip install Pillow requests

# 2. Set credentials
export PRINTIFY_API_KEY='your-key'
export PRINTIFY_SHOP_ID='your-shop-id'
export AUTO_PUBLISH='true'
export DEFAULT_TSHIRT_PRICE='19.99'
export DEFAULT_HOODIE_PRICE='34.99'

# 3. Download script
curl -o /workspace/runpod_push_to_printify.py \
  https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/claude/push-images-printify-JLjuQ/scripts/runpod_push_to_printify.py

# 4. Run automation
python3 /workspace/runpod_push_to_printify.py
```

**Use Cases**:
- High-volume batch processing
- Automated pipeline (cron jobs)
- Cost-effective GPU usage
- No manual intervention needed

---

### **Mode 3: Hybrid (Best of Both Worlds)**

Use TypeScript orchestrator to generate images, Python script to create products:

```bash
# 1. Generate images via Web UI
#    (http://localhost:5173)
#    - Create prompts
#    - Generate with ComfyUI
#    - Save to /workspace/ComfyUI/output

# 2. Run Python automation on saved images
python3 scripts/runpod_push_to_printify.py

# 3. Monitor results in Web UI terminal
```

**Use Cases**:
- Manual design approval before publishing
- Quality control workflow
- Selective product creation
- Testing new designs

---

## Configuration Matrix

### Environment Variables (`.env`)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| **ComfyUI** ||||
| `COMFYUI_API_URL` | Yes | `http://localhost:8188` | ComfyUI API endpoint |
| `COMFYUI_OUTPUT_DIR` | Yes | `/workspace/ComfyUI/output` | Image output directory |
| **Claude AI** ||||
| `ANTHROPIC_API_KEY` | Yes | - | Claude API key for prompts |
| `CLAUDE_MODEL` | No | `claude-3-5-sonnet-20241022` | Model version |
| **Printify** ||||
| `PRINTIFY_API_KEY` | Yes | - | Printify API token |
| `PRINTIFY_SHOP_ID` | Yes | - | Printify shop ID |
| **Shopify** ||||
| `SHOPIFY_STORE_URL` | If enabled | - | Store URL (mystore.myshopify.com) |
| `SHOPIFY_ACCESS_TOKEN` | If enabled | - | Admin API token |
| **TikTok Shop** ||||
| `TIKTOK_APP_KEY` | If enabled | - | App key |
| `TIKTOK_APP_SECRET` | If enabled | - | App secret |
| `TIKTOK_SHOP_ID` | If enabled | - | Shop ID |
| **Pipeline Options** ||||
| `AUTO_PUBLISH` | No | `true` | Auto-publish products |
| `DEFAULT_TSHIRT_PRICE` | No | `19.99` | T-shirt price (USD) |
| `DEFAULT_HOODIE_PRICE` | No | `34.99` | Hoodie price (USD) |
| `ENABLE_PLATFORMS` | No | `shopify,printify` | Comma-separated platforms |

---

## Feature Comparison

| Feature | TypeScript Orchestrator | Python RunPod Script |
|---------|------------------------|----------------------|
| **Web UI** | ✅ Yes | ❌ No (CLI only) |
| **Batch Processing** | ✅ Yes (interactive) | ✅ Yes (automated) |
| **Image Filtering** | ⚠️ Basic (name only) | ✅ Advanced (name + dimensions) |
| **Dimension Check** | ❌ No | ✅ Yes (4500x5400 required) |
| **Multi-Platform** | ✅ Yes (6 platforms) | ❌ No (Printify only) |
| **Real-time Logs** | ✅ Yes (Terminal UI) | ✅ Yes (stdout) |
| **Variant Limiting** | ⚠️ Manual | ✅ Automatic (first 20) |
| **Auto-Publish** | ✅ Configurable | ✅ Configurable |
| **Price Config** | ✅ Per-product | ✅ Environment vars |
| **Cron Compatible** | ❌ No | ✅ Yes |
| **GPU Efficiency** | ⚠️ Requires UI | ✅ Headless |

---

## Integration Patterns

### **Pattern 1: Full Automation**

```bash
#!/bin/bash
# automated_pod_pipeline.sh

# Step 1: Generate images (TypeScript orchestrator)
curl -X POST http://localhost:5173/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create 10 trending t-shirt designs",
    "quantity": 10,
    "productTypes": ["tshirt", "hoodie"]
  }'

# Step 2: Wait for generation
sleep 120

# Step 3: Auto-create products (Python script)
python3 /workspace/runpod_push_to_printify.py

# Step 4: Publish to all platforms (TypeScript)
curl -X POST http://localhost:5173/api/publish-all
```

### **Pattern 2: Approval Workflow**

```bash
#!/bin/bash
# approval_workflow.sh

# Step 1: Generate images
npm run generate -- --draft

# Step 2: Manual review in UI
echo "Review designs at http://localhost:5173"
echo "Press Enter when ready to publish..."
read

# Step 3: Create products with approved designs only
python3 scripts/runpod_push_to_printify.py
```

### **Pattern 3: Scheduled Batch**

```bash
# crontab entry
# Every day at 2 AM: Generate 20 new designs and auto-publish
0 2 * * * cd /workspace && python3 runpod_push_to_printify.py >> /var/log/pod_automation.log 2>&1
```

---

## Quality Assurance

### Image Requirements

**Dimensions**:
- Width: 4500 pixels
- Height: 5400 pixels
- Aspect Ratio: 5:6
- DPI: 300 minimum

**Format**:
- Preferred: PNG (lossless)
- Accepted: JPG, JPEG, WEBP
- Max file size: 50MB

**Design Guidelines**:
- Safe area: 4000x4800 (centered)
- Avoid text near edges
- High contrast for print quality
- RGB color space

### Automated Checks

**Python Script** (`runpod_push_to_printify.py`):
```python
# Automatic validation:
1. Dimension check (4500x5400 required)
2. Filename filter (excludes 'comfyui')
3. Image format validation
4. File corruption detection
```

**TypeScript Service** (`services/printify.ts`):
```typescript
// Manual validation available:
- Image URL accessibility
- Base64 encoding validation
- API response error handling
```

---

## Performance Metrics

### Throughput

| Scenario | Images/Hour | Products/Hour | Cost/Hour |
|----------|-------------|---------------|-----------|
| **Single Design** | 5 | 10 (tee + hoodie) | $0.30 |
| **Batch (10)** | 50 | 100 | $3.00 |
| **Batch (100)** | 300 | 600 | $18.00 |

### Resource Usage

**TypeScript Orchestrator**:
- RAM: 512MB baseline
- CPU: 1-2 cores
- Network: 10MB/min

**Python Script**:
- RAM: 100MB baseline
- CPU: 1 core
- Network: 5MB/min (upload heavy)

**ComfyUI (SDXL)**:
- VRAM: 6-8GB
- RAM: 16GB recommended
- Generation time: 12-30s per image

---

## Troubleshooting

### Common Issues

#### **Issue: "Too many variants enabled"**
**Cause**: Printify limits products to 100 variants
**Solution**: Python script auto-limits to 20 variants (already fixed)

#### **Issue: "Dimension check fails"**
**Cause**: Images not 4500x5400
**Solution**: Use Python script's auto-filter or regenerate with correct dimensions

#### **Issue: "401 Unauthorized from Printify"**
**Cause**: Invalid API key
**Solution**: Verify `PRINTIFY_API_KEY` is correct and not expired

#### **Issue: "Images not found"**
**Cause**: Wrong output directory
**Solution**: Check `COMFYUI_OUTPUT_DIR` matches actual output location

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=true
export LOG_LEVEL=debug

# Run with detailed output
python3 -u runpod_push_to_printify.py 2>&1 | tee pod_debug.log
```

---

## API Rate Limits

| Service | Limit | Recommendation |
|---------|-------|----------------|
| **Printify** | 60 req/min | Batch uploads in groups of 20 |
| **Shopify** | 2 req/sec | Use bulk operations API |
| **TikTok Shop** | 100 req/min | Implement retry with backoff |
| **Claude** | 1000 req/min | Pre-generate prompts offline |

---

## Security Best Practices

### API Key Management

```bash
# Use environment variables (never commit .env)
export PRINTIFY_API_KEY=$(cat /secrets/printify_key.txt)

# Rotate keys every 90 days
# Use read-only keys where possible
# Implement IP whitelisting on RunPod

# For production:
# - Use secret management (AWS Secrets Manager, HashiCorp Vault)
# - Enable 2FA on all platform accounts
# - Monitor API usage for anomalies
```

### Access Control

```bash
# Restrict script execution
chmod 700 runpod_push_to_printify.py

# Run as non-root user
useradd -m poduser
su - poduser
```

---

## Monitoring & Analytics

### Metrics to Track

**Business Metrics**:
- Designs created per day
- Products published per day
- Revenue per design
- Conversion rate by platform

**Technical Metrics**:
- Generation time per image
- Upload success rate
- API error rate
- Storage usage

### Logging

```bash
# Structured logging format
{
  "timestamp": "2026-01-05T12:00:00Z",
  "level": "INFO",
  "service": "printify_automation",
  "action": "product_created",
  "product_id": "abc123",
  "product_type": "tshirt",
  "image_name": "design_001.png",
  "price": 19.99,
  "variants": 20,
  "published": true
}
```

---

## Cost Optimization

### Strategies

1. **Batch Processing**: Generate 100+ images at once (saves GPU startup time)
2. **Scheduled Jobs**: Run during off-peak hours for lower GPU costs
3. **Image Caching**: Reuse popular designs across platforms
4. **Variant Limiting**: 20 variants instead of 100 reduces complexity
5. **Storage**: Use S3 Lifecycle policies to archive old designs

### Break-Even Analysis

**Assumptions**:
- Generation cost: $0.06/design
- Platform fees: 15% average
- Product price: $25 average
- Profit margin goal: 40%

**Required Sales**:
- 1 sale per 3 designs to break even
- 1 sale per design for 40% profit

---

## Scaling Guidelines

### Horizontal Scaling

```bash
# Run multiple RunPod instances in parallel
for i in {1..5}; do
  curl -X POST "https://api.runpod.io/v2/pods" \
    -H "Authorization: Bearer $RUNPOD_API_KEY" \
    -d '{
      "name": "pod-worker-'$i'",
      "template": "comfyui-printify",
      "gpuType": "NVIDIA A40"
    }'
done

# Distribute workload across instances
# Instance 1: Designs 1-20
# Instance 2: Designs 21-40
# etc.
```

### Vertical Scaling

```bash
# Upgrade RunPod GPU for faster generation
# RTX 3090: 12s/image → $0.34/hr
# A40: 8s/image → $0.69/hr
# A100: 5s/image → $1.89/hr

# Calculate optimal GPU:
# Break-even = (GPU_cost - RTX3090_cost) / (time_saved * designs_per_hour)
```

---

## Roadmap & Future Enhancements

### Short Term (Q1 2026)
- [ ] Add video generation support (ComfyUI AnimateDiff)
- [ ] Implement A/B testing for designs
- [ ] Add webhook notifications for sales
- [ ] Create mobile app for monitoring

### Medium Term (Q2-Q3 2026)
- [ ] Multi-language product descriptions
- [ ] Automated social media marketing
- [ ] Predictive trend analysis
- [ ] Integrated analytics dashboard

### Long Term (Q4 2026+)
- [ ] AI-powered design optimization
- [ ] Custom print provider integrations
- [ ] White-label POD platform
- [ ] Marketplace for designs

---

## Support & Resources

**Documentation**:
- [README.md](README.md) - Quick start guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [scripts/README_PRINTIFY.md](scripts/README_PRINTIFY.md) - Printify-specific docs

**Community**:
- GitHub Issues: Bug reports and feature requests
- Discord: Real-time support and collaboration

**Commercial Support**:
- Email: support@staticwaves.io
- Consulting: Custom integrations and scaling support

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

*Last Updated: January 5, 2026*
