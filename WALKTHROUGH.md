# StaticWaves POD Studio - Complete Walkthrough

This walkthrough will guide you through deploying and testing your application on RunPod from start to finish.

---

## Part 1: Pre-Deployment Checklist

### Step 1.1: Verify Local Setup ✅

First, let's make sure everything works locally:

```bash
# Navigate to project directory
cd /path/to/ssiens-oss-static_pod

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Result:** Server starts at `http://localhost:3000`

**Checkpoint:**
- [ ] Application loads in browser
- [ ] No console errors
- [ ] UI displays correctly

### Step 1.2: Test Production Build 🔨

```bash
# Build for production
npm run build

# Preview the production build
npm run preview
```

**Expected Result:**
- Build completes successfully
- Preview server starts at `http://localhost:4173`

**Checkpoint:**
- [ ] Build succeeds (no errors)
- [ ] Health endpoint works: `curl http://localhost:4173/health.json`
- [ ] Application loads and functions correctly

---

## Part 2: Docker Preparation

### Step 2.1: Install Docker (if needed)

**macOS:**
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

**Verify Installation:**
```bash
docker --version
docker compose version
```

### Step 2.2: Test Local Docker Build 🐳

```bash
# Build the Docker image
docker build -t staticwaves-pod-studio:beta .
```

**Watch for:**
- ✓ Both build stages complete
- ✓ Final image size (~200-300MB)
- ✓ No errors in build output

**Checkpoint:**
- [ ] Image builds successfully
- [ ] No build errors or warnings

### Step 2.3: Test Container Locally 🧪

```bash
# Run the container
docker run -d -p 8080:80 --name staticwaves-test staticwaves-pod-studio:beta

# Wait 5 seconds for startup
sleep 5

# Test health endpoint
curl http://localhost:8080/health.json

# Expected output:
# {
#   "status": "healthy",
#   "service": "staticwaves-pod-studio",
#   "version": "6.0",
#   "environment": "beta",
#   "timestamp": "2025-12-29"
# }
```

**Test the Application:**
```bash
# Open in browser
open http://localhost:8080

# Or test with curl
curl -I http://localhost:8080
```

**Checkpoint:**
- [ ] Health check returns 200 OK
- [ ] Application loads in browser
- [ ] All features work (batch mode, editor, logs)
- [ ] No console errors

**Cleanup:**
```bash
# Stop and remove test container
docker stop staticwaves-test
docker rm staticwaves-test
```

---

## Part 3: Deploy to Docker Hub

### Step 3.1: Create Docker Hub Account

1. Go to https://hub.docker.com
2. Sign up for free account (if you don't have one)
3. Verify your email
4. Note your username (you'll need it)

### Step 3.2: Login to Docker Hub 🔐

```bash
# Login from terminal
docker login

# Enter your Docker Hub username and password
# You should see: "Login Succeeded"
```

### Step 3.3: Tag and Push Image 📤

**Option A: Using the Automated Script** (Recommended)

```bash
# Set your Docker Hub username
export DOCKERHUB_USERNAME=your-actual-username

# Run the deployment script
./runpod-deploy.sh
```

The script will:
1. ✓ Build the Docker image
2. ✓ Test it locally
3. ✓ Tag for Docker Hub
4. ✓ Push to registry

**Option B: Manual Deployment**

```bash
# Set your username
DOCKERHUB_USERNAME=your-actual-username

# Build image
docker build -t staticwaves-pod-studio:beta .

# Tag for Docker Hub
docker tag staticwaves-pod-studio:beta $DOCKERHUB_USERNAME/staticwaves-pod-studio:beta

# Push to Docker Hub
docker push $DOCKERHUB_USERNAME/staticwaves-pod-studio:beta
```

**Watch for Progress:**
```
Pushing to dockerhub...
beta: digest: sha256:abc123... size: 1234
```

**Checkpoint:**
- [ ] Image pushed successfully
- [ ] Image visible at https://hub.docker.com/r/YOUR-USERNAME/staticwaves-pod-studio

---

## Part 4: RunPod Setup

### Step 4.1: Create RunPod Account

1. Go to https://www.runpod.io
2. Click "Sign Up"
3. Create account (can use Google/GitHub)
4. Verify email
5. Add payment method and credits ($10 minimum recommended)

### Step 4.2: Create Template 📋

1. **Navigate to Templates:**
   - Dashboard → Left sidebar → "Templates"
   - Click "New Template" button

2. **Configure Template:**

   **Container Configuration:**
   ```
   Template Name: StaticWaves POD Studio Beta
   Container Image: your-dockerhub-username/staticwaves-pod-studio:beta
   Docker Command: [leave empty]
   Container Disk: 10 GB
   ```

   **Port Configuration:**
   ```
   Expose HTTP Ports: 80
   Expose TCP Ports: [leave empty]
   ```

   **Environment Variables:** (Click "Add Environment Variable" for each)
   ```
   NODE_ENV=production
   BETA_MODE=true
   BETA_USERS_ALLOWED=true
   FEATURE_FLAG_BATCH_MODE=true
   FEATURE_FLAG_EDITOR=true
   LOG_LEVEL=info
   ```

3. **Save Template**
   - Click "Save Template" at bottom
   - You should see it in your templates list

**Checkpoint:**
- [ ] Template created successfully
- [ ] All environment variables added
- [ ] Port 80 exposed

### Step 4.3: Deploy Pod 🚀

1. **Start Deployment:**
   - Dashboard → "Pods" → "Deploy"
   - Or click "Deploy" on your template

2. **Choose GPU/CPU:**

   **Recommended Configuration:**
   ```
   GPU: RTX 3070 or RTX 3080
   CPU: 8+ vCPUs
   RAM: 16+ GB
   Storage: 50+ GB
   ```

   **Budget Option:**
   ```
   GPU: RTX 3060 Ti
   CPU: 4+ vCPUs
   RAM: 8+ GB
   Storage: 20+ GB
   ```

3. **Select Template:**
   - Choose "StaticWaves POD Studio Beta"

4. **Deploy:**
   - Click "Deploy On-Demand" or "Deploy Spot" (cheaper)
   - Wait for pod to start (30-60 seconds)

**Checkpoint:**
- [ ] Pod status shows "Running"
- [ ] No error messages

---

## Part 5: Access and Test Your Deployment

### Step 5.1: Get Your Pod URL 🌐

Once deployed, you'll see:

```
Pod ID: abc123xyz
Status: Running
Port 80: https://abc123xyz-80.proxy.runpod.net
```

**Copy your URL** - it will look like:
```
https://[pod-id]-80.proxy.runpod.net
```

### Step 5.2: Test Health Endpoint 🏥

```bash
# Replace with your actual pod URL
curl https://your-pod-id-80.proxy.runpod.net/health.json

# Expected response:
# {
#   "status": "healthy",
#   "service": "staticwaves-pod-studio",
#   "version": "6.0",
#   "environment": "beta",
#   "timestamp": "2025-12-29"
# }
```

**Checkpoint:**
- [ ] Health check returns 200 OK
- [ ] JSON response is valid

### Step 5.3: Access Application 🎨

Open in your browser:
```
https://your-pod-id-80.proxy.runpod.net
```

**You should see:**
- StaticWaves POD Studio interface
- Left sidebar with controls
- Preview panels in center
- Terminal at bottom

**Checkpoint:**
- [ ] Page loads without errors
- [ ] UI displays correctly
- [ ] No 502/503 errors

---

## Part 6: Beta Testing

### Step 6.1: Test Single Drop Processing 🎯

1. **Configure Settings:**
   ```
   Drop Name: TestDrop1
   Design Count: 5
   Blueprint ID: 6
   Provider ID: 1
   ```

2. **Run Simulation:**
   - Click "Run Single Drop"
   - Watch the logs appear in real-time

3. **Verify Output:**
   - [ ] Logs show progress
   - [ ] Progress bar updates
   - [ ] Design preview appears
   - [ ] Mockup preview loads
   - [ ] Queue items appear
   - [ ] Process completes at 100%

### Step 6.2: Test Batch Mode 🚀

1. **Configure Batch:**
   ```
   Batch List: Drop1, Drop2, Drop3
   Design Count: 3
   ```

2. **Run Batch:**
   - Click "Run Batch Mode"
   - Watch multiple drops process

3. **Verify:**
   - [ ] All drops process sequentially
   - [ ] Progress shows cumulative completion
   - [ ] Logs distinguish between drops
   - [ ] Queue accumulates all items

### Step 6.3: Test Design Editor ✏️

1. **Generate a Design:**
   - Run a single drop simulation
   - Wait for design preview to appear

2. **Use Editor Controls:**
   - Click "Zoom In" (+) several times
   - Click "Zoom Out" (-)
   - Use arrow buttons to pan (↑↓←→)
   - Click "Save Edit"

3. **Verify:**
   - [ ] Zoom changes design scale
   - [ ] Pan moves design position
   - [ ] Save confirms in logs

### Step 6.4: Stress Test 💪

1. **High Volume Test:**
   ```
   Design Count: 50
   Batch List: [leave empty]
   ```
   - Run and monitor performance

2. **Multi-Batch Test:**
   ```
   Batch List: Drop1,Drop2,Drop3,Drop4,Drop5,Drop6,Drop7,Drop8,Drop9,Drop10
   Design Count: 10
   ```
   - Run and watch queue management

3. **Verify:**
   - [ ] No crashes or freezes
   - [ ] Logs continue updating
   - [ ] Memory usage stays reasonable
   - [ ] Process completes successfully

---

## Part 7: Monitoring and Logs

### Step 7.1: View Pod Logs 📊

**In RunPod Dashboard:**
1. Go to "My Pods"
2. Click on your pod
3. Click "Logs" tab

**You should see:**
```
=========================================
StaticWaves POD Studio - RunPod Startup
=========================================
Pod ID: abc123xyz
...
✓ Nginx configuration is valid
✓ Nginx started with PID: 1
=========================================
Server is ready!
Health check: http://localhost/health.json
Application: http://localhost/
=========================================
```

### Step 7.2: Monitor Resource Usage 📈

**In RunPod Dashboard:**
1. Click on your pod
2. View "Metrics" tab

**Monitor:**
- CPU usage (should be low when idle)
- Memory usage (should be ~200-500MB)
- Network traffic
- Disk usage

**Healthy Metrics:**
```
CPU: 0-10% idle, 20-50% under load
Memory: 200-500 MB
Disk: < 5 GB
```

### Step 7.3: Check Container Health 🏥

```bash
# From your local terminal
# Check health status every 30 seconds
watch -n 30 curl -s https://your-pod-id-80.proxy.runpod.net/health.json
```

---

## Part 8: Sharing with Beta Testers

### Step 8.1: Prepare Beta Tester Instructions 📧

Send your beta testers:

**Email Template:**
```
Subject: StaticWaves POD Studio Beta Access

Hi [Name],

You've been invited to beta test StaticWaves POD Studio!

Access URL: https://your-pod-id-80.proxy.runpod.net

What to test:
1. Single drop processing
2. Batch mode with multiple drops
3. Design editor controls
4. Overall performance and UX

Please report any issues to:
https://github.com/ssiens-oss/ssiens-oss-static_pod/issues

Testing guide:
https://github.com/ssiens-oss/ssiens-oss-static_pod/blob/claude/runpod-deployment-beta-bYWSF/BETA_TESTING.md

Thanks for your help!
```

### Step 8.2: Monitor Beta Feedback 📝

**Track these channels:**
1. GitHub Issues: Check daily for bug reports
2. Direct feedback: Note all user comments
3. Analytics: Monitor error logs in RunPod

**Create a feedback spreadsheet:**
```
| Tester | Feature | Issue | Severity | Status |
|--------|---------|-------|----------|--------|
| User1  | Batch   | Slow  | Medium   | Open   |
```

---

## Part 9: Troubleshooting

### Issue: Container Won't Start

**Symptoms:**
- Pod shows "Starting" for > 2 minutes
- Pod status shows "Exited" or "Error"

**Solutions:**
```bash
# 1. Check logs in RunPod dashboard
# 2. Verify image name is correct
# 3. Try redeploying pod
# 4. Test image locally:
docker pull your-username/staticwaves-pod-studio:beta
docker run -p 8080:80 your-username/staticwaves-pod-studio:beta
```

### Issue: 502 Bad Gateway

**Symptoms:**
- Browser shows "502 Bad Gateway"
- Health check fails

**Solutions:**
```bash
# 1. Wait 60 seconds (container may still be starting)
# 2. Check pod logs for nginx errors
# 3. Verify port 80 is exposed in template
# 4. Restart the pod
```

### Issue: Application Loads but Features Don't Work

**Symptoms:**
- Page loads but simulation won't run
- Console shows JavaScript errors

**Solutions:**
1. Check browser console (F12)
2. Verify all assets loaded (Network tab)
3. Clear browser cache
4. Try different browser
5. Check if CDN URLs are accessible (aistudiocdn.com)

### Issue: Slow Performance

**Symptoms:**
- Simulation takes very long
- UI is laggy

**Solutions:**
1. Check pod resource usage (upgrade GPU if needed)
2. Reduce design count for testing
3. Check network latency to RunPod
4. Verify no other heavy processes running

---

## Part 10: Next Steps

### After Successful Beta Testing:

1. **Gather Feedback:**
   - Compile all bug reports
   - Prioritize fixes
   - Note feature requests

2. **Iterate:**
   - Fix critical bugs
   - Rebuild Docker image
   - Redeploy to RunPod

3. **Scale Up:**
   - Deploy multiple pods for load balancing
   - Set up CDN for static assets
   - Add backend API if needed

4. **Production Release:**
   - Update version from beta
   - Add authentication if needed
   - Set up monitoring/alerting
   - Create production deployment guide

---

## Summary Checklist

Use this as your master checklist:

### Pre-Deployment
- [ ] Local development server works
- [ ] Production build succeeds
- [ ] Docker installed and working
- [ ] Local Docker container tested

### Docker Hub
- [ ] Docker Hub account created
- [ ] Logged in from terminal
- [ ] Image built successfully
- [ ] Image pushed to registry

### RunPod
- [ ] RunPod account created
- [ ] Credits added
- [ ] Template created with correct settings
- [ ] Pod deployed successfully

### Testing
- [ ] Health endpoint accessible
- [ ] Application loads in browser
- [ ] Single drop processing works
- [ ] Batch mode works
- [ ] Design editor functions
- [ ] No critical errors

### Beta Testing
- [ ] URL shared with testers
- [ ] Feedback channel established
- [ ] Testing guide shared
- [ ] Monitoring in place

### Production Ready
- [ ] All critical bugs fixed
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Ready for wider release

---

## Support

Need help? Check these resources:

- **QUICKSTART.md** - Fast deployment guide
- **DEPLOYMENT.md** - Detailed deployment info
- **BETA_TESTING.md** - Testing guidelines
- **GitHub Issues** - Report problems

**Congratulations! You've successfully deployed StaticWaves POD Studio on RunPod!** 🎉
