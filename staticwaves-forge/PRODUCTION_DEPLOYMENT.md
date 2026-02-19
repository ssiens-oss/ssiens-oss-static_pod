# 🚀 StaticWaves Forge - Production Deployment Guide

Complete guide for deploying StaticWaves Forge in production with automated CI/CD, versioning, and rollback support.

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [CI/CD Pipeline](#cicd-pipeline)
- [Manual Deployment](#manual-deployment)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- GitHub account with GHCR access

### One-Command Deployment

```bash
# Set your version
export VERSION=v1.0.0
export GITHUB_REPOSITORY=your-org/your-repo

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

Access your services:
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔄 CI/CD Pipeline

### Automated Releases

The GitHub Actions workflow automatically builds and pushes Docker images when you create a new tag.

#### Creating a Release

```bash
# 1. Commit your changes
git add .
git commit -m "Release v1.1.0: Add new features"

# 2. Create a version tag
git tag v1.1.0

# 3. Push tag to trigger CI/CD
git push origin v1.1.0
```

This will automatically:
- ✅ Build web and API images
- ✅ Tag with version number (v1.1.0, 1.1, 1, latest)
- ✅ Push to GitHub Container Registry
- ✅ Generate deployment summary

#### Manual Trigger

You can also manually trigger builds from GitHub:

1. Go to **Actions** → **Build & Push StaticWaves Images**
2. Click **Run workflow**
3. Enter version tag (e.g., `v1.0.0`)
4. Click **Run workflow**

### Image Tags

Each release creates multiple tags:

```
ghcr.io/your-org/your-repo/web:v1.2.3   # Full version
ghcr.io/your-org/your-repo/web:1.2      # Major.Minor
ghcr.io/your-org/your-repo/web:1        # Major only
ghcr.io/your-org/your-repo/web:latest   # Always latest
ghcr.io/your-org/your-repo/web:main-abc123  # Commit SHA
```

---

## 🖥️ Manual Deployment

### Step 1: Pull Images

```bash
# Set your version
export VERSION=v1.0.0
export GITHUB_REPOSITORY=your-org/your-repo

# Pull all images
docker compose -f docker-compose.prod.yml pull
```

### Step 2: Start Services

```bash
# Start in detached mode
docker compose -f docker-compose.prod.yml up -d

# Or with logs
docker compose -f docker-compose.prod.yml up
```

### Step 3: Verify Deployment

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Health check
curl http://localhost:8000/
curl http://localhost:3000
```

---

## ⏪ Rollback Procedures

### Quick Rollback

Use the automated rollback script:

```bash
# List available versions
./scripts/rollback.sh

# Rollback to specific version
./scripts/rollback.sh v1.0.0
```

The script will:
1. Pull the specified version
2. Stop current services
3. Start services with the target version
4. Verify health checks
5. Report status

### Manual Rollback

```bash
# 1. Set target version
export VERSION=v1.0.0

# 2. Pull images
docker compose -f docker-compose.prod.yml pull

# 3. Restart services
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Emergency Rollback (Zero Downtime)

```bash
# Update only the failing service
docker compose -f docker-compose.prod.yml up -d --no-deps --build web

# Or scale down and back up
docker compose -f docker-compose.prod.yml scale web=0
export VERSION=v1.0.0
docker compose -f docker-compose.prod.yml scale web=1
```

---

## 📊 Monitoring & Health Checks

### Built-in Health Checks

All services include health checks:

```bash
# View health status
docker compose -f docker-compose.prod.yml ps

# Inspect specific service
docker inspect staticwaves-web --format='{{.State.Health.Status}}'
```

### Manual Health Checks

```bash
# API Health
curl http://localhost:8000/

# Web Health
curl -I http://localhost:3000

# Redis Health
docker exec staticwaves-redis redis-cli ping
```

### Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f web

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.prod.yml logs

# Verify images exist
docker images | grep staticwaves

# Pull images manually
docker pull ghcr.io/your-org/your-repo/web:latest
docker pull ghcr.io/your-org/your-repo/api:latest
```

### Port Conflicts

```bash
# Check what's using ports
sudo netstat -tulpn | grep -E ':(3000|8000|6379)'

# Use different ports
export WEB_PORT=3001
export API_PORT=8001
docker compose -f docker-compose.prod.yml up -d
```

### Image Pull Failures

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Verify repository name
export GITHUB_REPOSITORY=your-org/your-repo

# Pull manually
docker pull ghcr.io/$GITHUB_REPOSITORY/web:latest
```

### Health Check Failures

```bash
# Increase startup time
# Edit docker-compose.prod.yml:
healthcheck:
  start_period: 60s  # Increase from 40s

# Restart services
docker compose -f docker-compose.prod.yml restart
```

---

## 🔒 Security Best Practices

### Environment Variables

Never commit secrets. Use `.env` file:

```bash
# Create .env file
cat > .env << EOF
VERSION=v1.0.0
GITHUB_REPOSITORY=your-org/your-repo
DATABASE_URL=postgresql://user:pass@host/db
API_KEY=your-secret-key
EOF

# Docker Compose will load automatically
docker compose -f docker-compose.prod.yml up -d
```

### Image Scanning

```bash
# Scan images for vulnerabilities
docker scan ghcr.io/your-org/your-repo/web:latest
docker scan ghcr.io/your-org/your-repo/api:latest
```

### Network Security

```bash
# Services communicate via internal network
# Only expose necessary ports to host

# To restrict external access:
# Edit docker-compose.prod.yml and change:
ports:
  - "127.0.0.1:3000:3000"  # Only localhost
```

---

## 📦 Version Management

### Semantic Versioning

Follow SemVer (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes (v2.0.0)
- **MINOR**: New features (v1.1.0)
- **PATCH**: Bug fixes (v1.0.1)

### Tagging Strategy

```bash
# Stable release
git tag v1.0.0

# Release candidate
git tag v1.1.0-rc1

# Beta release
git tag v2.0.0-beta.1
```

### Viewing Current Version

```bash
# Check running version
docker inspect staticwaves-web \
  --format='{{index .Config.Labels "com.staticwaves.version"}}'

# List all versions
docker images ghcr.io/your-org/your-repo/web --format "{{.Tag}}"
```

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] Version tag created
- [ ] Images built and pushed
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Health checks configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Rollback plan tested
- [ ] Documentation updated

---

## 📞 Support

For issues or questions:

- GitHub Issues: https://github.com/your-org/your-repo/issues
- Documentation: https://github.com/your-org/your-repo/wiki
- API Docs: http://localhost:8000/docs

---

**Version**: 1.0.0
**Last Updated**: 2026-01-01
