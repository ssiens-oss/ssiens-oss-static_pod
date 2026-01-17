# Fresh Linux Installation Guide

Complete guide for setting up StaticWaves POD Gateway on a brand new Linux system.

## 🚀 Quick Install (Recommended)

Run this single command to install everything automatically:

```bash
bash <(curl -sSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/fresh-linux-install.sh)
```

Or if you prefer to review the script first:

```bash
curl -sSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/fresh-linux-install.sh -o install.sh
chmod +x install.sh
./install.sh
```

**What it does:**
1. ✅ Installs system dependencies (Python 3, pip, git, curl)
2. ✅ Clones the repository to `~/staticwaves-pod`
3. ✅ Creates Python virtual environment
4. ✅ Installs all Python dependencies
5. ✅ Creates data directories
6. ✅ Configures the POD Gateway
7. ✅ Creates a convenient start script

## 📦 Manual Installation

If you prefer to do it manually or the automated script doesn't work for your system:

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install -y python3 python3-pip python3-virtualenv git curl
```

**Arch/Manjaro:**
```bash
sudo pacman -Sy python python-pip python-virtualenv git curl
```

### Step 2: Clone the Repository

```bash
cd ~
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod
```

### Step 3: Set Up POD Gateway

```bash
cd gateway

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install flask==3.0.2 requests==2.31.0 Pillow==10.2.0 python-dotenv==1.0.1

# Create data directories
mkdir -p data/images data/state data/archive

# Create configuration
cp .env.example .env
```

### Step 4: Configure API Keys

Edit the configuration file:
```bash
nano .env
```

Update these lines with your actual Printify credentials:
```bash
PRINTIFY_API_KEY=your_actual_api_key_here
PRINTIFY_SHOP_ID=your_actual_shop_id_here
```

Also update the paths to match your installation:
```bash
POD_IMAGE_DIR=/home/YOUR_USERNAME/ssiens-oss-static_pod/gateway/data/images
POD_STATE_FILE=/home/YOUR_USERNAME/ssiens-oss-static_pod/gateway/data/state.json
POD_ARCHIVE_DIR=/home/YOUR_USERNAME/ssiens-oss-static_pod/gateway/data/archive
```

### Step 5: Start the Gateway

```bash
# From the gateway directory
.venv/bin/python app/main.py
```

Or create a start script:

```bash
cat > ~/start-gateway.sh << 'EOF'
#!/bin/bash
cd ~/ssiens-oss-static_pod/gateway
export PYTHONPATH=~/ssiens-oss-static_pod/gateway
.venv/bin/python app/main.py
EOF

chmod +x ~/start-gateway.sh
~/start-gateway.sh
```

## 🔑 Getting Printify API Credentials

Before you can publish designs, you need Printify API access:

1. **Sign up for Printify**
   - Go to https://printify.com
   - Create an account (free)

2. **Get API Access**
   - Log into your Printify account
   - Navigate to: **Settings → API**
   - Click "Generate API Token"
   - Copy your API Key

3. **Get Shop ID**
   - Your Shop ID is visible in the API settings
   - Or check your shop URL: `printify.com/app/shops/{SHOP_ID}/`

4. **Update Configuration**
   ```bash
   nano ~/ssiens-oss-static_pod/gateway/.env
   ```

   Replace:
   ```bash
   PRINTIFY_API_KEY=your_actual_api_key_here
   PRINTIFY_SHOP_ID=12345
   ```

## ✅ Verify Installation

### 1. Check Dependencies

```bash
cd ~/ssiens-oss-static_pod/gateway
source .venv/bin/activate
python -c "import flask, requests, PIL; print('✓ All dependencies OK')"
```

### 2. Test App Initialization

```bash
cd ~/ssiens-oss-static_pod/gateway
.venv/bin/python -c "from app.main import app; print('✓ App initialized')"
```

### 3. Start the Service

```bash
cd ~/ssiens-oss-static_pod/gateway
.venv/bin/python app/main.py
```

You should see:
```
🚀 POD Gateway starting...
🌐 Running on http://0.0.0.0:5000
```

### 4. Access Web UI

Open your browser to:
```
http://localhost:5000
```

You should see the POD Gateway web interface!

## 🎯 Quick Start Workflow

### 1. Add Test Images

Copy some design images to the images directory:

```bash
cp /path/to/your/designs/*.png ~/ssiens-oss-static_pod/gateway/data/images/
```

Or create test images:

```bash
# Download a sample image
curl -o ~/ssiens-oss-static_pod/gateway/data/images/test.png \
  https://via.placeholder.com/2400x3000/000000/FFFFFF?text=Test+Design
```

### 2. Start the Gateway

```bash
cd ~/ssiens-oss-static_pod/gateway
.venv/bin/python app/main.py
```

### 3. Review in Browser

1. Open http://localhost:5000
2. You'll see your images in the gallery
3. Click "Approve" on designs you like
4. Click "Publish" to create products on Printify

### 4. Check Printify

1. Log into Printify: https://printify.com
2. Go to "My Products"
3. Your published designs should appear!

## 🔧 Configuration Options

Edit `~/ssiens-oss-static_pod/gateway/.env` to customize:

### Product Settings

```bash
# Product Blueprint (what type of product)
PRINTIFY_BLUEPRINT_ID=3    # 3=T-Shirt, 77=Hoodie, 380=Softstyle

# Print Provider (who prints it)
PRINTIFY_PROVIDER_ID=99    # 99=Printify Choice, 39=SwiftPOD
```

**Common Blueprint IDs:**
- `3` - Gildan 5000 T-Shirt
- `77` - Gildan 18500 Heavy Blend Hoodie
- `380` - Gildan 64000 Softstyle T-Shirt
- `6` - Bella+Canvas 3001 Unisex T-Shirt

**Provider IDs:**
- `39` - SwiftPOD (US-based, reliable)
- `99` - Printify Choice (global fulfillment)

### Server Settings

```bash
FLASK_HOST=0.0.0.0    # Listen on all interfaces
FLASK_PORT=5000       # Web UI port
FLASK_DEBUG=false     # Debug mode (set true for development)
```

## 📁 Directory Structure

After installation, your setup will look like:

```
~/ssiens-oss-static_pod/           # Main project
├── gateway/                       # POD Gateway application
│   ├── .venv/                    # Python virtual environment
│   ├── .env                      # Configuration (YOU EDIT THIS)
│   ├── app/                      # Application code
│   │   ├── main.py              # Entry point
│   │   ├── state_manager.py    # State tracking
│   │   └── printify_client.py  # Printify API
│   ├── templates/               # Web UI templates
│   │   └── index.html
│   ├── data/                    # Runtime data
│   │   ├── images/             # Your designs (ADD IMAGES HERE)
│   │   ├── state/              # State tracking
│   │   └── archive/            # Archived designs
│   └── requirements.txt        # Python dependencies
├── start-gateway.sh             # Quick start script
├── fresh-linux-install.sh       # Installation script
└── FRESH_INSTALL.md            # This file
```

## 🚨 Troubleshooting

### Installation Fails

**"python3: command not found"**
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

**"No module named 'venv'"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# Or create without venv
pip3 install --user flask requests pillow python-dotenv
```

**"Permission denied"**
```bash
# Don't use sudo - install in your home directory
cd ~
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
```

### Service Won't Start

**"Invalid Printify Shop ID"**
- Update `PRINTIFY_SHOP_ID` in `.env` to be a numeric value (not "your_shop_id_here")

**"Port 5000 already in use"**
```bash
# Change port in .env
nano ~/ssiens-oss-static_pod/gateway/.env
# Set: FLASK_PORT=8080
```

**"ModuleNotFoundError: No module named 'flask'"**
```bash
# Reinstall dependencies
cd ~/ssiens-oss-static_pod/gateway
source .venv/bin/activate
pip install -r requirements.txt
```

### No Images Showing

**Check images directory:**
```bash
ls -la ~/ssiens-oss-static_pod/gateway/data/images/
```

**Verify paths in .env:**
```bash
cat ~/ssiens-oss-static_pod/gateway/.env | grep POD_IMAGE_DIR
```

**Add test image:**
```bash
curl -o ~/ssiens-oss-static_pod/gateway/data/images/test.png \
  https://via.placeholder.com/2400x3000
```

### Can't Connect to Printify

**Test your API key:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.printify.com/v1/shops.json
```

**Common issues:**
1. API key is incorrect or expired
2. Shop ID is wrong
3. Network connectivity issues

## 🔒 Security Best Practices

### For Development/Testing
```bash
# Access only from localhost
FLASK_HOST=127.0.0.1
```

### For Production

1. **Use a reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name pod.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
       }
   }
   ```

2. **Add authentication:**
   - Use HTTP Basic Auth in nginx
   - Or add authentication middleware to Flask

3. **Protect your .env file:**
   ```bash
   chmod 600 ~/ssiens-oss-static_pod/gateway/.env
   ```

4. **Use firewall:**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw enable
   ```

## 🚀 Advanced: Systemd Service (Optional)

To run POD Gateway as a system service that starts on boot:

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/pod-gateway.service
```

Add:
```ini
[Unit]
Description=POD Gateway
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/ssiens-oss-static_pod/gateway
Environment="PYTHONPATH=/home/YOUR_USERNAME/ssiens-oss-static_pod/gateway"
ExecStart=/home/YOUR_USERNAME/ssiens-oss-static_pod/gateway/.venv/bin/python /home/YOUR_USERNAME/ssiens-oss-static_pod/gateway/app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual username.

### 2. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable pod-gateway
sudo systemctl start pod-gateway
```

### 3. Manage Service

```bash
sudo systemctl status pod-gateway    # Check status
sudo systemctl restart pod-gateway   # Restart
sudo systemctl stop pod-gateway      # Stop
sudo journalctl -u pod-gateway -f    # View logs
```

## 📚 Additional Resources

- **Main README:** [`README.md`](README.md)
- **Setup Guide:** [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
- **Linux Quick Start:** [`LINUX_QUICKSTART.md`](LINUX_QUICKSTART.md)
- **Gateway Documentation:** [`gateway/README.md`](gateway/README.md)
- **Printify Blueprints:** [`docs/PRINTIFY_BLUEPRINTS.md`](docs/PRINTIFY_BLUEPRINTS.md)

## 💡 Tips

1. **Use ComfyUI for AI image generation**
   - Set `COMFYUI_OUTPUT_DIR` to point to `gateway/data/images`
   - Or symlink: `ln -s /path/to/comfyui/output gateway/data/images`

2. **Batch process designs**
   - Drop multiple images into `data/images/`
   - Review all at once in the web UI
   - Approve multiple designs quickly

3. **Archive old designs**
   - The gateway automatically archives published designs
   - Check `data/archive/` for history

4. **Monitor the logs**
   - Check `journalctl -u pod-gateway -f` for real-time logs
   - Debug issues by checking error messages

## 🎉 You're Ready!

Your POD Gateway is now installed and ready to use. Here's your checklist:

- [ ] Installation complete
- [ ] Printify API keys configured
- [ ] Service starts without errors
- [ ] Web UI accessible at http://localhost:5000
- [ ] Test image appears in gallery
- [ ] Can approve and publish designs

**Start publishing your AI-generated designs to Printify! 🚀**

---

Need help? Check the [troubleshooting section](#-troubleshooting) or review the [main documentation](README.md).
