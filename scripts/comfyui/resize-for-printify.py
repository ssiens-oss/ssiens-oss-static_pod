#!/usr/bin/env python3
"""
Auto-Resize ComfyUI Output for Printify
Watches ComfyUI output folder and auto-resizes to 4500×5400 PNG
"""

import os
import time
import subprocess
from pathlib import Path

# Configuration
SRC_DIR = os.getenv("COMFYUI_OUTPUT_DIR", "/workspace/ComfyUI/output")
DST_DIR = os.getenv("PRINTIFY_OUTPUT_DIR", "/workspace/printify_ready")
TARGET_WIDTH = 4500
TARGET_HEIGHT = 5400
WATCH_INTERVAL = 2  # seconds

def ensure_imagemagick():
    """Check if ImageMagick is installed"""
    try:
        subprocess.run(["convert", "-version"], capture_output=True, check=True)
        print("✅ ImageMagick detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ImageMagick not found. Install with: apt install -y imagemagick")
        return False

def resize_image(src_path: str, dst_path: str):
    """Resize image to Printify specs using ImageMagick"""
    try:
        subprocess.run([
            "convert",
            src_path,
            "-background", "none",
            "-gravity", "center",
            "-resize", f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
            "-extent", f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
            dst_path
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Resize failed for {src_path}: {e.stderr.decode()}")
        return False

def main():
    """Main watch loop"""
    if not ensure_imagemagick():
        return

    # Create destination directory
    Path(DST_DIR).mkdir(parents=True, exist_ok=True)

    print(f"📁 Watching: {SRC_DIR}")
    print(f"📁 Output: {DST_DIR}")
    print(f"📐 Target: {TARGET_WIDTH}×{TARGET_HEIGHT}")
    print("🔄 Starting watch loop...\n")

    seen = set()

    while True:
        try:
            if not os.path.exists(SRC_DIR):
                print(f"⚠️  Source directory not found: {SRC_DIR}")
                time.sleep(WATCH_INTERVAL)
                continue

            for filename in os.listdir(SRC_DIR):
                if not filename.lower().endswith(".png"):
                    continue

                src_path = os.path.join(SRC_DIR, filename)
                dst_path = os.path.join(DST_DIR, filename)

                # Skip if already processed
                if src_path in seen:
                    continue

                # Skip if file is still being written (check size twice)
                size1 = os.path.getsize(src_path)
                time.sleep(0.5)
                size2 = os.path.getsize(src_path)
                if size1 != size2:
                    continue  # File still being written

                print(f"🖼️  Processing: {filename}")
                if resize_image(src_path, dst_path):
                    print(f"✅ Resized: {filename} → {DST_DIR}")
                    seen.add(src_path)
                else:
                    print(f"❌ Failed: {filename}")

            time.sleep(WATCH_INTERVAL)

        except KeyboardInterrupt:
            print("\n👋 Stopping resize watcher...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(WATCH_INTERVAL)

if __name__ == "__main__":
    main()
