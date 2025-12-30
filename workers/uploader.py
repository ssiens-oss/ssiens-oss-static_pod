#!/usr/bin/env python3
"""
Printify Uploader Worker
Handles image uploads and product creation on Printify
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime

# Printify API configuration
PRINTIFY_API_KEY = os.environ.get("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID")
PRINTIFY_API_BASE = "https://api.printify.com/v1"

class PrintifyUploader:
    """Printify API client"""

    def __init__(self, api_key=None, shop_id=None):
        self.api_key = api_key or PRINTIFY_API_KEY
        self.shop_id = shop_id or PRINTIFY_SHOP_ID

        if not self.api_key:
            raise ValueError("PRINTIFY_API_KEY not set")
        if not self.shop_id:
            raise ValueError("PRINTIFY_SHOP_ID not set")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def upload_image(self, image_path, file_name=None):
        """
        Upload image to Printify

        Args:
            image_path: Path to image file
            file_name: Optional custom file name

        Returns:
            str: Image ID
        """

        if file_name is None:
            file_name = Path(image_path).name

        # Read image as base64
        import base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        # Upload to Printify
        url = f"{PRINTIFY_API_BASE}/uploads/images.json"

        payload = {
            "file_name": file_name,
            "contents": image_data
        }

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Image upload failed: {response.text}")

        result = response.json()
        image_id = result["id"]

        print(f"✅ Uploaded image: {file_name} → {image_id}")

        return image_id

    def create_product(self, product_data):
        """
        Create product on Printify

        Args:
            product_data: Product configuration

        Returns:
            dict: Created product info
        """

        url = f"{PRINTIFY_API_BASE}/shops/{self.shop_id}/products.json"

        # Build Printify product payload
        payload = {
            "title": product_data["title"],
            "description": product_data.get("description", ""),
            "blueprint_id": self._get_blueprint_id(product_data.get("type", "hoodie")),
            "print_provider_id": 99,  # Default print provider
            "variants": self._build_variants(product_data),
            "print_areas": self._build_print_areas(product_data)
        }

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Product creation failed: {response.text}")

        result = response.json()

        print(f"✅ Created product: {product_data['title']} → {result['id']}")

        return result

    def publish_product(self, product_id, publish=True):
        """
        Publish product to connected sales channel

        Args:
            product_id: Printify product ID
            publish: Whether to publish (True) or unpublish (False)
        """

        url = f"{PRINTIFY_API_BASE}/shops/{self.shop_id}/products/{product_id}/publish.json"

        payload = {
            "title": publish,
            "description": publish,
            "images": publish,
            "variants": publish,
            "tags": publish
        }

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Product publish failed: {response.text}")

        print(f"✅ Published product: {product_id}")

        return response.json()

    def _get_blueprint_id(self, product_type):
        """Map product type to Printify blueprint ID"""
        blueprints = {
            "hoodie": 384,
            "tee": 6,
            "poster": 19,
            "mug": 91,
            "tank": 3,
            "sweatshirt": 377
        }
        return blueprints.get(product_type, 384)

    def _build_variants(self, product_data):
        """Build product variants with pricing"""
        price = int(product_data.get("price", 49.99) * 100)  # Convert to cents

        # Basic variant structure
        # In production, expand with sizes, colors, etc.
        return [
            {
                "id": 17390,  # Variant ID for hoodie - adjust per blueprint
                "price": price,
                "is_enabled": True
            }
        ]

    def _build_print_areas(self, product_data):
        """Build print areas configuration"""

        # Assume we have uploaded design image
        image_id = product_data.get("image_id", "")

        return [
            {
                "variant_ids": [17390],
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

def upload_design(design_path, product_data):
    """
    Complete upload workflow

    Args:
        design_path: Path to design image
        product_data: Product metadata

    Returns:
        dict: Upload result with IDs
    """

    uploader = PrintifyUploader()

    # Upload design image
    image_id = uploader.upload_image(design_path)

    # Add image ID to product data
    product_data["image_id"] = image_id

    # Create product
    product = uploader.create_product(product_data)

    # Publish to sales channel
    uploader.publish_product(product["id"])

    return {
        "image_id": image_id,
        "product_id": product["id"],
        "printify_url": f"https://printify.com/app/products/{product['id']}"
    }

if __name__ == "__main__":
    # CLI usage
    import argparse

    parser = argparse.ArgumentParser(description="Upload design to Printify")
    parser.add_argument("design", help="Path to design image")
    parser.add_argument("--title", required=True, help="Product title")
    parser.add_argument("--type", default="hoodie", help="Product type")
    parser.add_argument("--price", type=float, default=49.99, help="Product price")
    parser.add_argument("--description", default="", help="Product description")

    args = parser.parse_args()

    design_path = Path(args.design)

    if not design_path.exists():
        print(f"❌ Design not found: {design_path}")
        sys.exit(1)

    product_data = {
        "title": args.title,
        "type": args.type,
        "price": args.price,
        "description": args.description
    }

    try:
        result = upload_design(design_path, product_data)
        print(f"\n✅ Upload complete:")
        print(f"  Product ID: {result['product_id']}")
        print(f"  URL: {result['printify_url']}")
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        sys.exit(1)
