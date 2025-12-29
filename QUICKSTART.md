# RunPod Deployment - Quick Start Guide

## ✅ Build Verification Complete

The application has been successfully built and tested locally:
- ✅ Build completes successfully (217 KB bundle)
- ✅ Health check endpoint working at `/health.json`
- ✅ Application serves correctly with all assets
- ✅ Ready for Docker containerization

## 🚀 Deploy to RunPod in 3 Steps

### Step 1: Build and Push Docker Image

You have two options:

#### Option A: Automated Script (Recommended)
```bash
# Set your Docker Hub username
export DOCKERHUB_USERNAME=your-dockerhub-username

# Run the deployment script
./runpod-deploy.sh
```

This script will:
1. Build the Docker image
2. Test it locally
3. Tag it for Docker Hub
4. Push to your registry

#### Option B: Manual Build
```bash
# Build the image
docker build -t staticwaves-pod-studio:beta .

# Tag for Docker Hub
docker tag staticwaves-pod-studio:beta your-username/staticwaves-pod-studio:beta

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push your-username/staticwaves-pod-studio:beta
```

### Step 2: Create RunPod Template

1. Go to [RunPod Dashboard](https://runpod.io) → **Templates** → **New Template**

2. Configure the template:
   ```
   Container Image: your-username/staticwaves-pod-studio:beta
   Container Disk: 10 GB
   Exposed HTTP Port: 80
   ```

3. Add environment variables (optional):
   ```
   NODE_ENV=production
   BETA_MODE=true
   BETA_USERS_ALLOWED=true
   FEATURE_FLAG_BATCH_MODE=true
   FEATURE_FLAG_EDITOR=true
   ```

4. Click **Save Template**

### Step 3: Deploy Pod

1. Go to **Pods** → **Deploy**
2. Select your template
3. Choose a GPU/CPU tier:
   - **Recommended**: RTX 3070 or better
   - **Minimum**: 8GB RAM, 20GB storage
4. Click **Deploy**

Your pod will be available at:
```
https://<pod-id>-80.proxy.runpod.net
```

## 🧪 Test Your Deployment

Once deployed, verify:

### 1. Health Check
```bash
curl https://<pod-id>-80.proxy.runpod.net/health.json
```

Expected response:
```json
{
  "status": "healthy",
  "service": "staticwaves-pod-studio",
  "version": "6.0",
  "environment": "beta",
  "timestamp": "2025-12-29"
}
```

### 2. Application Access
Open in browser:
```
https://<pod-id>-80.proxy.runpod.net
```

You should see the StaticWaves POD Studio interface.

### 3. Basic Functionality Test
1. Enter a drop name (e.g., "TestDrop1")
2. Set design count to 5
3. Click "Run Single Drop"
4. Verify logs appear and progress updates

## 📊 Monitoring

### View Pod Logs
In RunPod Dashboard:
1. Go to your Pod
2. Click **Logs** tab
3. Monitor startup and runtime logs

### Check Container Health
RunPod automatically monitors the `/health.json` endpoint every 30 seconds.

## 🐛 Troubleshooting

### Build Fails
```bash
# Check Docker is installed
docker --version

# Check you're logged in
docker login
```

### Container Won't Start
```bash
# Test locally first
docker run -p 8080:80 your-username/staticwaves-pod-studio:beta

# Check logs
docker logs <container-id>
```

### 502 Bad Gateway
- Wait 30-60 seconds for container to fully start
- Check RunPod logs for errors
- Verify port 80 is exposed in template

### Health Check Failing
```bash
# Test locally
docker run -p 8080:80 your-username/staticwaves-pod-studio:beta
curl http://localhost:8080/health.json
```

## 📝 Next Steps

1. **Share with Beta Testers**
   - Send them the pod URL
   - Direct them to [BETA_TESTING.md](BETA_TESTING.md)

2. **Collect Feedback**
   - GitHub Issues: [Report bugs/features](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
   - Monitor performance metrics

3. **Iterate**
   - Make improvements based on feedback
   - Rebuild and redeploy as needed

## 🔄 Update Deployment

When you make changes:

```bash
# 1. Commit changes
git add .
git commit -m "Your changes"
git push

# 2. Rebuild image
docker build -t your-username/staticwaves-pod-studio:beta .
docker push your-username/staticwaves-pod-studio:beta

# 3. Restart pod in RunPod dashboard
# Or create new pod with updated image
```

## 📚 Additional Resources

- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
- [BETA_TESTING.md](BETA_TESTING.md) - Beta testing guide
- [beta-config.json](beta-config.json) - Feature flags and configuration
- [docker-compose.yml](docker-compose.yml) - Local testing setup

## 💡 Pro Tips

1. **Test Locally First**: Always test with `docker-compose up` before pushing
2. **Use Specific Tags**: Tag images with version numbers for easy rollback
3. **Monitor Resources**: Check CPU/memory usage in RunPod dashboard
4. **Set Up Alerts**: Configure RunPod webhooks for pod failures
5. **Keep Images Small**: Current image is ~200MB, optimized for fast deployment

## ⚡ Quick Commands Reference

```bash
# Local development
npm run dev                        # Start dev server
npm run build                      # Build for production
npm run preview                    # Preview production build

# Docker local testing
npm run docker:build               # Build Docker image
npm run docker:run                 # Run container locally
npm run docker:compose:build       # Build with docker-compose
npm run docker:compose             # Run with docker-compose
npm run docker:compose:down        # Stop docker-compose

# Deployment
./runpod-deploy.sh                 # Automated deployment
```

---

**Ready to deploy?** Start with Step 1 above! 🚀
