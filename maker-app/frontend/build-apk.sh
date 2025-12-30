#!/bin/bash

echo "========================================"
echo "StaticWaves Maker - APK Build Script"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install JDK 17+"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"
echo "✓ Java version: $(java --version | head -n 1)"
echo ""

# Step 1: Install dependencies
echo "[1/5] Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Step 2: Build Next.js app
echo "[2/5] Building Next.js app..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✓ Next.js app built"
echo ""

# Step 3: Check if Capacitor is initialized
if [ ! -d "android" ]; then
    echo "[3/5] Initializing Capacitor..."
    npx cap init "StaticWaves Maker" "com.staticwaves.maker" --web-dir=out
    npx cap add android
    echo "✓ Capacitor initialized"
else
    echo "[3/5] Capacitor already initialized"
fi
echo ""

# Step 4: Sync web assets to Android
echo "[4/5] Syncing web assets to Android..."
npx cap sync android
if [ $? -ne 0 ]; then
    echo "❌ Sync failed"
    exit 1
fi
echo "✓ Assets synced"
echo ""

# Step 5: Open in Android Studio
echo "[5/5] Opening Android Studio..."
echo ""
echo "========================================"
echo "Next Steps in Android Studio:"
echo "========================================"
echo "1. Wait for Gradle sync to complete"
echo "2. Build → Generate Signed Bundle/APK"
echo "3. Choose APK"
echo "4. Create/select keystore"
echo "5. Build release APK"
echo ""
echo "APK will be at:"
echo "android/app/build/outputs/apk/release/app-release.apk"
echo "========================================"
echo ""

npx cap open android

echo ""
echo "✓ Build script complete!"
echo "Follow the instructions in Android Studio to generate the APK."
