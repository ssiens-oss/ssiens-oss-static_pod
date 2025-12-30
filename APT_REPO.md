# APT Repository Setup Guide

Complete guide to setting up your own APT repository for StaticWaves POD.

---

## Why an APT Repository?

Benefits:
- ✅ One-line installs: `apt install staticwaves-pod`
- ✅ Automatic updates: `apt upgrade`
- ✅ Cryptographically signed & trusted
- ✅ Enterprise-grade distribution
- ✅ No manual .deb downloads

---

## Server Setup

### Requirements

- Ubuntu/Debian VPS or dedicated server
- Nginx or Apache
- Sufficient storage (1GB+ recommended)
- SSH access
- Domain name (optional but recommended)

---

## Step 1: Generate GPG Signing Key

```bash
# On your build machine (can be local)
gpg --full-generate-key
```

Choose:
- Type: **RSA and RSA**
- Size: **4096**
- Expiration: **1-3 years**
- Name: **StaticWaves**
- Email: **ops@staticwaves.io**

Verify key:
```bash
gpg --list-keys
```

Export public key:
```bash
gpg --armor --export ops@staticwaves.io > staticwaves-pod.gpg
```

Export private key (KEEP SECURE):
```bash
gpg --export-secret-keys ops@staticwaves.io > staticwaves-private.key
```

---

## Step 2: Create Repository Structure

On your server:

```bash
# Create directory structure
sudo mkdir -p /var/www/apt
sudo mkdir -p /var/www/apt/pool/main/s/staticwaves-pod
sudo mkdir -p /var/www/apt/dists/stable/main/binary-amd64

# Set permissions
sudo chown -R www-data:www-data /var/www/apt
sudo chmod -R 755 /var/www/apt
```

Directory layout:
```
/var/www/apt/
├── dists/
│   └── stable/
│       ├── Release
│       ├── Release.gpg
│       ├── InRelease
│       └── main/
│           └── binary-amd64/
│               ├── Packages
│               └── Packages.gz
└── pool/
    └── main/
        └── s/
            └── staticwaves-pod/
                └── staticwaves-pod_1.0.0_amd64.deb
```

---

## Step 3: Add Your .deb Package

```bash
# Copy your signed .deb package
scp staticwaves-pod_1.0.0_amd64.deb \
    user@your-server:/var/www/apt/pool/main/s/staticwaves-pod/
```

---

## Step 4: Generate Package Index

On your server:

```bash
cd /var/www/apt

# Generate Packages file
dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages

# Compress it
gzip -kf dists/stable/main/binary-amd64/Packages
```

---

## Step 5: Create Release File

```bash
cd /var/www/apt/dists/stable

# Create Release file
cat > Release <<EOF
Origin: StaticWaves
Label: StaticWaves POD
Suite: stable
Codename: stable
Architectures: amd64
Components: main
Description: StaticWaves AI POD Engine Repository
Date: $(date -Ru)
EOF

# Add checksums
apt-ftparchive release . >> Release
```

---

## Step 6: Sign Repository

Import your GPG key on the server:
```bash
gpg --import staticwaves-private.key
```

Sign the Release file:
```bash
cd /var/www/apt/dists/stable

# Detached signature
gpg --default-key ops@staticwaves.io \
    --armor --detach-sign \
    -o Release.gpg Release

# Clearsign
gpg --default-key ops@staticwaves.io \
    --clearsign \
    -o InRelease Release
```

---

## Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/apt-staticwaves
```

Add:
```nginx
server {
    listen 80;
    server_name apt.staticwaves.io;  # Or your domain

    root /var/www/apt;
    autoindex on;

    location / {
        try_files $uri $uri/ =404;
    }

    # Enable directory listing
    location /pool/ {
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }

    # Add CORS headers (optional)
    add_header Access-Control-Allow-Origin *;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/apt-staticwaves /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 8: Add SSL (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d apt.staticwaves.io
```

---

## Step 9: Create Update Script

```bash
sudo nano /var/www/apt/update-repo.sh
```

Add:
```bash
#!/bin/bash
set -e

cd /var/www/apt

echo "🔄 Updating APT repository..."

# Regenerate Packages index
dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages
gzip -kf dists/stable/main/binary-amd64/Packages

# Regenerate Release
cd dists/stable
rm -f Release Release.gpg InRelease

cat > Release <<EOF
Origin: StaticWaves
Label: StaticWaves POD
Suite: stable
Codename: stable
Architectures: amd64
Components: main
Description: StaticWaves AI POD Engine Repository
Date: $(date -Ru)
EOF

apt-ftparchive release . >> Release

# Sign Release
gpg --default-key ops@staticwaves.io \
    --armor --detach-sign \
    -o Release.gpg Release

gpg --default-key ops@staticwaves.io \
    --clearsign \
    -o InRelease Release

echo "✅ Repository updated"
```

Make executable:
```bash
sudo chmod +x /var/www/apt/update-repo.sh
```

---

## Client Usage

### First-Time Setup

```bash
# Add GPG key
curl -fsSL https://apt.staticwaves.io/staticwaves-pod.gpg \
 | sudo gpg --dearmor -o /usr/share/keyrings/staticwaves-pod.gpg

# Add repository
echo "deb [signed-by=/usr/share/keyrings/staticwaves-pod.gpg] https://apt.staticwaves.io stable main" \
 | sudo tee /etc/apt/sources.list.d/staticwaves-pod.list

# Update package list
sudo apt update
```

### Install Package

```bash
sudo apt install staticwaves-pod
```

### Update Package

```bash
sudo apt update
sudo apt upgrade staticwaves-pod
```

---

## Pushing Updates

### 1. Build New Version

```bash
# Update version in DEBIAN/control
sed -i 's/Version: .*/Version: 1.0.1/' debian-pkg/DEBIAN/control

# Build
./build-deb.sh

# Sign
dpkg-sig --sign builder staticwaves-pod_1.0.1_amd64.deb
```

### 2. Upload to Repository

```bash
scp staticwaves-pod_1.0.1_amd64.deb \
    user@your-server:/var/www/apt/pool/main/s/staticwaves-pod/
```

### 3. Update Repository Index

```bash
ssh user@your-server '/var/www/apt/update-repo.sh'
```

### 4. Users Get Update Automatically

```bash
sudo apt update
sudo apt upgrade  # Will show staticwaves-pod update available
```

---

## Automation with GitHub Actions

Add to `.github/workflows/build-release.yml`:

```yaml
- name: Upload to APT repository
  if: startsWith(github.ref, 'refs/tags/')
  run: |
    # Setup SSH
    mkdir -p ~/.ssh
    echo "${{ secrets.APT_REPO_SSH_KEY }}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    ssh-keyscan -H apt.staticwaves.io >> ~/.ssh/known_hosts

    # Upload package
    scp staticwaves-pod_*.deb \
        user@apt.staticwaves.io:/var/www/apt/pool/main/s/staticwaves-pod/

    # Update repo
    ssh user@apt.staticwaves.io '/var/www/apt/update-repo.sh'
```

Required secrets:
- `APT_REPO_SSH_KEY`
- `APT_REPO_HOST`
- `APT_REPO_USER`

---

## Multi-Client Repositories

For white-label clients, create separate repositories:

```bash
# Client-specific repo
/var/www/apt-acme/
/var/www/apt-cryptohype/
```

Each with:
- Separate GPG keys
- Separate domains: `apt-acme.staticwaves.io`
- Client-specific packages
- Independent billing/licensing

---

## Monitoring

### Check Repository Health

```bash
# Test repository
curl -I https://apt.staticwaves.io/dists/stable/Release

# Verify GPG signature
curl -s https://apt.staticwaves.io/dists/stable/InRelease | gpg --verify

# Check package availability
curl -s https://apt.staticwaves.io/dists/stable/main/binary-amd64/Packages | grep staticwaves-pod
```

### Server Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### GPG Verification Failed

**Problem**: `GPG error: The following signatures couldn't be verified`

**Solution**:
```bash
# Re-add GPG key
curl -fsSL https://apt.staticwaves.io/staticwaves-pod.gpg \
 | sudo gpg --dearmor -o /usr/share/keyrings/staticwaves-pod.gpg

# Update
sudo apt update
```

### Package Not Found

**Problem**: `E: Unable to locate package staticwaves-pod`

**Solutions**:
```bash
# 1. Check repository is added
cat /etc/apt/sources.list.d/staticwaves-pod.list

# 2. Update package list
sudo apt update

# 3. Verify repository accessible
curl https://apt.staticwaves.io/dists/stable/main/binary-amd64/Packages
```

### 404 Not Found

**Problem**: Repository URL returns 404

**Solutions**:
```bash
# Check Nginx config
sudo nginx -t

# Verify files exist
ls -la /var/www/apt/dists/stable/

# Check permissions
sudo chown -R www-data:www-data /var/www/apt
```

---

## Best Practices

1. **Always sign packages** - GPG signatures ensure trust
2. **Use HTTPS** - Encrypt downloads with SSL
3. **Backup GPG keys** - Store securely offline
4. **Version incrementally** - Semantic versioning (1.0.0 → 1.0.1)
5. **Test before pushing** - Verify in staging environment
6. **Monitor access logs** - Track downloads and errors
7. **Automate updates** - Use CI/CD for consistency

---

## Cost Estimate

| Service | Provider | Cost/month |
|---------|----------|------------|
| VPS | DigitalOcean | $6-12 |
| Domain | Namecheap | $1 |
| SSL | Let's Encrypt | Free |
| **Total** | | **$7-13/mo** |

---

## Support

Questions about APT repository setup:
- [GitHub Discussions](https://github.com/ssiens-oss/ssiens-oss-static_pod/discussions)
- Email: ops@staticwaves.io
