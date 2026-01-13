# Production POD Engine - Deployment Guide

This guide will help you deploy the Production POD Engine in various environments.

## Quick Start (5 Minutes)

### 1. Initial Setup

```bash
# Clone and navigate to project
cd ssiens-oss-static_pod

# Run deployment setup
npm run production:deploy
```

This will:
- Check prerequisites (Node.js 18+, npm)
- Install dependencies
- Create configuration files
- Set up directories
- Validate environment

### 2. Configure Environment

Edit the configuration files created:

```bash
# Edit API keys and settings
nano production/.env

# Edit detailed configuration
nano production/config.json
```

**Required:**
- `CLAUDE_API_KEY` - Your Claude API key
- `COMFYUI_API_URL` - ComfyUI instance URL (default: http://127.0.0.1:8188)

**Optional:**
- Printify, Shopify, TikTok, Etsy credentials
- Database settings
- Worker configuration

### 3. Start ComfyUI

Make sure ComfyUI is running before starting the engine:

```bash
# Check if ComfyUI is running
curl http://127.0.0.1:8188/system_stats

# If not running, start ComfyUI first
cd /path/to/comfyui
python main.py
```

### 4. Validate Setup

```bash
npm run production:validate
```

This checks:
- ✅ Node.js version
- ✅ Configuration files
- ✅ Required directories
- ✅ API keys
- ✅ External services

### 5. Start the Engine

**Option A: Worker Pool with API (Recommended)**
```bash
npm run production:api
```

**Option B: Single Worker (Development)**
```bash
npm run production:worker
```

**Option C: Docker (Production)**
```bash
npm run production:docker
```

### 6. Verify Running

```bash
# Check status
npm run production:status

# Or manually check the API
curl http://localhost:3000/health
```

## Deployment Methods

### Method 1: Local Node.js

Best for: Development, testing, small workloads

```bash
# Setup and configure
npm run production:deploy

# Edit configuration
nano production/.env
nano production/config.json

# Validate
npm run production:validate

# Start worker pool with API
npm run production:api

# In another terminal, check status
npm run production:status
```

**Pros:**
- Quick to set up
- Easy to debug
- No container overhead

**Cons:**
- No isolation
- Manual process management
- Not suitable for production at scale

### Method 2: Docker Compose

Best for: Production deployments, isolated environments

```bash
# Setup configuration
npm run production:deploy

# Edit .env file
nano production/.env

# Build and start all services
npm run production:docker-build

# Check status
cd production && docker-compose ps
docker-compose logs -f pod-engine
```

**Services included:**
- PostgreSQL database
- ComfyUI (GPU required)
- Redis
- POD Engine API

**Pros:**
- Complete isolation
- Easy scaling
- Production-ready
- Health checks and auto-restart

**Cons:**
- Requires Docker
- Needs GPU for ComfyUI
- More complex troubleshooting

### Method 3: Kubernetes

Best for: Enterprise deployments, high availability

```bash
# Create namespace
kubectl create namespace pod-engine

# Create secrets
kubectl create secret generic pod-engine-secrets \
  --from-literal=claude-api-key=your_key \
  --from-literal=database-url=postgresql://... \
  -n pod-engine

# Apply configuration
kubectl apply -f production/k8s/ -n pod-engine

# Check status
kubectl get pods -n pod-engine
kubectl logs -f deployment/pod-engine -n pod-engine
```

See `production/README.md` for full Kubernetes configuration.

**Pros:**
- Horizontal scaling
- High availability
- Load balancing
- Self-healing

**Cons:**
- Complex setup
- Requires K8s cluster
- Higher resource requirements

### Method 4: PM2 (Process Manager)

Best for: VPS/server deployments, always-on services

```bash
# Install PM2 globally
npm install -g pm2

# Setup
npm run production:deploy

# Start with PM2
pm2 start production/examples/worker-pool-api.ts \
  --name pod-engine \
  --interpreter ts-node

# Save configuration
pm2 save

# Setup auto-start on boot
pm2 startup
```

**Pros:**
- Process monitoring
- Auto-restart on failure
- Log management
- Cluster mode

**Cons:**
- Manual setup
- Less isolation than Docker

## Configuration

### Environment Variables (.env)

```bash
# Required
CLAUDE_API_KEY=sk-ant-...
COMFYUI_API_URL=http://127.0.0.1:8188

# Database
DATABASE_TYPE=memory  # or 'postgres'
DATABASE_URL=postgresql://user:pass@localhost:5432/pod_engine

# Platforms (Optional)
PRINTIFY_API_KEY=...
PRINTIFY_SHOP_ID=...
SHOPIFY_STORE_URL=...
SHOPIFY_ACCESS_TOKEN=...

# Engine Settings
WORKER_COUNT=3
MAX_CONCURRENT_JOBS=5
API_PORT=3000
API_AUTH_TOKEN=your_secret_token
```

### Configuration File (config.json)

See `production/config.example.json` for full options:

```json
{
  "orchestrator": {
    "comfyui": { ... },
    "claude": { ... },
    "storage": { ... },
    "options": {
      "enabledPlatforms": ["printify"],
      "autoPublish": false
    }
  },
  "engine": {
    "maxConcurrentJobs": 5,
    "jobTimeout": 3600000,
    "enableAutoRetry": true
  },
  "workerPool": {
    "workerCount": 3,
    "autoRestart": true
  },
  "api": {
    "port": 3000,
    "enableCors": true
  }
}
```

## Management Commands

### Start/Stop

```bash
# Start (worker pool with API)
npm run production:start

# Start single worker
npm run production:worker

# Start with Docker
npm run production:docker

# Stop all
npm run production:stop

# Stop Docker only
./production/scripts/stop.sh docker
```

### Status & Monitoring

```bash
# Check status
npm run production:status

# Health check
curl http://localhost:3000/health

# Statistics
curl http://localhost:3000/stats

# Dashboard data
curl http://localhost:3000/dashboard

# Logs (Docker)
docker-compose -f production/docker-compose.yml logs -f
```

### Job Management

```bash
# Submit a job
curl -X POST http://localhost:3000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "Cyber Punk",
    "productTypes": ["tshirt"],
    "count": 2
  }'

# Get job status
curl http://localhost:3000/jobs/<job-id>

# List jobs
curl http://localhost:3000/jobs?status=completed&limit=10
```

### Scaling

```bash
# Scale workers (API call)
curl -X POST http://localhost:3000/scale \
  -H "Content-Type: application/json" \
  -d '{"workerCount": 5}'

# Scale Docker services
docker-compose -f production/docker-compose.yml up -d --scale pod-engine=3
```

## Database Setup

### PostgreSQL (Production)

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE pod_engine;
CREATE USER pod_user WITH ENCRYPTED PASSWORD 'pod_password';
GRANT ALL PRIVILEGES ON DATABASE pod_engine TO pod_user;
EOF

# Run schema
psql -U pod_user -d pod_engine -f production/schema.sql

# Update .env
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://pod_user:pod_password@localhost:5432/pod_engine
```

### In-Memory (Development)

No setup required - just set in `.env`:

```bash
DATABASE_TYPE=memory
```

## Troubleshooting

### Engine Won't Start

```bash
# Check prerequisites
npm run production:validate

# Check logs
cat logs/*.log

# Check if port is in use
lsof -i :3000

# Check ComfyUI
curl http://127.0.0.1:8188/system_stats
```

### Workers Not Processing Jobs

```bash
# Check worker status
curl http://localhost:3000/workers

# Check queue stats
curl http://localhost:3000/stats

# Check logs for errors
curl http://localhost:3000/alerts
```

### High Memory Usage

```bash
# Reduce concurrent jobs
# Edit config.json:
{
  "engine": {
    "maxConcurrentJobs": 2  # Reduce from 5
  }
}

# Reduce worker count
{
  "workerPool": {
    "workerCount": 2  # Reduce from 3
  }
}

# Restart
npm run production:stop
npm run production:start
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql "$DATABASE_URL" -c "SELECT 1"

# Check if schema is loaded
psql "$DATABASE_URL" -c "\dt"

# Reload schema
psql "$DATABASE_URL" -f production/schema.sql

# Fall back to in-memory
# Edit .env:
DATABASE_TYPE=memory
```

### Docker Issues

```bash
# Check Docker status
docker-compose -f production/docker-compose.yml ps

# View logs
docker-compose -f production/docker-compose.yml logs -f

# Restart services
docker-compose -f production/docker-compose.yml restart

# Clean rebuild
docker-compose -f production/docker-compose.yml down -v
docker-compose -f production/docker-compose.yml up -d --build
```

## Performance Tuning

### For High Throughput

```json
{
  "workerPool": {
    "workerCount": 5  // More workers
  },
  "engine": {
    "maxConcurrentJobs": 10  // More jobs per worker
  }
}
```

### For Low Memory

```json
{
  "workerPool": {
    "workerCount": 1
  },
  "engine": {
    "maxConcurrentJobs": 2
  }
}
```

### For Reliability

```json
{
  "engine": {
    "enableAutoRetry": true,
    "retryDelay": 60000  // 1 minute
  },
  "workerPool": {
    "autoRestart": true,
    "maxRestarts": 5
  }
}
```

## Security

### API Authentication

Enable authentication in production:

```bash
# Generate secure token
API_AUTH_TOKEN=$(openssl rand -hex 32)

# Add to .env
echo "API_AUTH_TOKEN=$API_AUTH_TOKEN" >> production/.env

# Use in requests
curl -H "Authorization: Bearer $API_AUTH_TOKEN" \
  http://localhost:3000/health
```

### Database Security

```bash
# Use strong passwords
# Limit network access in pg_hba.conf
# Use SSL connections

DATABASE_URL=postgresql://user:pass@localhost:5432/db?sslmode=require
```

### Docker Security

```bash
# Don't expose ports publicly
# Use Docker secrets
# Run as non-root user

docker secret create claude_api_key ./api_key.txt
```

## Monitoring & Logging

### Logs

```bash
# Application logs
tail -f logs/engine.log

# Docker logs
docker-compose logs -f pod-engine

# PM2 logs
pm2 logs pod-engine
```

### Metrics

Access metrics via API:

```bash
# Job duration metrics
curl http://localhost:3000/metrics?name=job_duration

# Worker metrics
curl http://localhost:3000/metrics?name=workers_running
```

### Alerts

```bash
# Get recent alerts
curl http://localhost:3000/alerts

# Filter by severity
curl http://localhost:3000/alerts?severity=critical
```

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
pg_dump pod_engine > backup_$(date +%Y%m%d).sql

# Restore
psql pod_engine < backup_20240101.sql
```

### Configuration Backup

```bash
# Backup configs
tar -czf config_backup.tar.gz production/.env production/config.json

# Restore
tar -xzf config_backup.tar.gz
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- Documentation: `/production/README.md`
- Scripts: `/production/scripts/`

## Next Steps

1. ✅ Complete initial setup
2. ✅ Configure API keys
3. ✅ Start ComfyUI
4. ✅ Deploy engine
5. ✅ Submit test job
6. 📊 Monitor performance
7. 🚀 Scale as needed
