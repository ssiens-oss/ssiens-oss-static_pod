<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Studio

[![CI/CD Pipeline](https://github.com/ssiens-oss/ssiens-oss-static_pod/actions/workflows/pod-pipeline.yml/badge.svg)](https://github.com/ssiens-oss/ssiens-oss-static_pod/actions/workflows/pod-pipeline.yml)
[![Docker Image](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://hub.docker.com/r/your-username/staticwaves-pod-studio)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-6.0-blue.svg)](https://github.com/ssiens-oss/ssiens-oss-static_pod/releases)

A web-based automation suite for Print-on-Demand, featuring batch processing, real-time logging, and an interactive design editor with advanced transform controls.

**🎨 Live Demo:** https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

## ✨ Features

- 🚀 **Batch Processing** - Process multiple drops in sequence
- 📊 **Real-time Logging** - Live updates with color-coded output
- 🎨 **Interactive Editor** - Scale, rotate, pan, and transform designs
- 🖼️ **Product Mockup Preview** - Instant mockup generation
- 📦 **Upload Queue Management** - Track Printify upload status
- 🔄 **CI/CD Pipeline** - Automated builds and multi-platform deployments
- 🐳 **Docker Ready** - One-command deployment
- ☁️ **Cloud Deploy** - RunPod, Kubernetes, Docker Compose support

## 🚀 Quick Start

### Option 1: Using Make (Recommended)

```bash
# Install dependencies and start dev server
make install
make dev

# Or run full local Docker test
make local
```

### Option 2: Manual Setup

**Prerequisites:** Node.js 20+

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment (optional):**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run the app:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   ```
   http://localhost:5173
   ```

### Option 3: Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🐳 Docker Deployment

### Quick Deploy

```bash
# Build and deploy using automated script
./deploy.sh

# Or use Make
make deploy
```

### Deploy to RunPod

1. **Using the deploy script:**
   ```bash
   ./deploy.sh latest dockerhub
   ```

2. **Deploy on RunPod:**
   - Go to [RunPod](https://www.runpod.io/)
   - Deploy custom container
   - Use image: `your-username/staticwaves-pod-studio:latest`
   - Expose port: `80`
   - Deploy!

### Deploy to Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

See [POD_PIPELINE.md](POD_PIPELINE.md) for detailed Kubernetes configuration.

## 📚 Documentation

- **[POD_PIPELINE.md](POD_PIPELINE.md)** - Complete CI/CD pipeline guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment instructions
- **[.env.example](.env.example)** - Configuration template
- **[Makefile](Makefile)** - Development commands

## 🛠️ Development

### Available Commands

Run `make help` to see all available commands:

```bash
make install        # Install dependencies
make dev            # Start development server
make build          # Build production bundle
make check-types    # Run TypeScript type checking
make docker-build   # Build Docker image
make docker-run     # Run Docker container locally
make health         # Check application health
make quick-test     # Quick test (type check + build)
make local          # Full local testing
```

### Project Structure

```
.
├── App.tsx                      # Main application component
├── components/
│   ├── Terminal.tsx             # Log viewer component
│   └── EditorControls.tsx       # Image editor controls (zoom, rotate, reset)
├── services/
│   └── mockEngine.ts            # Simulation engine
├── types.ts                     # TypeScript type definitions
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml           # Docker Compose configuration
├── nginx.conf                   # Nginx web server configuration
├── deploy.sh                    # Deployment automation script
├── Makefile                     # Development task automation
├── .github/workflows/
│   └── pod-pipeline.yml         # CI/CD workflow
├── DEPLOYMENT.md                # Deployment guide
├── POD_PIPELINE.md              # Pipeline documentation
└── .env.example                 # Environment configuration template
```

## 🎨 Editor Features

The interactive design editor includes:

- **Zoom Controls** - Scale designs by 90% or 110%
- **Rotation** - Rotate designs ±15° increments
- **Pan Controls** - Move designs in any direction
- **Reset Transform** - Restore to default state
- **Save Edited Image** - Save with transforms applied
- **Export Design** - Download transformed design

## 🔄 CI/CD Pipeline

Automated pipeline with GitHub Actions:

- ✅ **Build & Test** - Type checking and production builds
- ✅ **Docker Build** - Multi-platform container builds (amd64, arm64)
- ✅ **Health Checks** - Automated container testing
- ✅ **Multi-Registry** - Push to Docker Hub and GHCR
- ✅ **Deployment Ready** - Automated deployment notifications

See [POD_PIPELINE.md](POD_PIPELINE.md) for complete pipeline documentation.

## 🌐 Deployment Options

| Platform | Complexity | Cost | Best For |
|----------|-----------|------|----------|
| **RunPod** | Low | Pay-per-use | Quick deployment, GPU access |
| **Docker Compose** | Low | Self-hosted | Local testing, single server |
| **Kubernetes** | High | Variable | Production, scaling, multi-region |
| **GitHub Pages** | N/A | Free | Static hosting (build only) |

## 📊 Performance

- **Build Size**: ~2MB gzipped
- **Container Size**: ~50MB (multi-stage build)
- **Memory Usage**: ~512MB average
- **Response Time**: <100ms (static assets)
- **Supported Platforms**: linux/amd64, linux/arm64

## 🔐 Configuration

Create `.env.local` from template:

```bash
cp .env.example .env.local
```

Key configuration options:

- `VITE_APP_MODE` - `mock` or `production`
- `VITE_PRINTIFY_API_TOKEN` - Printify API access
- `VITE_GEMINI_API_KEY` - AI generation (optional)
- `VITE_ENABLE_BATCH_MODE` - Enable/disable batch processing
- `VITE_MAX_BATCH_SIZE` - Maximum batch size limit

See [.env.example](.env.example) for all options.

## 🧪 Testing

```bash
# Type checking
make check-types

# Build test
make build

# Full local test
make quick-test

# Docker health check
make health
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines (coming soon).

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/ssiens-oss/ssiens-oss-static_pod/discussions)
- **RunPod Support**: [RunPod Discord](https://discord.gg/runpod)

## 🌟 Acknowledgments

Built with:
- [React](https://react.dev/) - UI framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Vite](https://vitejs.dev/) - Build tool
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Lucide Icons](https://lucide.dev/) - Icons
- [Nginx](https://nginx.org/) - Web server
- [Docker](https://www.docker.com/) - Containerization

---

<div align="center">
Made with ❤️ by the StaticWaves team
</div>
