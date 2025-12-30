# POD Studio Complete - Deployment Guide

## 🚀 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Browser)                    │
│              pod-studio-complete.html                   │
│         React UI with Agent Status Monitoring           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (Python Flask)                 │
│                  autonomous_pod.py                      │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │   LangChain  │   CrewAI     │  Flask Webhooks  │    │
│  │   Chains     │   Agents     │                  │    │
│  └──────────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │   GPT-4   │  │  Claude   │  │  Grok-4   │
    │  OpenAI   │  │ Anthropic │  │   X.AI    │
    └───────────┘  └───────────┘  └───────────┘
           │              │              │
           └──────────────┼──────────────┘
                          ▼
                 ┌─────────────────┐
                 │    Llama 3.3    │
                 │      Groq       │
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     ComfyUI     │
                 │     RunPod      │
                 └─────────────────┘
                          │
                          ▼
         ┌────────────────┴────────────────┐
         ▼                                  ▼
    ┌──────────┐                      ┌──────────┐
    │ Printify │                      │  Social  │
    │   POD    │                      │ Instagram│
    └──────────┘                      │  TikTok  │
         │                            └──────────┘
         ▼
    ┌──────────┐
    │  Shopify │
    │   Etsy   │
    └──────────┘
```

## 📋 Prerequisites

### Required API Keys

1. **LLM Providers** (at least 2 recommended):
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - X.AI: https://x.ai/api
   - Groq: https://console.groq.com/

2. **Services**:
   - RunPod: https://runpod.io/console
   - Printify: https://printify.com/app/account/api
   - Instagram account with 2FA disabled (or app password)

3. **Server** (for production):
   - AWS EC2 / DigitalOcean / Any VPS
   - Ubuntu 22.04 LTS
   - 2+ CPU cores
   - 4GB+ RAM

## 🛠️ Local Development Setup

### 1. Clone and Setup

```bash
cd /home/user/ssiens-oss-static_pod

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env.pod

# Edit with your API keys
nano .env.pod
```

### 3. Test Individual Components

```bash
# Test LLM chain
python -c "
from autonomous_pod import Config, MultiLLMPromptGenerator
config = Config.load_from_file()
gen = MultiLLMPromptGenerator(config)
result = gen.generate_design_concept('cyberpunk')
print(result)
"

# Test ComfyUI connection
curl https://your-pod-id-8188.proxy.runpod.net/system_stats

# Test webhook server
python autonomous_pod.py
# In another terminal:
curl http://localhost:5000/health
```

### 4. Run Scheduler

```bash
# Run once for testing
python scheduler.py
# Press Ctrl+C after it completes one workflow

# For production, see deployment options below
```

## 🌐 Production Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f pod-backend
docker-compose logs -f pod-scheduler

# Stop
docker-compose down
```

### Option 2: Supervisor (VPS)

```bash
# Install supervisor
sudo apt update
sudo apt install supervisor

# Create virtual environment
cd /home/ubuntu
git clone https://github.com/your-repo/pod-studio.git
cd pod-studio/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy config
cp .env.example .env.pod
nano .env.pod  # Add your keys

# Setup supervisor
sudo cp supervisor.conf /etc/supervisor/conf.d/pod-studio.conf
# Edit paths in the file if needed
sudo nano /etc/supervisor/conf.d/pod-studio.conf

# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pod-studio:*

# Check status
sudo supervisorctl status
```

### Option 3: Systemd Services

```bash
# Create webhook service
sudo nano /etc/systemd/system/pod-webhook.service
```

```ini
[Unit]
Description=POD Studio Webhook Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pod-studio/backend
Environment="PATH=/home/ubuntu/pod-studio/venv/bin"
ExecStart=/home/ubuntu/pod-studio/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 autonomous_pod:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Create scheduler service
sudo nano /etc/systemd/system/pod-scheduler.service
```

```ini
[Unit]
Description=POD Studio Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pod-studio/backend
Environment="PATH=/home/ubuntu/pod-studio/venv/bin"
ExecStart=/home/ubuntu/pod-studio/venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable pod-webhook pod-scheduler
sudo systemctl start pod-webhook pod-scheduler

# Check status
sudo systemctl status pod-webhook
sudo systemctl status pod-scheduler

# View logs
sudo journalctl -u pod-webhook -f
sudo journalctl -u pod-scheduler -f
```

## 🔒 Setup HTTPS with Nginx

```bash
# Install Nginx and Certbot
sudo apt install nginx certbot python3-certbot-nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/pod-studio
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /webhook/ {
        proxy_pass http://127.0.0.1:5000/webhook/;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pod-studio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## ⚙️ Configure Printify Webhooks

1. Go to Printify Dashboard → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/printify`
3. Select events: `order:created`, `order:shipped`, `order:cancelled`
4. Copy the webhook secret to your `.env.pod` file

## 📱 Social Media Setup

### Instagram

```bash
# Test login
python -c "
from instagrapi import Client
cl = Client()
cl.login('your_username', 'your_password')
print('Login successful!')
"
```

If you get 2FA error:
1. Disable 2FA temporarily OR
2. Generate app-specific password

### TikTok

TikTok requires session cookies. Use browser extension:
1. Install "EditThisCookie" extension
2. Login to TikTok in browser
3. Export cookies as JSON
4. Find `sessionid` value
5. Add to `.env.pod`

## 🎯 RunPod ComfyUI Setup

### 1. Start RunPod Pod

```bash
# Use template: RunPod ComfyUI (or custom)
# GPU: RTX 4090 / A100 (recommended)
# Storage: 50GB+
```

### 2. Enable CORS

SSH into pod:
```bash
cd /workspace/runpod-slim/ComfyUI
source .venv/bin/activate

# Start with CORS enabled
python main.py --listen 0.0.0.0 --enable-cors-header --port 8188
```

### 3. Get Proxy URL

From RunPod dashboard:
- Click "Connect"
- Copy proxy URL (e.g., `https://abc123-8188.proxy.runpod.net`)
- Add to `.env.pod` as `COMFYUI_URL`

## 📊 Monitoring & Logs

### View Logs

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u pod-webhook -f
sudo journalctl -u pod-scheduler -f

# Supervisor
sudo tail -f /var/log/pod-webhook.log
sudo tail -f /var/log/pod-scheduler.log

# Application log
tail -f backend/pod_automation.log
```

### Health Checks

```bash
# Webhook server
curl http://localhost:5000/health

# Full system test
curl -X POST http://localhost:5000/test/workflow
```

## 🔧 Troubleshooting

### LLM Chain Fails

```bash
# Check API keys
python -c "
from autonomous_pod import Config
config = Config.load_from_file()
print('OpenAI:', bool(config.openai_api_key))
print('Anthropic:', bool(config.anthropic_api_key))
print('XAI:', bool(config.xai_api_key))
print('Groq:', bool(config.groq_api_key))
"
```

### ComfyUI Connection Errors

1. Verify pod is running: Check RunPod dashboard
2. Test endpoint: `curl https://your-pod-url/system_stats`
3. Check CORS: Must use `--enable-cors-header` flag

### Printify Upload Fails

1. Verify API key has write permissions
2. Check shop ID is correct
3. Ensure blueprint ID (6 = T-shirt) exists in your account

### Social Media Posting Fails

**Instagram:**
- Use app-specific password if 2FA enabled
- Avoid posting too frequently (max 1/hour)
- Use unique captions (no duplicates)

**TikTok:**
- Session ID expires (refresh every 7-30 days)
- Check video format (MP4, H264)

## 📈 Scaling

### Increase Throughput

```bash
# More Gunicorn workers
gunicorn -w 8 -b 0.0.0.0:5000 autonomous_pod:app

# Parallel batch processing
# Edit scheduler.py:
# Change batch_size to 20-50
```

### Use Redis Queue

```bash
# Install Celery
pip install celery redis

# Start workers
celery -A autonomous_pod worker --loglevel=info
```

### Multiple RunPod Pods

Edit `.env.pod`:
```
COMFYUI_URL=https://pod1-8188.proxy.runpod.net,https://pod2-8188.proxy.runpod.net
```

## 💰 Cost Estimates

### API Costs (per 100 designs)

- **LLMs**: $5-15 (GPT+Claude+Grok+Llama chains)
- **RunPod GPU**: $0.50-2/hr (RTX 4090: ~2min/image = $1.67/hr)
- **Printify**: Free (pay on order)
- **Instagram/TikTok**: Free

**Total**: ~$10-20 per 100 designs

### Optimization Tips

1. Use Groq (Llama) for most agents (free tier)
2. Cache prompt chains (reduce LLM calls)
3. Use RunPod Spot instances (50% cheaper)
4. Batch generate 10+ images per pod session

## 📚 Additional Resources

- **LangChain Docs**: https://python.langchain.com/docs/
- **CrewAI Docs**: https://docs.crewai.com/
- **ComfyUI Workflows**: https://comfyanonymous.github.io/ComfyUI_examples/
- **Printify API**: https://developers.printify.com/
- **RunPod Guide**: https://docs.runpod.io/

## 🆘 Support

Issues? Check:
1. Application logs: `backend/pod_automation.log`
2. System logs: `journalctl` or supervisor logs
3. API status: Check service status pages
4. GitHub Issues: https://github.com/your-repo/issues

---

**Happy Automating! 🚀**
