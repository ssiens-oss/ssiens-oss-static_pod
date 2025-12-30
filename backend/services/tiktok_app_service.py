"""
TikTok Shop App Service
OAuth installation and seller authorization
"""
import hmac
import hashlib
import secrets
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests
from loguru import logger

from config.settings import settings


class TikTokAppService:
    """Service for TikTok Shop App OAuth and management"""

    # OAuth endpoints
    AUTH_URL = "https://services.tiktokshop.com/open/authorize"
    TOKEN_URL = "https://auth.tiktok-shops.com/api/v2/token/get"

    # Required permissions
    PERMISSIONS = [
        "product.list",
        "product.write",
        "order.list",
        "order.fulfillment",
        "shop.read",
    ]

    # App URLs
    APP_URL = settings.APP_URL if hasattr(settings, 'APP_URL') else "https://your-app.com"
    REDIRECT_URI = f"{APP_URL}/api/tiktok-app/callback"

    def __init__(self):
        self.app_key = settings.TIKTOK_APP_KEY
        self.app_secret = settings.TIKTOK_APP_SECRET

    def generate_install_url(self, state: Optional[str] = None) -> str:
        """
        Generate TikTok Shop authorization URL

        Args:
            state: CSRF protection token

        Returns:
            Authorization URL to redirect seller to
        """
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "app_key": self.app_key,
            "state": state,
        }

        url = f"{self.AUTH_URL}?{urlencode(params)}"

        logger.info("Generated TikTok Shop authorization URL")
        return url

    def _generate_signature(self, params: Dict[str, str], endpoint: str = "") -> str:
        """
        Generate signature for TikTok Shop API requests

        Args:
            params: Request parameters
            endpoint: API endpoint path

        Returns:
            HMAC-SHA256 signature
        """
        # Sort parameters
        sorted_keys = sorted(params.keys())

        # Concatenate: endpoint + key1 + value1 + key2 + value2 ...
        concatenated = endpoint + "".join([f"{key}{params[key]}" for key in sorted_keys])

        # Generate HMAC-SHA256
        sign = hmac.new(
            self.app_secret.encode("utf-8"),
            concatenated.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

        return sign

    async def exchange_code_for_token(self, auth_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            auth_code: Authorization code from TikTok callback

        Returns:
            Token data including access_token and refresh_token
        """
        endpoint = "/api/v2/token/get"
        timestamp = str(int(time.time()))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "auth_code": auth_code,
            "grant_type": "authorized_code",
        }

        # Generate signature
        params["sign"] = self._generate_signature(params, endpoint)

        try:
            response = requests.post(
                self.TOKEN_URL,
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"Token exchange failed: {data.get('message')}")

            result = data.get("data", {})

            logger.info("✅ Obtained TikTok Shop access token")

            return {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "access_token_expire_in": result.get("access_token_expire_in"),
                "refresh_token_expire_in": result.get("refresh_token_expire_in"),
                "seller_base_region": result.get("seller_base_region"),
                "shop_id": result.get("shop_id"),
                "shop_cipher": result.get("shop_cipher"),
            }

        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh expired access token

        Args:
            refresh_token: Refresh token

        Returns:
            New token data
        """
        endpoint = "/api/v2/token/refresh"
        timestamp = str(int(time.time()))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        params["sign"] = self._generate_signature(params, endpoint)

        try:
            response = requests.post(
                "https://auth.tiktok-shops.com/api/v2/token/refresh",
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"Token refresh failed: {data.get('message')}")

            result = data.get("data", {})

            logger.info("✅ Refreshed TikTok Shop access token")

            return {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "access_token_expire_in": result.get("access_token_expire_in"),
                "refresh_token_expire_in": result.get("refresh_token_expire_in"),
            }

        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

    async def get_seller_info(self, access_token: str, shop_id: str) -> Dict[str, Any]:
        """
        Fetch seller shop information

        Args:
            access_token: Shop's access token
            shop_id: Shop ID

        Returns:
            Shop details
        """
        endpoint = "/api/shop/get_authorized_shop"
        timestamp = str(int(time.time()))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "access_token": access_token,
            "shop_id": shop_id,
        }

        params["sign"] = self._generate_signature(params, endpoint)

        try:
            response = requests.get(
                f"https://open-api.tiktok.com{endpoint}",
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"Failed to get seller info: {data.get('message')}")

            result = data.get("data", {})

            logger.info(f"Fetched TikTok seller info: {result.get('shop_name')}")

            return {
                "shop_id": result.get("shop_id"),
                "shop_name": result.get("shop_name"),
                "shop_cipher": result.get("shop_cipher"),
                "region": result.get("region"),
                "seller_type": result.get("seller_type"),
            }

        except Exception as e:
            logger.error(f"Failed to fetch seller info: {e}")
            raise

    async def revoke_access(self, access_token: str, shop_id: str):
        """
        Revoke app authorization (uninstall)

        Args:
            access_token: Shop's access token
            shop_id: Shop ID
        """
        endpoint = "/api/v2/token/revoke"
        timestamp = str(int(time.time()))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "access_token": access_token,
            "shop_id": shop_id,
        }

        params["sign"] = self._generate_signature(params, endpoint)

        try:
            response = requests.post(
                f"https://auth.tiktok-shops.com{endpoint}",
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()

            logger.info(f"Revoked access for TikTok shop: {shop_id}")

        except Exception as e:
            logger.error(f"Failed to revoke access: {e}")
            raise
