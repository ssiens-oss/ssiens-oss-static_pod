#!/bin/bash
set -e

# White-Label Package Builder
# Creates client-specific branded installers

echo "🏷️  StaticWaves POD White-Label Builder"

# Check arguments
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <client_id> <tier> <expires>"
    echo ""
    echo "Example:"
    echo "  $0 acme agency 2025-12-31"
    echo ""
    echo "Tiers: solo, agency, enterprise, unlimited"
    exit 1
fi

CLIENT_ID="$1"
TIER="$2"
EXPIRES="$3"
VERSION="1.0.0"
ARCH="amd64"

PACKAGE_NAME="staticwaves-pod-client-${CLIENT_ID}"
BUILD_DIR="build-${CLIENT_ID}"
DEB_NAME="${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo ""
echo "Client: $CLIENT_ID"
echo "Tier: $TIER"
echo "Expires: $EXPIRES"
echo ""

# Clean previous builds
rm -rf "$BUILD_DIR"
rm -f "${PACKAGE_NAME}"_*.deb

# Create build directory structure
echo "📁 Creating build structure..."
mkdir -p "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}"
mkdir -p "$BUILD_DIR/usr/lib/systemd/system"
mkdir -p "$BUILD_DIR/DEBIAN"

# Copy application files
echo "📦 Copying application files..."
cp -r api "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}/"
cp -r workers "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}/"
cp -r config "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}/"
cp -r data "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}/"

# Generate client-specific license
echo "🔑 Generating license..."
cat > "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}/license.json" <<EOF
{
  "client_id": "$CLIENT_ID",
  "tier": "$TIER",
  "expires": "$EXPIRES",
  "issued": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "signature": "$(echo -n "${CLIENT_ID}${TIER}${EXPIRES}" | sha256sum | cut -d' ' -f1)"
}
EOF

# Customize systemd services for client
echo "⚙️  Customizing systemd services..."
sed "s/staticwaves-pod/staticwaves-pod-${CLIENT_ID}/g" systemd/staticwaves-pod-api.service > "$BUILD_DIR/usr/lib/systemd/system/staticwaves-pod-${CLIENT_ID}-api.service"
sed "s/staticwaves-pod/staticwaves-pod-${CLIENT_ID}/g" systemd/staticwaves-pod-worker.service > "$BUILD_DIR/usr/lib/systemd/system/staticwaves-pod-${CLIENT_ID}-worker.service"

# Customize DEBIAN control
echo "📋 Customizing package metadata..."
sed "s/Package: staticwaves-pod/Package: ${PACKAGE_NAME}/" debian-pkg/DEBIAN/control > "$BUILD_DIR/DEBIAN/control"
sed -i "s|/opt/staticwaves-pod|/opt/staticwaves-pod-${CLIENT_ID}|g" "$BUILD_DIR/DEBIAN/control"

# Customize postinst script
sed "s|/opt/staticwaves-pod|/opt/staticwaves-pod-${CLIENT_ID}|g" debian-pkg/DEBIAN/postinst > "$BUILD_DIR/DEBIAN/postinst"
sed -i "s/staticwaves-pod-api/staticwaves-pod-${CLIENT_ID}-api/g" "$BUILD_DIR/DEBIAN/postinst"
sed -i "s/staticwaves-pod-worker/staticwaves-pod-${CLIENT_ID}-worker/g" "$BUILD_DIR/DEBIAN/postinst"

# Customize prerm script
sed "s/staticwaves-pod-api/staticwaves-pod-${CLIENT_ID}-api/g" debian-pkg/DEBIAN/prerm > "$BUILD_DIR/DEBIAN/prerm"
sed -i "s/staticwaves-pod-worker/staticwaves-pod-${CLIENT_ID}-worker/g" "$BUILD_DIR/DEBIAN/prerm"

# Copy postrm
cp debian-pkg/DEBIAN/postrm "$BUILD_DIR/DEBIAN/"

# Set permissions
chmod 755 "$BUILD_DIR/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/DEBIAN/prerm"
chmod 755 "$BUILD_DIR/DEBIAN/postrm"
chmod -R 755 "$BUILD_DIR/opt/staticwaves-pod-${CLIENT_ID}"

# Build .deb package
echo "📦 Building white-label package..."
dpkg-deb --build "$BUILD_DIR" "$DEB_NAME"

# Sign package
if command -v dpkg-sig &> /dev/null; then
    echo "🔐 Signing package..."
    dpkg-sig --sign builder "$DEB_NAME" || echo "⚠️  Signing skipped"
fi

# Cleanup
rm -rf "$BUILD_DIR"

echo ""
echo "✅ White-label package built: $DEB_NAME"
echo ""
echo "📧 Deliver to client: $CLIENT_ID"
echo "🔑 License tier: $TIER"
echo "📅 Expires: $EXPIRES"
echo ""
echo "📦 Install command for client:"
echo "   sudo dpkg -i $DEB_NAME"
echo ""
