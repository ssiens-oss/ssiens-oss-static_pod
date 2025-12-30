#!/bin/bash
set -e

echo "🔨 Building StaticWaves POD .deb package"

# Configuration
PACKAGE_NAME="staticwaves-pod"
VERSION="1.0.0"
ARCH="amd64"
BUILD_DIR="build"
DEB_NAME="${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$BUILD_DIR"
rm -f "${PACKAGE_NAME}"_*.deb

# Create build directory structure
echo "📁 Creating build directory structure..."
mkdir -p "$BUILD_DIR/opt/staticwaves-pod"
mkdir -p "$BUILD_DIR/usr/lib/systemd/system"
mkdir -p "$BUILD_DIR/DEBIAN"

# Copy application files
echo "📦 Copying application files..."
cp -r api "$BUILD_DIR/opt/staticwaves-pod/"
cp -r workers "$BUILD_DIR/opt/staticwaves-pod/"
cp -r config "$BUILD_DIR/opt/staticwaves-pod/"
cp -r data "$BUILD_DIR/opt/staticwaves-pod/"

# Copy systemd services
echo "⚙️  Copying systemd services..."
cp systemd/*.service "$BUILD_DIR/usr/lib/systemd/system/"

# Copy DEBIAN control files
echo "📋 Copying package metadata..."
cp debian-pkg/DEBIAN/* "$BUILD_DIR/DEBIAN/"

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 "$BUILD_DIR/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/DEBIAN/prerm"
chmod 755 "$BUILD_DIR/DEBIAN/postrm"
chmod -R 755 "$BUILD_DIR/opt/staticwaves-pod"

# Build .deb package
echo "📦 Building .deb package..."
dpkg-deb --build "$BUILD_DIR" "$DEB_NAME"

# Verify package
echo "✅ Verifying package..."
dpkg-deb --info "$DEB_NAME"

# Sign package (if GPG key available)
if command -v dpkg-sig &> /dev/null; then
    echo "🔐 Signing package..."
    dpkg-sig --sign builder "$DEB_NAME" || echo "⚠️  Signing skipped (no GPG key configured)"
fi

# Cleanup
rm -rf "$BUILD_DIR"

echo ""
echo "✅ Package built successfully: $DEB_NAME"
echo ""
echo "📦 Install with:"
echo "   sudo dpkg -i $DEB_NAME"
echo "   sudo apt --fix-broken install"
echo ""
echo "🗑️  Uninstall with:"
echo "   sudo dpkg -r $PACKAGE_NAME"
echo ""
