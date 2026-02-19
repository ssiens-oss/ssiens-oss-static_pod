# Getting Started with StaticWaves Forge

This guide will help you get StaticWaves Forge running locally in under 10 minutes.

---

## Prerequisites

### Required
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Blender 3.0+** - [Download](https://www.blender.org/download/)

### Optional
- **Docker** - For worker deployment
- **Git** - For version control
- **Redis** - For production job queue (can use Docker)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ssiens-oss/staticwaves-forge
cd staticwaves-forge
```

### 2. Install Dependencies

#### Root Dependencies
```bash
npm install
```

#### API Dependencies
```bash
cd apps/api
pip install -r requirements.txt
cd ../..
```

#### Web Dependencies
```bash
cd apps/web
npm install
cd ../..
```

### 3. Configure Blender Path

Set the Blender executable path in your environment:

```bash
# Linux/Mac
export BLENDER_PATH=/usr/bin/blender

# Windows
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
```

Or add it to a `.env` file in the root:

```env
BLENDER_PATH=/usr/bin/blender
```

---

## Running the Platform

### Option 1: Development Mode (Recommended for Testing)

#### Terminal 1: Start API Server
```bash
cd apps/api
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Terminal 2: Start Web UI
```bash
cd apps/web
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### Open Browser
Navigate to: **http://localhost:3000**

---

### Option 2: Using Docker (Production-Like)

```bash
cd infra/runpod
docker-compose up
```

This starts:
- Redis (job queue)
- API server
- Worker (asset generator)

---

## Your First Asset

### Via Web UI

1. Open http://localhost:3000
2. Click **"Start Generating"**
3. Enter a prompt: `"A low-poly medieval sword"`
4. Select:
   - Asset Type: **Weapon**
   - Style: **Low Poly**
   - Target Engine: **Unity**
   - Poly Budget: **5000**
5. Click **"Generate Asset"**
6. Wait ~30 seconds
7. Preview in 3D viewport
8. Download GLB/FBX

### Via API

```bash
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A low-poly medieval sword",
    "asset_type": "weapon",
    "style": "low-poly",
    "target_engine": "unity",
    "poly_budget": 5000,
    "export_formats": ["glb", "fbx"]
  }'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "progress": 0.0
}
```

Check status:
```bash
curl http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000
```

### Via Python Script

```python
import requests
import time

# Create job
response = requests.post('http://localhost:8000/api/generate/', json={
    "prompt": "A cyberpunk vending machine",
    "asset_type": "prop",
    "style": "stylized",
    "poly_budget": 10000
})

job_id = response.json()['job_id']
print(f"Job created: {job_id}")

# Poll for completion
while True:
    status = requests.get(f'http://localhost:8000/api/jobs/{job_id}').json()
    print(f"Status: {status['status']} ({status['progress']*100:.0f}%)")

    if status['status'] == 'completed':
        print("✅ Asset ready!")
        print(f"Files: {status['output_files']}")
        break
    elif status['status'] == 'failed':
        print(f"❌ Failed: {status['error_message']}")
        break

    time.sleep(2)
```

---

## Common Tasks

### Generate Multiple Assets (Batch)

```bash
python scripts/generate_batch.py creature 10 --style low-poly --output ./my_creatures
```

This generates 10 creature assets and saves them to `./my_creatures/`.

### Create an Asset Pack

```bash
python packages/packager/build_pack.py MyPack gumroad ./packs/
```

### Reproduce an Asset from Seed

```bash
python scripts/seed_replay.py 42 --output ./reproduced.glb
```

---

## Configuration

### Environment Variables

Create `.env` file in the root:

```env
# Blender
BLENDER_PATH=/usr/bin/blender

# API
API_HOST=0.0.0.0
API_PORT=8000

# Worker
REDIS_URL=redis://localhost:6379
OUTPUT_DIR=/tmp/forge_output

# Storage (Optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=staticwaves-assets

# Web UI
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Advanced Settings

Edit `apps/api/main.py` for:
- CORS origins
- Rate limiting
- Authentication

Edit `infra/runpod/worker.py` for:
- Timeout values
- GPU settings
- Queue behavior

---

## Troubleshooting

### Blender Not Found
```
Error: Blender executable not found
```

**Solution:** Set `BLENDER_PATH` environment variable or add Blender to PATH.

### Port Already in Use
```
Error: [Errno 48] Address already in use
```

**Solution:** Change port in command:
```bash
uvicorn main:app --port 8001
```

### Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:** Install dependencies:
```bash
cd apps/api
pip install -r requirements.txt
```

### Asset Generation Timeout
```
Error: Blender script timed out
```

**Solution:** Increase timeout in `infra/runpod/worker.py`:
```python
timeout=600  # 10 minutes
```

---

## Next Steps

### Learn More
- [API Documentation](./API.md)
- [Blender Pipeline](./BLENDER_PIPELINE.md)
- [Asset Pack Creation](./ASSET_PACKS.md)

### Extend the Platform
- Add custom procedural generators
- Integrate AI models
- Build marketplace integrations

### Deploy to Production
- [RunPod Deployment Guide](./DEPLOYMENT.md)
- [AWS Infrastructure Setup](./AWS_SETUP.md)

---

## Getting Help

- **Discord:** https://discord.gg/staticwaves
- **Issues:** https://github.com/ssiens-oss/staticwaves-forge/issues
- **Email:** support@staticwaves.io

---

**Ready to build? Start generating! 🚀**
