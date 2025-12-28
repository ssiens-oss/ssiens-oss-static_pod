"""
TikTok Seller API Uploader
===========================
Automated product upload to TikTok Shop via official Seller API.

Features:
- OAuth 2.0 authentication with auto-refresh
- Bulk product upload
- Error recovery and retry logic
- Rate limiting compliance
- Upload status tracking

API Documentation:
https://partner.tiktokshop.com/docv2/page/650aa8f6715c0302be9ba7bf

CRITICAL: TikTok's API has strict rate limits:
- 10 requests/second per seller
- 1000 requests/hour per app
- Exceeding limits = 24-48hr ban
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests")
    sys.exit(1)

from core.logger import get_logger

log = get_logger("TIKTOK-UPLOADER")

# TikTok API Configuration
API_BASE_URL = os.getenv(
    "TIKTOK_API_BASE_URL",
    "https://open-api.tiktokglobalshop.com"
)
SELLER_ID = os.getenv("TIKTOK_SELLER_ID", "")
ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
REFRESH_TOKEN = os.getenv("TIKTOK_REFRESH_TOKEN", "")
APP_KEY = os.getenv("TIKTOK_APP_KEY", "")
APP_SECRET = os.getenv("TIKTOK_APP_SECRET", "")
REGION = os.getenv("TIKTOK_REGION", "US")

# Rate limiting
MAX_REQUESTS_PER_SECOND = 8  # Buffer below 10/sec limit
REQUEST_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND

# Token refresh threshold (refresh 1 hour before expiry)
TOKEN_REFRESH_BUFFER = 3600


class TikTokAPIError(Exception):
    """Custom exception for TikTok API errors."""
    pass


class TikTokUploader:
    """TikTok Seller API client with OAuth auto-refresh."""

    def __init__(self):
        """Initialize uploader with credentials from environment."""
        self.seller_id = SELLER_ID
        self.access_token = ACCESS_TOKEN
        self.refresh_token = REFRESH_TOKEN
        self.app_key = APP_KEY
        self.app_secret = APP_SECRET
        self.region = REGION

        self.token_expires_at = None
        self.last_request_time = 0

        # Validate credentials
        if not all([self.seller_id, self.access_token]):
            log.error("❌ Missing TikTok credentials in environment")
            log.info("Required: TIKTOK_SELLER_ID, TIKTOK_ACCESS_TOKEN")
            raise ValueError("Incomplete TikTok credentials")

        log.info(f"✅ TikTok Uploader initialized (Region: {self.region})")

    def _get_headers(self) -> Dict[str, str]:
        """
        Build request headers with current access token.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "x-tts-access-token": self.access_token
        }

    def _rate_limit(self):
        """
        Enforce rate limiting to prevent API bans.

        Ensures minimum interval between requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < REQUEST_INTERVAL:
            sleep_time = REQUEST_INTERVAL - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def refresh_access_token(self) -> bool:
        """
        Refresh OAuth access token using refresh token.

        Returns:
            True if refresh successful, False otherwise

        Raises:
            TikTokAPIError: If refresh fails
        """
        if not self.refresh_token:
            log.warning("⚠️  No refresh token available")
            return False

        log.info("🔄 Refreshing TikTok access token")

        endpoint = f"{API_BASE_URL}/api/token/refresh"
        payload = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("code") == 0:
                self.access_token = data["data"]["access_token"]
                self.refresh_token = data["data"]["refresh_token"]
                expires_in = data["data"]["access_token_expire_in"]

                self.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=expires_in
                )

                log.info("✅ Access token refreshed successfully")
                log.info(f"🕐 Token expires: {self.token_expires_at}")

                # Update environment (for current process only)
                os.environ["TIKTOK_ACCESS_TOKEN"] = self.access_token
                os.environ["TIKTOK_REFRESH_TOKEN"] = self.refresh_token

                return True
            else:
                log.error(f"❌ Token refresh failed: {data.get('message')}")
                raise TikTokAPIError(data.get("message", "Unknown error"))

        except requests.RequestException as e:
            log.error(f"❌ Token refresh request failed: {str(e)}")
            raise TikTokAPIError(f"Network error: {str(e)}")

    def check_token_expiry(self):
        """
        Check if token needs refresh and refresh if necessary.
        """
        if not self.token_expires_at:
            # Assume token is valid if expiry not tracked
            return

        time_until_expiry = (
            self.token_expires_at - datetime.utcnow()
        ).total_seconds()

        if time_until_expiry < TOKEN_REFRESH_BUFFER:
            log.info(
                f"⏰ Token expires in {time_until_expiry:.0f}s, refreshing"
            )
            self.refresh_access_token()

    def upload_product(
        self,
        product: Dict[str, Any],
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Upload a single product to TikTok Shop.

        Args:
            product: Product dictionary (TikTok API format)
            retry_count: Number of retry attempts on failure

        Returns:
            API response with product ID

        Raises:
            TikTokAPIError: If upload fails after retries

        Example:
            >>> uploader.upload_product({
                "product_name": "Hoodie",
                "price": 49,
                ...
            })
        """
        self.check_token_expiry()
        self._rate_limit()

        endpoint = f"{API_BASE_URL}/product/{API_VERSION}/products"
        headers = self._get_headers()

        # Add required seller context
        payload = {
            "product": product,
            "seller_id": self.seller_id,
            "region": self.region
        }

        for attempt in range(retry_count):
            try:
                log.info(
                    f"📤 Uploading: {product.get('product_name', 'Unknown')} "
                    f"(Attempt {attempt + 1}/{retry_count})"
                )

                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                response.raise_for_status()
                data = response.json()

                if data.get("code") == 0:
                    product_id = data["data"]["product_id"]
                    log.info(f"✅ Product uploaded: ID={product_id}")
                    return data["data"]
                else:
                    error_msg = data.get("message", "Unknown error")
                    log.warning(f"⚠️  Upload warning: {error_msg}")

                    # Check if error is retryable
                    if "rate limit" in error_msg.lower():
                        wait_time = 60 * (attempt + 1)
                        log.info(f"⏸️  Rate limited, waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue

                    raise TikTokAPIError(error_msg)

            except requests.RequestException as e:
                log.error(f"❌ Upload request failed: {str(e)}")

                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    log.info(f"🔄 Retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    raise TikTokAPIError(f"Upload failed: {str(e)}")

        raise TikTokAPIError("Upload failed after all retries")

    def bulk_upload(
        self,
        products: List[Dict[str, Any]],
        on_progress: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Upload multiple products in sequence.

        Args:
            products: List of product dictionaries
            on_progress: Optional callback for progress updates

        Returns:
            Summary of upload operation

        Example:
            >>> uploader.bulk_upload(products, lambda i, total: print(f"{i}/{total}"))
        """
        log.info(f"📦 Starting bulk upload: {len(products)} products")

        results = {
            "total": len(products),
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        for i, product in enumerate(products, 1):
            try:
                self.upload_product(product)
                results["successful"] += 1

                if on_progress:
                    on_progress(i, len(products))

            except TikTokAPIError as e:
                log.error(f"❌ Failed to upload product: {str(e)}")
                results["failed"] += 1
                results["errors"].append({
                    "product": product.get("product_name", "Unknown"),
                    "error": str(e)
                })

        log.info("=" * 60)
        log.info(f"✅ Successful: {results['successful']}/{results['total']}")
        log.info(f"❌ Failed: {results['failed']}/{results['total']}")

        return results


# API version (TikTok uses versioned endpoints)
API_VERSION = "202401"


def main():
    """CLI entry point for testing."""
    log.info("🚀 TikTok Uploader Test")
    log.info("=" * 60)

    try:
        uploader = TikTokUploader()

        # Test product (minimal payload)
        test_product = {
            "product_name": "StaticWaves Test Hoodie",
            "description": "Test upload - delete after verification",
            "category_id": "100001",
            "brand_id": "",
            "main_images": ["https://cdn.staticwaves.ai/test.png"],
            "skus": [{
                "sales_attributes": [],
                "price": {"amount": "4900", "currency": "USD"},
                "inventory": [{"quantity": 999}]
            }]
        }

        log.info("📤 Uploading test product...")
        result = uploader.upload_product(test_product)
        log.info(f"✅ Test upload successful: {result}")

    except Exception as e:
        log.error(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
