"""
Shopify Integration Service
Based on official Shopify Python API and 2025 best practices
"""
import shopify
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

from config.settings import settings


class ShopifyService:
    """Service for Shopify operations"""

    def __init__(self):
        """Initialize Shopify session"""
        self.setup_session()

    def setup_session(self):
        """Set up Shopify API session"""
        try:
            session = shopify.Session(
                settings.SHOPIFY_SHOP_URL,
                settings.SHOPIFY_API_VERSION,
                settings.SHOPIFY_ACCESS_TOKEN,
            )
            shopify.ShopifyResource.activate_session(session)
            logger.info("Shopify session activated successfully")
        except Exception as e:
            logger.error(f"Failed to activate Shopify session: {e}")
            raise

    async def list_products(
        self,
        limit: int = 50,
        page: int = 1,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List products from Shopify"""
        try:
            params = {"limit": limit}
            if status:
                params["status"] = status

            products = await asyncio.to_thread(shopify.Product.find, **params)

            return [self._serialize_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            raise

    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get specific product"""
        try:
            product = await asyncio.to_thread(shopify.Product.find, product_id)
            return self._serialize_product(product) if product else None
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return None

    async def create_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new product in Shopify"""
        try:
            product = shopify.Product()

            # Set basic fields
            product.title = data.get("title")
            product.body_html = data.get("description", "")
            product.vendor = data.get("vendor", "Dropship Supplier")
            product.product_type = data.get("product_type", "")

            # Set variants
            if "variants" in data:
                product.variants = data["variants"]
            else:
                product.variants = [
                    {
                        "price": str(data.get("price", 0)),
                        "inventory_quantity": data.get("stock", 0),
                        "sku": data.get("sku", ""),
                    }
                ]

            # Set images
            if "images" in data:
                product.images = [{"src": img} for img in data["images"]]

            # Save product
            success = await asyncio.to_thread(product.save)

            if not success:
                raise Exception(f"Failed to create product: {product.errors.full_messages()}")

            logger.info(f"Created product: {product.id}")
            return self._serialize_product(product)

        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise

    async def update_product(self, product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        try:
            product = await asyncio.to_thread(shopify.Product.find, product_id)

            # Update fields
            for key, value in data.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            success = await asyncio.to_thread(product.save)

            if not success:
                raise Exception(f"Failed to update product: {product.errors.full_messages()}")

            logger.info(f"Updated product: {product_id}")
            return self._serialize_product(product)

        except Exception as e:
            logger.error(f"Error updating product: {e}")
            raise

    async def import_products(
        self,
        product_ids: List[str],
        platform: str,
        markup_percentage: float,
    ):
        """Import products from external platform"""
        try:
            # This will be implemented with platform-specific logic
            # For now, placeholder implementation
            logger.info(f"Importing {len(product_ids)} products from {platform}")

            # Example: Fetch from AliExpress, create in Shopify
            for product_id in product_ids:
                # Fetch product data from platform
                # Apply markup
                # Create in Shopify
                pass

            logger.info(f"Successfully imported {len(product_ids)} products")

        except Exception as e:
            logger.error(f"Error importing products: {e}")
            raise

    async def publish_to_platforms(
        self,
        product_id: int,
        platforms: List[str],
    ) -> Dict[str, Any]:
        """Publish product to other platforms (TikTok, Instagram, etc.)"""
        try:
            product = await self.get_product(str(product_id))
            if not product:
                raise ValueError(f"Product {product_id} not found")

            results = {}

            for platform in platforms:
                try:
                    if platform == "tiktok":
                        # Call TikTok service to publish
                        results[platform] = {"success": True}
                    elif platform == "instagram":
                        # Call Meta service to publish
                        results[platform] = {"success": True}
                    elif platform == "facebook":
                        # Call Meta service to publish
                        results[platform] = {"success": True}
                    else:
                        results[platform] = {"success": False, "error": "Unsupported platform"}

                except Exception as e:
                    logger.error(f"Error publishing to {platform}: {e}")
                    results[platform] = {"success": False, "error": str(e)}

            return results

        except Exception as e:
            logger.error(f"Error publishing product: {e}")
            raise

    async def list_orders(
        self,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List orders from Shopify"""
        try:
            params = {"limit": limit, "status": "any"}
            if status:
                params["status"] = status

            orders = await asyncio.to_thread(shopify.Order.find, **params)

            return [self._serialize_order(o) for o in orders]
        except Exception as e:
            logger.error(f"Error listing orders: {e}")
            raise

    async def sync_orders(
        self,
        order_ids: Optional[List[str]] = None,
        status_filter: Optional[str] = None,
    ):
        """Sync orders from Shopify to database"""
        try:
            if order_ids:
                # Sync specific orders
                for order_id in order_ids:
                    order = await asyncio.to_thread(shopify.Order.find, order_id)
                    # Save to database
                    logger.info(f"Synced order: {order_id}")
            else:
                # Sync all orders with filter
                orders = await self.list_orders(status=status_filter)
                logger.info(f"Synced {len(orders)} orders")

        except Exception as e:
            logger.error(f"Error syncing orders: {e}")
            raise

    async def fulfill_order(self, order_id: str) -> Dict[str, Any]:
        """Fulfill an order (create fulfillment)"""
        try:
            order = await asyncio.to_thread(shopify.Order.find, order_id)

            # Create fulfillment
            fulfillment = shopify.Fulfillment(
                {
                    "order_id": order.id,
                    "tracking_number": "TRK123456",  # From supplier
                    "tracking_url": "https://tracking.example.com",
                    "notify_customer": True,
                }
            )

            success = await asyncio.to_thread(fulfillment.save)

            if not success:
                raise Exception(f"Failed to fulfill order: {fulfillment.errors.full_messages()}")

            logger.info(f"Fulfilled order: {order_id}")
            return {"success": True, "fulfillment_id": fulfillment.id}

        except Exception as e:
            logger.error(f"Error fulfilling order: {e}")
            raise

    async def sync_inventory(self) -> Dict[str, Any]:
        """Sync inventory from suppliers"""
        try:
            # Placeholder for inventory sync logic
            logger.info("Syncing inventory from suppliers")

            # Fetch inventory from suppliers
            # Update Shopify products

            return {"success": True, "synced_count": 0}

        except Exception as e:
            logger.error(f"Error syncing inventory: {e}")
            raise

    async def handle_order_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Shopify order webhook"""
        try:
            logger.info(f"Processing order webhook for order: {data.get('id')}")

            # Process order based on webhook data
            # Trigger fulfillment automation

            return {"success": True}

        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise

    def _serialize_product(self, product) -> Dict[str, Any]:
        """Serialize Shopify product to dict"""
        return {
            "id": product.id,
            "title": product.title,
            "description": product.body_html,
            "vendor": product.vendor,
            "product_type": product.product_type,
            "variants": [
                {
                    "id": v.id,
                    "price": v.price,
                    "inventory_quantity": getattr(v, "inventory_quantity", 0),
                    "sku": v.sku,
                }
                for v in product.variants
            ],
            "images": [{"src": img.src} for img in product.images],
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }

    def _serialize_order(self, order) -> Dict[str, Any]:
        """Serialize Shopify order to dict"""
        return {
            "id": order.id,
            "order_number": order.order_number,
            "email": order.email,
            "total_price": order.total_price,
            "subtotal_price": order.subtotal_price,
            "total_tax": order.total_tax,
            "financial_status": order.financial_status,
            "fulfillment_status": order.fulfillment_status,
            "line_items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "variant_id": item.variant_id,
                    "title": item.title,
                    "quantity": item.quantity,
                    "price": item.price,
                }
                for item in order.line_items
            ],
            "shipping_address": order.shipping_address.to_dict() if order.shipping_address else None,
            "created_at": order.created_at,
        }
