# Auto-Download Images to Your Local Machine

This guide shows you how to automatically download generated images from your RunPod to your local computer.

## 🚀 Quick Start

### For Mac/Linux Users:

**Option 1: Auto-Sync (Continuous)**
```bash
# Set your RunPod SSH connection
export RUNPOD_SSH_HOST="your-pod-id@ssh.runpod.io"

# Run the auto-sync script (keeps running, downloads new images every 60 seconds)
./scripts/auto-download-images.sh
```

**Option 2: One-Time Download**
```bash
# Set your RunPod SSH connection
export RUNPOD_SSH_HOST="your-pod-id@ssh.runpod.io"

# Download all images once
./scripts/download-images.sh
```

### For Windows Users:

**Auto-Sync (PowerShell)**
```powershell
# Open PowerShell and run:
$env:RUNPOD_SSH_HOST = "your-pod-id@ssh.runpod.io"

# Run the auto-sync script
.\scripts\auto-download-images.ps1
```

## 📋 Setup Instructions

### 1. Get Your RunPod SSH Connection

In your RunPod interface:
1. Click on your running pod
2. Go to the **"Connect"** tab
3. Find the **SSH** section
4. Copy the SSH command, it looks like:
   ```
   ssh podid-xxxx@ssh.runpod.io -i ~/.ssh/your_key
   ```
5. Your `RUNPOD_SSH_HOST` is: `podid-xxxx@ssh.runpod.io`

### 2. Configure Environment Variables

**Mac/Linux:**
```bash
# In your terminal or add to ~/.bashrc or ~/.zshrc
export RUNPOD_SSH_HOST="your-pod-id@ssh.runpod.io"
export RUNPOD_SSH_KEY="$HOME/.ssh/id_ed25519"  # Optional, defaults to this
export LOCAL_PATH="$HOME/POD-Designs"           # Optional, where to save images
export SYNC_INTERVAL=60                         # Optional, seconds between syncs
```

**Windows:**
```powershell
# In PowerShell or add to your PowerShell profile
$env:RUNPOD_SSH_HOST = "your-pod-id@ssh.runpod.io"
$env:RUNPOD_SSH_KEY = "$env:USERPROFILE\.ssh\id_ed25519"
```

### 3. Run the Auto-Download Script

The script will:
- ✅ Connect to your RunPod via SSH
- ✅ Check for new images every 60 seconds (configurable)
- ✅ Download only NEW images (skips duplicates)
- ✅ Save to `~/POD-Designs/` on your local machine
- ✅ Show progress and count

## 📁 Where Are Images Saved?

**Default locations:**
- **Mac/Linux**: `~/POD-Designs/`
- **Windows**: `C:\Users\YourName\POD-Designs\`

**Custom location:**
```bash
# Mac/Linux
export LOCAL_PATH="/path/to/your/folder"

# Windows
$env:LOCAL_PATH = "C:\MyImages\POD"
```

## ⚙️ Customization

### Change Sync Interval

**Mac/Linux:**
```bash
export SYNC_INTERVAL=30  # Check every 30 seconds
./scripts/auto-download-images.sh
```

**Windows:**
```powershell
.\scripts\auto-download-images.ps1 -SyncInterval 30
```

### Custom Remote Path

If you changed where images are saved on RunPod:
```bash
export REMOTE_PATH="/workspace/my-custom-folder"
```

## 🔧 Troubleshooting

### "SSH connection failed"

1. **Make sure your RunPod is running**
   - Check RunPod dashboard

2. **Verify your SSH key**
   - Make sure `~/.ssh/id_ed25519` exists
   - Or specify custom key: `export RUNPOD_SSH_KEY="/path/to/key"`

3. **Test SSH manually**
   ```bash
   ssh your-pod-id@ssh.runpod.io -i ~/.ssh/id_ed25519
   ```

### "rsync: command not found" (Mac/Linux)

Install rsync:
```bash
# Mac
brew install rsync

# Ubuntu/Debian
sudo apt-get install rsync
```

### Windows: "ssh: command not found"

Install OpenSSH Client:
1. Settings → Apps → Optional Features
2. Add a feature → OpenSSH Client
3. Install
4. Restart PowerShell

## 💡 Tips

### Run in Background (Mac/Linux)

```bash
# Run auto-sync in background
nohup ./scripts/auto-download-images.sh > /tmp/pod-sync.log 2>&1 &

# Check if running
ps aux | grep auto-download

# View logs
tail -f /tmp/pod-sync.log

# Stop background process
pkill -f auto-download-images
```

### Run on Startup (Mac)

Create a Launch Agent:
```bash
# Create ~/Library/LaunchAgents/com.pod.autosync.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pod.autosync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/scripts/auto-download-images.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

### Run on Startup (Windows)

Create a scheduled task:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\path\to\scripts\auto-download-images.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $action -Trigger $trigger `
    -TaskName "POD Auto Sync" -Description "Auto-download POD images"
```

## 🔄 How It Works

1. **Auto-Sync Script**: Runs continuously and checks for new files
2. **Uses rsync/scp**: Only downloads NEW or CHANGED files (fast!)
3. **No duplicates**: Compares local vs remote, skips existing files
4. **Progress tracking**: Shows exactly what was downloaded
5. **Handles reconnection**: If SSH drops, reconnects automatically

## 📊 What Gets Downloaded?

All files in your RunPod's `/data/designs/` directory:
- Generated AI images (PNG, JPG, etc.)
- Associated metadata files (JSON)
- Organized by date/batch (if you set it up that way)

## 🎯 Next Steps

Once auto-download is running:
1. Generate images via the POD pipeline
2. Images automatically appear in `~/POD-Designs/`
3. Use them for your print-on-demand products!

Need help? Check the main README.md or SETUP_GUIDE.md
