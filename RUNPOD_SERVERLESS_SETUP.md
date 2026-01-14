# RunPod Serverless ComfyUI Setup

## 🚀 Why Serverless?

### Cost Comparison

**Dedicated Pod (RTX 3090):**
- Running 24/7: **$244/month** ($0.34/hr × 720 hrs)
- Running 8hr/day: **$81/month** ($0.34/hr × 240 hrs)
- Idle time: **You still pay**

**Serverless:**
- Per image: **~$0.002** (0.2 cents)
- 1,000 images: **~$2.00**
- Idle time: **$0** (pay only when generating)
- **10-50x cheaper** for intermittent use

---

## 📋 Serverless vs Dedicated Pod

| Feature | Serverless | Dedicated Pod |
|---------|-----------|---------------|
| **Cost** | $0.002/image | $0.34/hour |
| **Startup time** | 30-90 seconds | Instant |
| **Idle cost** | $0 | Full hourly rate |
| **Best for** | Intermittent use | Continuous generation |
| **Scaling** | Auto-scales | Fixed capacity |

---

## 🎯 When to Use What

**Use Serverless If:**
- ✅ Generating < 100 images/day
- ✅ Sporadic usage (few times per week)
- ✅ Want zero idle costs
- ✅ Don't mind 30-90 second cold starts

**Use Dedicated Pod If:**
- ✅ Generating > 500 images/day
- ✅ Continuous workflow sessions
- ✅ Need instant generation (no cold start)
- ✅ Experimenting/iterating rapidly

---

## 🚀 Deploy Serverless ComfyUI

### Step 1: Go to RunPod Serverless

**Visit:** https://runpod.io/console/serverless

### Step 2: Create New Endpoint

**Click:** "New Endpoint" or "Deploy"

**Template Selection:**
```
Search: "ComfyUI"
Select: "ComfyUI Serverless Worker"
```

**Alternative Templates:**
- `runpod/worker-comfy` (official)
- `timothybrooks/comfyui-serverless` (community)
- `luc-labs/comfyui-serverless` (with custom nodes)

### Step 3: Configure Endpoint

**Worker Configuration:**
```
GPU Types: RTX 3090, RTX 4090, A4000 (check all for faster cold starts)
Max Workers: 1-3 (how many can run simultaneously)
Idle Timeout: 30 seconds (worker shuts down after this)
Execution Timeout: 300 seconds (max generation time)
```

**Environment Variables:**
```
COMFYUI_PORT=8188
COMFYUI_ENV=production
```

**Networking:**
```
✅ Enable Public Endpoint
```

### Step 4: Deploy & Get Endpoint URL

After deployment, you'll get:

```
Endpoint URL: https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run
API Key: YOUR_API_KEY
```

**Save both of these!**

---

## 🔧 Integration with Local Pipeline

### Option A: Direct API Calls

**Create serverless client script:**
```bash
cd ~/ssiens-oss-static_pod/gateway
nano comfyui_serverless.py
```

**Add this code:**
```python
import requests
import time
import os

RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
RUNPOD_ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID")

def generate_image(prompt: str, output_path: str):
    """
    Generate image using RunPod Serverless ComfyUI
    """
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/run"

    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "workflow": {
                "3": {
                    "inputs": {"text": prompt},
                    "class_type": "CLIPTextEncode"
                },
                # Add your full workflow here
            }
        }
    }

    # Submit job
    response = requests.post(url, json=payload, headers=headers)
    job_id = response.json()["id"]

    # Poll for completion
    status_url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}"

    while True:
        status = requests.get(status_url, headers=headers).json()

        if status["status"] == "COMPLETED":
            image_url = status["output"]["images"][0]

            # Download image
            img_data = requests.get(image_url).content
            with open(output_path, 'wb') as f:
                f.write(img_data)

            return output_path

        elif status["status"] == "FAILED":
            raise Exception(f"Generation failed: {status.get('error')}")

        time.sleep(2)

# Usage
if __name__ == "__main__":
    generate_image(
        prompt="minimalist mountain landscape",
        output_path="./images/test.png"
    )
```

### Option B: Update .env for Serverless

```bash
cd ~/ssiens-oss-static_pod
nano .env
```

**Add these lines:**
```bash
# RunPod Serverless Configuration
RUNPOD_MODE=serverless  # or "dedicated"
RUNPOD_API_KEY=your_runpod_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here

# For dedicated pod mode:
COMFYUI_API_URL=https://xxxxx-8188.proxy.runpod.net
```

---

## 🎮 Using Serverless ComfyUI

### Method 1: Via RunPod Dashboard

1. Go to https://runpod.io/console/serverless
2. Click your endpoint
3. Click "Test"
4. Enter workflow JSON
5. Submit & wait for result

### Method 2: Via API (Python)

```python
import requests

# Submit job
response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "prompt": "mountain landscape",
            "steps": 30,
            "seed": 12345
        }
    }
)

job_id = response.json()["id"]
print(f"Job submitted: {job_id}")
```

### Method 3: Via cURL

```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "mountain landscape",
      "steps": 30
    }
  }'
```

---

## 💰 Actual Cost Examples

### Scenario 1: Hobbyist (10 images/day)
```
Dedicated Pod: $81/month (8hr/day)
Serverless: $0.60/month (10 × 30 days × $0.002)

Savings: $80.40/month (99% cheaper!)
```

### Scenario 2: Active User (100 images/day)
```
Dedicated Pod: $81/month (8hr/day)
Serverless: $6/month (100 × 30 days × $0.002)

Savings: $75/month (93% cheaper!)
```

### Scenario 3: Heavy User (1,000 images/day)
```
Dedicated Pod: $244/month (24/7)
Serverless: $60/month (1000 × 30 days × $0.002)

Savings: $184/month (75% cheaper!)
```

### Break-Even Point
```
Serverless becomes more expensive than dedicated pod at:
~12,000 images/month (400/day continuous)
```

---

## ⚡ Performance Optimization

### Reduce Cold Start Time

**Use Warm Workers:**
```python
# Keep workers warm with ping
import schedule
import requests

def keep_warm():
    requests.post(
        "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run",
        headers={"Authorization": "Bearer YOUR_API_KEY"},
        json={"input": {"action": "ping"}}
    )

schedule.every(20).seconds.do(keep_warm)
```

**Cost:** ~$0.20/hour for continuous warm worker (still cheaper than dedicated for < 100 images/hr)

### Use Multiple Workers

```
Max Workers: 3
Benefit: Handle 3 concurrent generations
Cost: Only pay for what you use
```

### Batch Processing

```python
# Submit multiple jobs at once
jobs = []
for prompt in prompts:
    response = requests.post(endpoint, json={"input": {"prompt": prompt}})
    jobs.append(response.json()["id"])

# Collect results
results = [get_result(job_id) for job_id in jobs]
```

---

## 🔍 Monitoring & Debugging

### Check Worker Status

```bash
curl "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/health" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### View Logs

```
RunPod Console → Your Endpoint → Logs
See real-time worker execution logs
```

### Check Billing

```
RunPod Console → Billing → Usage
See per-request costs and total spend
```

---

## 🎯 Quick Start: Serverless in 5 Minutes

**1. Deploy Endpoint:**
```
https://runpod.io/console/serverless
→ New Endpoint
→ Select "ComfyUI Serverless Worker"
→ Deploy
```

**2. Get Credentials:**
```
Copy: Endpoint ID
Copy: API Key
```

**3. Test:**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "test"}}'
```

**4. Integrate:**
```bash
# Add to .env
RUNPOD_MODE=serverless
RUNPOD_API_KEY=your_key
RUNPOD_ENDPOINT_ID=your_id
```

**5. Generate:**
```python
python comfyui_serverless.py
```

---

## 🆚 Final Recommendation

**For Most Users: Start with Serverless**
- $0 idle cost
- Pay only for what you use
- Scale automatically
- Switch to dedicated pod later if needed

**When to Switch to Dedicated:**
- Generating > 400 images/day
- Need instant generation (no cold start)
- Long active work sessions (4+ hours)

---

## 📚 Related Docs

- **[RUNPOD_COMFYUI_SETUP.md](./RUNPOD_COMFYUI_SETUP.md)** - Dedicated pod setup
- **[POD_GATEWAY_INTEGRATION.md](./POD_GATEWAY_INTEGRATION.md)** - Gateway architecture
- **[PIPELINE_ARCHITECTURE.md](./PIPELINE_ARCHITECTURE.md)** - Full pipeline overview

---

**Need help choosing?** Drop me a message with your expected usage and I'll recommend the best option!
