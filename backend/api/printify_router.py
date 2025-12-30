"""
Printify Integration API Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from services.printify_service import PrintifyService

router = APIRouter()
printify_service = PrintifyService()


class ProductCreateRequest(BaseModel):
    title: str
    description: str
    blueprint_id: int
    print_provider_id: int
    variants: List[Dict[str, Any]]
    print_areas: List[Dict[str, Any]]


@router.post("/products/create")
async def create_product(request: ProductCreateRequest):
    """Create POD product in Printify"""
    try:
        product = await printify_service.create_product(request.dict())
        return {"success": True, "data": product}
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def list_products():
    """List Printify products"""
    try:
        products = await printify_service.list_products()
        return {"success": True, "data": products}
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/create")
async def create_order(data: Dict[str, Any]):
    """Create order in Printify"""
    try:
        order = await printify_service.create_order(data)
        return {"success": True, "data": order}
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/blueprints")
async def get_blueprints():
    """Get available product blueprints"""
    try:
        blueprints = await printify_service.get_blueprints()
        return {"success": True, "data": blueprints}
    except Exception as e:
        logger.error(f"Error getting blueprints: {e}")
        raise HTTPException(status_code=500, detail=str(e))
