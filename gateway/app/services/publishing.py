"""
Publishing Service

Handles publishing images to Printify and other platforms.
"""
import logging
from typing import Dict, Optional

from app.printify_client import PrintifyClient, PrintifyError, RetryConfig
from app.services.image import ImageService
from app.state import ImageStatus

logger = logging.getLogger(__name__)


class PublishingService:
    """Service for publishing images to POD platforms"""

    def __init__(
        self,
        printify_client: Optional[PrintifyClient],
        image_service: ImageService
    ):
        """
        Initialize publishing service.

        Args:
            printify_client: Printify API client (optional)
            image_service: Image service for status updates
        """
        self.printify = printify_client
        self.image_service = image_service

    @property
    def is_available(self) -> bool:
        """Check if publishing is available"""
        return self.printify is not None

    def publish(
        self,
        image_id: str,
        title: str,
        description: Optional[str] = None,
        price_cents: int = 3499,
        blueprint_id: int = 77,
        provider_id: int = 39
    ) -> Dict:
        """
        Publish an image to Printify.

        Args:
            image_id: Image identifier
            title: Product title
            description: Optional product description
            price_cents: Price in cents
            blueprint_id: Printify blueprint ID
            provider_id: Printify provider ID

        Returns:
            Dict with success status and product_id or error
        """
        if not self.printify:
            return {"success": False, "error": "Printify not configured"}

        # Check image status
        status = self.image_service.get_status(image_id)
        if status not in [ImageStatus.APPROVED.value, ImageStatus.FAILED.value]:
            return {
                "success": False,
                "error": f"Image must be approved first (current: {status})"
            }

        # Get image path
        image_path = self.image_service.get_image_path(image_id)
        if not image_path:
            return {"success": False, "error": "Image file not found"}

        # Update status to publishing
        self.image_service.set_status(image_id, ImageStatus.PUBLISHING)

        try:
            # Publish via Printify
            product_id = self.printify.create_and_publish(
                image_path=str(image_path),
                title=title,
                blueprint_id=blueprint_id,
                provider_id=provider_id,
                price_cents=price_cents,
                description=description
            )

            if product_id:
                self.image_service.set_status(
                    image_id,
                    ImageStatus.PUBLISHED,
                    {"product_id": product_id, "title": title}
                )
                logger.info(f"Published {image_id} -> Product {product_id}")
                return {
                    "success": True,
                    "status": ImageStatus.PUBLISHED.value,
                    "product_id": product_id
                }
            else:
                self._handle_failure(image_id, "Printify API failed to create product")
                return {"success": False, "error": "Failed to create product"}

        except PrintifyError as e:
            error_msg = f"Printify error: {str(e)}"
            self._handle_failure(image_id, error_msg)
            return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Publishing error for {image_id}: {e}", exc_info=True)
            self._handle_failure(image_id, error_msg)
            return {"success": False, "error": "Internal server error"}

    def _handle_failure(self, image_id: str, error_msg: str) -> None:
        """Handle publish failure by updating status"""
        logger.error(f"Publish failed for {image_id}: {error_msg}")
        self.image_service.set_status(
            image_id,
            ImageStatus.FAILED,
            {"error_message": error_msg}
        )


def create_publishing_service(
    api_key: Optional[str],
    shop_id: Optional[str],
    image_service: ImageService,
    retry_config: Optional[RetryConfig] = None
) -> PublishingService:
    """
    Factory function to create a publishing service.

    Args:
        api_key: Printify API key
        shop_id: Printify shop ID
        image_service: Image service instance
        retry_config: Optional retry configuration

    Returns:
        PublishingService instance
    """
    printify_client = None

    if api_key and shop_id:
        try:
            printify_client = PrintifyClient(api_key, shop_id, retry_config)
            logger.info("Printify client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Printify: {e}")

    return PublishingService(printify_client, image_service)
