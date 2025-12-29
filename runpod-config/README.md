# RunPod Pod Engine Configuration

This directory contains all RunPod-specific configurations, scripts, and tools for deploying and managing the StaticWaves POD Studio on RunPod infrastructure.

## 📁 Directory Contents

| File | Purpose | Usage |
|------|---------|-------|
| `pod-template.json` | Pod configuration template | Use to create RunPod template |
| `pod-startup.sh` | Main startup script | Automatically run on pod start |
| `optimize-pod.sh` | System optimization script | Run during startup |
| `health-monitor.sh` | Health monitoring service | Background monitoring |
| `runpod-api.sh` | RunPod API CLI tool | Manage pods via API |
| `.env.production` | Production environment vars | Configuration reference |

## 🚀 Quick Start

### 1. Deploy to RunPod

```bash
# Build and push Docker image
docker build -t your-username/staticwaves-pod-studio:beta .
docker push your-username/staticwaves-pod-studio:beta

# Create RunPod template using pod-template.json
# Then deploy pod via RunPod dashboard
```

### 2. Access Your Pod

Once deployed, access your pod at:
```
https://[pod-id]-80.proxy.runpod.net
```

Health check:
```
https://[pod-id]-80.proxy.runpod.net/health.json
```

## 📋 Pod Configuration Template

### Using `pod-template.json`

This file contains the recommended configuration for deploying StaticWaves POD Studio:

**Key Settings:**
- **GPU**: NVIDIA RTX 3070 (minimum)
- **Memory**: 8 GB RAM
- **Storage**: 50 GB volume + 20 GB container disk
- **Ports**: 80 (HTTP)
- **CUDA**: 12.1

**To customize:**
1. Edit `pod-template.json`
2. Update `imageName` with your Docker Hub username
3. Adjust resource requirements as needed
4. Import template in RunPod dashboard

## 🔧 Scripts Reference

### pod-startup.sh

Main startup orchestrator that runs on pod initialization.

**What it does:**
1. Runs system optimizations
2. Validates configuration
3. Sets file permissions
4. Starts health monitoring
5. Launches nginx server
6. Performs final health check

**Environment variables:**
- `NODE_ENV` - Environment (production/staging)
- `RUNPOD_POD_ID` - Pod identifier
- `BETA_MODE` - Enable beta features

**Logs:**
- Stdout: Startup progress
- `/var/log/nginx/access.log` - Access logs
- `/var/log/nginx/error.log` - Error logs

### optimize-pod.sh

System and GPU optimization script.

**Features:**
- Increases file descriptor limits
- Optimizes network settings
- Configures memory management
- Enables GPU persistence mode
- Sets optimal GPU power limits

**Usage:**
```bash
# Automatically run during startup
# Or run manually:
/runpod-config/optimize-pod.sh

# Check optimization status:
cat /tmp/pod-optimization-status.json
```

**Output:**
```json
{
  "timestamp": "2025-12-29T12:00:00Z",
  "pod_id": "abc123xyz",
  "optimizations_applied": {
    "file_descriptors": true,
    "network_tuning": true,
    "gpu_persistence": true
  },
  "status": "optimized"
}
```

### health-monitor.sh

Continuous health monitoring service.

**Monitors:**
- Application health endpoint
- CPU usage (alert if > 80%)
- Memory usage (alert if > 85%)
- Disk usage (alert if > 90%)
- GPU utilization (if available)
- Nginx process status

**Usage:**
```bash
# Start continuous monitoring (runs automatically)
/runpod-config/health-monitor.sh monitor

# One-time health check
/runpod-config/health-monitor.sh check
```

**Health Report:**
```json
{
  "timestamp": "2025-12-29T12:00:00Z",
  "pod_id": "abc123xyz",
  "overall_status": "healthy",
  "checks": {
    "application": { "status": "HEALTHY" },
    "cpu": { "status": "OK:45%" },
    "memory": { "status": "OK:60%" },
    "disk": { "status": "OK:35%" },
    "gpu": { "status": "OK:GPU-70%,MEM-50%,TEMP-65C" }
  }
}
```

**Logs:**
- `/var/log/health-monitor.log`

### runpod-api.sh

CLI tool for managing pods via RunPod GraphQL API.

**Prerequisites:**
```bash
export RUNPOD_API_KEY=your-api-key
```

Get API key from: https://www.runpod.io/console/user/settings

**Commands:**

```bash
# List all pods
./runpod-api.sh list-pods

# Get pod details
./runpod-api.sh get-pod <pod_id>

# Start a stopped pod
./runpod-api.sh start-pod <pod_id>

# Stop a running pod
./runpod-api.sh stop-pod <pod_id>

# Terminate a pod
./runpod-api.sh terminate-pod <pod_id>

# Monitor pod metrics
./runpod-api.sh monitor-pod <pod_id> [interval_seconds]

# View account info
./runpod-api.sh account-info
```

**Examples:**
```bash
# Monitor pod every 60 seconds
./runpod-api.sh monitor-pod abc123xyz 60

# Get detailed pod information
./runpod-api.sh get-pod abc123xyz | jq .
```

## 🔒 Environment Configuration

### .env.production

Production environment template with all configuration options.

**Key sections:**
- **Application**: Basic app settings
- **Beta Configuration**: Beta features and limits
- **Feature Flags**: Enable/disable features
- **Performance**: Resource limits and optimization
- **Security**: CORS, rate limiting
- **Monitoring**: Health checks and metrics
- **RunPod Specific**: Pod identifiers
- **External Services**: API integrations (optional)

**Usage:**
1. Copy to pod as environment variables
2. Override in RunPod template
3. Or mount as file: `-v .env.production:/app/.env`

## 📊 Monitoring & Debugging

### View Logs

**Nginx access logs:**
```bash
tail -f /var/log/nginx/access.log
```

**Nginx error logs:**
```bash
tail -f /var/log/nginx/error.log
```

**Health monitor logs:**
```bash
tail -f /var/log/health-monitor.log
```

### Check System Status

**Application health:**
```bash
curl http://localhost/health.json | jq .
```

**System resources:**
```bash
# CPU and memory
top

# Disk usage
df -h

# GPU status (if available)
nvidia-smi
```

**Optimization status:**
```bash
cat /tmp/pod-optimization-status.json | jq .
```

**Health status:**
```bash
cat /tmp/health-report.json | jq .
```

### Common Issues

**Problem: Pod won't start**
```bash
# Check Docker logs
docker logs <container_id>

# Verify startup script
bash -x /runpod-config/pod-startup.sh
```

**Problem: High CPU usage**
```bash
# Check health monitor for alerts
cat /tmp/health-report.json

# Identify process
top -bn1 | head -20
```

**Problem: Health check failing**
```bash
# Test endpoint manually
curl -v http://localhost/health.json

# Check nginx status
ps aux | grep nginx

# Restart nginx
nginx -s reload
```

## 🎯 Production Checklist

Before deploying to production:

### Configuration
- [ ] Update `imageName` in `pod-template.json`
- [ ] Set production environment variables
- [ ] Configure resource limits appropriately
- [ ] Set up API keys (if needed)
- [ ] Configure monitoring/alerting

### Security
- [ ] Update `SESSION_SECRET` in environment
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Review file permissions
- [ ] Enable HTTPS (handled by RunPod)

### Performance
- [ ] Choose appropriate GPU tier
- [ ] Set optimal worker processes
- [ ] Configure caching
- [ ] Enable compression (nginx)
- [ ] Test under load

### Monitoring
- [ ] Enable health checks
- [ ] Configure alert thresholds
- [ ] Set up log aggregation
- [ ] Enable metrics collection
- [ ] Test monitoring scripts

### Testing
- [ ] Deploy to staging first
- [ ] Run health check
- [ ] Test all features
- [ ] Verify performance
- [ ] Check logs for errors

## 🔄 Updates & Maintenance

### Updating the Deployment

```bash
# 1. Build new image
docker build -t your-username/staticwaves-pod-studio:beta .

# 2. Push to registry
docker push your-username/staticwaves-pod-studio:beta

# 3. Stop old pod (via RunPod dashboard or API)
./runpod-api.sh stop-pod <pod_id>

# 4. Deploy new pod with updated image
# (Use RunPod dashboard or API)
```

### Scaling

**Vertical scaling:**
- Upgrade GPU tier in RunPod
- Increase memory/CPU allocation
- Adjust resource limits in template

**Horizontal scaling:**
- Deploy multiple pods
- Use load balancer
- Configure session persistence

## 📞 Support

**Resources:**
- Main README: `../README.md`
- Deployment Guide: `../DEPLOYMENT.md`
- Quick Start: `../QUICKSTART.md`
- Walkthrough: `../WALKTHROUGH.md`

**Issues:**
- GitHub: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- RunPod Support: https://www.runpod.io/support

## 📝 Notes

- All scripts assume running on RunPod infrastructure
- GPU optimizations only work with NVIDIA GPUs
- Health monitoring runs continuously in background
- Logs rotate automatically (nginx)
- Default timezone: UTC

---

**Last Updated:** 2025-12-29
**Version:** 6.0-beta.1
**RunPod Engine:** v1.0
