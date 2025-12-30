"""
AliExpress Integration Service
Based on AliExpress Open Platform API
"""
import requests
import hashlib
import hmac
import time
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

from config.settings import settings


class AliExpressService:
    """Service for AliExpress operations"""

    def __init__(self):
        self.base_url = "https://api-sg.aliexpress.com/rest"
        self.app_key = settings.ALIEXPRESS_APP_KEY
        self.app_secret = settings.ALIEXPRESS_APP_SECRET
        self.access_token = settings.ALIEXPRESS_ACCESS_TOKEN

    def _generate_signature(self, endpoint: str, params: Dict[str, str]) -> str:
        """Generate HMAC-SHA256 signature for API requests"""
        sorted_keys = sorted(params.keys())
        concatenated = endpoint + "".join([f"{key}{params[key]}" for key in sorted_keys])

        sign = hmac.new(
            self.app_secret.encode("utf-8"),
            concatenated.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

        return sign

    async def search_products(
        self,
        keywords: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_orders: Optional[int] = 100,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search for products on AliExpress"""
        try:
            endpoint = "/aliexpress.affiliate.product.query"
            timestamp = str(int(time.time() * 1000))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "sign_method": "sha256",
                "keywords": keywords,
                "page_size": str(limit),
            }

            if min_price:
                params["min_price"] = str(int(min_price * 100))  # Convert to cents
            if max_price:
                params["max_price"] = str(int(max_price * 100))

            # Generate signature
            params["sign"] = self._generate_signature(endpoint, params)

            # Make request
            url = self.base_url + endpoint
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response
            products = data.get("resp_result", {}).get("result", {}).get("products", [])

            # Filter by orders if needed
            if min_orders:
                products = [p for p in products if p.get("volume", 0) >= min_orders]

            logger.info(f"Found {len(products)} products for '{keywords}'")
            return products

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise

    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed product information"""
        try:
            endpoint = "/aliexpress.ds.product.get"
            timestamp = str(int(time.time() * 1000))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "sign_method": "sha256",
                "session": self.access_token,
                "product_id": product_id,
                "local_country": "US",
                "local_language": "en",
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            product = data.get("resp_result", {}).get("result", {})

            logger.info(f"Retrieved product details for {product_id}")
            return product

        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            raise

    async def place_order(
        self,
        shopify_order_id: str,
        products: List[Dict[str, Any]],
        shipping_address: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Place order on AliExpress for fulfillment"""
        try:
            endpoint = "/aliexpress.trade.buy.placeorder"
            timestamp = str(int(time.time() * 1000))

            # Prepare order data
            order_param = {
                "products": products,
                "buyer_address": {
                    "name": shipping_address.get("name"),
                    "address": shipping_address.get("address1"),
                    "city": shipping_address.get("city"),
                    "country": shipping_address.get("country"),
                    "zip": shipping_address.get("zip"),
                    "phone": shipping_address.get("phone"),
                },
            }

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "sign_method": "sha256",
                "session": self.access_token,
                "order_param": json.dumps(order_param),
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            result = data.get("resp_result", {}).get("result", {})

            logger.info(f"Placed order for Shopify order {shopify_order_id}")
            return result

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status from AliExpress"""
        try:
            endpoint = "/aliexpress.trade.seller.orderlist.get"
            timestamp = str(int(time.time() * 1000))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "sign_method": "sha256",
                "session": self.access_token,
                "order_id": order_id,
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            status = data.get("resp_result", {}).get("result", {})

            return status

        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get product categories"""
        try:
            endpoint = "/aliexpress.ds.category.get"
            timestamp = str(int(time.time() * 1000))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "sign_method": "sha256",
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            categories = data.get("resp_result", {}).get("result", {}).get("categories", [])

            return categories

        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise

    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh API access token"""
        try:
            endpoint = "/auth/token/refresh"
            timestamp = str(int(time.time() * 1000))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "sign_method": "sha256",
                "refresh_token": self.access_token,  # Assuming we have refresh token
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            result = data.get("resp_result", {}).get("result", {})

            # Update access token
            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Successfully refreshed AliExpress access token")

            return result

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
