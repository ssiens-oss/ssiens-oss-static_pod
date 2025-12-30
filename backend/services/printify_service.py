"""
Printify Integration Service
"""
import requests
from typing import List, Dict, Any, Optional
from loguru import logger

from config.settings import settings


class PrintifyService:
    """Service for Printify POD operations"""

    def __init__(self):
        self.base_url = "https://api.printify.com/v1"
        self.api_token = settings.PRINTIFY_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def create_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create POD product in Printify"""
        try:
            url = f"{self.base_url}/shops/{{shop_id}}/products.json"

            payload = {
                "title": data.get("title"),
                "description": data.get("description"),
                "blueprint_id": data.get("blueprint_id"),
                "print_provider_id": data.get("print_provider_id"),
                "variants": data.get("variants", []),
                "print_areas": data.get("print_areas", []),
            }

            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            product = response.json()
            logger.info(f"Created Printify product: {product.get('id')}")

            return product

        except Exception as e:
            logger.error(f"Error creating Printify product: {e}")
            raise

    async def list_products(self) -> List[Dict[str, Any]]:
        """List Printify products"""
        try:
            url = f"{self.base_url}/shops/{{shop_id}}/products.json"

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            products = data.get("data", [])

            return products

        except Exception as e:
            logger.error(f"Error listing Printify products: {e}")
            return []

    async def create_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create order in Printify"""
        try:
            url = f"{self.base_url}/shops/{{shop_id}}/orders.json"

            payload = {
                "external_id": data.get("external_id"),
                "line_items": data.get("line_items", []),
                "shipping_method": data.get("shipping_method", 1),
                "address_to": data.get("address_to"),
                "send_shipping_notification": True,
            }

            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            order = response.json()
            logger.info(f"Created Printify order: {order.get('id')}")

            return order

        except Exception as e:
            logger.error(f"Error creating Printify order: {e}")
            raise

    async def get_blueprints(self) -> List[Dict[str, Any]]:
        """Get available product blueprints"""
        try:
            url = f"{self.base_url}/catalog/blueprints.json"

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            blueprints = response.json()
            return blueprints

        except Exception as e:
            logger.error(f"Error getting blueprints: {e}")
            return []
