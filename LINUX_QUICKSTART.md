# Linux Quick Start Guide - POD Gateway

This guide will help you set up and run the POD Gateway serverless engine on a fresh Linux installation.

## Prerequisites

- Linux system (Ubuntu 20.04+, Debian 11+, or similar)
- Python 3.10+ with pip and venv
- Internet connection for downloading dependencies
- Printify account with API access

## Installation Methods

### Method 1: Automated Installation (Recommended)

The automated installer sets up POD Gateway as a systemd service for production use.

```bash
cd gateway
sudo ./install_standalone.sh
```

**What it installs:**
- System dependencies (python3, python3-pip, python3-venv, curl)
- Python virtual environment at `/opt/pod-gateway/.venv`
- Application files at `/opt/pod-gateway/`
- Systemd service at `/etc/systemd/system/pod-gateway.service`
- Auto-start on system boot

**Configure your API keys:**
```bash
sudo nano /opt/pod-gateway/.env
```

Update:
```bash
PRINTIFY_API_KEY=your_actual_api_key
PRINTIFY_SHOP_ID=your_actual_shop_id
```

**Start the service:**
```bash
sudo systemctl start pod-gateway
sudo systemctl status pod-gateway
```

**Access the UI:**
```
http://localhost:5000
```

### Method 2: Development Mode

For development or testing without systemd:

```bash
cd gateway

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy example config
cp .env.example .env
nano .env  # Configure your API keys

# Start the server
./start.sh
```

### Method 3: Docker

For containerized deployment:

```bash
cd gateway

# Configure environment
cp .env.example .env
nano .env  # Configure your API keys

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Post-Installation Configuration

### Required API Keys

1. **Printify API Key**
   - Go to: https://printify.com
   - Navigate to: Settings → API
   - Generate an API token
   - Copy your Shop ID

2. **Update Configuration**
   ```bash
   # For systemd installation
   sudo nano /opt/pod-gateway/.env

   # For development mode
   nano gateway/.env
   ```

3. **Configure Settings**
   ```bash
   # Required
   PRINTIFY_API_KEY=your_api_key_here
   PRINTIFY_SHOP_ID=your_shop_id_here

   # Optional
   POD_IMAGE_DIR=/path/to/comfyui/output
   FLASK_PORT=5000
   PRINTIFY_BLUEPRINT_ID=3  # 3=T-shirt, 77=Hoodie
   PRINTIFY_PROVIDER_ID=99  # 99=Printify Choice, 39=SwiftPOD
   ```

## Service Management

### Using Control Script (All Methods)

```bash
cd gateway
./pod-gateway-ctl.sh start      # Start
./pod-gateway-ctl.sh stop       # Stop
./pod-gateway-ctl.sh restart    # Restart
./pod-gateway-ctl.sh status     # Check status
./pod-gateway-ctl.sh logs       # View logs
./pod-gateway-ctl.sh health     # Health check
```

### Using Systemd (Method 1)

```bash
sudo systemctl start pod-gateway       # Start
sudo systemctl stop pod-gateway        # Stop
sudo systemctl restart pod-gateway     # Restart
sudo systemctl status pod-gateway      # Status
sudo journalctl -u pod-gateway -f      # Live logs
```

### Using Docker (Method 3)

```bash
docker-compose up -d                   # Start
docker-compose down                    # Stop
docker-compose restart                 # Restart
docker-compose logs -f                 # Live logs
```

## Verify Installation

### 1. Check Service Status

```bash
# Systemd
sudo systemctl status pod-gateway

# Docker
docker-compose ps

# Development
ps aux | grep "python.*main.py"
```

### 2. Health Check

```bash
curl http://localhost:5000/health
```

Should return: `{"status": "healthy"}`

### 3. Access Web UI

Open browser:
```
http://localhost:5000
```

Or from remote machine:
```
http://YOUR_SERVER_IP:5000
```

### 4. Test API

```bash
# List images
curl http://localhost:5000/api/images

# Approve an image
curl -X POST http://localhost:5000/api/approve/IMAGE_ID

# Publish to Printify
curl -X POST http://localhost:5000/api/publish/IMAGE_ID
```

## Integration with ComfyUI

The POD Gateway works as a human-in-the-loop system between ComfyUI and Printify:

```
ComfyUI → POD Gateway → Printify → Shopify/TikTok/Etsy
         (YOU APPROVE)
```

### Configure Image Directory

**Option A: Update POD_IMAGE_DIR**
```bash
# In .env file
POD_IMAGE_DIR=/path/to/comfyui/output
```

**Option B: Create Symbolic Link**
```bash
ln -s /path/to/comfyui/output /opt/pod-gateway/data/images
```

**Option C: Configure ComfyUI**
```bash
# In main project .env
COMFYUI_OUTPUT_DIR=/opt/pod-gateway/data/images
```

## Workflow

1. **Generate Designs**
   - Run ComfyUI to create AI-generated images
   - Images saved to configured output directory

2. **Review in Gateway**
   - Open http://localhost:5000
   - Browse generated images in web gallery
   - Approve designs you want to publish

3. **Publish to Printify**
   - Click "Publish" on approved designs
   - Gateway creates product on Printify
   - Product ready for sale

4. **Monitor Status**
   - Track approval status in web UI
   - View logs for publishing activity
   - Check Printify for published products

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
# Systemd
sudo journalctl -u pod-gateway -n 50

# Docker
docker-compose logs

# Development
cat /tmp/pod-gateway.log
```

**Common issues:**
1. Missing API keys in `.env`
2. Port 5000 already in use
3. Python dependencies not installed
4. Incorrect directory permissions

### Cannot Connect to Printify

1. Verify API key is correct
2. Check Shop ID is correct
3. Test API connection:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.printify.com/v1/shops.json
   ```

### Port Already in Use

Change port in `.env`:
```bash
FLASK_PORT=8080
```

Then restart the service.

### Permission Errors

Fix file permissions:
```bash
# Systemd installation
sudo chown -R root:root /opt/pod-gateway
sudo chmod -R 755 /opt/pod-gateway
sudo chmod 644 /opt/pod-gateway/.env

# Development mode
chmod +x gateway/start.sh
chmod +x gateway/pod-gateway-ctl.sh
```

### Images Not Appearing

1. Check `POD_IMAGE_DIR` path is correct
2. Verify images exist in directory:
   ```bash
   ls -la /opt/pod-gateway/data/images/
   ```
3. Check file permissions
4. Restart the service

## Network Limitations

If installing on a system without internet access:

1. **Pre-download packages on another machine:**
   ```bash
   pip download -r requirements.txt -d ./packages/
   ```

2. **Transfer to target system and install:**
   ```bash
   pip install --no-index --find-links=./packages/ -r requirements.txt
   ```

3. **Or use the pre-configured setup:**
   - All files have been prepared at `/opt/pod-gateway/`
   - Configuration created at `/opt/pod-gateway/.env`
   - Systemd service installed at `/etc/systemd/system/pod-gateway.service`
   - Run completion script when internet is available:
     ```bash
     sudo /opt/pod-gateway/complete-setup.sh
     ```

## Security Considerations

### Production Deployment

1. **Use reverse proxy with SSL:**
   ```nginx
   server {
       listen 443 ssl;
       server_name pod.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Restrict Flask to localhost:**
   ```bash
   FLASK_HOST=127.0.0.1
   ```

3. **Add authentication:**
   - Implement Basic Auth in nginx
   - Or add authentication middleware to Flask

4. **Firewall rules:**
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

5. **Regular backups:**
   ```bash
   sudo tar -czf pod-gateway-backup.tar.gz /opt/pod-gateway/data/
   ```

## Directory Structure

```
/opt/pod-gateway/           # Production installation
├── app/                    # Flask application
│   ├── main.py            # Entry point
│   ├── state_manager.py   # State tracking
│   └── printify_client.py # API client
├── templates/             # Web UI
│   └── index.html
├── data/                  # Runtime data
│   ├── images/           # Generated images
│   ├── state/            # State files
│   └── archive/          # Archived designs
├── .venv/                # Python environment
├── .env                  # Configuration
├── requirements.txt      # Dependencies
├── start.sh              # Startup script
├── pod-gateway-ctl.sh    # Control script
└── complete-setup.sh     # Installation finisher

/var/log/pod-gateway/      # Logs (systemd only)
├── output.log            # Standard output
└── error.log             # Error output

/etc/systemd/system/       # Service (systemd only)
└── pod-gateway.service   # Service definition
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI gallery |
| `/api/images` | GET | List all images with status |
| `/api/approve/<id>` | POST | Approve an image |
| `/api/reject/<id>` | POST | Reject an image |
| `/api/publish/<id>` | POST | Publish to Printify |
| `/api/reset/<id>` | POST | Reset status |
| `/health` | GET | Health check |

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POD_IMAGE_DIR` | No | `./data/images` | Image directory |
| `POD_STATE_FILE` | No | `./data/state.json` | State file |
| `POD_ARCHIVE_DIR` | No | `./data/archive` | Archive directory |
| `FLASK_HOST` | No | `0.0.0.0` | Server host |
| `FLASK_PORT` | No | `5000` | Server port |
| `FLASK_DEBUG` | No | `false` | Debug mode |
| `PRINTIFY_API_KEY` | **YES** | - | API key |
| `PRINTIFY_SHOP_ID` | **YES** | - | Shop ID |
| `PRINTIFY_BLUEPRINT_ID` | No | `3` | Product type |
| `PRINTIFY_PROVIDER_ID` | No | `99` | Print provider |

## Additional Resources

- **Main Documentation:** `/home/user/ssiens-oss-static_pod/README.md`
- **Setup Guide:** `/home/user/ssiens-oss-static_pod/SETUP_GUIDE.md`
- **Gateway README:** `/home/user/ssiens-oss-static_pod/gateway/README.md`
- **Standalone Deployment:** `/home/user/ssiens-oss-static_pod/gateway/STANDALONE_DEPLOYMENT.md`
- **Printify Blueprints:** `/home/user/ssiens-oss-static_pod/docs/PRINTIFY_BLUEPRINTS.md`

## Next Steps

1. ✅ Install using your preferred method
2. ✅ Configure API keys in `.env`
3. ✅ Start the service
4. ✅ Verify at http://localhost:5000
5. ✅ Connect ComfyUI output directory
6. ✅ Start approving and publishing!

---

**Quick Commands Cheat Sheet:**

```bash
# Install
sudo gateway/install_standalone.sh

# Configure
sudo nano /opt/pod-gateway/.env

# Start
sudo systemctl start pod-gateway

# Check status
./gateway/pod-gateway-ctl.sh status

# View logs
sudo journalctl -u pod-gateway -f

# Access UI
xdg-open http://localhost:5000
```
