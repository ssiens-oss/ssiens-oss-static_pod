# POD Gateway - Standalone Deployment Guide

## Overview

POD Gateway can now run as an independent, self-contained application with multiple deployment options:

1. **Systemd Service** - Linux service with auto-start and auto-restart
2. **Docker Container** - Containerized deployment with Docker Compose
3. **Supervisor** - Process manager for production environments
4. **Daemon Mode** - Background process with management commands

---

## Deployment Options

### Option 1: Systemd Service (Recommended for Linux Servers)

**Best for:** Linux servers, VPS, dedicated machines

#### Installation

```bash
cd gateway
sudo ./install_standalone.sh
```

This will:
- Install system dependencies
- Create installation directory (`/opt/pod-gateway`)
- Set up Python virtual environment
- Create and enable systemd service
- Start the service automatically

#### Management

```bash
# Start service
sudo systemctl start pod-gateway

# Stop service
sudo systemctl stop pod-gateway

# Restart service
sudo systemctl restart pod-gateway

# Check status
sudo systemctl status pod-gateway

# View logs
sudo journalctl -u pod-gateway -f

# Enable auto-start on boot (already enabled by installer)
sudo systemctl enable pod-gateway

# Disable auto-start
sudo systemctl disable pod-gateway
```

#### Configuration

Edit configuration file:
```bash
sudo nano /opt/pod-gateway/.env
```

After changing configuration:
```bash
sudo systemctl restart pod-gateway
```

#### Uninstall

```bash
cd gateway
sudo ./install_standalone.sh uninstall
```

---

### Option 2: Docker Container

**Best for:** Any platform with Docker, easy deployment, isolation

#### Prerequisites

- Docker installed
- Docker Compose installed

#### Quick Start

```bash
cd gateway

# First time: Copy environment file
cp .env.example .env
# Edit .env with your configuration
nano .env

# Build and start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

#### Management

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

#### Accessing the Container

```bash
# Execute commands in container
docker-compose exec pod-gateway bash

# View container logs
docker logs pod-gateway -f
```

#### Data Persistence

Data is stored in `./data/` directory:
```
gateway/data/
├── images/   # Generated images
├── state/    # State file
└── archive/  # Archived images
```

To backup:
```bash
tar -czf pod-gateway-backup.tar.gz data/
```

---

### Option 3: Supervisor

**Best for:** Production environments, shared hosting, process monitoring

#### Installation

```bash
# Install supervisor
sudo apt-get install supervisor  # Debian/Ubuntu
sudo yum install supervisor      # CentOS/RHEL

# Copy configuration
sudo cp supervisord.conf /etc/supervisor/conf.d/pod-gateway.conf

# Update configuration paths if needed
sudo nano /etc/supervisor/conf.d/pod-gateway.conf

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
```

#### Management

```bash
# Start
sudo supervisorctl start pod-gateway

# Stop
sudo supervisorctl stop pod-gateway

# Restart
sudo supervisorctl restart pod-gateway

# Status
sudo supervisorctl status pod-gateway

# View logs
sudo tail -f /var/log/pod-gateway.log
```

---

### Option 4: Daemon Mode

**Best for:** Development, testing, manual control

#### Usage

```bash
# Start daemon
./daemon.py start

# Stop daemon
./daemon.py stop

# Restart daemon
./daemon.py restart

# Check status
./daemon.py status
```

#### Logs

Logs are written to `/var/log/pod-gateway.log`

```bash
tail -f /var/log/pod-gateway.log
```

---

## Unified Control Script

The `pod-gateway-ctl.sh` script automatically detects your deployment method and provides a unified interface:

```bash
# Make executable (first time only)
chmod +x pod-gateway-ctl.sh

# Start service
./pod-gateway-ctl.sh start

# Stop service
./pod-gateway-ctl.sh stop

# Restart service
./pod-gateway-ctl.sh restart

# Show status
./pod-gateway-ctl.sh status

# View logs
./pod-gateway-ctl.sh logs

# Check health
./pod-gateway-ctl.sh health
```

The script works with both systemd and Docker deployments automatically.

---

## Configuration

### Environment Variables

Create or edit `.env` file:

```bash
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Directories
POD_IMAGE_DIR=/opt/pod-gateway/data/images
POD_STATE_FILE=/opt/pod-gateway/data/state/state.json
POD_ARCHIVE_DIR=/opt/pod-gateway/data/archive

# Printify Configuration
PRINTIFY_API_KEY=your-api-key-here
PRINTIFY_SHOP_ID=your-shop-id-here
PRINTIFY_BLUEPRINT_ID=3
PRINTIFY_PROVIDER_ID=99
PRINTIFY_DEFAULT_PRICE_CENTS=1999

# Retry Configuration
API_MAX_RETRIES=3
API_INITIAL_BACKOFF_SECONDS=1.0
API_MAX_BACKOFF_SECONDS=30.0
API_BACKOFF_MULTIPLIER=2.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Obtaining Printify Credentials

1. Go to https://printify.com/
2. Sign up or log in
3. Navigate to **My Account** → **Connections** → **API**
4. Generate API token
5. Find your Shop ID in the API section

---

## Health Checks

### Manual Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "printify": true,
  "image_dir": true,
  "state_file": true
}
```

### Automated Health Checks

All deployment methods include automatic health checks:

- **Systemd**: Monitored by systemd, auto-restart on failure
- **Docker**: Built-in healthcheck (30s interval)
- **Supervisor**: Auto-restart on failure
- **Daemon**: Manual monitoring required

---

## Monitoring

### Systemd Logs

```bash
# Follow logs
sudo journalctl -u pod-gateway -f

# Show last 100 lines
sudo journalctl -u pod-gateway -n 100

# Show logs since today
sudo journalctl -u pod-gateway --since today

# Show errors only
sudo journalctl -u pod-gateway -p err
```

### Docker Logs

```bash
# Follow logs
docker-compose logs -f

# Show last 100 lines
docker-compose logs --tail=100

# Show timestamps
docker-compose logs -f --timestamps
```

### Log Files

Default log locations:
- **Systemd**: `journalctl -u pod-gateway`
- **Docker**: `docker-compose logs`
- **Supervisor**: `/var/log/pod-gateway.log`
- **Daemon**: `/var/log/pod-gateway.log`

---

## Troubleshooting

### Service Won't Start

1. **Check configuration:**
   ```bash
   sudo systemctl status pod-gateway
   ```

2. **View detailed logs:**
   ```bash
   sudo journalctl -u pod-gateway -n 50
   ```

3. **Verify .env file exists:**
   ```bash
   ls -la /opt/pod-gateway/.env
   ```

4. **Check port availability:**
   ```bash
   sudo lsof -i :5000
   ```

### Container Issues

1. **Check container status:**
   ```bash
   docker-compose ps
   ```

2. **View logs:**
   ```bash
   docker-compose logs
   ```

3. **Rebuild container:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

4. **Check volumes:**
   ```bash
   docker volume ls
   ```

### Permission Issues

```bash
# Fix ownership (systemd)
sudo chown -R root:root /opt/pod-gateway

# Fix permissions
sudo chmod -R 755 /opt/pod-gateway
sudo chmod 600 /opt/pod-gateway/.env
```

### Port Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process (if safe)
sudo kill -9 <PID>

# Or change port in .env
# Edit FLASK_PORT=5001
```

---

## Security Considerations

### Production Hardening

1. **Use HTTPS with reverse proxy:**
   ```bash
   # Install nginx
   sudo apt-get install nginx

   # Configure SSL with Let's Encrypt
   sudo certbot --nginx
   ```

2. **Firewall rules:**
   ```bash
   # Allow only from specific IP
   sudo ufw allow from 192.168.1.0/24 to any port 5000
   ```

3. **Disable debug mode:**
   ```bash
   # In .env
   FLASK_DEBUG=false
   ```

4. **Regular updates:**
   ```bash
   # Update dependencies
   source .venv/bin/activate
   pip install --upgrade -r requirements.txt
   ```

5. **Monitor logs for suspicious activity:**
   ```bash
   sudo journalctl -u pod-gateway -f | grep -i error
   ```

---

## Performance Tuning

### Systemd Service Limits

Edit `/etc/systemd/system/pod-gateway.service`:

```ini
[Service]
# Increase file descriptors
LimitNOFILE=65536

# Memory limit (adjust as needed)
MemoryLimit=2G

# CPU limit (50% of one core)
CPUQuota=50%
```

Reload after changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart pod-gateway
```

### Docker Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  pod-gateway:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          memory: 512M
```

---

## Auto-Start on Boot

### Systemd (Already Enabled)

```bash
# Verify enabled
sudo systemctl is-enabled pod-gateway

# Enable if not
sudo systemctl enable pod-gateway
```

### Docker with System Restart

```bash
# Already configured in docker-compose.yml
# restart: unless-stopped
```

To start on boot, enable Docker service:
```bash
sudo systemctl enable docker
```

---

## Migration Between Deployment Methods

### From Manual to Systemd

```bash
# Stop manual process
./daemon.py stop

# Install as service
sudo ./install_standalone.sh

# Copy data if needed
sudo cp -r data/* /opt/pod-gateway/data/
```

### From Systemd to Docker

```bash
# Stop systemd service
sudo systemctl stop pod-gateway

# Copy data
cp -r /opt/pod-gateway/data ./

# Start Docker
docker-compose up -d
```

---

## Backup and Restore

### Backup

```bash
# Create backup directory
mkdir -p ~/pod-gateway-backups

# Backup data (systemd)
sudo tar -czf ~/pod-gateway-backups/backup-$(date +%Y%m%d).tar.gz \
  -C /opt/pod-gateway data/ .env

# Backup data (docker)
tar -czf ~/pod-gateway-backups/backup-$(date +%Y%m%d).tar.gz data/ .env
```

### Restore

```bash
# Extract backup (systemd)
sudo tar -xzf ~/pod-gateway-backups/backup-YYYYMMDD.tar.gz \
  -C /opt/pod-gateway

# Extract backup (docker)
tar -xzf ~/pod-gateway-backups/backup-YYYYMMDD.tar.gz

# Restart service
sudo systemctl restart pod-gateway
# or
docker-compose restart
```

### Automated Backups

Create cron job:
```bash
sudo crontab -e

# Add line (daily backup at 2 AM)
0 2 * * * tar -czf /backup/pod-gateway-$(date +\%Y\%m\%d).tar.gz -C /opt/pod-gateway data/ .env
```

---

## Support

For issues or questions:
1. Check logs first
2. Verify configuration
3. Review this documentation
4. Open GitHub issue with logs and configuration (remove sensitive data)

---

**Ready to deploy!** Choose your deployment method and get started. 🚀
