"""
Printify API Client
Handles product creation and publishing with dynamic variant fetching and retry logic
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

PRINTIFY_API = "https://api.printify.com/v1"


class PrintifyError(Exception):
    """Base exception for Printify API errors"""
    pass


class PrintifyAuthError(PrintifyError):
    """Authentication error"""
    pass


class PrintifyRateLimitError(PrintifyError):
    """Rate limit exceeded"""
    pass


class PrintifyAPIError(PrintifyError):
    """General API error"""
    pass


@dataclass
class Variant:
    """Product variant (size, color, etc.)"""
    id: int
    title: str
    is_available: bool


@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    initial_backoff: float = 1.0
    max_backoff: float = 30.0
    backoff_multiplier: float = 2.0


class PrintifyClient:
    """
    Enhanced Printify API client with:
    - Dynamic variant fetching
    - Exponential backoff retry logic
    - Comprehensive error handling
    - Type safety
    """

    def __init__(
        self,
        api_key: str,
        shop_id: str,
        retry_config: Optional[RetryConfig] = None
    ):
        if not api_key or not shop_id:
            raise PrintifyAuthError("Printify API key or Shop ID missing")

        self.api_key = api_key
        self.shop_id = shop_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.retry_config = retry_config or RetryConfig()
        self._variant_cache: Dict[Tuple[int, int], List[Variant]] = {}

        # Configure session with HTTPAdapter and retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.retry_config.max_retries,
            backoff_factor=self.retry_config.backoff_multiplier,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"Initialized Printify client for shop {shop_id}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            PrintifyError: On API errors
        """
        url = f"{PRINTIFY_API}{endpoint}"
        retries = 0
        backoff = self.retry_config.initial_backoff

        while retries <= self.retry_config.max_retries:
            try:
                logger.debug(f"{method} {endpoint} (attempt {retries + 1}/{self.retry_config.max_retries + 1})")

                response = self.session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=30,
                    **kwargs
                )

                # Handle specific HTTP status codes
                if response.status_code == 401:
                    raise PrintifyAuthError("Invalid API key or authentication failed")
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded, retrying...")
                    raise PrintifyRateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}, retrying...")
                    raise PrintifyAPIError(f"Server error: {response.status_code}")
                elif not response.ok:
                    error_msg = f"API error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise PrintifyAPIError(error_msg)

                logger.debug(f"Request successful: {response.status_code}")
                return response

            except (requests.Timeout, requests.ConnectionError, PrintifyRateLimitError, PrintifyAPIError) as e:
                retries += 1
                if retries > self.retry_config.max_retries:
                    logger.error(f"Max retries exceeded for {method} {endpoint}")
                    raise PrintifyError(f"Request failed after {self.retry_config.max_retries} retries: {str(e)}")

                # Calculate exponential backoff
                sleep_time = min(backoff, self.retry_config.max_backoff)
                logger.info(f"Retrying in {sleep_time:.1f}s... ({retries}/{self.retry_config.max_retries})")
                time.sleep(sleep_time)
                backoff *= self.retry_config.backoff_multiplier

            except PrintifyAuthError:
                # Don't retry auth errors
                raise

    def get_blueprint_variants(
        self,
        blueprint_id: int,
        provider_id: int,
        use_cache: bool = True,
        color_filter: Optional[str] = None,
        max_variants: Optional[int] = None
    ) -> List[Variant]:
        """
        Fetch available variants for a blueprint and print provider

        Args:
            blueprint_id: Printify blueprint ID (e.g., 3 for t-shirt)
            provider_id: Print provider ID (e.g., 99 for SwiftPOD)
            use_cache: Whether to use cached variants
            color_filter: Filter variants by color (e.g., "black", "white")
            max_variants: Maximum number of variants to return (POD optimization)

        Returns:
            List of Variant objects
        """
        cache_key = (blueprint_id, provider_id)

        if use_cache and cache_key in self._variant_cache:
            logger.debug(f"Using cached variants for blueprint {blueprint_id}, provider {provider_id}")
            cached_variants = self._variant_cache[cache_key]
        else:
            try:
                logger.info(f"Fetching variants for blueprint {blueprint_id}, provider {provider_id}")
                response = self._make_request(
                    "GET",
                    f"/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json"
                )

                variants_data = response.json().get("variants", [])
                cached_variants = [
                    Variant(
                        id=v["id"],
                        title=v.get("title", f"Variant {v['id']}"),
                        is_available=v.get("is_available", True)
                    )
                    for v in variants_data
                ]

                # Cache the results
                self._variant_cache[cache_key] = cached_variants
                logger.info(f"Fetched {len(cached_variants)} total variants")

            except Exception as e:
                logger.error(f"Failed to fetch variants: {e}")
                raise PrintifyError(f"Failed to fetch blueprint variants: {str(e)}")

        # Apply filters
        variants = cached_variants

        # Color filter (POD optimization: reduce SKU count)
        if color_filter:
            color_lower = color_filter.lower()
            variants = [
                v for v in variants
                if color_lower in v.title.lower()
            ]
            logger.info(f"🎨 Filtered to {len(variants)} {color_filter} variants (from {len(cached_variants)} total)")

        # Limit variants (POD optimization: reduce complexity and costs)
        if max_variants and len(variants) > max_variants:
            variants = variants[:max_variants]
            logger.info(f"📊 Limited to {max_variants} variants for POD efficiency")

        return variants

    def upload_image(self, image_path: str, filename: str) -> Optional[str]:
        """
        Upload image to Printify

        Args:
            image_path: Local path to image file
            filename: Name for the uploaded file

        Returns:
            Printify image ID or None on failure
        """
        try:
            logger.info(f"Uploading image: {filename}")

            # File uploads need special handling - use session directly
            # Don't set Content-Type (let requests handle multipart/form-data)
            upload_headers = {"Authorization": f"Bearer {self.api_key}"}

            with open(image_path, "rb") as f:
                files = {"file": (filename, f, "image/png")}

                response = self.session.post(
                    f"{PRINTIFY_API}/uploads/images.json",
                    files=files,
                    headers=upload_headers,
                    timeout=30
                )

            # Check for errors and log detailed response
            if not response.ok:
                error_detail = response.text
                logger.error(f"Printify upload failed ({response.status_code}): {error_detail}")
                response.raise_for_status()

            image_id = response.json().get("id")
            logger.info(f"✅ Image uploaded successfully: {image_id}")
            return image_id

        except requests.HTTPError as e:
            logger.error(f"HTTP error uploading image: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None

    def create_product(
        self,
        title: str,
        image_id: str,
        blueprint_id: int,
        provider_id: int,
        price_cents: int = 1999,
        variant_ids: Optional[List[int]] = None,
        description: Optional[str] = None,
        color_filter: Optional[str] = None,
        max_variants: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Create a product with uploaded image

        Args:
            title: Product title
            image_id: Printify image ID from upload_image()
            blueprint_id: Blueprint ID (e.g., 3 for t-shirt)
            provider_id: Print provider ID (e.g., 99 for SwiftPOD)
            price_cents: Price in cents (e.g., 1999 = $19.99)
            variant_ids: Optional list of variant IDs to enable. If None, fetches variants with filters
            description: Optional product description
            color_filter: Filter variants by color (POD optimization: e.g., "black")
            max_variants: Maximum variants to enable (POD optimization: e.g., 50)

        Returns:
            Product data dict or None on failure
        """
        try:
            # Fetch variants if not provided
            if variant_ids is None:
                logger.info("Fetching available variants...")
                variants = self.get_blueprint_variants(
                    blueprint_id,
                    provider_id,
                    color_filter=color_filter,
                    max_variants=max_variants
                )
                variant_ids = [v.id for v in variants if v.is_available]
                logger.info(f"✅ Using {len(variant_ids)} variants for product")

            if not variant_ids:
                logger.error("No variants available for this blueprint/provider combination")
                return None

            # Build variant configurations
            variant_configs = [
                {"id": vid, "price": price_cents, "is_enabled": True}
                for vid in variant_ids
            ]

            payload = {
                "title": title,
                "description": description or title,
                "blueprint_id": blueprint_id,
                "print_provider_id": provider_id,
                "variants": variant_configs,
                "print_areas": [{
                    "variant_ids": variant_ids,
                    "placeholders": [{
                        "position": "front",
                        "images": [{
                            "id": image_id,
                            "x": 0.5,
                            "y": 0.5,
                            "scale": 1,
                            "angle": 0
                        }]
                    }]
                }]
            }

            logger.info(f"Creating product: {title}")
            response = self._make_request(
                "POST",
                f"/shops/{self.shop_id}/products.json",
                json=payload
            )

            product = response.json()
            logger.info(f"Product created successfully: {product.get('id')}")
            return product

        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return None

    def publish_product(self, product_id: str, publish_to_channels: bool = True) -> bool:
        """
        Publish product to connected sales channels

        Args:
            product_id: Printify product ID
            publish_to_channels: Whether to publish to sales channels (requires connected channels)

        Returns:
            True if published successfully, False otherwise
        """
        try:
            logger.info(f"Publishing product: {product_id}")

            # Printify publish requires at least one connected sales channel
            # If no channels connected, this will fail with 400/422
            # Common issue: "No sales channels connected to shop"
            self._make_request(
                "POST",
                f"/shops/{self.shop_id}/products/{product_id}/publish.json",
                json={
                    "title": publish_to_channels,
                    "description": publish_to_channels,
                    "images": publish_to_channels,
                    "variants": publish_to_channels,
                    "tags": publish_to_channels
                }
            )

            logger.info(f"✅ Product published successfully: {product_id}")
            return True

        except requests.HTTPError as e:
            # Handle common publish errors gracefully
            if e.response.status_code in [400, 422]:
                error_msg = e.response.text
                if "sales channel" in error_msg.lower() or "no channels" in error_msg.lower():
                    logger.warning(f"⚠️ Product {product_id} created but not published: No sales channels connected")
                    logger.info(f"💡 Tip: Connect a sales channel (Shopify, Etsy, etc.) in Printify dashboard to enable publishing")
                else:
                    logger.warning(f"⚠️ Product {product_id} created but publishing failed: {error_msg}")
            else:
                logger.error(f"❌ Error publishing product {product_id}: {e}")
            return False

        except Exception as e:
            logger.error(f"❌ Unexpected error publishing product {product_id}: {e}")
            return False

    def create_and_publish(
        self,
        image_path: str,
        title: str,
        blueprint_id: int,
        provider_id: int,
        price_cents: int = 1999,
        description: Optional[str] = None,
        color_filter: str = "black",
        max_variants: int = 50
    ) -> Optional[str]:
        """
        Complete workflow: upload image, create product, and publish

        POD-optimized defaults:
        - Only black variants (reduces SKU complexity)
        - Maximum 50 variants (improves managability and reduces costs)

        Args:
            image_path: Local path to image file
            title: Product title
            blueprint_id: Blueprint ID (e.g., 3 for t-shirt)
            provider_id: Print provider ID (e.g., 99 for SwiftPOD)
            price_cents: Price in cents
            description: Optional product description
            color_filter: Color to filter variants (default: "black" for POD optimization)
            max_variants: Maximum variants per product (default: 50 for POD optimization)

        Returns:
            Product ID if successful, None otherwise
        """
        logger.info(f"🎨 POD Settings: {color_filter} variants only, max {max_variants} SKUs")

        # Upload image
        image_id = self.upload_image(image_path, title)
        if not image_id:
            logger.error("Failed to upload image")
            return None

        # Create product with POD optimizations
        product = self.create_product(
            title=title,
            image_id=image_id,
            blueprint_id=blueprint_id,
            provider_id=provider_id,
            price_cents=price_cents,
            description=description,
            color_filter=color_filter,
            max_variants=max_variants
        )
        if not product:
            logger.error("Failed to create product")
            return None

        product_id = product.get("id")
        if not product_id:
            logger.error("Product created but no ID returned")
            return None

        # Publish
        if not self.publish_product(product_id):
            logger.warning(f"Product {product_id} created but failed to publish")
            # Still return product_id as it was created successfully
            return product_id

        return product_id

    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get product details

        Args:
            product_id: Printify product ID

        Returns:
            Product data or None
        """
        try:
            response = self._make_request(
                "GET",
                f"/shops/{self.shop_id}/products/{product_id}.json"
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return None

    def list_products(self, page: int = 1, limit: int = 100) -> List[Dict]:
        """
        List products in shop

        Args:
            page: Page number
            limit: Items per page

        Returns:
            List of product data dicts
        """
        try:
            response = self._make_request(
                "GET",
                f"/shops/{self.shop_id}/products.json",
                params={"page": page, "limit": limit}
            )
            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return []
