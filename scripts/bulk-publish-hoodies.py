#!/usr/bin/env python3
"""
Bulk publish all ComfyUI output images to Printify as hoodies
"""

import os
import sys
import requests
import time
import base64
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
COMFYUI_OUTPUT = Path(os.getenv("COMFYUI_OUTPUT_DIR", "./ComfyUI/output"))

# Printify API endpoints
PRINTIFY_BASE_URL = "https://api.printify.com/v1"
UPLOAD_URL = f"{PRINTIFY_BASE_URL}/uploads/images.json"
PRODUCTS_URL = f"{PRINTIFY_BASE_URL}/shops/{PRINTIFY_SHOP_ID}/products.json"

# Hoodie blueprint and variant IDs
BLUEPRINT_ID = 12  # Unisex Heavy Blend Hoodie (Gildan 18500)
PRINT_PROVIDER_ID = 99  # Monster Digital


def upload_image_to_printify(image_path: Path) -> dict:
    """Upload an image to Printify and return the image info"""

    print(f"📤 Uploading: {image_path.name}")

    # Read and encode image as base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        'file_name': image_path.name,
        'contents': image_base64
    }

    response = requests.post(UPLOAD_URL, headers=headers, json=data)

    if response.status_code == 200:
        image_info = response.json()
        print(f"   ✅ Uploaded: {image_info['id']}")
        return image_info
    else:
        print(f"   ❌ Upload failed: {response.status_code} - {response.text}")
        return None


def create_hoodie_product(image_id: str, design_name: str) -> dict:
    """Create a hoodie product on Printify with the uploaded image"""

    print(f"🎽 Creating hoodie: {design_name}")

    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    # Product data - hoodie with all sizes and colors
    product_data = {
        "title": f"{design_name} - Hoodie",
        "description": f"Premium quality hoodie featuring {design_name} design. Soft, comfortable, and stylish.",
        "blueprint_id": BLUEPRINT_ID,
        "print_provider_id": PRINT_PROVIDER_ID,
        "variants": [
            # Black hoodies - all sizes
            {"id": 18099, "price": 3499, "is_enabled": True},  # Black / XS
            {"id": 18100, "price": 3499, "is_enabled": True},  # Black / S
            {"id": 18101, "price": 3499, "is_enabled": True},  # Black / M
            {"id": 18102, "price": 3499, "is_enabled": True},  # Black / L
            {"id": 18103, "price": 3499, "is_enabled": True},  # Black / XL
            {"id": 18104, "price": 3499, "is_enabled": True},  # Black / 2XL
            {"id": 18105, "price": 3499, "is_enabled": True},  # Black / 3XL
            {"id": 18106, "price": 3499, "is_enabled": True},  # Black / 4XL
        ],
        "print_areas": [
            {
                "variant_ids": [18099, 18100, 18101, 18102, 18103, 18104, 18105, 18106],
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

    response = requests.post(PRODUCTS_URL, headers=headers, json=product_data)

    if response.status_code == 200:
        product = response.json()
        print(f"   ✅ Product created: {product['id']}")
        return product
    else:
        print(f"   ❌ Product creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def publish_product(product_id: str):
    """Publish a product to make it available for sale"""

    print(f"🚀 Publishing product: {product_id}")

    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    publish_url = f"{PRINTIFY_BASE_URL}/shops/{PRINTIFY_SHOP_ID}/products/{product_id}/publish.json"

    publish_data = {
        "title": True,
        "description": True,
        "images": True,
        "variants": True,
        "tags": True
    }

    response = requests.post(publish_url, headers=headers, json=publish_data)

    if response.status_code == 200:
        print(f"   ✅ Product published successfully!")
        return True
    else:
        print(f"   ⚠️  Publish status: {response.status_code}")
        return False


def main():
    """Main function to bulk publish all images"""

    print("🎨 Printify Bulk Hoodie Publisher")
    print("=" * 50)

    # Check configuration
    if not PRINTIFY_API_KEY:
        print("❌ PRINTIFY_API_KEY not set in environment")
        sys.exit(1)

    if not PRINTIFY_SHOP_ID:
        print("❌ PRINTIFY_SHOP_ID not set in environment")
        sys.exit(1)

    print(f"✅ Printify configured")
    print(f"📁 ComfyUI Output: {COMFYUI_OUTPUT}")
    print(f"🏪 Shop ID: {PRINTIFY_SHOP_ID}")
    print()

    # Find all images
    image_files = list(COMFYUI_OUTPUT.glob("*.png"))
    image_files.extend(COMFYUI_OUTPUT.glob("*.jpg"))
    image_files.extend(COMFYUI_OUTPUT.glob("*.jpeg"))

    if not image_files:
        print("⚠️  No images found in ComfyUI output directory")
        sys.exit(0)

    print(f"📸 Found {len(image_files)} images to publish")
    print()

    # Process each image
    success_count = 0
    failed_count = 0

    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {image_path.name}")
        print("-" * 50)

        try:
            # Upload image
            image_info = upload_image_to_printify(image_path)
            if not image_info:
                failed_count += 1
                continue

            time.sleep(1)  # Rate limiting

            # Create product
            design_name = image_path.stem.replace('_', ' ').title()
            product = create_hoodie_product(image_info['id'], design_name)
            if not product:
                failed_count += 1
                continue

            time.sleep(1)  # Rate limiting

            # Publish product
            if publish_product(product['id']):
                success_count += 1
                print(f"   🎉 Success! View at: https://printify.com/app/products/{product['id']}")
            else:
                failed_count += 1

            time.sleep(2)  # Rate limiting between products

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            failed_count += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 Publishing Summary")
    print("=" * 50)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📦 Total: {len(image_files)}")
    print()
    print(f"🌐 View your products: https://printify.com/app/store/products")


if __name__ == "__main__":
    main()
