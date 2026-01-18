"""
Base Platform Interface for POD Publishing
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


class PlatformError(Exception):
    """Base exception for platform errors"""
    pass


@dataclass
class PublishResult:
    """Result of publishing to a platform"""
    success: bool
    product_id: Optional[str] = None
    product_url: Optional[str] = None
    error: Optional[str] = None
    platform: str = ""


class BasePlatform(ABC):
    """Abstract base class for POD platforms"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize platform with configuration

        Args:
            config: Platform-specific configuration dict
        """
        self.config = config
        self.platform_name = self.__class__.__name__.replace('Platform', '')

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if platform is properly configured"""
        pass

    @abstractmethod
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
        Publish design to platform

        Args:
            image_path: Local path to image file
            title: Product title
            description: Product description
            tags: List of tags/keywords
            price: Price in cents (platform may have different pricing)
            **kwargs: Platform-specific options

        Returns:
            PublishResult with success status and product info
        """
        pass

    @abstractmethod
    def get_product_url(self, product_id: str) -> str:
        """Get URL to product on platform"""
        pass

    def validate_image(self, image_path: str) -> tuple[bool, str]:
        """
        Validate image meets platform requirements

        Returns:
            (is_valid, error_message)
        """
        # Default validation - platforms can override
        import os
        if not os.path.exists(image_path):
            return False, "Image file not found"
        return True, ""
