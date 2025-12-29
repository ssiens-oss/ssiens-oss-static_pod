#!/usr/bin/env python3
"""
Printify Worker - Handles product upload and creation
"""
import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import setup_logger
from engine.retry import api_retry

log = setup_logger("PRINTIFY", "logs/printify_worker.log")

# API Configuration
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
API_BASE = "https://api.printify.com/v1"

HEADERS = {
    "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    "Content-Type": "application/json"
}

class PrintifyWorker:
    """Handles Printify product creation and uploads"""

    def __init__(self):
        self.queue_dir = Path("queues/done")
        self.failed_dir = Path("queues/failed")
        self.published_dir = Path("queues/published")

        # Ensure directories exist
        for dir in [self.queue_dir, self.failed_dir, self.published_dir]:
            dir.mkdir(parents=True, exist_ok=True)

    @api_retry
    def upload_image(self, image_path: Path) -> str:
        """
        Upload image to Printify

        Args:
            image_path: Path to image file

        Returns:
            Image ID from Printify
        """
        log.info(f"Uploading image: {image_path.name}")

        # Read image and convert to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()

        # Upload to Printify
        response = requests.post(
            f"{API_BASE}/uploads/images.json",
            headers=HEADERS,
            json={
                "file_name": image_path.name,
                "contents": image_data
            },
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        image_id = result["id"]

        log.info(f"✅ Image uploaded: {image_id}")
        return image_id

    @api_retry
    def create_product(
        self,
        image_id: str,
        title: str = "Custom POD Product",
        blueprint_id: int = 6,
        print_provider_id: int = 1
    ) -> Dict[str, Any]:
        """
        Create a product on Printify

        Args:
            image_id: Printify image ID
            title: Product title
            blueprint_id: Blueprint ID (6 = hoodie)
            print_provider_id: Print provider ID

        Returns:
            Product data
        """
        log.info(f"Creating product: {title}")

        # Get blueprint and variants
        product_data = {
            "title": title,
            "description": "Custom printed product",
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "variants": [
                {
                    "id": 45740,  # Size M variant
                    "price": 2999,  # $29.99 in cents
                    "is_enabled": True
                }
            ],
            "print_areas": [
                {
                    "variant_ids": [45740],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": image_id,
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1.0,
                                    "angle": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            f"{API_BASE}/shops/{PRINTIFY_SHOP_ID}/products.json",
            headers=HEADERS,
            json=product_data,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        log.info(f"✅ Product created: {result['id']}")

        return result

    def process_queue(self):
        """Process all images in the done queue"""
        images = list(self.queue_dir.glob("*.png")) + list(self.queue_dir.glob("*.jpg"))

        if not images:
            log.info("No images to process")
            return

        log.info(f"Processing {len(images)} images")

        for image_path in images:
            try:
                # Upload image
                image_id = self.upload_image(image_path)

                # Create product
                product = self.create_product(
                    image_id=image_id,
                    title=f"Custom Design - {image_path.stem}"
                )

                # Save product metadata
                metadata_path = self.published_dir / f"{image_path.stem}_product.json"
                metadata_path.write_text(json.dumps(product, indent=2))

                # Move image to published
                published_path = self.published_dir / image_path.name
                image_path.rename(published_path)

                log.info(f"✅ Completed: {image_path.name}")

            except Exception as e:
                log.error(f"❌ Failed to process {image_path.name}: {e}")

                # Move to failed directory
                failed_path = self.failed_dir / image_path.name
                image_path.rename(failed_path)

def main():
    """Main worker loop"""
    log.info("🚀 Printify Worker started")

    if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
        log.error("Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID")
        return

    worker = PrintifyWorker()
    worker.process_queue()

    log.info("✅ Printify Worker completed")

if __name__ == "__main__":
    main()
