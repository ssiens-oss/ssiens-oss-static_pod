#!/usr/bin/env python3
"""
Shopify Worker - Publishes products to Shopify store
"""
import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import setup_logger
from engine.retry import api_retry

log = setup_logger("SHOPIFY", "logs/shopify_worker.log")

# Shopify Configuration
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN")
API_VERSION = "2024-01"

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_TOKEN,
    "Content-Type": "application/json"
}

class ShopifyWorker:
    """Handles Shopify product publishing"""

    def __init__(self):
        self.queue_dir = Path("queues/published")
        self.base_url = f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{API_VERSION}"

    @api_retry
    def create_product(
        self,
        title: str,
        description: str,
        price: float,
        image_path: Path = None
    ) -> Dict[str, Any]:
        """
        Create product on Shopify

        Args:
            title: Product title
            description: Product description
            price: Product price
            image_path: Path to product image

        Returns:
            Created product data
        """
        log.info(f"Creating Shopify product: {title}")

        product_data = {
            "product": {
                "title": title,
                "body_html": description,
                "vendor": "StaticWaves POD",
                "product_type": "Apparel",
                "variants": [
                    {
                        "price": str(price),
                        "inventory_management": "shopify",
                        "inventory_policy": "deny",
                        "inventory_quantity": 999
                    }
                ]
            }
        }

        # Add image if provided
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode()
                product_data["product"]["images"] = [
                    {"attachment": image_b64}
                ]

        response = requests.post(
            f"{self.base_url}/products.json",
            headers=HEADERS,
            json=product_data,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()["product"]
        log.info(f"✅ Shopify product created: {result['id']}")

        return result

    def process_queue(self):
        """Process products in the published queue"""
        metadata_files = list(self.queue_dir.glob("*_product.json"))

        if not metadata_files:
            log.info("No products to publish")
            return

        log.info(f"Processing {len(metadata_files)} products")

        for metadata_file in metadata_files:
            try:
                # Load product metadata
                metadata = json.loads(metadata_file.read_text())

                # Find associated image
                image_name = metadata_file.stem.replace("_product", "")
                image_path = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    potential_path = self.queue_dir / f"{image_name}{ext}"
                    if potential_path.exists():
                        image_path = potential_path
                        break

                # Create Shopify product
                product = self.create_product(
                    title=metadata.get("title", f"Design {image_name}"),
                    description=metadata.get("description", "Custom printed product"),
                    price=29.99,
                    image_path=image_path
                )

                # Save Shopify product ID to metadata
                metadata["shopify_product_id"] = product["id"]
                metadata["shopify_url"] = f"https://{SHOPIFY_STORE}.myshopify.com/admin/products/{product['id']}"
                metadata_file.write_text(json.dumps(metadata, indent=2))

                log.info(f"✅ Published: {metadata_file.name}")

            except Exception as e:
                log.error(f"❌ Failed to publish {metadata_file.name}: {e}")

def main():
    """Main worker loop"""
    log.info("🚀 Shopify Worker started")

    if not SHOPIFY_STORE or not SHOPIFY_TOKEN:
        log.error("Missing SHOPIFY_STORE or SHOPIFY_TOKEN")
        return

    worker = ShopifyWorker()
    worker.process_queue()

    log.info("✅ Shopify Worker completed")

if __name__ == "__main__":
    main()
