# RunPod Production Deployment Guide

Complete guide for deploying the POD Engine on RunPod with full GUI monitoring.

## 🚀 Quick Start (Fresh RunPod Instance)

### Option 1: One-Line Setup

```bash
git clone -b claude/implement-pod-engine-IAaz2 https://github.com/ssiens-oss/ssiens-oss-static_pod.git /workspace/app && \
cd /workspace/app && \
chmod +x runpod-start.sh && \
./runpod-start.sh
```

**Note:** If you get authentication errors with HTTPS, use one of these alternatives:

```bash
# Option A: Use SSH (if you have SSH key set up)
git clone -b claude/implement-pod-engine-IAaz2 git@github.com:ssiens-oss/ssiens-oss-static_pod.git /workspace/app

# Option B: Download and extract ZIP (no authentication needed, RECOMMENDED)
wget https://github.com/ssiens-oss/ssiens-oss-static_pod/archive/refs/heads/claude/implement-pod-engine-IAaz2.zip
unzip implement-pod-engine-IAaz2.zip
mv ssiens-oss-static_pod-claude-implement-pod-engine-IAaz2 /workspace/app
```

### Option 2: Docker Compose (Recommended)

```bash
# Clone the repository (with correct branch)
git clone -b claude/implement-pod-engine-IAaz2 https://github.com/ssiens-oss/ssiens-oss-static_pod.git /workspace/app
cd /workspace/app

# Set your API key
export ANTHROPIC_API_KEY="your-actual-api-key-here"

# Start the stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 📋 Prerequisites

### RunPod Requirements

- **GPU**: Any NVIDIA GPU (RTX 3090, A100, etc.)
- **Template**: PyTorch 2.x with CUDA 11.8+
- **Storage**: Minimum 40GB (recommended 100GB)
- **Ports**: 3000, 8188, 5173 (exposed)

### Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` - Your Claude API key

**Optional (for publishing):**
- `PRINTIFY_API_KEY` - Printify integration
- `SHOPIFY_ACCESS_TOKEN` - Shopify integration
- `TIKTOK_ACCESS_TOKEN` - TikTok Shop integration
- etc.

---

## 🔧 Manual Setup Steps

### 1. Create RunPod Instance

1. Go to [RunPod](https://runpod.io)
2. Create a new GPU instance
3. Choose template: **PyTorch 2.1.0 + CUDA 11.8**
4. Select GPU (RTX 3090 or better recommended)
5. Set ports: `3000`, `8188`, `5173`
6. Start the instance

### 2. Connect to Instance

```bash
# SSH into your RunPod instance
ssh root@YOUR_POD_IP -p YOUR_SSH_PORT
```

### 3. Clone and Setup

```bash
# Navigate to workspace
cd /workspace

# Clone repository (with correct branch)
git clone -b claude/implement-pod-engine-IAaz2 https://github.com/ssiens-oss/ssiens-oss-static_pod.git app
cd app

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Edit `.env` and set:**
```bash
ANTHROPIC_API_KEY=your-actual-api-key
```

### 4. Start Services

```bash
# Make startup script executable
chmod +x runpod-start.sh

# Start all services
./runpod-start.sh
```

This will start:
- ✅ ComfyUI (port 8188)
- ✅ POD Engine API (port 3000)
- ✅ Monitoring GUI (port 5173)

---

## 🖥️ Accessing Services

### Monitoring Dashboard (Main Interface)

```
http://YOUR_POD_IP:5173
```

Features:
- Real-time job monitoring
- Submit new jobs
- View metrics and statistics
- Track job progress
- View success/failure rates

### POD Engine API

```
http://YOUR_POD_IP:3000
```

Key endpoints:
- `GET /health` - Health check
- `GET /api/metrics` - Engine metrics
- `POST /api/generate` - Submit job
- `GET /api/jobs` - List jobs

### ComfyUI

```
http://YOUR_POD_IP:8188
```

Direct access to ComfyUI for image generation.

---

## 📊 Using the Monitoring GUI

### 1. Open Dashboard

Navigate to `http://YOUR_POD_IP:5173`

### 2. View Metrics

The dashboard shows:
- Total jobs processed
- Success rate
- Running/pending jobs
- Average job time
- Uptime

### 3. Submit a Job

1. Enter your design prompt in the text field
2. Select priority (Low, Normal, High, Urgent)
3. Click "Submit Job"
4. Watch real-time progress in the jobs list

### 4. Monitor Jobs

Each job shows:
- Status (Pending → Running → Completed/Failed)
- Progress bar (for running jobs)
- Execution time
- Error details (if failed)

---

## 🔌 API Usage

### Health Check

```bash
curl http://YOUR_POD_IP:3000/health
```

Response:
```json
{
  "status": "healthy",
  "uptime": 123456,
  "timestamp": "2024-01-03T12:00:00.000Z"
}
```

### Get Metrics

```bash
curl http://YOUR_POD_IP:3000/api/metrics
```

Response:
```json
{
  "totalJobs": 10,
  "completedJobs": 8,
  "failedJobs": 2,
  "successRate": 80,
  "averageJobTime": 5234,
  "uptime": 123456
}
```

### Submit Job

```bash
curl -X POST http://YOUR_POD_IP:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "productTypes": ["tshirt", "hoodie"],
    "autoPublish": false,
    "priority": "high"
  }'
```

Response:
```json
{
  "jobId": "job_1234567890_abc123",
  "message": "Job submitted successfully",
  "status": "pending"
}
```

### Get Job Status

```bash
curl http://YOUR_POD_IP:3000/api/jobs/job_1234567890_abc123
```

### Submit Batch Jobs

```bash
curl -X POST http://YOUR_POD_IP:3000/api/generate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "prompt": "Design 1",
        "priority": "high"
      },
      {
        "prompt": "Design 2",
        "priority": "normal"
      }
    ]
  }'
```

---

## 🔄 Full Production Run Example

### 1. Start Services

```bash
./runpod-start.sh
```

Wait for all services to be ready (60-90 seconds).

### 2. Open Monitoring GUI

Navigate to `http://YOUR_POD_IP:5173`

### 3. Submit Test Jobs

**Via GUI:**
1. Enter prompt: "Urban street art with vibrant colors"
2. Select priority: High
3. Click Submit

**Via API:**
```bash
# Submit single job
curl -X POST http://YOUR_POD_IP:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Minimalist geometric pattern design",
    "productTypes": ["tshirt"],
    "priority": "urgent"
  }'

# Submit batch
curl -X POST http://YOUR_POD_IP:3000/api/generate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {"prompt": "Nature landscape", "priority": "normal"},
      {"prompt": "Abstract art", "priority": "high"},
      {"prompt": "Typography design", "priority": "low"}
    ]
  }'
```

### 4. Monitor Progress

Watch the GUI dashboard update in real-time:
- Jobs move from Pending → Running → Completed
- Progress bars show 10% → 30% → 90% → 100%
- Metrics update automatically

### 5. View Results

Check job results:

```bash
# Get all jobs
curl http://YOUR_POD_IP:3000/api/jobs

# Get specific job
curl http://YOUR_POD_IP:3000/api/jobs/JOB_ID
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -f Dockerfile.runpod-prod -t pod-engine:latest .
```

### Run Container

```bash
docker run -d \
  --name pod-engine \
  --gpus all \
  -p 3000:3000 \
  -p 8188:8188 \
  -p 5173:5173 \
  -e ANTHROPIC_API_KEY="your-key" \
  -v pod-data:/workspace/data \
  pod-engine:latest
```

### Using Docker Compose

```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down

# Rebuild
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔧 Configuration

### Environment Variables

Edit `/workspace/app/.env`:

```bash
# Required
ANTHROPIC_API_KEY=your-claude-api-key

# POD Engine
PORT=3000
MAX_CONCURRENT_JOBS=2
MAX_JOB_RETRIES=3
JOB_TIMEOUT_MS=600000

# ComfyUI
COMFYUI_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/workspace/data/comfyui/output

# Storage
STORAGE_TYPE=local
STORAGE_PATH=/workspace/data/designs

# Optional: Platform APIs
PRINTIFY_API_KEY=
SHOPIFY_ACCESS_TOKEN=
```

### Adjust Concurrency

To process more jobs simultaneously:

```bash
# In .env
MAX_CONCURRENT_JOBS=4
```

Restart the engine:
```bash
pkill -f pod-engine-api
npm run engine &
```

---

## 📁 File Structure

```
/workspace/
├── app/                          # Application code
│   ├── pod-engine-api.ts        # API server
│   ├── services/
│   │   └── podEngine.ts         # Core engine
│   ├── PodEngineMonitor.tsx     # Monitoring GUI
│   ├── runpod-start.sh          # Startup script
│   └── .env                     # Configuration
├── ComfyUI/                     # ComfyUI installation
├── data/                        # Persistent data
│   ├── designs/                 # Generated designs
│   ├── comfyui/output/         # ComfyUI outputs
│   └── pod-engine-state/       # Engine state
└── logs/                        # Service logs
    ├── comfyui.log
    ├── pod-engine.log
    └── monitor.log
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
tail -f /workspace/logs/*.log

# Check processes
ps aux | grep -E "python|node"

# Restart all services
pkill -f "python main.py"
pkill -f "pod-engine-api"
pkill -f "vite"
./runpod-start.sh
```

### ComfyUI Not Ready

```bash
# Check ComfyUI logs
tail -f /workspace/logs/comfyui.log

# Test ComfyUI endpoint
curl http://localhost:8188

# Restart ComfyUI
pkill -f "python main.py"
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 &
```

### API Not Responding

```bash
# Check API logs
tail -f /workspace/logs/pod-engine.log

# Test API
curl http://localhost:3000/health

# Restart API
pkill -f pod-engine-api
cd /workspace/app
npm run engine &
```

### GUI Not Loading

```bash
# Check monitor logs
tail -f /workspace/logs/monitor.log

# Restart GUI
pkill -f vite
cd /workspace/app
npm run monitor &
```

### Jobs Failing

Check:
1. ComfyUI is running: `curl http://localhost:8188`
2. Claude API key is set: `echo $ANTHROPIC_API_KEY`
3. Job details: `curl http://localhost:3000/api/jobs/JOB_ID`

---

## 🎯 Performance Tips

### Optimize for Speed

```bash
# Increase concurrent jobs (if you have powerful GPU)
MAX_CONCURRENT_JOBS=4

# Reduce retries for faster failures
MAX_JOB_RETRIES=1

# Shorter timeout
JOB_TIMEOUT_MS=300000  # 5 minutes
```

### Optimize for Reliability

```bash
# Conservative concurrency
MAX_CONCURRENT_JOBS=1

# More retries
MAX_JOB_RETRIES=5

# Longer timeout
JOB_TIMEOUT_MS=900000  # 15 minutes
```

---

## 🔒 Security

### Production Checklist

- [ ] Set strong API keys
- [ ] Don't expose sensitive ports publicly
- [ ] Use RunPod's network security features
- [ ] Enable HTTPS if using custom domain
- [ ] Regularly update dependencies
- [ ] Monitor logs for suspicious activity

---

## 📞 Support

### Logs Location

```bash
/workspace/logs/comfyui.log
/workspace/logs/pod-engine.log
/workspace/logs/monitor.log
```

### Common Issues

1. **Out of Memory**: Reduce `MAX_CONCURRENT_JOBS`
2. **Slow Performance**: Check GPU utilization
3. **Jobs Stuck**: Check ComfyUI logs
4. **API Errors**: Verify environment variables

---

## 🎉 You're Ready!

Your POD Engine is now running on RunPod with:

✅ Production-ready API
✅ Real-time monitoring GUI
✅ Automated job queue
✅ Full error handling
✅ State persistence

Access your dashboard at:
```
http://YOUR_POD_IP:5173
```

Happy automating! 🚀
