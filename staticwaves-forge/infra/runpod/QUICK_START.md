# 🚀 Quick Start - Unified RunPod Deployment

**Get both POD + Forge running in under 10 minutes**

---

## Step 1: SSH into RunPod

```bash
ssh root@YOUR_RUNPOD_URL
```

---

## Step 2: Clone & Configure

```bash
cd /workspace
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod
cd ssiens-oss-static_pod/staticwaves-forge/infra/runpod

# Copy and edit environment
cp .env.example .env
nano .env
```

**Minimum required:**
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your-bucket
STRIPE_KEY=sk_live_...
PRINTFUL_API_KEY=your_key
```

---

## Step 3: Deploy

```bash
chmod +x start_unified.sh
./start_unified.sh
```

Wait 30 seconds for services to start.

---

## Step 4: Access

Your services are live at:

```
https://YOUR_RUNPOD_ID-80.proxy.runpod.net/
```

- **POD (Merch)**: `/`
- **Forge (3D Assets)**: `/forge/`
- **Forge API Docs**: `/forge/docs`

---

## Quick Commands

```bash
# View logs
docker-compose -f docker-compose.unified.yml logs -f

# Restart service
docker-compose -f docker-compose.unified.yml restart forge-worker

# Stop all
docker-compose -f docker-compose.unified.yml down

# Check status
curl http://localhost/health
```

---

## Test It Works

```bash
# Test Forge API
curl "http://localhost/api/forge/health"

# Generate test asset
curl -X POST "http://localhost/api/forge/generate/quick?prompt=test&asset_type=prop"
```

---

## Port Map

| Service | Internal Port | Public URL |
|---------|---------------|------------|
| POD Web | 3000 | `/` |
| POD API | 8001 | `/api/pod/` |
| Forge Web | 3001 | `/forge/` |
| Forge API | 8000 | `/api/forge/` |
| Nginx | 80 | (entry point) |

---

## Next Steps

1. **Read full docs**: `cat ../docs/RUNPOD_DEPLOYMENT.md`
2. **Configure webhooks**: Auto-deploy on git push
3. **Set up monitoring**: Logs, metrics, alerts
4. **Add custom domain**: SSL certificates in nginx.conf

---

**Done! Both platforms running on one instance.** 🎉
