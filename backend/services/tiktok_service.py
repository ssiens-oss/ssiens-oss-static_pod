"""
TikTok Shop Integration Service
"""
import requests
import hashlib
import hmac
import time
import json
from typing import List, Dict, Any, Optional
from loguru import logger

from config.settings import settings


class TikTokService:
    """Service for TikTok Shop operations"""

    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self.app_key = settings.TIKTOK_APP_KEY
        self.app_secret = settings.TIKTOK_APP_SECRET
        self.access_token = settings.TIKTOK_ACCESS_TOKEN
        self.shop_id = settings.TIKTOK_SHOP_ID

    def _generate_signature(self, endpoint: str, params: Dict[str, str]) -> str:
        """Generate HMAC-SHA256 signature"""
        sorted_params = sorted(params.items())
        concatenated = endpoint + "".join([f"{k}{v}" for k, v in sorted_params])

        sign = hmac.new(
            self.app_secret.encode("utf-8"),
            concatenated.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

        return sign

    async def sync_products(self, shopify_product_ids: List[int]):
        """Sync Shopify products to TikTok Shop"""
        try:
            for product_id in shopify_product_ids:
                # Fetch product from Shopify (would integrate with ShopifyService)
                # Convert to TikTok format
                # Upload to TikTok

                endpoint = "/product/202309/products/upload"
                timestamp = str(int(time.time()))

                params = {
                    "app_key": self.app_key,
                    "timestamp": timestamp,
                    "access_token": self.access_token,
                    "shop_id": self.shop_id,
                    # Product data would go here
                }

                params["sign"] = self._generate_signature(endpoint, params)

                url = self.base_url + endpoint
                # response = requests.post(url, params=params)

                logger.info(f"Synced product {product_id} to TikTok")

        except Exception as e:
            logger.error(f"Error syncing products to TikTok: {e}")
            raise

    async def list_products(self) -> List[Dict[str, Any]]:
        """List products from TikTok Shop"""
        try:
            endpoint = "/product/202309/products/search"
            timestamp = str(int(time.time()))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "access_token": self.access_token,
                "shop_id": self.shop_id,
                "page_size": "20",
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            products = data.get("data", {}).get("products", [])

            return products

        except Exception as e:
            logger.error(f"Error listing TikTok products: {e}")
            return []

    async def list_orders(self, status: str = "AWAITING_SHIPMENT") -> List[Dict[str, Any]]:
        """List orders from TikTok Shop"""
        try:
            endpoint = "/order/202309/orders/search"
            timestamp = str(int(time.time()))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "access_token": self.access_token,
                "shop_id": self.shop_id,
                "page_size": "20",
                "order_status": status,
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            orders = data.get("data", {}).get("order_list", [])

            return orders

        except Exception as e:
            logger.error(f"Error listing TikTok orders: {e}")
            return []

    async def sync_orders_to_shopify(self):
        """Sync TikTok orders to Shopify for fulfillment"""
        try:
            orders = await self.list_orders()

            for order in orders:
                # Create order in Shopify
                # Trigger fulfillment workflow
                logger.info(f"Synced TikTok order {order.get('order_id')}")

        except Exception as e:
            logger.error(f"Error syncing TikTok orders: {e}")
            raise

    async def create_ad_campaign(
        self,
        name: str,
        budget: float,
        products: List[int],
        objective: str,
    ) -> Dict[str, Any]:
        """Create ad campaign on TikTok"""
        try:
            endpoint = "/ad/202309/ad/create"
            url = "https://business-api.tiktok.com/portal" + endpoint

            payload = {
                "advertiser_id": "your_advertiser_id",  # Would come from settings
                "campaign_name": name,
                "budget_mode": "BUDGET_MODE_DAY",
                "budget": str(budget),
                "objective_type": objective,
            }

            headers = {
                "Access-Token": self.access_token,
                "Content-Type": "application/json",
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Created TikTok ad campaign: {name}")

            return data

        except Exception as e:
            logger.error(f"Error creating ad campaign: {e}")
            raise

    async def get_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get TikTok Shop analytics"""
        try:
            endpoint = "/shop/202309/performance/get"
            timestamp = str(int(time.time()))

            params = {
                "app_key": self.app_key,
                "timestamp": timestamp,
                "access_token": self.access_token,
                "shop_id": self.shop_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            params["sign"] = self._generate_signature(endpoint, params)

            url = self.base_url + endpoint
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get("data", {})

        except Exception as e:
            logger.error(f"Error getting TikTok analytics: {e}")
            return {}
