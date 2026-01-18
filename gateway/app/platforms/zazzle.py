"""
Zazzle Platform Integration

Zazzle API Documentation:
https://www.zazzle.com/sell/developers

Note: Zazzle requires OAuth authentication and has specific
image requirements for products.
"""
from typing import Dict, Any, Optional
from .base import BasePlatform, PublishResult, PlatformError
import requests
import base64
import logging

logger = logging.getLogger(__name__)


class ZazzlePlatform(BasePlatform):
    """Zazzle POD platform"""

    API_BASE = "https://api.zazzle.com/v1"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.store_id = config.get('store_id')
        self.default_product_type = config.get('product_type', 'tshirt')

    def is_configured(self) -> bool:
        """Check if Zazzle is configured"""
        return bool(self.api_key and self.api_secret and self.store_id)

    def publish(
        self,
        image_path: str,
        title: str,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        price: Optional[int] = None,
        **kwargs
    ) -> PublishResult:
        """
        Publish design to Zazzle

        Args:
            image_path: Local path to image
            title: Product title
            description: Product description
            tags: Product tags/keywords
            price: Price in cents (Zazzle uses royalty model)
            **kwargs: Zazzle-specific options
                - product_type: tshirt, hoodie, poster, etc.
                - department: mens, womens, kids, etc.

        Returns:
            PublishResult with product info
        """
        if not self.is_configured():
            return PublishResult(
                success=False,
                error="Zazzle not configured",
                platform="Zazzle"
            )

        try:
            # Upload image to Zazzle
            image_id = self._upload_image(image_path)
            if not image_id:
                return PublishResult(
                    success=False,
                    error="Failed to upload image to Zazzle",
                    platform="Zazzle"
                )

            # Create product with uploaded image
            product_type = kwargs.get('product_type', self.default_product_type)
            department = kwargs.get('department', 'unisex')

            product_data = {
                "title": title,
                "description": description or title,
                "image_id": image_id,
                "product_type": product_type,
                "department": department,
                "tags": tags or [],
                "store_id": self.store_id
            }

            # Add royalty/pricing if provided
            if price:
                # Convert cents to Zazzle royalty percentage
                # Zazzle uses % royalty, not fixed price
                product_data["royalty_percentage"] = min(99, price // 100)

            product_id = self._create_product(product_data)

            if product_id:
                product_url = self.get_product_url(product_id)
                logger.info(f"Published to Zazzle: {product_id}")
                return PublishResult(
                    success=True,
                    product_id=product_id,
                    product_url=product_url,
                    platform="Zazzle"
                )
            else:
                return PublishResult(
                    success=False,
                    error="Failed to create Zazzle product",
                    platform="Zazzle"
                )

        except Exception as e:
            logger.error(f"Zazzle publish error: {e}")
            return PublishResult(
                success=False,
                error=str(e),
                platform="Zazzle"
            )

    def _upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload image to Zazzle

        Returns:
            Image ID or None on failure
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Base64 encode image
            encoded_image = base64.b64encode(image_data).decode('utf-8')

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "image_data": encoded_image,
                "filename": image_path.split('/')[-1]
            }

            response = requests.post(
                f"{self.API_BASE}/images",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 201:
                return response.json().get('image_id')
            else:
                logger.error(f"Zazzle image upload failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error uploading to Zazzle: {e}")
            return None

    def _create_product(self, product_data: Dict[str, Any]) -> Optional[str]:
        """
        Create product on Zazzle

        Returns:
            Product ID or None on failure
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{self.API_BASE}/products",
                headers=headers,
                json=product_data,
                timeout=60
            )

            if response.status_code == 201:
                return response.json().get('product_id')
            else:
                logger.error(f"Zazzle product creation failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating Zazzle product: {e}")
            return None

    def get_product_url(self, product_id: str) -> str:
        """Get Zazzle product URL"""
        return f"https://www.zazzle.com/pd/{product_id}"

    def validate_image(self, image_path: str) -> tuple[bool, str]:
        """
        Validate image for Zazzle requirements

        Zazzle requirements:
        - Min resolution: 1800x1800px
        - Max file size: 100MB
        - Formats: PNG, JPEG
        """
        is_valid, error = super().validate_image(image_path)
        if not is_valid:
            return False, error

        try:
            from PIL import Image
            import os

            # Check file size
            file_size = os.path.getsize(image_path)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                return False, "Image exceeds 100MB limit for Zazzle"

            # Check resolution
            with Image.open(image_path) as img:
                width, height = img.size
                if width < 1800 or height < 1800:
                    return False, f"Image resolution too low ({width}x{height}). Zazzle requires minimum 1800x1800px"

            return True, ""

        except Exception as e:
            return False, f"Image validation error: {str(e)}"
