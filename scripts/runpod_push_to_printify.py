#!/usr/bin/env python3
"""
Push images from ComfyUI output to Printify (runs directly on RunPod).
Excludes any files with 'comfyui' in their names.
"""

import os
import sys
import requests
from pathlib import Path
from typing import List, Optional

# Configuration - can be overridden by environment variables
COMFY_OUTPUT_DIR = os.getenv("COMFYUI_OUTPUT_DIR", "/workspace/ComfyUI/output")
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
PRINTIFY_API_BASE = "https://api.printify.com/v1"

# Supported image extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}


def find_local_images() -> List[Path]:
    """Find all image files in the ComfyUI output directory."""
    print(f"Searching for images in {COMFY_OUTPUT_DIR}...")

    if not os.path.exists(COMFY_OUTPUT_DIR):
        print(f"Error: Directory not found: {COMFY_OUTPUT_DIR}")
        return []

    all_images = []
    for ext in IMAGE_EXTENSIONS:
        all_images.extend(Path(COMFY_OUTPUT_DIR).rglob(f"*{ext}"))

    # Filter out files containing 'comfyui' in their name
    filtered_images = [
        img for img in all_images
        if 'comfyui' not in img.name.lower()
    ]

    print(f"Found {len(all_images)} total images, {len(filtered_images)} after filtering")
    return filtered_images


def upload_to_printify(image_path: Path) -> Optional[dict]:
    """Upload an image to Printify and return the image details."""
    if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
        print("Error: PRINTIFY_API_KEY or PRINTIFY_SHOP_ID not set")
        return None

    url = f"{PRINTIFY_API_BASE}/uploads/images.json"
    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    }

    try:
        with open(image_path, 'rb') as f:
            # Determine mime type from extension
            ext = image_path.suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/png')

            files = {
                'file': (image_path.name, f, mime_type)
            }
            data = {
                'file_name': image_path.name
            }

            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            print(f"✓ Uploaded: {image_path.name} (ID: {result.get('id')})")
            return result
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to upload {image_path.name}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"✗ Error processing {image_path.name}: {e}")
        return None


def main():
    """Main function to orchestrate the image push process."""
    print("=" * 70)
    print("ComfyUI to Printify Image Pusher (RunPod Local)")
    print("=" * 70)

    # Validate environment
    if not PRINTIFY_API_KEY or PRINTIFY_API_KEY == "your-printify-api-key":
        print("\nError: PRINTIFY_API_KEY environment variable not set")
        print("Set it with: export PRINTIFY_API_KEY='your-api-key'")
        sys.exit(1)

    if not PRINTIFY_SHOP_ID or PRINTIFY_SHOP_ID == "your-shop-id":
        print("\nError: PRINTIFY_SHOP_ID environment variable not set")
        print("Set it with: export PRINTIFY_SHOP_ID='your-shop-id'")
        sys.exit(1)

    # Find local images
    images = find_local_images()
    if not images:
        print("\nNo images found to upload.")
        return

    print(f"\nFound {len(images)} images to upload")
    print("\nFiles to upload:")
    for img in images[:10]:  # Show first 10
        print(f"  - {img.name}")
    if len(images) > 10:
        print(f"  ... and {len(images) - 10} more")

    # Confirm before proceeding
    try:
        response = input(f"\nProceed with uploading {len(images)} images to Printify? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    except EOFError:
        # Running in non-interactive mode, proceed automatically
        print("\nRunning in non-interactive mode, proceeding with upload...")

    # Upload images
    print("\nUploading images...")
    uploaded_count = 0
    failed_count = 0

    for image_path in images:
        result = upload_to_printify(image_path)
        if result:
            uploaded_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 70)
    print(f"Upload Summary:")
    print(f"  Successfully uploaded: {uploaded_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
