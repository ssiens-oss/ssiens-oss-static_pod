# RunPod Deployment Guide for StaticWaves POD Studio

This guide explains how to deploy the StaticWaves POD Studio application to RunPod.

## Prerequisites

1. Docker installed on your local machine
2. Docker Hub account (or other container registry)
3. RunPod account with credits

## Step 1: Build the Docker Image

Build the Docker image locally:

```bash
docker build -t staticwaves-pod-studio:latest .
```

Test the image locally:

```bash
docker run -p 8080:80 staticwaves-pod-studio:latest
```

Visit `http://localhost:8080` to verify the application works.

## Step 2: Push to Container Registry

### Using Docker Hub

1. Tag your image:
```bash
docker tag staticwaves-pod-studio:latest YOUR_DOCKERHUB_USERNAME/staticwaves-pod-studio:latest
```

2. Login to Docker Hub:
```bash
docker login
```

3. Push the image:
```bash
docker push YOUR_DOCKERHUB_USERNAME/staticwaves-pod-studio:latest
```

### Using GitHub Container Registry (GHCR)

1. Create a personal access token with `write:packages` permission
2. Login to GHCR:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

3. Tag and push:
```bash
docker tag staticwaves-pod-studio:latest ghcr.io/YOUR_GITHUB_USERNAME/staticwaves-pod-studio:latest
docker push ghcr.io/YOUR_GITHUB_USERNAME/staticwaves-pod-studio:latest
```

## Step 3: Deploy on RunPod

### Method 1: Using RunPod Web UI

1. Log in to [RunPod](https://www.runpod.io/)
2. Navigate to "Pods" > "Deploy"
3. Select "Deploy a Custom Container"
4. Configure the pod:
   - **Container Image**: `YOUR_DOCKERHUB_USERNAME/staticwaves-pod-studio:latest`
   - **Container Disk**: 5 GB (minimum)
   - **Expose HTTP Ports**: `80`
   - **GPU**: Not required (select CPU pod for cost savings)
   - **CPU**: 2 vCPU recommended
   - **Memory**: 2 GB minimum

5. Click "Deploy On-Demand" or "Deploy Spot" (cheaper but can be interrupted)

6. Once deployed, click on the pod and find the "Connect" button
7. Access your application via the provided HTTP endpoint

### Method 2: Using RunPod API

You can also deploy using the RunPod API with the provided `runpod-config.json`:

```bash
curl -X POST https://api.runpod.io/v2/pods \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d @runpod-config.json
```

## Step 4: Access Your Application

After deployment:

1. Navigate to your pod in the RunPod dashboard
2. Click on "Connect" to see available endpoints
3. Open the HTTP endpoint (e.g., `https://your-pod-id-80.proxy.runpod.net`)
4. Your StaticWaves POD Studio should now be accessible!

## Configuration

The application runs on port 80 inside the container and uses Nginx as the web server.

### Health Checks

The deployment includes health checks at the `/health` endpoint to ensure the application is running correctly.

### Environment Variables

Currently, no environment variables are required. If you need to add the GEMINI_API_KEY:

1. Update the Dockerfile to include env var support
2. Add the env var in RunPod pod configuration:
   - Key: `GEMINI_API_KEY`
   - Value: Your API key

## Troubleshooting

### Pod won't start
- Check the pod logs in RunPod dashboard
- Verify your Docker image is publicly accessible
- Ensure port 80 is exposed in the configuration

### Application not loading
- Check nginx logs: `docker logs <container_id>`
- Verify the build completed successfully
- Check the health endpoint: `curl http://your-pod-url/health`

### Performance issues
- Increase CPU/Memory allocation in pod settings
- Consider using a faster pod tier

## Updating the Deployment

To update your deployment:

1. Make changes to your code
2. Rebuild the Docker image with a new tag (e.g., `v1.1`)
3. Push to your container registry
4. In RunPod, stop the current pod
5. Deploy a new pod with the updated image tag

## Cost Optimization

- Use **Spot Pods** instead of On-Demand for significant savings
- No GPU is needed for this application (use CPU-only pods)
- Stop pods when not in use
- Set up auto-stop policies in RunPod settings

## Support

For issues with:
- Application: Check the project repository
- RunPod platform: Visit [RunPod Discord](https://discord.gg/runpod) or [Documentation](https://docs.runpod.io/)

## Security Notes

- The current configuration allows public access to port 80
- Add authentication if deploying to production
- Keep your Docker images updated with security patches
- Use HTTPS in production (RunPod provides HTTPS proxies)
