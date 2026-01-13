# POD Gateway - Quick Start (Standalone)

## 1-Minute Setup

### Option A: Systemd Service (Linux)

```bash
cd gateway
sudo ./install_standalone.sh
```

**That's it!** Service is now running at http://localhost:5000

#### Configure

```bash
# Edit configuration
sudo nano /opt/pod-gateway/.env

# Restart to apply changes
sudo systemctl restart pod-gateway
```

#### Control

```bash
./pod-gateway-ctl.sh status   # Check status
./pod-gateway-ctl.sh logs     # View logs
./pod-gateway-ctl.sh restart  # Restart
./pod-gateway-ctl.sh health   # Health check
```

---

### Option B: Docker

```bash
cd gateway

# Copy and configure environment
cp .env.example .env
nano .env  # Add your Printify credentials

# Start
docker-compose up -d

# View logs
docker-compose logs -f
```

**That's it!** Service is now running at http://localhost:5000

#### Control

```bash
./pod-gateway-ctl.sh status   # Check status
./pod-gateway-ctl.sh logs     # View logs
./pod-gateway-ctl.sh restart  # Restart
./pod-gateway-ctl.sh stop     # Stop
./pod-gateway-ctl.sh start    # Start
```

---

## Access Web UI

Open in browser: **http://localhost:5000**

Or if on remote server:
- http://your-server-ip:5000
- Make sure port 5000 is open in firewall

---

## Verify It's Running

```bash
# Check health
curl http://localhost:5000/health

# Should return:
{
  "status": "healthy",
  "printify": true,
  "image_dir": true,
  "state_file": true
}
```

---

## Next Steps

1. **Add images** to the watch directory:
   - Systemd: `/opt/pod-gateway/data/images/`
   - Docker: `./data/images/`

2. **Open web UI** and approve/reject designs

3. **Publish** approved designs to Printify

---

## Troubleshooting

### Service won't start?

```bash
# Systemd
sudo journalctl -u pod-gateway -n 50

# Docker
docker-compose logs
```

### Port 5000 already in use?

```bash
# Change port in .env
FLASK_PORT=5001

# Restart
sudo systemctl restart pod-gateway  # systemd
docker-compose restart              # docker
```

### Can't access from browser?

1. Check if service is running:
   ```bash
   ./pod-gateway-ctl.sh status
   ```

2. Check firewall:
   ```bash
   sudo ufw allow 5000
   ```

3. Try localhost first:
   ```bash
   curl http://localhost:5000/health
   ```

---

## Full Documentation

See [STANDALONE_DEPLOYMENT.md](./STANDALONE_DEPLOYMENT.md) for:
- Detailed configuration
- Security hardening
- Backup/restore
- Monitoring
- Performance tuning

---

## Uninstall

### Systemd

```bash
sudo ./install_standalone.sh uninstall
```

### Docker

```bash
docker-compose down -v
```

---

**Need help?** Check the logs first, then review [STANDALONE_DEPLOYMENT.md](./STANDALONE_DEPLOYMENT.md)
