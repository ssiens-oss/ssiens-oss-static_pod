"""
StaticWaves Forge - Asset Pack Routes
Endpoints for creating and managing asset packs
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List
import uuid
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../packages'))

from common.schemas import AssetPackMetadata

router = APIRouter()

# In-memory pack storage
packs_db = {}

@router.post("/", response_model=AssetPackMetadata)
async def create_pack(
    name: str,
    description: str,
    asset_ids: List[str],
    price: float = 0.0,
    tags: Optional[List[str]] = None
):
    """
    Create a new asset pack from existing assets

    This endpoint:
    1. Collects specified assets
    2. Packages them for various marketplaces
    3. Generates metadata and documentation
    4. Creates downloadable bundles
    """
    pack_id = str(uuid.uuid4())

    # TODO: Validate that all asset_ids exist
    # TODO: Actually package the assets

    pack_metadata = AssetPackMetadata(
        pack_id=pack_id,
        name=name,
        description=description,
        price=price,
        asset_count=len(asset_ids),
        tags=tags or [],
        version="1.0.0",
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        formats=["unity", "unreal", "roblox", "glb"],
        total_size_mb=len(asset_ids) * 2.5  # Mock calculation
    )

    packs_db[pack_id] = pack_metadata.dict()

    return pack_metadata

@router.get("/{pack_id}", response_model=AssetPackMetadata)
async def get_pack(pack_id: str):
    """Get metadata for a specific asset pack"""
    if pack_id not in packs_db:
        raise HTTPException(status_code=404, detail="Pack not found")

    return AssetPackMetadata(**packs_db[pack_id])

@router.get("/", response_model=List[AssetPackMetadata])
async def list_packs(
    limit: int = 50,
    offset: int = 0,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    List all available asset packs

    Filters:
    - min_price: Minimum pack price
    - max_price: Maximum pack price
    """
    packs = list(packs_db.values())

    # Filter by price
    if min_price is not None:
        packs = [p for p in packs if p["price"] >= min_price]
    if max_price is not None:
        packs = [p for p in packs if p["price"] <= max_price]

    # Pagination
    packs = packs[offset:offset + limit]

    return [AssetPackMetadata(**p) for p in packs]

@router.post("/{pack_id}/export/{format}")
async def export_pack(pack_id: str, format: str):
    """
    Export pack in specific marketplace format

    Formats:
    - unity: Unity Asset Store package
    - unreal: Unreal Marketplace package
    - roblox: Roblox Creator Store bundle
    - gumroad: Multi-format Gumroad package
    """
    if pack_id not in packs_db:
        raise HTTPException(status_code=404, detail="Pack not found")

    valid_formats = ["unity", "unreal", "roblox", "gumroad"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
        )

    # TODO: Actually generate the export
    # Call packager/build_pack.py with appropriate parameters

    download_url = f"/downloads/{pack_id}/{format}/{pack_id}.zip"

    return {
        "pack_id": pack_id,
        "format": format,
        "download_url": download_url,
        "expires_at": "2026-01-08T00:00:00Z"
    }

@router.delete("/{pack_id}")
async def delete_pack(pack_id: str):
    """Delete an asset pack"""
    if pack_id not in packs_db:
        raise HTTPException(status_code=404, detail="Pack not found")

    del packs_db[pack_id]

    return {"message": "Pack deleted successfully", "pack_id": pack_id}

@router.get("/presets/list")
async def get_pack_presets():
    """
    Get predefined pack templates for quick creation

    These are curated pack ideas that can be auto-generated
    """
    presets = [
        {
            "name": "Fantasy Creatures Starter",
            "description": "25 stylized fantasy creatures with animations",
            "asset_type": "creature",
            "count": 25,
            "suggested_price": 39,
            "tags": ["fantasy", "creatures", "lowpoly", "animated"]
        },
        {
            "name": "Sci-Fi Props Mega Kit",
            "description": "60 sci-fi props including crates, consoles, and doors",
            "asset_type": "prop",
            "count": 60,
            "suggested_price": 49,
            "tags": ["scifi", "props", "environment", "modular"]
        },
        {
            "name": "Low-Poly Environment Pack",
            "description": "40 buildings and terrain chunks for mobile games",
            "asset_type": "building",
            "count": 40,
            "suggested_price": 29,
            "tags": ["lowpoly", "environment", "mobile", "buildings"]
        },
        {
            "name": "Weapon Arsenal Collection",
            "description": "30 game-ready weapons with LODs",
            "asset_type": "weapon",
            "count": 30,
            "suggested_price": 35,
            "tags": ["weapons", "combat", "fps", "gameready"]
        }
    ]

    return presets

@router.post("/presets/{preset_name}/generate")
async def generate_from_preset(preset_name: str, background_tasks: BackgroundTasks):
    """
    Auto-generate an entire pack from a preset template

    This will:
    1. Generate all assets in the pack
    2. Package them together
    3. Create marketplace-ready bundles
    """
    # TODO: Implement preset-based generation
    # This would loop through asset generation for each item in the preset

    pack_id = str(uuid.uuid4())

    return {
        "pack_id": pack_id,
        "status": "generating",
        "message": f"Generating pack from preset: {preset_name}",
        "estimated_time_minutes": 15
    }
