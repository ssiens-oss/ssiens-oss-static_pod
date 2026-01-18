"""
Printify Platform Integration
"""
from typing import Dict, Any, Optional
from .base import BasePlatform, PublishResult, PlatformError
from ..printify_client import PrintifyClient, RetryConfig
import logging

logger = logging.getLogger(__name__)


class PrintifyPlatform(BasePlatform):
    """Printify POD platform"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.shop_id = config.get('shop_id')
        self.blueprint_id = config.get('blueprint_id', 3)
        self.provider_id = config.get('provider_id', 99)
        self.default_price = config.get('default_price_cents', 1999)

        if self.is_configured():
            retry_config = RetryConfig(
                max_retries=config.get('max_retries', 3),
                initial_backoff=config.get('initial_backoff', 1.0),
                max_backoff=config.get('max_backoff', 30.0),
                backoff_multiplier=config.get('backoff_multiplier', 2.0)
            )
            self.client = PrintifyClient(
                self.api_key,
                self.shop_id,
                retry_config
            )
        else:
            self.client = None

    def is_configured(self) -> bool:
        """Check if Printify is configured"""
        return bool(self.api_key and self.shop_id)

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
        Publish design to Printify

        Args:
            image_path: Local path to image
            title: Product title
            description: Product description
            tags: Tags (not used by Printify API)
            price: Price in cents
            **kwargs: Additional Printify-specific options
                - blueprint_id: Override default blueprint
                - provider_id: Override default provider

        Returns:
            PublishResult with product info
        """
        if not self.client:
            return PublishResult(
                success=False,
                error="Printify not configured",
                platform="Printify"
            )

        try:
            # Get options with defaults
            blueprint_id = kwargs.get('blueprint_id', self.blueprint_id)
            provider_id = kwargs.get('provider_id', self.provider_id)
            price_cents = price or self.default_price

            # Publish product
            product_id = self.client.create_and_publish(
                image_path=image_path,
                title=title,
                blueprint_id=blueprint_id,
                provider_id=provider_id,
                price_cents=price_cents,
                description=description
            )

            if product_id:
                product_url = self.get_product_url(product_id)
                logger.info(f"Published to Printify: {product_id}")
                return PublishResult(
                    success=True,
                    product_id=product_id,
                    product_url=product_url,
                    platform="Printify"
                )
            else:
                return PublishResult(
                    success=False,
                    error="Failed to create product",
                    platform="Printify"
                )

        except Exception as e:
            logger.error(f"Printify publish error: {e}")
            return PublishResult(
                success=False,
                error=str(e),
                platform="Printify"
            )

    def get_product_url(self, product_id: str) -> str:
        """Get Printify product URL"""
        return f"https://printify.com/app/products/{product_id}"
