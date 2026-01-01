# 🎮 StaticWaves Forge

**AI-Powered 3D Asset + Animation Generation Platform**

One prompt → production-ready game assets. Generate meshes, textures, rigs, and animations in seconds.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Blender 3.0+](https://img.shields.io/badge/blender-3.0+-orange.svg)](https://www.blender.org/)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/ssiens-oss/staticwaves-forge
cd staticwaves-forge

# Install dependencies
npm install

# Start the API server
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload

# Start the web UI (in another terminal)
cd apps/web
npm run dev

# Open http://localhost:3000
```

---

## 📋 What Is This?

StaticWaves Forge is an **end-to-end AI asset generation platform** that turns text prompts into complete, game-ready 3D assets.

### Complete Pipeline
1. ✅ **Mesh Generation** - Procedural + AI-driven geometry
2. ✅ **Auto-UV Mapping** - Clean, optimized UVs
3. ✅ **Texture Synthesis** - PBR materials (Base, Normal, Roughness, Metallic)
4. ✅ **Auto-Rigging** - Humanoid, quadruped, creature rigs
5. ✅ **Animation Generation** - Idle, walk, run, jump, attack
6. ✅ **LOD Optimization** - Automatic level-of-detail generation
7. ✅ **Multi-Engine Export** - Unity, Unreal, Roblox, Godot

### Time to Asset
- **Traditional workflow:** 2-4 weeks
- **StaticWaves Forge:** 30 seconds

---

## 🎯 Features

### For Indie Game Developers
- 🎨 Generate unlimited assets for prototyping
- 💰 Eliminate expensive artist costs
- ⚡ Iterate 100x faster
- 📦 Build entire asset libraries overnight

### For Asset Creators
- 💵 Monetize generated packs on marketplaces
- 🤖 Automate tedious rigging and optimization
- 🔄 Deterministic seeds for perfect iteration
- 🌐 Export to all major engines

### For Studios
- 🚀 Rapid concept visualization
- 🧪 A/B test different art styles instantly
- 📊 Scale content production without scaling team
- 🔌 API access for programmatic generation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Next.js Web Interface               │
│  (Prompt, Preview, Export, Pack Builder)   │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────┐
│         FastAPI Control Plane              │
│    (Job Queue, Status, S3/R2 Upload)      │
└────────────────┬───────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────┐
│      RunPod GPU Workers (Auto-Scale)      │
│  Blender Headless + Procedural Pipeline  │
└────────────────────────────────────────────┘
```

### Tech Stack
- **Frontend:** Next.js 14, React Three Fiber, Tailwind CSS
- **Backend:** FastAPI (Python), Redis queue
- **Workers:** Blender Python API, RunPod GPU instances
- **Storage:** S3/R2 for assets
- **Exports:** GLB, FBX, OBJ, GLTF

---

## 📦 Repository Structure

```
staticwaves-forge/
├── apps/
│   ├── web/                  # Next.js UI
│   │   ├── app/              # Pages & routes
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   └── api/                  # FastAPI backend
│       ├── routes/           # API endpoints
│       └── main.py           # Entry point
│
├── packages/
│   ├── blender/              # Blender automation scripts
│   │   ├── generate_asset.py
│   │   ├── auto_rig.py
│   │   ├── add_animation.py
│   │   └── export.py
│   ├── optimization/         # LOD & mesh optimization
│   ├── packager/             # Asset pack builder
│   └── common/               # Shared schemas
│
├── infra/
│   └── runpod/               # Docker & worker scripts
│       ├── Dockerfile
│       ├── worker.py
│       └── start_worker.sh
│
├── scripts/
│   ├── generate_batch.py     # Batch generation
│   ├── seed_replay.py        # Reproduce from seed
│   └── publish_pack.py       # Marketplace publisher
│
└── investor/
    ├── PITCH.md              # Investor pitch deck
    └── ECONOMICS.md          # Unit economics
```

---

## 🎮 Usage Examples

### Generate a Single Asset

```python
import requests

response = requests.post('http://localhost:8000/api/generate/', json={
    "prompt": "A stylized fantasy sword with glowing runes",
    "asset_type": "weapon",
    "style": "low-poly",
    "target_engine": "unity",
    "poly_budget": 5000,
    "include_rig": True,
    "include_animations": ["idle", "attack"],
    "export_formats": ["glb", "fbx"]
})

job_id = response.json()['job_id']
print(f"Job created: {job_id}")
```

### Batch Generate Assets

```bash
# Generate 25 creatures for an asset pack
python scripts/generate_batch.py creature 25 --style low-poly --output ./packs/fantasy_creatures
```

### Reproduce from Seed

```bash
# Regenerate exact asset from seed
python scripts/seed_replay.py 42 --output ./reproduced_asset.glb
```

### Create Asset Pack

```python
from packages.packager.build_pack import AssetPack, generate_gumroad_package

pack = AssetPack(
    name="Fantasy_Creatures_Starter",
    description="25 stylized creatures with animations",
    price=39,
    tags=["fantasy", "creatures", "lowpoly"]
)

# Add assets
pack.add_asset("./output/creature_1.glb")
pack.add_asset("./output/creature_2.glb")
# ... add more ...

# Generate marketplace package
generate_gumroad_package(pack, "./packs")
```

---

## 🐳 Docker Deployment

### Build Worker Image

```bash
cd infra/runpod
docker build -t staticwaves-forge-worker .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

### Deploy to RunPod

1. Push image to Docker Hub:
   ```bash
   docker tag staticwaves-forge-worker yourusername/forge-worker:latest
   docker push yourusername/forge-worker:latest
   ```

2. Create RunPod template with your image
3. Configure environment variables:
   - `REDIS_URL`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `S3_BUCKET`

---

## 🎨 Asset Types

| Type         | Description                    | Avg Poly Count |
|--------------|--------------------------------|----------------|
| Creature     | Fantasy/sci-fi creatures       | 5k - 20k       |
| Character    | Humanoid characters            | 8k - 30k       |
| Prop         | Environmental objects          | 500 - 5k       |
| Weapon       | Melee and ranged weapons       | 2k - 10k       |
| Building     | Structures and architecture    | 5k - 50k       |
| Environment  | Terrain, rocks, vegetation     | 1k - 20k       |
| Vehicle      | Cars, ships, mechs             | 10k - 50k      |

---

## 🎯 Supported Engines

- ✅ **Unity** - FBX with Humanoid rig mapping
- ✅ **Unreal Engine** - FBX with Mannequin compatibility
- ✅ **Roblox** - R15 rig-compatible FBX
- ✅ **Godot** - GLTF/GLB format
- ✅ **Generic** - OBJ, GLB for any engine

---

## 📊 Performance

### Generation Speed
- Simple prop: ~10 seconds
- Rigged character: ~30 seconds
- Animated character: ~60 seconds

### Quality Metrics
- Polygon count: Configurable (500 - 100k)
- Texture resolution: Up to 4K
- Animation frame rate: 24-60 fps
- File size: 0.5 - 10 MB per asset

### Scale
- Single worker: ~100 assets/hour
- Auto-scaling: Unlimited (RunPod fleet)

---

## 🛠️ Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Blender 3.0+ (for local development)
- Docker (for worker deployment)

### Setup Local Development

```bash
# Install Python dependencies
cd apps/api
pip install -r requirements.txt

# Install Node dependencies
npm install

# Start API in dev mode
cd apps/api
uvicorn main:app --reload

# Start web UI in dev mode
cd apps/web
npm run dev
```

### Run Tests

```bash
# API tests
cd apps/api
pytest

# Web UI tests
cd apps/web
npm test
```

---

## 💰 Pricing (When Launched)

| Tier       | Price/mo | Assets/mo | Features                    |
|------------|----------|-----------|------------------------------|
| Starter    | $29      | 100       | Props, basic export          |
| Creator    | $79      | 500       | All types, animations, API   |
| Studio     | $199     | Unlimited | Priority queue, white-label  |
| Enterprise | Custom   | Unlimited | On-prem, SLA, custom models  |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas we need help:
- 🎨 Additional procedural generators
- 🤖 AI model integration
- 🧪 Quality testing and validation
- 📚 Documentation and tutorials
- 🌐 Marketplace integrations

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Website:** https://forge.staticwaves.io
- **Documentation:** https://docs.forge.staticwaves.io
- **Discord:** https://discord.gg/staticwaves
- **Twitter:** https://twitter.com/staticwaves
- **YouTube:** Tutorials and demos

---

## 🙏 Acknowledgments

- Built with [Blender](https://www.blender.org/)
- Powered by [RunPod](https://runpod.io/)
- UI framework: [Next.js](https://nextjs.org/)
- 3D rendering: [Three.js](https://threejs.org/) & [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/ssiens-oss/staticwaves-forge/issues)
- **Email:** support@staticwaves.io
- **Discord:** [Community Server](https://discord.gg/staticwaves)

---

**Made with ❤️ by the StaticWaves team**

*Empowering creators to build unlimited worlds*
