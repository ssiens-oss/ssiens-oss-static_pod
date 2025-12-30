"""
TikTok Shop Integration API Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from services.tiktok_service import TikTokService

router = APIRouter()
tiktok_service = TikTokService()


class ProductSyncRequest(BaseModel):
    shopify_product_ids: List[int]


class CampaignCreateRequest(BaseModel):
    name: str
    budget: float
    products: List[int]
    objective: str = "SHOP_PURCHASES"


@router.post("/products/sync")
async def sync_products(request: ProductSyncRequest, background_tasks: BackgroundTasks):
    """Sync Shopify products to TikTok Shop"""
    try:
        background_tasks.add_task(
            tiktok_service.sync_products,
            request.shopify_product_ids,
        )

        return {
            "success": True,
            "message": f"Syncing {len(request.shopify_product_ids)} products to TikTok",
        }
    except Exception as e:
        logger.error(f"Error syncing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def list_products():
    """List products from TikTok Shop"""
    try:
        products = await tiktok_service.list_products()
        return {"success": True, "data": products}
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def list_orders(status: Optional[str] = "AWAITING_SHIPMENT"):
    """List orders from TikTok Shop"""
    try:
        orders = await tiktok_service.list_orders(status)
        return {"success": True, "data": orders}
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/sync")
async def sync_orders(background_tasks: BackgroundTasks):
    """Sync TikTok orders to Shopify"""
    try:
        background_tasks.add_task(tiktok_service.sync_orders_to_shopify)
        return {"success": True, "message": "Order sync initiated"}
    except Exception as e:
        logger.error(f"Error syncing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/create")
async def create_campaign(request: CampaignCreateRequest):
    """Create ad campaign for TikTok"""
    try:
        result = await tiktok_service.create_ad_campaign(
            name=request.name,
            budget=request.budget,
            products=request.products,
            objective=request.objective,
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics(start_date: str, end_date: str):
    """Get TikTok Shop analytics"""
    try:
        analytics = await tiktok_service.get_analytics(start_date, end_date)
        return {"success": True, "data": analytics}
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
