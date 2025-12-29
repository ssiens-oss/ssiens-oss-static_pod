<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Studio

A web-based simulation of the StaticWaves Print-on-Demand automation suite, featuring batch processing, real-time logging, and an interactive design editor.

**View in AI Studio:** https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

## 🚀 Quick Start

Choose your deployment method:

### Run Locally (Development)

**Prerequisites:** Node.js 18+

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Access at: `http://localhost:3000`

### Deploy to RunPod (Production)

**See:** [QUICKSTART.md](QUICKSTART.md) for complete deployment guide

```bash
# Quick deploy
export DOCKERHUB_USERNAME=your-username
./runpod-deploy.sh
```

### Docker (Local Testing)

```bash
# Using docker-compose
npm run docker:compose:build

# Or with Docker directly
docker build -t staticwaves-pod-studio:beta .
docker run -p 8080:80 staticwaves-pod-studio:beta
```

Access at: `http://localhost:8080`

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast track to RunPod deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **[BETA_TESTING.md](BETA_TESTING.md)** - Beta testing guide and checklist
- **[beta-config.json](beta-config.json)** - Feature flags and configuration

## ✨ Features

- **Batch Processing**: Process multiple drops simultaneously
- **Real-time Logging**: Live terminal output for all operations
- **Interactive Editor**: Transform and adjust designs before upload
- **Queue Management**: Track product upload status
- **Health Monitoring**: Built-in health check endpoint

## 🧪 Beta Version

**Version:** 6.0-beta.1
**Status:** Open Beta
**Environment:** Staging

See [BETA_TESTING.md](BETA_TESTING.md) for testing guidelines.
