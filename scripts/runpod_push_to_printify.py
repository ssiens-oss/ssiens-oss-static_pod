#!/usr/bin/env python3
"""
Push images from ComfyUI output to Printify (runs directly on RunPod).
Excludes any files with 'comfyui' in their names.
"""

import os
import sys
import base64
import requests
from pathlib import Path
from typing import List, Optional

# Configuration - can be overridden by environment variables
COMFY_OUTPUT_DIR = os.getenv("COMFYUI_OUTPUT_DIR", "/workspace/ComfyUI/output")
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
PRINTIFY_API_BASE = "https://api.printify.com/v1"
AUTO_PUBLISH = os.getenv("AUTO_PUBLISH", "true").lower() == "true"
DEFAULT_TSHIRT_PRICE = float(os.getenv("DEFAULT_TSHIRT_PRICE", "19.99"))
DEFAULT_HOODIE_PRICE = float(os.getenv("DEFAULT_HOODIE_PRICE", "34.99"))

# Printify Blueprint IDs (product types)
# T-Shirt (Gildan 64000) - Blueprint 5
# Hoodie (Gildan 18500) - Blueprint 6
TSHIRT_BLUEPRINT_ID = 5
HOODIE_BLUEPRINT_ID = 6

# Print Provider IDs - using Printify Choice for best TikTok compatibility
PRINT_PROVIDER_ID = 99  # Printify Choice - automatically selects best provider

# Supported image extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}

# Cache for variant IDs to avoid repeated API calls
_variant_cache = {}


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
        "Content-Type": "application/json"
    }

    try:
        # Read and base64 encode the image
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        # Prepare JSON payload
        payload = {
            "file_name": image_path.name,
            "contents": base64_image
        }

        response = requests.post(url, headers=headers, json=payload)
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


def create_product(image_id: str, image_name: str, blueprint_id: int, price: float, product_type: str) -> Optional[dict]:
    """Create a product on Printify using the uploaded image."""
    url = f"{PRINTIFY_API_BASE}/shops/{PRINTIFY_SHOP_ID}/products.json"
    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    # Generate product title from image name
    title = image_name.replace('_', ' ').replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
    title = f"{title} - {product_type}"

    # Product payload
    payload = {
        "title": title,
        "description": f"Custom {product_type} with unique design",
        "blueprint_id": blueprint_id,
        "print_provider_id": PRINT_PROVIDER_ID,
        "variants": [
            {"id": variant_id, "price": int(price * 100), "is_enabled": True}
            for variant_id in get_variant_ids(blueprint_id)
        ],
        "print_areas": [
            {
                "variant_ids": get_variant_ids(blueprint_id),
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1,
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        product_id = result.get('id')

        # Publish product if AUTO_PUBLISH is enabled
        if AUTO_PUBLISH and product_id:
            publish_product(product_id)

        return result
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to create {product_type}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Response: {e.response.text}")
        return None


def get_variant_ids(blueprint_id: int) -> List[int]:
    """Fetch actual variant IDs from Printify API for the blueprint and print provider."""
    # Check cache first
    cache_key = f"{blueprint_id}_{PRINT_PROVIDER_ID}"
    if cache_key in _variant_cache:
        return _variant_cache[cache_key]

    url = f"{PRINTIFY_API_BASE}/catalog/blueprints/{blueprint_id}/print_providers/{PRINT_PROVIDER_ID}/variants.json"
    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # SIMPLE FIX: Just use first 20 variants to stay well under 100 limit
        # This ensures we always stay under the limit
        all_variants = data.get('variants', [])
        variant_ids = [v['id'] for v in all_variants[:20]]

        # Cache the result
        _variant_cache[cache_key] = variant_ids

        print(f"  → Using {len(variant_ids)} variants (from {len(all_variants)} available)")
        return variant_ids
    except Exception as e:
        print(f"  ⚠ Warning: Could not fetch variants for blueprint {blueprint_id}: {e}")
        return []


def publish_product(product_id: str) -> bool:
    """Publish a product to make it available for sale."""
    url = f"{PRINTIFY_API_BASE}/shops/{PRINTIFY_SHOP_ID}/products/{product_id}/publish.json"
    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"title": True, "description": True, "images": True, "variants": True, "tags": True}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"    ✓ Published product")
        return True
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Failed to publish: {e}")
        return False


def main():
    """Main function to orchestrate the image push process."""
    print("=" * 70)
    print("ComfyUI to Printify Product Creator (RunPod Local)")
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

    # Debug output
    print(f"\nCredentials loaded:")
    print(f"  API Key: {PRINTIFY_API_KEY[:20]}... (length: {len(PRINTIFY_API_KEY)})")
    print(f"  Shop ID: {PRINTIFY_SHOP_ID}")

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

    # Upload images and create products
    print("\nProcessing images...")
    uploaded_count = 0
    failed_upload_count = 0
    tshirts_created = 0
    hoodies_created = 0
    failed_product_count = 0

    for image_path in images:
        print(f"\n📷 {image_path.name}")

        # Step 1: Upload image
        upload_result = upload_to_printify(image_path)
        if not upload_result:
            failed_upload_count += 1
            continue

        uploaded_count += 1
        image_id = upload_result.get('id')

        # Step 2: Create T-Shirt
        print(f"  Creating T-Shirt...")
        tshirt_result = create_product(
            image_id,
            image_path.name,
            TSHIRT_BLUEPRINT_ID,
            DEFAULT_TSHIRT_PRICE,
            "T-Shirt"
        )
        if tshirt_result:
            tshirts_created += 1
            print(f"  ✓ T-Shirt created (ID: {tshirt_result.get('id')})")
        else:
            failed_product_count += 1

        # Step 3: Create Hoodie
        print(f"  Creating Hoodie...")
        hoodie_result = create_product(
            image_id,
            image_path.name,
            HOODIE_BLUEPRINT_ID,
            DEFAULT_HOODIE_PRICE,
            "Hoodie"
        )
        if hoodie_result:
            hoodies_created += 1
            print(f"  ✓ Hoodie created (ID: {hoodie_result.get('id')})")
        else:
            failed_product_count += 1

    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  Images uploaded: {uploaded_count}")
    print(f"  Failed uploads: {failed_upload_count}")
    print(f"  T-Shirts created: {tshirts_created}")
    print(f"  Hoodies created: {hoodies_created}")
    print(f"  Failed product creations: {failed_product_count}")
    print(f"  Auto-publish: {'ENABLED' if AUTO_PUBLISH else 'DISABLED'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
