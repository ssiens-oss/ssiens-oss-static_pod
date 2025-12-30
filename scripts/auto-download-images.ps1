# Auto-download images from RunPod to Windows local machine
# Run this script on YOUR LOCAL WINDOWS MACHINE in PowerShell

param(
    [string]$RunPodSSH = $env:RUNPOD_SSH_HOST,
    [string]$SSHKey = "$env:USERPROFILE\.ssh\id_ed25519",
    [string]$RemotePath = "/data/designs",
    [string]$LocalPath = "$env:USERPROFILE\POD-Designs",
    [int]$SyncInterval = 60
)

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  POD Studio - Auto Image Downloader (Windows)    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if RunPod SSH is set
if (-not $RunPodSSH) {
    Write-Host "⚠ RunPod SSH not set!" -ForegroundColor Yellow
    Write-Host ""
    $RunPodSSH = Read-Host "Enter your RunPod SSH (e.g., podid-xxx@ssh.runpod.io)"
}

# Create local directory
if (-not (Test-Path $LocalPath)) {
    New-Item -ItemType Directory -Path $LocalPath | Out-Null
}

Write-Host "✓ Configuration:" -ForegroundColor Green
Write-Host "  Remote: $RunPodSSH`:$RemotePath" -ForegroundColor Cyan
Write-Host "  Local:  $LocalPath" -ForegroundColor Cyan
Write-Host "  Sync:   Every $SyncInterval seconds" -ForegroundColor Cyan
Write-Host ""

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
try {
    $testCmd = "ssh -i `"$SSHKey`" -o ConnectTimeout=5 -o StrictHostKeyChecking=no $RunPodSSH 'echo Connection successful' 2>&1"
    $result = Invoke-Expression $testCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ SSH connection successful" -ForegroundColor Green
    } else {
        throw "SSH connection failed"
    }
} catch {
    Write-Host "✗ SSH connection failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "1. Make sure your RunPod is running"
    Write-Host "2. Check your SSH key: $SSHKey"
    Write-Host "3. Verify RunPod SSH host: $RunPodSSH"
    Write-Host "4. Install OpenSSH client (Windows 10+): Settings > Apps > Optional Features"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting auto-sync... (Press Ctrl+C to stop)" -ForegroundColor Green
Write-Host ""

$totalDownloaded = 0

# Sync loop
while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Syncing..." -ForegroundColor Cyan

    # Get file list before sync
    $filesBefore = @{}
    if (Test-Path $LocalPath) {
        Get-ChildItem -Path $LocalPath -File -Recurse | ForEach-Object {
            $filesBefore[$_.FullName] = $true
        }
    }

    # Use SCP to download (Windows has scp built-in with OpenSSH)
    $scpCmd = "scp -i `"$SSHKey`" -o StrictHostKeyChecking=no -r ${RunPodSSH}:${RemotePath}/* `"$LocalPath\`" 2>&1"
    try {
        Invoke-Expression $scpCmd | Out-Null

        # Get file list after sync
        $newFiles = @()
        if (Test-Path $LocalPath) {
            Get-ChildItem -Path $LocalPath -File -Recurse | ForEach-Object {
                if (-not $filesBefore.ContainsKey($_.FullName)) {
                    $newFiles += $_.Name
                }
            }
        }

        if ($newFiles.Count -gt 0) {
            $totalDownloaded += $newFiles.Count
            Write-Host "✓ Downloaded $($newFiles.Count) new image(s) [Total: $totalDownloaded]" -ForegroundColor Green
            foreach ($file in $newFiles) {
                Write-Host "  → $file" -ForegroundColor Cyan
            }
        } else {
            Write-Host "○ No new images" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ Sync failed: $_" -ForegroundColor Red
    }

    Start-Sleep -Seconds $SyncInterval
}
