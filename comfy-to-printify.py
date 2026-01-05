#!/usr/bin/env python3
"""
Process ComfyUI outputs for Printify
- Find latest ComfyUI output
- Upscale to 4500x5400 (print-ready)
- Remove background
- Upload to Printify
- Create t-shirt and hoodie products
"""

import os
import sys
import glob
import json
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import base64
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

PRINTIFY_API_KEY = os.getenv('PRINTIFY_API_KEY')
PRINTIFY_SHOP_ID = os.getenv('PRINTIFY_SHOP_ID')

if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
    print("❌ Error: PRINTIFY_API_KEY and PRINTIFY_SHOP_ID must be set in .env")
    sys.exit(1)

class PrintifyUploader:
    def __init__(self):
        self.api_key = PRINTIFY_API_KEY
        self.shop_id = PRINTIFY_SHOP_ID
        self.base_url = "https://api.printify.com/v1"

    def upload_image(self, file_path, filename):
        """Upload image to Printify as base64"""
        print(f"📤 Uploading {filename} to Printify...")

        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')

        response = requests.post(
            f"{self.base_url}/uploads/images.json",
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'file_name': filename,
                'contents': base64_data
            }
        )

        if not response.ok:
            print(f"❌ Upload failed: {response.text}")
            raise Exception(f"Failed to upload image: {response.status_code}")

        data = response.json()
        print(f"✓ Image uploaded: {data['id']}")
        return data['id']

    def get_blueprint_variants(self, blueprint_id, provider_id):
        """Get all variants for a blueprint/provider combination"""
        # Correct endpoint format for Printify v1 API
        response = requests.get(
            f"{self.base_url}/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json",
            headers={'Authorization': f'Bearer {self.api_key}'}
        )

        if response.ok:
            data = response.json()
            variants = data.get('variants', [])
            if variants:
                print(f"✓ Found {len(variants)} variants")
                return variants

        print(f"⚠️  API call failed ({response.status_code}), fetching blueprint details...")

        # Fallback: Get blueprint details
        response2 = requests.get(
            f"{self.base_url}/catalog/blueprints/{blueprint_id}.json",
            headers={'Authorization': f'Bearer {self.api_key}'}
        )

        if response2.ok:
            blueprint = response2.json()
            # Find the print provider in the blueprint
            for provider in blueprint.get('print_providers', []):
                if provider['id'] == provider_id:
                    variants = provider.get('variants', [])
                    if variants:
                        print(f"✓ Found {len(variants)} variants from blueprint")
                        return variants

        print(f"❌ Could not fetch variants. Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return []

    def create_product(self, image_id, title, blueprint_id, provider_id, price):
        """Create a product on Printify"""
        print(f"🎨 Creating {title} (blueprint {blueprint_id})...")

        # Get variants from API
        variants_data = self.get_blueprint_variants(blueprint_id, provider_id)

        if not variants_data:
            print(f"❌ Cannot create product without variants")
            return None

        # Use all available variants
        variants = [
            {
                'id': v['id'],
                'price': int(price * 100),
                'is_enabled': True
            }
            for v in variants_data
        ]
        variant_ids = [v['id'] for v in variants]

        print(f"   Using {len(variants)} variants")

        payload = {
            'title': title,
            'description': f'Unique print-ready design created {datetime.now().strftime("%Y-%m-%d")}',
            'blueprint_id': blueprint_id,
            'print_provider_id': provider_id,
            'variants': variants,
            'print_areas': [{
                'variant_ids': variant_ids,
                'placeholders': [{
                    'position': 'front',
                    'images': [{
                        'id': image_id,
                        'x': 0.5,
                        'y': 0.5,
                        'scale': 1,
                        'angle': 0
                    }]
                }]
            }]
        }

        response = requests.post(
            f"{self.base_url}/shops/{self.shop_id}/products.json",
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json=payload
        )

        if not response.ok:
            print(f"❌ Failed to create product: {response.text}")
            return None

        data = response.json()
        print(f"✅ Created product: {data['id']}")
        print(f"   View at: https://printify.com/app/products/{data['id']}")
        return data['id']

def find_latest_comfy_output():
    """Find the most recent ComfyUI output image"""
    output_dir = "/workspace/ComfyUI/output"

    if not os.path.exists(output_dir):
        print(f"❌ ComfyUI output directory not found: {output_dir}")
        return None

    # Find all PNG files
    images = glob.glob(f"{output_dir}/*.png")

    if not images:
        print(f"❌ No images found in {output_dir}")
        return None

    # Sort by modification time, get most recent
    latest = max(images, key=os.path.getmtime)
    print(f"✓ Found latest image: {latest}")
    return latest

def upscale_image(input_path, output_path, target_size=(4500, 5400)):
    """Upscale image to print-ready resolution"""
    print(f"📐 Upscaling to {target_size[0]}x{target_size[1]}...")

    img = Image.open(input_path)
    print(f"   Original size: {img.size}")

    # Upscale with high-quality resampling
    upscaled = img.resize(target_size, Image.Resampling.LANCZOS)

    # Save as high-quality PNG
    upscaled.save(output_path, 'PNG', optimize=False)
    print(f"✓ Upscaled image saved: {output_path}")

    return output_path

def remove_background(input_path, output_path):
    """Remove background from image"""
    print("🎨 Removing background...")

    try:
        # Force CPU to avoid CUDA issues
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        from rembg import remove

        img = Image.open(input_path).convert("RGBA")
        result = remove(img)
        result.save(output_path, 'PNG')

        print(f"✓ Background removed: {output_path}")
        return output_path

    except Exception as e:
        print(f"⚠️  Background removal failed: {e}")
        print("   Using upscaled image without background removal")
        return input_path

def main():
    print("══════════════════════════════════════════════════════")
    print("  ComfyUI → Printify Pipeline")
    print("  Print-Ready: 4500x5400 Resolution")
    print("══════════════════════════════════════════════════════")
    print("")

    # Create output directory
    process_dir = "/workspace/data/print-ready"
    os.makedirs(process_dir, exist_ok=True)

    # Step 1: Find latest ComfyUI output
    latest_image = find_latest_comfy_output()
    if not latest_image:
        sys.exit(1)

    # Step 2: Upscale
    basename = os.path.splitext(os.path.basename(latest_image))[0]
    upscaled_path = f"{process_dir}/{basename}_print_upscaled.png"
    upscale_image(latest_image, upscaled_path)

    # Step 3: Remove background
    transparent_path = f"{process_dir}/{basename}_print_transparent.png"
    final_image = remove_background(upscaled_path, transparent_path)

    print("")
    print("══════════════════════════════════════════════════════")
    print("  Uploading to Printify")
    print("══════════════════════════════════════════════════════")
    print("")

    # Step 4: Upload to Printify and create products
    uploader = PrintifyUploader()

    filename = f"print_ready_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image_id = uploader.upload_image(final_image, filename)

    # Create products
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    products = []

    # T-Shirt (Blueprint 3, Provider 99 - Gildan 5000)
    tshirt_id = uploader.create_product(
        image_id=image_id,
        title=f"Print Ready Design - T-Shirt - {timestamp}",
        blueprint_id=3,
        provider_id=99,
        price=19.99
    )
    if tshirt_id:
        products.append(f"T-Shirt: https://printify.com/app/products/{tshirt_id}")

    # Hoodie (Blueprint 165, Provider 99 - Gildan 18500)
    hoodie_id = uploader.create_product(
        image_id=image_id,
        title=f"Print Ready Design - Hoodie - {timestamp}",
        blueprint_id=165,
        provider_id=99,
        price=34.99
    )
    if hoodie_id:
        products.append(f"Hoodie: https://printify.com/app/products/{hoodie_id}")

    print("")
    print("══════════════════════════════════════════════════════")
    print("✅ COMPLETE!")
    print("══════════════════════════════════════════════════════")
    print("")
    print(f"Files created:")
    print(f"  Upscaled:    {upscaled_path}")
    print(f"  Transparent: {transparent_path}")
    print("")
    print(f"Products created:")
    for product in products:
        print(f"  {product}")
    print("")

if __name__ == '__main__':
    main()
