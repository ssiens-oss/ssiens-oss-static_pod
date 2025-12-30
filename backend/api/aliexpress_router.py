"""
AliExpress Integration API Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from services.aliexpress_service import AliExpressService

router = APIRouter()
ali_service = AliExpressService()


class ProductSearchRequest(BaseModel):
    keywords: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_orders: Optional[int] = 100
    limit: int = 20


class OrderPlaceRequest(BaseModel):
    shopify_order_id: str
    products: List[Dict[str, Any]]
    shipping_address: Dict[str, Any]


@router.post("/products/search")
async def search_products(request: ProductSearchRequest):
    """Search for products on AliExpress"""
    try:
        products = await ali_service.search_products(
            keywords=request.keywords,
            min_price=request.min_price,
            max_price=request.max_price,
            min_orders=request.min_orders,
            limit=request.limit,
        )

        return {
            "success": True,
            "data": products,
            "count": len(products),
        }
    except Exception as e:
        logger.error(f"Error searching AliExpress products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get detailed product information"""
    try:
        product = await ali_service.get_product_details(product_id)
        return {"success": True, "data": product}
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/place")
async def place_order(request: OrderPlaceRequest, background_tasks: BackgroundTasks):
    """Place order on AliExpress (for fulfillment)"""
    try:
        # Add to background tasks for async processing
        background_tasks.add_task(
            ali_service.place_order,
            request.shopify_order_id,
            request.products,
            request.shipping_address,
        )

        return {
            "success": True,
            "message": "Order placement initiated",
            "shopify_order_id": request.shopify_order_id,
        }
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}/status")
async def get_order_status(order_id: str):
    """Get order status from AliExpress"""
    try:
        status = await ali_service.get_order_status(order_id)
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get AliExpress product categories"""
    try:
        categories = await ali_service.get_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/refresh")
async def refresh_token():
    """Refresh AliExpress API access token"""
    try:
        result = await ali_service.refresh_access_token()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
