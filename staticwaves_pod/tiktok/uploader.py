"""
TikTok Product Uploader

Main orchestrator for uploading products to TikTok Shop.
Integrates:
- OAuth auto-refresh
- Appeal-safe copy generation
- Analytics tracking
"""

import requests
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from tiktok.oauth import get_token
from tiktok.appeal_safe_copy import generate, generate_title
from tiktok.analytics import record_event

log = get_logger("UPLOADER")

TIKTOK_API_BASE = "https://open-api.tiktokglobalshop.com"


class TikTokUploader:
    """
    TikTok Shop product uploader with auto-refresh OAuth.
    """

    def __init__(self):
        """Initialize uploader with OAuth token."""
        self.token = get_token()
        log.info("✅ TikTok uploader initialized")

    def refresh_token(self):
        """Refresh OAuth token if needed."""
        self.token = get_token()

    def upload_product(
        self,
        sku: str,
        name: str,
        price: float,
        images: List[str],
        product_type: str = "hoodie",
        features: List[str] = None
    ) -> Dict:
        """
        Upload a product to TikTok Shop.

        Args:
            sku: Product SKU
            name: Product name
            price: Product price
            images: List of image URLs
            product_type: Product type (hoodie, t-shirt, etc.)
            features: Optional product features

        Returns:
            API response dictionary
        """
        log.info(f"📤 Uploading {sku}: {name} @ ${price}")

        # Generate appeal-safe copy
        title = generate_title(name)
        description = generate(name, product_type, features)

        # Prepare product data
        product_data = {
            "title": title,
            "description": description,
            "price": price,
            "sku": sku,
            "images": images,
            "category_id": self._get_category_id(product_type),
            "stock": 999  # High stock for POD
        }

        # Upload to TikTok (placeholder - adjust for real API)
        response = self._api_request(
            "POST",
            "/product/create",
            json=product_data
        )

        if response.get("code") == 0:
            log.info(f"✅ Uploaded {sku} successfully")

            # Track impression (upload = first impression)
            record_event(sku, price, "impressions")
        else:
            log.error(f"❌ Upload failed for {sku}: {response}")

        return response

    def update_price(self, product_id: str, new_price: float) -> Dict:
        """
        Update product price.

        Args:
            product_id: TikTok product ID
            new_price: New price

        Returns:
            API response
        """
        log.info(f"💰 Updating price for {product_id} to ${new_price}")

        response = self._api_request(
            "PUT",
            f"/product/{product_id}/price",
            json={"price": new_price}
        )

        if response.get("code") == 0:
            log.info(f"✅ Price updated successfully")
        else:
            log.error(f"❌ Price update failed: {response}")

        return response

    def deactivate_product(self, product_id: str) -> Dict:
        """
        Deactivate a product (used for price pruning).

        Args:
            product_id: TikTok product ID

        Returns:
            API response
        """
        log.info(f"🚫 Deactivating product {product_id}")

        response = self._api_request(
            "PUT",
            f"/product/{product_id}/deactivate",
            json={}
        )

        if response.get("code") == 0:
            log.info(f"✅ Product deactivated")
        else:
            log.error(f"❌ Deactivation failed: {response}")

        return response

    def _api_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated API request to TikTok.

        Args:
            method: HTTP method
            endpoint: API endpoint
            json: Optional JSON body

        Returns:
            API response dictionary
        """
        # Refresh token if needed
        self.refresh_token()

        url = f"{TIKTOK_API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=json)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            log.error(f"API request failed: {e}")
            return {"code": -1, "message": str(e)}

    def _get_category_id(self, product_type: str) -> str:
        """
        Get TikTok category ID for product type.

        Args:
            product_type: Product type

        Returns:
            Category ID string
        """
        # Placeholder - map to real TikTok category IDs
        category_map = {
            "hoodie": "100001",
            "t-shirt": "100002",
            "sweatshirt": "100003"
        }

        return category_map.get(product_type, "100000")


if __name__ == "__main__":
    # Demo usage
    uploader = TikTokUploader()

    # Upload a product
    result = uploader.upload_product(
        sku="HOODIE-001",
        name="Midnight Waves Hoodie",
        price=29.99,
        images=["https://example.com/image1.jpg"],
        product_type="hoodie",
        features=["premium cotton blend", "unique graphic design"]
    )

    print(f"\n📊 Upload result: {result}\n")
