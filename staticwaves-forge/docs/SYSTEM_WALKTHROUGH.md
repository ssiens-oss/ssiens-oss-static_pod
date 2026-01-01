# 🎮 StaticWaves Forge - Complete System Walkthrough

## ✅ What We've Accomplished

### 1. System is Running
- ✅ FastAPI backend running on `http://localhost:8000`
- ✅ All endpoints operational and responding
- ✅ Job queue system working
- ✅ Asset generation pipeline ready

### 2. Verified Components
- ✅ Health check endpoint
- ✅ Job creation endpoint
- ✅ Job status tracking
- ✅ Pack management system
- ✅ Quick generation endpoint

---

## 🚀 API Endpoints Reference

### Core Endpoints

#### 1. Health & Status
```bash
# Basic health check
curl http://localhost:8000/

# Detailed health
curl http://localhost:8000/health

# Platform stats
curl http://localhost:8000/api/stats
```

#### 2. Asset Generation
```bash
# Create generation job
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A low-poly fantasy sword",
    "asset_type": "weapon",
    "style": "low-poly",
    "target_engine": "unity",
    "export_formats": ["glb", "fbx"],
    "poly_budget": 5000,
    "include_rig": false,
    "include_animations": [],
    "generate_lods": true
  }'

# Quick generation (simplified)
curl "http://localhost:8000/api/generate/quick?prompt=cyberpunk+vending+machine&asset_type=prop"
```

#### 3. Job Management
```bash
# Get job status
curl http://localhost:8000/api/jobs/{job_id}

# List all jobs
curl http://localhost:8000/api/jobs/

# List by status
curl "http://localhost:8000/api/jobs/?status=completed"

# Cancel job
curl -X DELETE http://localhost:8000/api/jobs/{job_id}

# Retry failed job
curl -X POST http://localhost:8000/api/jobs/{job_id}/retry

# Job statistics
curl http://localhost:8000/api/jobs/stats/summary
```

#### 4. Asset Packs
```bash
# List pack presets
curl http://localhost:8000/api/packs/presets/list

# Create pack
curl -X POST http://localhost:8000/api/packs/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fantasy Creatures",
    "description": "25 low-poly creatures",
    "asset_ids": ["id1", "id2"],
    "price": 39.00,
    "tags": ["fantasy", "creatures", "lowpoly"]
  }'

# Get pack details
curl http://localhost:8000/api/packs/{pack_id}

# Export pack
curl -X POST http://localhost:8000/api/packs/{pack_id}/export/gumroad
```

---

## 📱 Interactive API Documentation

The FastAPI server provides two interactive documentation interfaces:

### Swagger UI (OpenAPI)
```
http://localhost:8000/docs
```
- Interactive API explorer
- Try endpoints directly in browser
- View request/response schemas
- See all available parameters

### ReDoc
```
http://localhost:8000/redoc
```
- Clean, readable documentation
- Detailed endpoint descriptions
- Schema definitions
- Example requests/responses

---

## 🎨 Example Workflows

### Workflow 1: Generate Single Asset

```bash
# Step 1: Create job
RESPONSE=$(curl -s -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A stylized sci-fi crate",
    "asset_type": "prop",
    "style": "stylized",
    "poly_budget": 3000
  }')

# Step 2: Extract job ID
JOB_ID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Job created: $JOB_ID"

# Step 3: Poll status
curl http://localhost:8000/api/jobs/$JOB_ID

# Step 4: Download when complete
# Files will be in output_files field
```

### Workflow 2: Batch Generate for Pack

```bash
# Generate 10 creatures
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/api/generate/ \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"Fantasy creature variation $i\",
      \"asset_type\": \"creature\",
      \"style\": \"low-poly\",
      \"poly_budget\": 5000,
      \"include_rig\": true,
      \"include_animations\": [\"idle\", \"walk\"]
    }"

  echo "Generated creature $i"
done
```

### Workflow 3: Create Marketable Pack

```bash
# 1. Generate assets (as above)
# 2. Collect job IDs
# 3. Create pack

curl -X POST http://localhost:8000/api/packs/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fantasy Creatures Starter Pack",
    "description": "25 stylized creatures with animations",
    "asset_ids": ["job_id_1", "job_id_2", ...],
    "price": 39.00,
    "tags": ["fantasy", "creatures", "animated", "lowpoly"]
  }'

# 4. Export for marketplaces
PACK_ID="your_pack_id"

curl -X POST http://localhost:8000/api/packs/$PACK_ID/export/unity
curl -X POST http://localhost:8000/api/packs/$PACK_ID/export/unreal
curl -X POST http://localhost:8000/api/packs/$PACK_ID/export/roblox
curl -X POST http://localhost:8000/api/packs/$PACK_ID/export/gumroad
```

---

## 🖥️ Web UI (When Available)

The Next.js web interface provides:

### Features
- **3D Viewport**: Real-time preview with React Three Fiber
- **Prompt Panel**: Interactive asset configuration
- **Job Monitoring**: Live progress tracking
- **Export Controls**: Download in multiple formats
- **Pack Builder**: Create marketplace packages

### To Start Web UI
```bash
cd /home/user/ssiens-oss-static_pod/staticwaves-forge/apps/web
npm install  # First time only
npm run dev
```

Then open: **http://localhost:3000**

---

## 🎯 Asset Types & Configurations

### Supported Asset Types
- **creature** - Fantasy/sci-fi creatures
- **character** - Humanoid characters
- **prop** - Environmental objects
- **weapon** - Melee and ranged weapons
- **building** - Structures
- **environment** - Terrain, vegetation
- **vehicle** - Cars, ships, mechs

### Visual Styles
- **low-poly** - Mobile-friendly, indie games
- **realistic** - High-fidelity assets
- **stylized** - Artistic, cartoony
- **voxel** - Minecraft-style
- **toon** - Cell-shaded
- **roblox-safe** - Roblox-optimized

### Target Engines
- **unity** - Unity (FBX, Humanoid rig)
- **unreal** - Unreal Engine (FBX, Mannequin)
- **roblox** - Roblox Studio (FBX, R15)
- **godot** - Godot Engine (GLTF/GLB)
- **generic** - Universal formats

### Export Formats
- **glb** - Binary GLTF (universal)
- **fbx** - Autodesk FBX (industry standard)
- **obj** - Wavefront OBJ (static mesh)
- **gltf** - GLTF separate files

---

## 🐳 Running with Docker

### Build Worker Image
```bash
cd /home/user/ssiens-oss-static_pod/staticwaves-forge/infra/runpod
docker build -t staticwaves-forge-worker .
```

### Run with Docker Compose
```bash
docker-compose up -d

# Check logs
docker-compose logs -f worker

# Stop
docker-compose down
```

### Deploy to RunPod
1. Push image to Docker Hub:
   ```bash
   docker tag staticwaves-forge-worker yourusername/forge-worker:latest
   docker push yourusername/forge-worker:latest
   ```

2. Create RunPod pod with:
   - GPU: RTX 4090 or A5000
   - Image: `yourusername/forge-worker:latest`
   - Env vars: REDIS_URL, AWS keys, S3_BUCKET

---

## 🛠️ Command-Line Scripts

### Batch Generation
```bash
cd /home/user/ssiens-oss-static_pod/staticwaves-forge

# Generate 10 creatures
python scripts/generate_batch.py creature 10 \
  --style low-poly \
  --output ./output/creatures

# Generate props
python scripts/generate_batch.py prop 25 \
  --style stylized \
  --output ./output/props
```

### Seed Replay (Reproduce Assets)
```bash
# Regenerate exact asset from seed
python scripts/seed_replay.py 42 --output ./reproduced.glb
```

### Pack Publishing
```bash
# Publish to marketplace
python scripts/publish_pack.py ./packs/MyPack.zip \
  --marketplace gumroad \
  --price 39 \
  --title "Fantasy Creatures" \
  --description "25 stylized creatures"
```

---

## 📊 Testing the System

### Test 1: API Health
```bash
curl http://localhost:8000/
# Expected: {"service":"StaticWaves Forge","status":"online",...}
```

### Test 2: Quick Generation
```bash
curl "http://localhost:8000/api/generate/quick?prompt=test&asset_type=prop"
# Expected: Job created with job_id
```

### Test 3: Job Status
```bash
curl http://localhost:8000/api/jobs/{job_id_from_test_2}
# Expected: Job details with status, progress, etc.
```

### Test 4: Pack Presets
```bash
curl http://localhost:8000/api/packs/presets/list
# Expected: List of 4 preset packs
```

---

## 🎁 Pre-Configured Asset Packs

The system includes 4 ready-to-generate pack templates:

1. **Fantasy Creatures Starter** - 25 creatures, $39
2. **Sci-Fi Props Mega Kit** - 60 props, $49
3. **Low-Poly Environment Pack** - 40 buildings, $29
4. **Weapon Arsenal Collection** - 30 weapons, $35

Generate these with:
```bash
curl -X POST http://localhost:8000/api/packs/presets/Fantasy_Creatures_Starter/generate
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process on port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn main:app --port 8001
```

### Missing Dependencies
```bash
# Reinstall API deps
cd apps/api
pip install -r requirements.txt

# Reinstall web deps
cd apps/web
npm install
```

### Blender Not Found
```bash
# Install Blender
# Ubuntu/Debian:
sudo apt install blender

# macOS:
brew install blender

# Or download from blender.org

# Set path
export BLENDER_PATH=/usr/bin/blender
```

---

## 📚 Next Steps

### Immediate
1. ✅ Explore API docs at http://localhost:8000/docs
2. ✅ Test quick generation endpoint
3. ✅ Review pack presets

### This Week
1. Start the web UI
2. Generate your first assets
3. Create a test asset pack

### This Month
1. Deploy worker to RunPod
2. Generate 100+ asset library
3. Publish first pack to marketplace

---

## 🔗 Useful Links

- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc
- **Web UI**: http://localhost:3000 (when running)

---

**The complete StaticWaves Forge platform is running and ready to generate 3D assets!** 🚀

Try the quick generation endpoint to create your first asset right now:
```bash
curl "http://localhost:8000/api/generate/quick?prompt=medieval+sword&asset_type=weapon"
```
