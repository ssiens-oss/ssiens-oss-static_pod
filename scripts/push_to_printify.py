#!/usr/bin/env python3
"""
Push images from ComfyUI output on RunPod to Printify.
Excludes any files with 'comfyui' in their names.
"""

import os
import sys
import subprocess
import tempfile
import requests
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
RUNPOD_SSH_HOST = "tleofuk3ify4lk-64410e97@ssh.runpod.io"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
REMOTE_COMFY_OUTPUT = "/workspace/ComfyUI/output"
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
PRINTIFY_API_BASE = "https://api.printify.com/v1"

# Supported image extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}


def run_ssh_command(command: str) -> str:
    """Execute a command on the RunPod instance via SSH."""
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY_PATH,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        RUNPOD_SSH_HOST,
        command
    ]

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"SSH command failed: {e.stderr}")
        raise


def list_remote_images() -> List[str]:
    """List all image files in the remote ComfyUI output directory."""
    print(f"Listing images in {REMOTE_COMFY_OUTPUT}...")

    # Find all image files
    extensions = ' -o '.join([f'-name "*.{ext[1:]}"' for ext in IMAGE_EXTENSIONS])
    find_cmd = f"find {REMOTE_COMFY_OUTPUT} -type f \\( {extensions} \\)"

    try:
        output = run_ssh_command(find_cmd)
        files = [f.strip() for f in output.split('\n') if f.strip()]

        # Filter out files containing 'comfyui' in their name
        filtered_files = [
            f for f in files
            if 'comfyui' not in os.path.basename(f).lower()
        ]

        print(f"Found {len(files)} total images, {len(filtered_files)} after filtering")
        return filtered_files
    except Exception as e:
        print(f"Error listing remote images: {e}")
        return []


def download_image(remote_path: str, local_dir: str) -> Optional[str]:
    """Download an image from RunPod to local directory."""
    filename = os.path.basename(remote_path)
    local_path = os.path.join(local_dir, filename)

    scp_cmd = [
        "scp",
        "-i", SSH_KEY_PATH,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{RUNPOD_SSH_HOST}:{remote_path}",
        local_path
    ]

    try:
        subprocess.run(scp_cmd, check=True, capture_output=True)
        print(f"Downloaded: {filename}")
        return local_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {filename}: {e.stderr.decode()}")
        return None


def upload_to_printify(image_path: str, filename: str) -> Optional[dict]:
    """Upload an image to Printify and return the image details."""
    if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
        print("Error: PRINTIFY_API_KEY or PRINTIFY_SHOP_ID not set in .env")
        return None

    url = f"{PRINTIFY_API_BASE}/uploads/images.json"
    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    }

    try:
        with open(image_path, 'rb') as f:
            files = {
                'file': (filename, f, 'image/png')
            }
            data = {
                'file_name': filename
            }

            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            print(f"Uploaded to Printify: {filename} (ID: {result.get('id')})")
            return result
    except requests.exceptions.RequestException as e:
        print(f"Failed to upload {filename} to Printify: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


def main():
    """Main function to orchestrate the image push process."""
    print("=" * 60)
    print("ComfyUI to Printify Image Pusher")
    print("=" * 60)

    # Validate environment
    if not PRINTIFY_API_KEY or PRINTIFY_API_KEY == "your-printify-api-key":
        print("\nError: Please set PRINTIFY_API_KEY in your .env file")
        sys.exit(1)

    if not PRINTIFY_SHOP_ID or PRINTIFY_SHOP_ID == "your-shop-id":
        print("\nError: Please set PRINTIFY_SHOP_ID in your .env file")
        sys.exit(1)

    # Check SSH key exists
    if not os.path.exists(SSH_KEY_PATH):
        print(f"\nError: SSH key not found at {SSH_KEY_PATH}")
        sys.exit(1)

    # List remote images
    remote_images = list_remote_images()
    if not remote_images:
        print("\nNo images found to upload.")
        return

    print(f"\nFound {len(remote_images)} images to upload")
    print("\nFiles to upload:")
    for img in remote_images:
        print(f"  - {os.path.basename(img)}")

    # Confirm before proceeding
    response = input(f"\nProceed with uploading {len(remote_images)} images to Printify? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # Create temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nDownloading images to {temp_dir}...")

        uploaded_count = 0
        failed_count = 0

        for remote_path in remote_images:
            filename = os.path.basename(remote_path)
            print(f"\nProcessing: {filename}")

            # Download image
            local_path = download_image(remote_path, temp_dir)
            if not local_path:
                failed_count += 1
                continue

            # Upload to Printify
            result = upload_to_printify(local_path, filename)
            if result:
                uploaded_count += 1
            else:
                failed_count += 1

    print("\n" + "=" * 60)
    print(f"Upload Summary:")
    print(f"  Successfully uploaded: {uploaded_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
