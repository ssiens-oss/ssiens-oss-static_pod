#!/bin/bash
# StaticWaves TikTok Integration - systemd Installation Script
# =============================================================
#
# This script installs and enables the TikTok feed generator
# as a systemd service with automatic scheduling.
#
# Usage:
#   sudo ./systemd/install.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="staticwaves-tiktok"
INSTALL_DIR="/opt/staticwaves_pod"
SYSTEMD_DIR="/etc/systemd/system"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}StaticWaves TikTok systemd Installer${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo -e "${RED}❌ systemd not found. Use cron instead.${NC}"
    echo -e "${YELLOW}See systemd/cron.example for cron setup${NC}"
    exit 1
fi

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}📁 Creating installation directory: $INSTALL_DIR${NC}"
    mkdir -p "$INSTALL_DIR"
fi

# Copy project files (assumes script is run from project root)
echo -e "${GREEN}📦 Copying project files...${NC}"
cp -r . "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/tools/"*.py

# Create logs and exports directories
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/exports"
mkdir -p "$INSTALL_DIR/queues/published"

# Install systemd service file
echo -e "${GREEN}⚙️  Installing systemd service...${NC}"
cp "$INSTALL_DIR/systemd/${SERVICE_NAME}.service" "$SYSTEMD_DIR/"
chmod 644 "$SYSTEMD_DIR/${SERVICE_NAME}.service"

# Install systemd timer file
echo -e "${GREEN}⏰ Installing systemd timer...${NC}"
cp "$INSTALL_DIR/systemd/${SERVICE_NAME}.timer" "$SYSTEMD_DIR/"
chmod 644 "$SYSTEMD_DIR/${SERVICE_NAME}.timer"

# Reload systemd
echo -e "${GREEN}🔄 Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Check if .env exists
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo -e "${YELLOW}📝 Creating .env from example...${NC}"

    if [ -f "$INSTALL_DIR/.env.example" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit $INSTALL_DIR/.env with your TikTok credentials${NC}"
    else
        echo -e "${RED}❌ .env.example not found. Create .env manually.${NC}"
    fi
fi

# Set permissions
echo -e "${GREEN}🔒 Setting permissions...${NC}"
chown -R staticwaves:staticwaves "$INSTALL_DIR" 2>/dev/null || \
    echo -e "${YELLOW}⚠️  User 'staticwaves' not found. Run as current user or create user first.${NC}"

# Enable and start timer
echo -e "${GREEN}✅ Enabling systemd timer...${NC}"
systemctl enable "${SERVICE_NAME}.timer"
systemctl start "${SERVICE_NAME}.timer"

# Show status
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${GREEN}Service Status:${NC}"
systemctl status "${SERVICE_NAME}.timer" --no-pager || true
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo -e "  1. Edit $INSTALL_DIR/.env with TikTok credentials"
echo -e "  2. Add design files to $INSTALL_DIR/queues/published/"
echo -e "  3. Test manually: python3 $INSTALL_DIR/tools/tiktok_feed_generator.py"
echo ""
echo -e "${GREEN}Useful Commands:${NC}"
echo -e "  View timer status:    systemctl status ${SERVICE_NAME}.timer"
echo -e "  View service logs:    journalctl -u ${SERVICE_NAME} -f"
echo -e "  Run manually:         systemctl start ${SERVICE_NAME}"
echo -e "  Disable auto-run:     systemctl disable ${SERVICE_NAME}.timer"
echo ""
