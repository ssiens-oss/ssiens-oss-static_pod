"""
Shopify Integration API Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from services.shopify_service import ShopifyService
from config.settings import settings

router = APIRouter()
shopify_service = ShopifyService()


class ProductImportRequest(BaseModel):
    product_ids: List[str]
    platform: str = "shopify"
    markup_percentage: float = 30.0


class OrderSyncRequest(BaseModel):
    order_ids: Optional[List[str]] = None
    status_filter: Optional[str] = None


class ProductPublishRequest(BaseModel):
    product_id: int
    platforms: List[str]  # e.g., ["tiktok", "instagram", "facebook"]


@router.get("/products")
async def list_shopify_products(
    limit: int = 50,
    page: int = 1,
    status: Optional[str] = None,
):
    """List products from Shopify store"""
    try:
        products = await shopify_service.list_products(
            limit=limit,
            page=page,
            status=status,
        )
        return {
            "success": True,
            "data": products,
            "count": len(products),
        }
    except Exception as e:
        logger.error(f"Error listing Shopify products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/import")
async def import_products(request: ProductImportRequest, background_tasks: BackgroundTasks):
    """Import products from supplier to Shopify"""
    try:
        # Add background task for async processing
        background_tasks.add_task(
            shopify_service.import_products,
            request.product_ids,
            request.platform,
            request.markup_percentage,
        )

        return {
            "success": True,
            "message": f"Import started for {len(request.product_ids)} products",
            "product_ids": request.product_ids,
        }
    except Exception as e:
        logger.error(f"Error importing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get specific product from Shopify"""
    try:
        product = await shopify_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"success": True, "data": product}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/products/{product_id}")
async def update_product(product_id: str, data: Dict[str, Any]):
    """Update product in Shopify"""
    try:
        updated_product = await shopify_service.update_product(product_id, data)
        return {"success": True, "data": updated_product}
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/publish")
async def publish_to_platforms(request: ProductPublishRequest):
    """Publish Shopify product to other platforms (TikTok, Instagram, etc.)"""
    try:
        results = await shopify_service.publish_to_platforms(
            request.product_id,
            request.platforms,
        )
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Error publishing product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def list_orders(
    limit: int = 50,
    status: Optional[str] = None,
):
    """List orders from Shopify"""
    try:
        orders = await shopify_service.list_orders(limit=limit, status=status)
        return {"success": True, "data": orders, "count": len(orders)}
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/sync")
async def sync_orders(request: OrderSyncRequest, background_tasks: BackgroundTasks):
    """Sync orders from Shopify to database"""
    try:
        background_tasks.add_task(
            shopify_service.sync_orders,
            request.order_ids,
            request.status_filter,
        )

        return {
            "success": True,
            "message": "Order sync started",
        }
    except Exception as e:
        logger.error(f"Error syncing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/{order_id}/fulfill")
async def fulfill_order(order_id: str):
    """Fulfill an order (trigger supplier fulfillment)"""
    try:
        result = await shopify_service.fulfill_order(order_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error fulfilling order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/sync")
async def sync_inventory():
    """Sync inventory levels from suppliers"""
    try:
        result = await shopify_service.sync_inventory()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error syncing inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/orders")
async def order_webhook(data: Dict[str, Any]):
    """Handle Shopify order webhooks"""
    try:
        # Process order webhook
        result = await shopify_service.handle_order_webhook(data)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
