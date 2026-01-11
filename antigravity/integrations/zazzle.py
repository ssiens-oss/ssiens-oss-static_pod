"""
Zazzle API integration for POD operations.

Zazzle is a print-on-demand marketplace that allows you to create and sell
custom products. This module provides a clean interface to the Zazzle API.

API Documentation: https://www.zazzle.com/sell/developers
"""

import os
import requests
import time
from typing import Dict, Any, List, Optional
from pathlib import Path


class ZazzleError(Exception):
    """Raised when Zazzle API operations fail."""
    pass


class ZazzleClient:
    """
    Client for Zazzle API operations.

    Zazzle uses a different model than Printify - you create products via
    their web interface and then manage them via API, or use their
    Associate API for affiliate-style operations.
    """

    # Zazzle API endpoints
    BASE_URL = "https://api.zazzle.com/v1"
    ASSOCIATE_URL = "https://www.zazzle.com/api/create/at-{associate_id}"

    # Product types (Zazzle department IDs)
    PRODUCT_TYPES = {
        "tshirt": "1",
        "hoodie": "5",
        "poster": "228",
        "mug": "168",
        "sticker": "217",
        "phone_case": "256",
        "tote_bag": "223",
        "pillow": "189",
        "mousepad": "163",
        "keychain": "104",
    }

    def __init__(
        self,
        associate_id: Optional[str] = None,
        api_key: Optional[str] = None,
        store_id: Optional[str] = None,
    ):
        """
        Initialize Zazzle client.

        Args:
            associate_id: Zazzle Associate ID (for affiliate API)
            api_key: Zazzle API key (if using full API)
            store_id: Your Zazzle store ID
        """
        self.associate_id = associate_id or os.environ.get("ZAZZLE_ASSOCIATE_ID")
        self.api_key = api_key or os.environ.get("ZAZZLE_API_KEY")
        self.store_id = store_id or os.environ.get("ZAZZLE_STORE_ID")

        if not self.associate_id and not self.api_key:
            raise ValueError(
                "Either ZAZZLE_ASSOCIATE_ID or ZAZZLE_API_KEY must be set"
            )

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

    def upload_image(
        self,
        image_path: str,
        image_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload an image to Zazzle.

        Note: Zazzle's image upload requires authentication and may have
        specific requirements. This is a placeholder implementation.

        Args:
            image_path: Path to image file
            image_name: Optional name for the image

        Returns:
            Dict with image_id and other metadata
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if not image_name:
            image_name = Path(image_path).stem

        # Zazzle image upload endpoint (requires authentication)
        # This is simplified - actual implementation depends on Zazzle's upload API

        print(f"📤 Uploading to Zazzle: {image_name}")

        # Placeholder - actual implementation would use Zazzle's upload API
        # For now, return mock data
        return {
            "image_id": f"zazzle_{int(time.time())}",
            "image_name": image_name,
            "url": f"https://rlv.zcache.com/mock_{image_name}.jpg",
            "status": "uploaded",
        }

    def create_product(
        self,
        product_type: str,
        title: str,
        description: str,
        image_id: str,
        price: float,
        tags: Optional[List[str]] = None,
        royalty_percentage: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Create a product on Zazzle.

        Note: Zazzle product creation typically happens through their
        web interface. This method provides a programmatic interface
        that may use the Associate API or require manual setup.

        Args:
            product_type: Type of product (tshirt, hoodie, etc.)
            title: Product title
            description: Product description
            image_id: Uploaded image ID
            price: Product price
            tags: Product tags/keywords
            royalty_percentage: Royalty percentage (5-99%)

        Returns:
            Dict with product info
        """
        if product_type not in self.PRODUCT_TYPES:
            raise ValueError(
                f"Invalid product type: {product_type}. "
                f"Valid types: {list(self.PRODUCT_TYPES.keys())}"
            )

        department_id = self.PRODUCT_TYPES[product_type]

        print(f"🎨 Creating Zazzle {product_type}: {title}")

        # Zazzle product creation (simplified)
        # Actual implementation depends on which Zazzle API you're using

        product_data = {
            "product_id": f"zazzle_product_{int(time.time())}",
            "product_type": product_type,
            "department_id": department_id,
            "title": title,
            "description": description,
            "image_id": image_id,
            "price": price,
            "royalty_percentage": royalty_percentage,
            "tags": tags or [],
            "store_id": self.store_id,
            "url": f"https://www.zazzle.com/pd/{self.store_id}/{product_type}",
            "status": "created",
        }

        return product_data

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get product details.

        Args:
            product_id: Zazzle product ID

        Returns:
            Product details
        """
        # Zazzle API call to get product
        # Placeholder implementation

        return {
            "product_id": product_id,
            "status": "active",
        }

    def update_product(
        self,
        product_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update product details.

        Args:
            product_id: Zazzle product ID
            updates: Dict of fields to update

        Returns:
            Updated product details
        """
        print(f"🔄 Updating Zazzle product: {product_id}")

        # Zazzle API call to update product
        # Placeholder implementation

        return {
            "product_id": product_id,
            "status": "updated",
            "updates": updates,
        }

    def publish_product(self, product_id: str) -> bool:
        """
        Publish a product to make it live.

        Args:
            product_id: Zazzle product ID

        Returns:
            True if successful
        """
        print(f"📢 Publishing Zazzle product: {product_id}")

        # Zazzle API call to publish
        # Placeholder implementation

        return True

    def unpublish_product(self, product_id: str) -> bool:
        """
        Unpublish a product (make it inactive).

        Args:
            product_id: Zazzle product ID

        Returns:
            True if successful
        """
        print(f"📥 Unpublishing Zazzle product: {product_id}")

        return True

    def list_products(
        self,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List products in your Zazzle store.

        Args:
            status: Filter by status (active, inactive, etc.)
            limit: Maximum number of products to return

        Returns:
            List of product dicts
        """
        # Zazzle API call to list products
        # Placeholder implementation

        return []

    def get_product_url(self, product_id: str) -> str:
        """
        Get the public URL for a product.

        Args:
            product_id: Zazzle product ID

        Returns:
            Product URL
        """
        if self.store_id:
            return f"https://www.zazzle.com/pd/{product_id}"
        return f"https://www.zazzle.com/pd/{product_id}"

    def get_store_url(self) -> str:
        """Get your Zazzle store URL."""
        if self.store_id:
            return f"https://www.zazzle.com/store/{self.store_id}"
        return "https://www.zazzle.com"


def create_zazzle_product(
    image_path: str,
    title: str,
    description: str,
    product_type: str = "tshirt",
    price: float = 19.99,
    tags: Optional[List[str]] = None,
    royalty_percentage: float = 10.0,
) -> Dict[str, Any]:
    """
    High-level function to create a Zazzle product.

    Args:
        image_path: Path to design image
        title: Product title
        description: Product description
        product_type: Type of product
        price: Product price
        tags: Product tags
        royalty_percentage: Royalty percentage

    Returns:
        Dict with product info including URL
    """
    client = ZazzleClient()

    # Upload image
    image_result = client.upload_image(image_path, Path(image_path).stem)

    # Create product
    product = client.create_product(
        product_type=product_type,
        title=title,
        description=description,
        image_id=image_result["image_id"],
        price=price,
        tags=tags,
        royalty_percentage=royalty_percentage,
    )

    # Publish product
    client.publish_product(product["product_id"])

    # Add URL
    product["url"] = client.get_product_url(product["product_id"])

    return product


# Product templates for common use cases
ZAZZLE_TEMPLATES = {
    "tshirt_basic": {
        "product_type": "tshirt",
        "price": 19.99,
        "royalty_percentage": 10.0,
    },
    "tshirt_premium": {
        "product_type": "tshirt",
        "price": 24.99,
        "royalty_percentage": 15.0,
    },
    "hoodie_basic": {
        "product_type": "hoodie",
        "price": 39.99,
        "royalty_percentage": 10.0,
    },
    "hoodie_premium": {
        "product_type": "hoodie",
        "price": 49.99,
        "royalty_percentage": 15.0,
    },
    "poster": {
        "product_type": "poster",
        "price": 14.99,
        "royalty_percentage": 20.0,
    },
    "mug": {
        "product_type": "mug",
        "price": 12.99,
        "royalty_percentage": 15.0,
    },
}


def get_zazzle_template(template_name: str) -> Dict[str, Any]:
    """Get a Zazzle product template."""
    if template_name not in ZAZZLE_TEMPLATES:
        raise ValueError(
            f"Unknown template: {template_name}. "
            f"Available: {list(ZAZZLE_TEMPLATES.keys())}"
        )
    return ZAZZLE_TEMPLATES[template_name].copy()
