# RunPod ComfyUI Image Sync Guide

Automatically download images from RunPod ComfyUI to your local POD Gateway.

## Setup

### 1. Get RunPod SSH Connection Details

From RunPod dashboard:
1. Go to your pod
2. Click "Connect"
3. Copy the SSH command, it looks like:
   ```
   ssh root@pod-abc123-ssh.runpod.io -p 12345
   ```

Extract:
- **Host**: `pod-abc123-ssh.runpod.io`
- **Port**: `12345`
- **User**: `root`

### 2. Set Up SSH Key

**Option A: Use existing SSH key**
```bash
# If you already have an SSH key
ls ~/.ssh/id_rsa
```

**Option B: Generate new SSH key**
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/runpod_key -N ""

# Copy public key to RunPod
ssh-copy-id -i ~/.ssh/runpod_key.pub -p PORT root@pod-xxx-ssh.runpod.io
```

**Option C: Use RunPod's SSH key (if provided)**
```bash
# Download from RunPod dashboard and save as:
mv ~/Downloads/runpod_key ~/.ssh/runpod_key
chmod 600 ~/.ssh/runpod_key
```

### 3. Configure Sync

```bash
# Copy configuration file
sudo cp ~/ssiens-oss-static_pod/gateway/runpod-sync.conf /opt/pod-gateway/

# Edit with your RunPod details
sudo nano /opt/pod-gateway/runpod-sync.conf
```

**Edit these values:**
```bash
RUNPOD_HOST=pod-xxxxx-ssh.runpod.io    # Your pod host
RUNPOD_PORT=12345                       # Your pod SSH port
RUNPOD_SSH_KEY=/root/.ssh/id_rsa        # Path to SSH key
DELETE_AFTER_DOWNLOAD=false             # Set to true to delete after download
```

### 4. Copy Download Script

```bash
# Copy the script
sudo cp ~/ssiens-oss-static_pod/gateway/download-runpod-images.sh /opt/pod-gateway/
sudo chmod +x /opt/pod-gateway/download-runpod-images.sh
```

## Usage

### Manual Download

```bash
# Load configuration and download
source /opt/pod-gateway/runpod-sync.conf
/opt/pod-gateway/download-runpod-images.sh
```

Or with inline config:
```bash
# One-time download
export RUNPOD_HOST=pod-xxx-ssh.runpod.io
export RUNPOD_PORT=12345
cd ~/ssiens-oss-static_pod/gateway
./download-runpod-images.sh
```

### Automatic Sync (Systemd Timer)

**Install timer:**
```bash
# Copy systemd files
sudo cp ~/ssiens-oss-static_pod/gateway/pod-gateway-sync.service /etc/systemd/system/
sudo cp ~/ssiens-oss-static_pod/gateway/pod-gateway-sync.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable pod-gateway-sync.timer
sudo systemctl start pod-gateway-sync.timer

# Check status
sudo systemctl status pod-gateway-sync.timer
```

**Timer runs every 5 minutes automatically!**

**Manage timer:**
```bash
# Check when next sync will run
systemctl list-timers pod-gateway-sync.timer

# View sync logs
sudo journalctl -u pod-gateway-sync.service -f

# Stop automatic sync
sudo systemctl stop pod-gateway-sync.timer

# Disable automatic sync
sudo systemctl disable pod-gateway-sync.timer

# Trigger manual sync now
sudo systemctl start pod-gateway-sync.service
```

### Cron Job (Alternative)

If you prefer cron:
```bash
# Edit root crontab
sudo crontab -e

# Add line (sync every 5 minutes)
*/5 * * * * source /opt/pod-gateway/runpod-sync.conf && /opt/pod-gateway/download-runpod-images.sh >> /var/log/pod-gateway-sync.log 2>&1
```

## Test Connection

```bash
# Test SSH connection
ssh -i ~/.ssh/id_rsa -p PORT root@pod-xxx-ssh.runpod.io "ls /workspace/ComfyUI/output"

# Should list your ComfyUI output files
```

## Workflow

1. **ComfyUI generates images** on RunPod → `/workspace/ComfyUI/output/`
2. **Sync script downloads** → `/opt/pod-gateway/data/images/`
3. **POD Gateway detects** new images automatically
4. **You review** in web UI at http://localhost:5000
5. **Approve/Reject** designs
6. **Publish** to Printify

## Configuration Options

### Delete After Download

Set `DELETE_AFTER_DOWNLOAD=true` to automatically delete images from RunPod after downloading.

**⚠️ Warning:** Only enable if you're sure the download was successful!

### Custom Directories

Change remote directory:
```bash
REMOTE_COMFY_DIR=/workspace/ComfyUI/output
```

Change local directory:
```bash
LOCAL_IMAGE_DIR=/opt/pod-gateway/data/images
```

### Sync Frequency

Edit timer file to change frequency:
```bash
sudo nano /etc/systemd/system/pod-gateway-sync.timer

# Change this line:
OnUnitActiveSec=5min   # 5 minutes
# To:
OnUnitActiveSec=1min   # 1 minute
OnUnitActiveSec=10min  # 10 minutes
OnUnitActiveSec=1h     # 1 hour

# Reload
sudo systemctl daemon-reload
sudo systemctl restart pod-gateway-sync.timer
```

## Troubleshooting

### Connection Refused

```bash
# Check SSH key permissions
ls -la ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa

# Test connection manually
ssh -i ~/.ssh/id_rsa -p PORT root@pod-xxx-ssh.runpod.io
```

### No Images Downloaded

```bash
# Check remote directory
ssh -i ~/.ssh/id_rsa -p PORT root@pod-xxx-ssh.runpod.io "ls -la /workspace/ComfyUI/output"

# Check if images exist
ssh -i ~/.ssh/id_rsa -p PORT root@pod-xxx-ssh.runpod.io "find /workspace/ComfyUI/output -name '*.png'"
```

### Permission Denied

```bash
# Fix local directory permissions
sudo chown -R root:root /opt/pod-gateway/data/images
sudo chmod 755 /opt/pod-gateway/data/images
```

### Sync Not Running

```bash
# Check timer status
systemctl status pod-gateway-sync.timer

# Check service status
systemctl status pod-gateway-sync.service

# View logs
sudo journalctl -u pod-gateway-sync.service -n 50
```

## Monitoring

```bash
# Watch for new images
watch -n 2 "ls -lh /opt/pod-gateway/data/images/ | tail -10"

# Monitor sync logs
sudo journalctl -u pod-gateway-sync.service -f

# Check API
watch -n 5 "curl -s http://localhost:5000/api/images | python3 -m json.tool | head -20"
```

## Advanced: Selective Download

Only download images matching pattern:
```bash
# Edit the script and modify the rsync/scp command
# Add pattern matching, for example:
--include='ComfyUI_*.png'  # Only ComfyUI generated images
--include='2026-*.png'      # Only images from 2026
```

## Security Notes

- Keep SSH keys private (`chmod 600`)
- Use separate SSH key for RunPod (don't use your main key)
- Regularly rotate SSH keys
- Monitor sync logs for unauthorized access
- Consider using SSH key passphrase for extra security

## Complete Example

```bash
# 1. Get RunPod details
RUNPOD_HOST=pod-abc123-ssh.runpod.io
RUNPOD_PORT=12345

# 2. Test connection
ssh -p 12345 root@pod-abc123-ssh.runpod.io "ls /workspace/ComfyUI/output"

# 3. Configure
sudo nano /opt/pod-gateway/runpod-sync.conf
# (add your host and port)

# 4. Test manual sync
source /opt/pod-gateway/runpod-sync.conf
/opt/pod-gateway/download-runpod-images.sh

# 5. Enable automatic sync
sudo systemctl enable pod-gateway-sync.timer
sudo systemctl start pod-gateway-sync.timer

# 6. Monitor
sudo journalctl -u pod-gateway-sync.service -f
```

Now images will automatically sync from RunPod to your local POD Gateway every 5 minutes! 🚀
