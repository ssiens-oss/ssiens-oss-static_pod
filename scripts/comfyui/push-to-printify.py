#!/usr/bin/env python3
"""
Auto-Publish to Printify
Reads images from printify_ready/ and creates hoodie + tee products
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List

# Configuration
API_BASE = "https://api.printify.com/v1"
IMG_DIR = os.getenv("PRINTIFY_OUTPUT_DIR", "/workspace/printify_ready")
API_TOKEN = os.getenv("PRINTIFY_API_TOKEN")
STORE_ID = os.getenv("PRINTIFY_STORE_ID")

# Product blueprints
BLUEPRINTS = {
    "hoodie": {
        "blueprint_id": 6,  # Gildan 18500 Heavy Blend Hoodie
        "print_provider_id": 1,
        "name_suffix": "Hoodie"
    },
    "tee": {
        "blueprint_id": 3,  # Gildan 5000 T-shirt
        "print_provider_id": 1,
        "name_suffix": "Tee"
    }
}

def check_config():
    """Validate required environment variables"""
    if not API_TOKEN:
        print("❌ PRINTIFY_API_TOKEN not set")
        print("Get token: Printify → Account → Connections → API")
        sys.exit(1)

    if not STORE_ID:
        print("❌ PRINTIFY_STORE_ID not set")
        print("Find ID: Printify → My Stores")
        sys.exit(1)

    if not os.path.exists(IMG_DIR):
        print(f"❌ Image directory not found: {IMG_DIR}")
        sys.exit(1)

def get_headers() -> Dict[str, str]:
    """Get API headers with auth"""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

def upload_image(image_path: str) -> str:
    """Upload image to Printify and return image ID"""
    print(f"📤 Uploading: {os.path.basename(image_path)}")

    with open(image_path, "rb") as f:
        response = requests.post(
            f"{API_BASE}/uploads/images.json",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            files={"file": (os.path.basename(image_path), f, "image/png")}
        )

    response.raise_for_status()
    image_id = response.json()["id"]
    print(f"✅ Uploaded with ID: {image_id}")
    return image_id

def create_product(title: str, image_id: str, product_type: str) -> str:
    """Create a product on Printify"""
    blueprint_config = BLUEPRINTS[product_type]
    full_title = f"{title} - {blueprint_config['name_suffix']}"

    print(f"🛍️  Creating: {full_title}")

    payload = {
        "title": full_title,
        "description": f"StaticWaves {blueprint_config['name_suffix']} - Cyberpunk streetwear design",
        "blueprint_id": blueprint_config["blueprint_id"],
        "print_provider_id": blueprint_config["print_provider_id"],
        "variants": [],
        "print_areas": [{
            "variant_ids": [],
            "placeholders": [{
                "position": "front",
                "images": [{
                    "id": image_id,
                    "x": 0.5,
                    "y": 0.5,
                    "scale": 1,
                    "angle": 0
                }]
            }]
        }]
    }

    response = requests.post(
        f"{API_BASE}/shops/{STORE_ID}/products.json",
        headers=get_headers(),
        data=json.dumps(payload)
    )

    response.raise_for_status()
    product_id = response.json()["id"]
    print(f"✅ Created product ID: {product_id}")
    return product_id

def publish_product(product_id: str):
    """Publish a product to make it live"""
    response = requests.post(
        f"{API_BASE}/shops/{STORE_ID}/products/{product_id}/publish.json",
        headers=get_headers(),
        data=json.dumps({"title": True, "description": True, "images": True, "variants": True, "tags": True})
    )

    response.raise_for_status()
    print(f"🚀 Published product: {product_id}")

def process_images():
    """Main processing loop"""
    images = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(".png")]

    if not images:
        print(f"⚠️  No PNG images found in {IMG_DIR}")
        return

    print(f"📦 Found {len(images)} images to process")
    print("")

    for image_file in images:
        try:
            image_path = os.path.join(IMG_DIR, image_file)

            # Generate title from filename
            title = image_file.replace(".png", "").replace("_", " ").title()

            print(f"{'='*60}")
            print(f"Processing: {image_file}")
            print(f"{'='*60}")

            # Upload image once
            image_id = upload_image(image_path)

            # Create hoodie
            hoodie_id = create_product(title, image_id, "hoodie")
            publish_product(hoodie_id)

            # Create tee
            tee_id = create_product(title, image_id, "tee")
            publish_product(tee_id)

            print(f"✅ Completed: {title}")
            print("")

        except requests.HTTPError as e:
            print(f"❌ API Error: {e}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"❌ Error processing {image_file}: {e}")

def main():
    print("╔════════════════════════════════════════════════════╗")
    print("║  StaticWaves → Printify Auto-Publisher           ║")
    print("╚════════════════════════════════════════════════════╝")
    print("")

    check_config()

    print(f"📁 Image directory: {IMG_DIR}")
    print(f"🏪 Store ID: {STORE_ID}")
    print("")

    process_images()

    print("")
    print("╔════════════════════════════════════════════════════╗")
    print("║  ✅ Publishing Complete                           ║")
    print("╚════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
