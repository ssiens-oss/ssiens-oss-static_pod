# StaticWaves Music Studio - Installation Guide

## 🚀 One-Command Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/install.sh | bash
```

Or if you already have the repo:

```bash
./install.sh
```

This automatically installs:
- ✅ All dependencies (Node, Python, Docker)
- ✅ Music API and Worker
- ✅ Redis queue
- ✅ Web GUI
- ✅ Startup scripts

**Installation time:** 10-15 minutes (mostly Docker image building)

---

## 📋 Manual Installation

If you prefer to install manually:

### Prerequisites

**Required:**
- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.10+ ([Download](https://www.python.org/))
- Docker & Docker Compose ([Download](https://www.docker.com/))
- Git

**Optional:**
- NVIDIA GPU with CUDA (for production music quality)
- Anthropic API key (for AI lyrics)
- Stripe API key (for billing)

### Step 1: Clone Repository

```bash
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod
```

### Step 2: Install Node Dependencies

```bash
npm install
```

### Step 3: Install Python Dependencies

```bash
# API dependencies
pip install -r music-engine/requirements-api.txt

# Worker dependencies
pip install -r music-engine/requirements-worker.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

**Required variables:**
```bash
VITE_MUSIC_API_URL=http://localhost:8000
REDIS_HOST=localhost
REDIS_PORT=6379
OUTPUT_DIR=/tmp/staticwaves/output
```

**Optional variables:**
```bash
ANTHROPIC_API_KEY=your_key_here  # For AI lyrics
STRIPE_API_KEY=your_key_here      # For billing
MUSICGEN_MODEL=facebook/musicgen-medium
```

### Step 5: Start Services

```bash
# Start Music API and Worker
cd music-engine
docker-compose up -d
cd ..

# Start GUI
npm run dev:music
```

### Step 6: Open Browser

```
http://localhost:5174
```

---

## 🐳 Docker-Only Installation

If you want to run everything in Docker:

### Create docker-compose.full.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  music-api:
    build:
      context: .
      dockerfile: music-engine/docker/api.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - OUTPUT_DIR=/data/output
    depends_on:
      - redis
    volumes:
      - music_output:/data/output

  music-worker:
    build:
      context: .
      dockerfile: music-engine/docker/worker.Dockerfile
    environment:
      - REDIS_HOST=redis
      - OUTPUT_DIR=/data/output
      - MUSICGEN_MODEL=facebook/musicgen-medium
    depends_on:
      - redis
    volumes:
      - music_output:/data/output
      - model_cache:/root/.cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  music-gui:
    build:
      context: .
      dockerfile: Dockerfile.gui
    ports:
      - "5174:80"
    depends_on:
      - music-api

volumes:
  music_output:
  model_cache:
```

### Run

```bash
docker-compose -f docker-compose.full.yml up -d
```

---

## 🖥️ Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y nodejs npm python3 python3-pip docker.io docker-compose git

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Run installer
./install.sh
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install prerequisites
brew install node python3 git

# Install Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Run installer
./install.sh
```

### Windows (WSL2)

```bash
# Install WSL2
wsl --install

# Open WSL2 Ubuntu terminal
# Then follow Ubuntu instructions above
```

---

## 🚀 Quick Start After Installation

### Start Everything

```bash
./start-music-studio.sh
```

This starts:
- Music API (port 8000)
- GPU Worker
- Redis
- Web GUI (port 5174)

### Stop Everything

```bash
./stop-music-studio.sh
```

### Test Installation

```bash
./test-music-generation.sh
```

---

## 🔧 Troubleshooting

### Docker Daemon Not Running

**Linux:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

**Mac/Windows:**
- Start Docker Desktop application

### Permission Denied

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Port Already in Use

Change ports in `.env`:
```bash
VITE_MUSIC_API_URL=http://localhost:8001  # Change API port
```

And in `vite.music.config.ts`:
```typescript
server: {
  port: 5175,  // Change GUI port
}
```

### GPU Not Detected

**Check NVIDIA driver:**
```bash
nvidia-smi
```

**Install NVIDIA Docker runtime:**
```bash
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Module Not Found Errors

**Reinstall dependencies:**
```bash
# Node
rm -rf node_modules package-lock.json
npm install

# Python
pip install -r music-engine/requirements-api.txt --upgrade
pip install -r music-engine/requirements-worker.txt --upgrade
```

### Services Won't Start

**Check logs:**
```bash
cd music-engine
docker-compose logs
```

**Restart services:**
```bash
docker-compose restart
```

---

## 📦 Uninstallation

### Stop Services

```bash
./stop-music-studio.sh
```

### Remove Docker Containers

```bash
cd music-engine
docker-compose down -v
```

### Remove Files

```bash
cd ..
rm -rf ssiens-oss-static_pod
```

---

## 🎓 Next Steps

After installation:

1. **Read the Quick Start:** `music-engine/QUICKSTART.md`
2. **Explore Features:** `music-engine/FEATURES.md`
3. **API Documentation:** http://localhost:8000/docs
4. **Generate your first song!**

---

## 💡 Tips

### Development vs Production

**Development (default):**
- Mock music generation (CPU)
- Fast startup
- Good for testing UI

**Production (real AI):**
```bash
# Install real MusicGen
pip install torch audiocraft librosa

# Worker will auto-detect and use GPU
```

### Save Disk Space

Remove model cache:
```bash
rm -rf ~/.cache/huggingface
```

### Update to Latest Version

```bash
git pull origin main
./install.sh
```

---

## 🆘 Getting Help

- **Documentation:** Check `music-engine/` folder
- **Issues:** Open issue on GitHub
- **Logs:** `docker-compose logs -f`
- **API Status:** http://localhost:8000/health

---

**Need help?** Open an issue on GitHub with:
- Your OS and version
- Error messages
- Output of `docker-compose logs`

Happy music making! 🎵
