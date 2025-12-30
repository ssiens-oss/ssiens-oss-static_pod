# POD Studio Pipeline Documentation

Complete guide to the StaticWaves POD Studio CI/CD pipeline and deployment workflow.

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Local Development](#local-development)
- [CI/CD Workflows](#cicd-workflows)
- [Container Registry Options](#container-registry-options)
- [Deployment Strategies](#deployment-strategies)
- [Monitoring & Debugging](#monitoring--debugging)
- [Best Practices](#best-practices)

## Overview

The POD Studio pipeline provides automated build, test, and deployment workflows for the StaticWaves Print-on-Demand automation suite. The pipeline supports multiple deployment targets and container registries.

### Pipeline Features

- ✅ Automated Docker builds with multi-platform support
- ✅ Continuous integration with type checking and builds
- ✅ Multi-registry support (Docker Hub, GitHub Container Registry)
- ✅ Automated health checks and testing
- ✅ RunPod deployment ready
- ✅ GitHub Actions workflow automation
- ✅ Manual deployment script with interactive prompts

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Source Code Push                         │
│                  (main, develop, or PR)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions Workflow Triggered               │
│                 (.github/workflows/pod-pipeline.yml)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                              │
        ▼                              ▼
┌──────────────────┐         ┌──────────────────┐
│  Build & Test    │         │  Docker Build    │
│  - npm ci        │         │  - Multi-arch    │
│  - Type check    │         │  - Cache layers  │
│  - npm build     │         │  - Health check  │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │        Both Complete       │
         └──────────────┬─────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                              │
         ▼                              ▼
┌──────────────────┐         ┌──────────────────┐
│  Push to         │         │  Push to GHCR    │
│  Docker Hub      │         │  - ghcr.io       │
│  - Multi-arch    │         │  - Auto versioned│
│  - Tagged        │         │  - Public/Private│
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         └──────────────┬─────────────┘
                        │
                        ▼
         ┌────────────────────────────┐
         │    Deployment Ready        │
         │  - RunPod                  │
         │  - Kubernetes              │
         │  - Docker Compose          │
         └────────────────────────────┘
```

## Local Development

### Prerequisites

- Node.js 20+
- Docker (for local testing)
- Git

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/ssiens-oss-static_pod.git
   cd ssiens-oss-static_pod
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Access the app:**
   Open http://localhost:5173

### Local Docker Testing

Build and test the Docker image locally:

```bash
# Build the image
docker build -t staticwaves-pod-studio:test .

# Run the container
docker run -p 8080:80 staticwaves-pod-studio:test

# Test the application
curl http://localhost:8080/health
open http://localhost:8080
```

## CI/CD Workflows

### GitHub Actions Pipeline

The pipeline is defined in `.github/workflows/pod-pipeline.yml` and includes:

#### Job 1: Build & Test

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Manual workflow dispatch

**Steps:**
1. Checkout code
2. Setup Node.js 20
3. Install dependencies (npm ci)
4. Type check (TypeScript)
5. Build application
6. Upload build artifacts

**Environment:**
- OS: Ubuntu Latest
- Node: 20.x
- Cache: npm dependencies

#### Job 2: Docker Build

**Requires:** Build & Test job to pass

**Steps:**
1. Checkout code
2. Setup Docker Buildx
3. Extract metadata (tags, labels)
4. Build Docker image
5. Test Docker image (health checks)
6. Save Docker image artifact

**Docker Build Features:**
- Multi-stage build (Node → Nginx)
- Layer caching (GitHub Actions cache)
- Health check validation
- Build artifact preservation

#### Job 3: Push to Docker Hub

**Requires:** Docker Build job to pass

**Triggers:**
- Push events (not PRs)
- Manual workflow dispatch with registry selection

**Steps:**
1. Login to Docker Hub
2. Build multi-platform image (amd64, arm64)
3. Push with tags:
   - Branch name (e.g., `main`, `develop`)
   - Git SHA (e.g., `main-abc1234`)
   - `latest` (for default branch only)

**Required Secrets:**
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

#### Job 4: Push to GitHub Container Registry

**Requires:** Docker Build job to pass

**Triggers:**
- Push events (not PRs)
- Manual workflow dispatch with registry selection

**Steps:**
1. Login to GHCR (uses GITHUB_TOKEN)
2. Build multi-platform image
3. Push with tags (same as Docker Hub)
4. Image URL: `ghcr.io/your-org/staticwaves-pod-studio`

**Permissions:**
- `contents: read`
- `packages: write`

#### Job 5: Deployment Ready

**Requires:** At least one registry push succeeds

**Steps:**
- Generate deployment summary
- Provide RunPod deployment instructions
- Link to deployment guides

### Workflow Configuration

#### Automatic Triggers

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'App.tsx'
      - 'components/**'
      - 'services/**'
      - 'Dockerfile'
      - 'package.json'
      - '.github/workflows/pod-pipeline.yml'
  pull_request:
    branches: [main, develop]
```

#### Manual Triggers

```yaml
workflow_dispatch:
  inputs:
    registry:
      description: 'Container Registry'
      type: choice
      options: [dockerhub, ghcr, both]
      default: 'dockerhub'
    tag:
      description: 'Image Tag'
      default: 'latest'
```

**Manual dispatch usage:**
1. Go to Actions tab in GitHub
2. Select "POD Studio CI/CD Pipeline"
3. Click "Run workflow"
4. Select registry and tag
5. Click "Run workflow"

## Container Registry Options

### Docker Hub

**Advantages:**
- Most popular container registry
- Excellent RunPod compatibility
- Free public repositories
- Simple authentication

**Setup:**
1. Create Docker Hub account
2. Generate access token (Account Settings → Security)
3. Add GitHub secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your access token

**Image URL Format:**
```
docker.io/your-username/staticwaves-pod-studio:latest
```

### GitHub Container Registry (GHCR)

**Advantages:**
- Integrated with GitHub
- Free for public repositories
- No additional account needed
- Automatic authentication in workflows

**Setup:**
1. No additional setup needed (uses `GITHUB_TOKEN`)
2. Make package public:
   - Go to package settings in GitHub
   - Change visibility to public

**Image URL Format:**
```
ghcr.io/your-org/staticwaves-pod-studio:latest
```

### Multi-Registry Strategy

Push to both registries for redundancy:

```bash
# Via GitHub Actions (manual dispatch)
# Select "both" as registry option

# Via deploy.sh script
./deploy.sh latest both
```

## Deployment Strategies

### RunPod Deployment

**Method 1: Web UI**

1. Login to [RunPod](https://www.runpod.io/)
2. Navigate to "Pods" → "Deploy"
3. Select "Deploy a Custom Container"
4. Configure:
   ```
   Container Image: your-username/staticwaves-pod-studio:latest
   Container Disk: 5 GB
   Expose HTTP Ports: 80
   GPU: None (CPU pod)
   CPU: 2 vCPU
   Memory: 2 GB
   ```
5. Click "Deploy On-Demand" or "Deploy Spot"
6. Access via provided HTTP endpoint

**Method 2: RunPod API**

```bash
curl -X POST https://api.runpod.io/v2/pods \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @runpod-config.json
```

**Method 3: Automated Script**

Use the deployment script with interactive prompts:

```bash
# Build, test, and deploy
./deploy.sh

# Specify version
./deploy.sh v1.0.0

# Specify registry
./deploy.sh latest dockerhub

# Multi-platform build
./deploy.sh latest dockerhub linux/amd64,linux/arm64
```

### Kubernetes Deployment

Create a Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-studio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pod-studio
  template:
    metadata:
      labels:
        app: pod-studio
    spec:
      containers:
      - name: pod-studio
        image: your-username/staticwaves-pod-studio:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: pod-studio
spec:
  selector:
    app: pod-studio
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Docker Compose Deployment

```yaml
version: '3.8'

services:
  pod-studio:
    image: your-username/staticwaves-pod-studio:latest
    ports:
      - "8080:80"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Run:
```bash
docker-compose up -d
```

## Monitoring & Debugging

### Health Checks

**Endpoint:** `GET /health`

**Expected Response:**
```
HTTP/1.1 200 OK
Content-Type: text/plain

healthy
```

**Test:**
```bash
curl http://your-pod-url/health
```

### Container Logs

**Docker:**
```bash
docker logs <container-id>
```

**Kubernetes:**
```bash
kubectl logs deployment/pod-studio
kubectl logs -f deployment/pod-studio  # Follow logs
```

**RunPod:**
- View logs in RunPod dashboard
- SSH into pod and check `/var/log/nginx/`

### Common Issues

**Issue: Pod won't start**
- Check logs for errors
- Verify image is public/accessible
- Ensure port 80 is exposed
- Check resource limits

**Issue: Application not loading**
- Test health endpoint
- Check nginx configuration
- Verify build completed successfully
- Check browser console for errors

**Issue: Build failures**
- Check TypeScript errors
- Verify dependencies install
- Check Docker build logs
- Ensure sufficient disk space

**Issue: Registry push failures**
- Verify credentials/secrets
- Check token permissions
- Ensure package/image is public
- Try manual login and push

## Best Practices

### Development

1. **Always test locally before pushing**
   ```bash
   npm run build
   docker build -t test .
   docker run -p 8080:80 test
   ```

2. **Use feature branches**
   ```bash
   git checkout -b feature/new-editor-tool
   git push origin feature/new-editor-tool
   # Create PR to develop
   ```

3. **Keep dependencies updated**
   ```bash
   npm outdated
   npm update
   ```

### CI/CD

1. **Tag releases properly**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. **Use semantic versioning**
   - MAJOR: Breaking changes
   - MINOR: New features
   - PATCH: Bug fixes

3. **Monitor workflow runs**
   - Check Actions tab regularly
   - Fix failing workflows promptly
   - Review deployment summaries

### Deployment

1. **Use spot instances for development**
   - Cheaper than on-demand
   - Acceptable for non-production

2. **Set resource limits**
   - Prevent cost overruns
   - Ensure stable performance

3. **Enable auto-stop**
   - Save costs when idle
   - Configure in RunPod settings

4. **Use HTTPS in production**
   - RunPod provides HTTPS proxies
   - Enable for security

### Security

1. **Keep secrets secure**
   - Never commit API keys
   - Use GitHub secrets
   - Rotate tokens regularly

2. **Use private registries for sensitive code**
   - GHCR supports private packages
   - Docker Hub private repos

3. **Update images regularly**
   - Patch security vulnerabilities
   - Update base images
   - Monitor CVEs

## Support

For issues with:
- **Application**: Check project repository issues
- **Pipeline**: Review GitHub Actions logs
- **RunPod**: Visit [RunPod Discord](https://discord.gg/runpod) or [Docs](https://docs.runpod.io/)
- **Docker**: Check [Docker Documentation](https://docs.docker.com/)

## Version History

- **v6.0** - Enhanced editor features, CI/CD pipeline, multi-registry support
- **v5.0** - RunPod deployment configuration
- **v4.0** - Docker containerization
- **v3.0** - Batch processing and queue management
- **v2.0** - Interactive design editor
- **v1.0** - Initial POD automation suite
