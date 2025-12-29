# StaticWaves POD Studio - Deployment Guide

## RunPod Deployment (Beta)

This guide covers deploying the StaticWaves POD Studio to RunPod for beta testing.

### Prerequisites

- Docker installed locally (for testing)
- RunPod account with credits
- Git installed

### Quick Start

#### 1. Local Testing with Docker

Before deploying to RunPod, test the container locally:

```bash
# Build the Docker image
docker build -t staticwaves-pod-studio:beta .

# Run locally
docker run -p 8080:80 staticwaves-pod-studio:beta

# Or use docker-compose
docker-compose up
```

Access the application at: `http://localhost:8080`

Check health: `http://localhost:8080/health.json`

#### 2. Deploy to RunPod

##### Option A: Using RunPod Docker Registry

1. **Build and tag your image:**
   ```bash
   docker build -t <your-dockerhub-username>/staticwaves-pod-studio:beta .
   docker push <your-dockerhub-username>/staticwaves-pod-studio:beta
   ```

2. **Create RunPod Template:**
   - Go to RunPod Dashboard → Templates
   - Click "New Template"
   - Set container image: `<your-dockerhub-username>/staticwaves-pod-studio:beta`
   - Set exposed HTTP port: `80`
   - Add environment variables from `.env.example`

3. **Deploy Pod:**
   - Go to Pods → Deploy
   - Select your template
   - Choose GPU/CPU configuration
   - Click "Deploy"

##### Option B: Direct Deployment from GitHub

1. **Fork/Clone Repository:**
   ```bash
   git clone https://github.com/<your-org>/ssiens-oss-static_pod.git
   cd ssiens-oss-static_pod
   ```

2. **Create RunPod Template with GitHub:**
   - Container Image: Build from GitHub
   - Repository URL: Your repository URL
   - Branch: `claude/runpod-deployment-beta-bYWSF`
   - Dockerfile Path: `/Dockerfile`
   - Exposed Port: `80`

### Environment Variables

Configure these in your RunPod template:

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Application environment |
| `BETA_MODE` | `true` | Enable beta features |
| `BETA_USERS_ALLOWED` | `true` | Allow beta user access |
| `FEATURE_FLAG_BATCH_MODE` | `true` | Enable batch processing |
| `FEATURE_FLAG_EDITOR` | `true` | Enable design editor |
| `LOG_LEVEL` | `info` | Logging level |

### Health Checks

The application includes built-in health checks:

- **Endpoint:** `/health.json`
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "staticwaves-pod-studio",
    "version": "6.0",
    "environment": "beta"
  }
  ```

### Accessing Your Deployment

Once deployed, RunPod will provide:
- **Pod URL:** `https://<pod-id>-80.proxy.runpod.net`
- **Direct IP:** For advanced networking

### Beta Testing Checklist

- [ ] Container builds successfully
- [ ] Health check returns 200 OK
- [ ] Application UI loads
- [ ] Batch mode works correctly
- [ ] Design editor functions properly
- [ ] Logs are accessible
- [ ] No console errors

### Monitoring

#### View Logs

```bash
# Docker logs (local)
docker logs <container-id> -f

# Docker Compose logs
docker-compose logs -f

# RunPod Logs
# Access through RunPod dashboard → Pod → Logs
```

#### Performance Metrics

Monitor these metrics during beta testing:
- Response time for UI loads
- Batch processing speed
- Memory usage
- CPU utilization

### Troubleshooting

#### Container Won't Start

```bash
# Check build logs
docker build -t staticwaves-pod-studio:beta . --progress=plain

# Validate nginx config
docker run staticwaves-pod-studio:beta nginx -t
```

#### Health Check Failing

```bash
# Test locally
curl http://localhost:8080/health.json

# Check nginx logs
docker exec <container-id> tail -f /var/log/nginx/error.log
```

#### Application Not Loading

1. Check nginx is running: `docker ps`
2. Verify port mapping: `docker port <container-id>`
3. Check browser console for errors
4. Verify build output exists: `docker exec <container-id> ls /usr/share/nginx/html`

### Scaling Considerations

For production deployment:

1. **Load Balancing:** Deploy multiple pods behind a load balancer
2. **CDN:** Use CloudFlare or similar for static assets
3. **Database:** Add persistent storage for user data
4. **API Backend:** Integrate with StaticWaves API service
5. **Monitoring:** Set up Prometheus/Grafana

### Security Notes

- HTTPS is handled by RunPod proxy
- No sensitive data is stored in the container
- API keys should be passed via environment variables
- CORS is configurable via `.env`

### Rollback Procedure

If issues occur during beta:

```bash
# Redeploy previous image
docker pull <your-dockerhub-username>/staticwaves-pod-studio:previous-tag
docker tag <your-dockerhub-username>/staticwaves-pod-studio:previous-tag \
  <your-dockerhub-username>/staticwaves-pod-studio:beta
docker push <your-dockerhub-username>/staticwaves-pod-studio:beta
```

### Support

For issues or questions:
- GitHub Issues: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- AI Studio: https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

### Next Steps

After successful beta deployment:
1. Gather user feedback
2. Monitor performance metrics
3. Iterate on features
4. Plan production release
