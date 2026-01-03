<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# StaticWaves POD Studio

A web-based simulation of the StaticWaves Print-on-Demand automation suite, featuring batch processing, real-time logging, and an interactive design editor.

View your app in AI Studio: https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   ```bash
   npm install
   ```

2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key (optional)

3. Run the app:
   ```bash
   npm run dev
   ```

4. Open http://localhost:5173 in your browser

## Deploy to RunPod

This application can be deployed to RunPod for cloud hosting with full Printify integration.

### Full Stack Deployment (Recommended)

**Complete pipeline: Local → Docker → RunPod → Printify**

```bash
# 1. Copy environment template
cp .env.deploy.example .env.deploy

# 2. Configure your credentials
nano .env.deploy

# 3. Run full-stack deployment
source .env.deploy
./deploy-full-stack.sh
```

This automated script handles:
- ✅ Local environment validation
- ✅ Docker build and push
- ✅ RunPod deployment
- ✅ Health checks
- ✅ Printify API integration
- ✅ Auto-kill configuration

### Quick Deploy (Simple)

```bash
# Build and deploy using the basic script
./deploy.sh

# Or manually build the Docker image
docker build -t staticwaves-pod-studio .
```

### Deployment Guides

- **[DEPLOY-GUIDE.md](DEPLOY-GUIDE.md)** - Full stack deployment with Printify integration
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Basic RunPod deployment instructions

Includes:
- Building the Docker image
- Pushing to container registries
- Deploying to RunPod
- Printify webhook configuration
- Auto-kill cost optimization
- SSH setup
- Troubleshooting

## Features

- **Batch Processing**: Process multiple drops in sequence
- **Real-time Logging**: See live updates as your POD automation runs
- **Interactive Editor**: Scale and transform designs in real-time
- **Product Mockup Preview**: View generated mockups instantly
- **Upload Queue Management**: Track Printify upload status

## Project Structure

```
.
├── App.tsx                    # Main application component
├── components/
│   ├── Terminal.tsx           # Log viewer component
│   └── EditorControls.tsx     # Image editor controls
├── services/
│   └── mockEngine.ts          # Simulation engine
├── types.ts                   # TypeScript type definitions
├── Dockerfile                 # Docker container configuration
├── nginx.conf                 # Nginx web server configuration
├── deploy.sh                  # Basic deployment script
├── deploy-full-stack.sh       # Full pipeline deployment script
├── .env.deploy.example        # Environment variables template
├── DEPLOYMENT.md              # Basic deployment guide
└── DEPLOY-GUIDE.md            # Full stack deployment guide
```
