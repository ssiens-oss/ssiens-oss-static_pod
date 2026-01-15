#!/usr/bin/env python3
"""
Diagnostic script to check gateway image discovery
"""
from pathlib import Path
from dotenv import load_dotenv
import os
import re

# Load environment
load_dotenv('../.env')

# Get image directory
image_dir = Path(os.getenv('POD_IMAGE_DIR', '/home/static/ssiens-oss-static_pod/gateway/images'))

print("🔍 Gateway Image Discovery Diagnostic")
print("=" * 60)
print(f"\n📁 Image Directory: {image_dir}")
print(f"   Exists: {image_dir.exists()}")
print(f"   Readable: {os.access(image_dir, os.R_OK) if image_dir.exists() else 'N/A'}")

if not image_dir.exists():
    print(f"\n❌ Directory does not exist!")
    print(f"   Please create it: mkdir -p {image_dir}")
    exit(1)

# List all PNG files
png_files = list(image_dir.glob("*.png"))
print(f"\n🖼️  PNG files found: {len(png_files)}")

if not png_files:
    print("   ❌ No PNG files found in directory")
    print(f"   Make sure images are saved to: {image_dir}")
    exit(1)

# Check each image
print("\n📋 Image Details:")
for img_file in png_files:
    img_id = img_file.stem
    size = img_file.stat().st_size

    # Validate ID format (same as gateway)
    is_valid = bool(re.match(r'^[a-zA-Z0-9_-]+$', img_id))

    print(f"\n   File: {img_file.name}")
    print(f"   ID: {img_id}")
    print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
    print(f"   Valid ID: {'✅ Yes' if is_valid else '❌ No'}")

    if not is_valid:
        print(f"   ⚠️  Invalid image ID format - gateway will skip this file")

print("\n" + "=" * 60)
print("\n✅ Diagnosis complete!")
print("\n📋 Next steps:")
print("   1. Make sure gateway is running: ./start.sh")
print("   2. Check gateway startup shows correct directory")
print("   3. Open gateway: http://localhost:8099")
print("   4. Refresh the page if needed")
