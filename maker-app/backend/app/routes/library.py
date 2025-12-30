"""
Library routes - User's saved creations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.deps import get_current_user
from app.models import Library, GenerationJob

router = APIRouter(prefix="/library", tags=["library"])


class SaveCreationRequest(BaseModel):
    job_id: int
    title: Optional[str] = None


@router.get("/")
async def get_library(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's saved creations"""
    items = db.query(Library).filter(
        Library.brand_id == user["brand_id"]
    ).order_by(
        Library.favorited.desc(),
        Library.created_at.desc()
    ).limit(limit).offset(offset).all()

    results = []
    for item in items:
        job = db.query(GenerationJob).filter_by(id=item.job_id).first()
        if job:
            results.append({
                "id": item.id,
                "job_id": item.job_id,
                "title": item.title or job.prompt[:50],
                "type": job.type,
                "output_url": job.output_url,
                "output_format": job.output_format,
                "favorited": item.favorited,
                "downloads": item.downloads,
                "created_at": item.created_at.isoformat()
            })

    return {
        "items": results,
        "total": len(results)
    }


@router.post("/save")
async def save_to_library(
    req: SaveCreationRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a completed generation to library"""
    # Verify job belongs to user
    job = db.query(GenerationJob).filter(
        GenerationJob.id == req.job_id,
        GenerationJob.brand_id == user["brand_id"]
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    # Check if already saved
    existing = db.query(Library).filter(
        Library.brand_id == user["brand_id"],
        Library.job_id == req.job_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in library")

    # Save to library
    item = Library(
        brand_id=user["brand_id"],
        job_id=req.job_id,
        title=req.title
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "saved": True
    }


@router.post("/{item_id}/favorite")
async def toggle_favorite(
    item_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle favorite status"""
    item = db.query(Library).filter(
        Library.id == item_id,
        Library.brand_id == user["brand_id"]
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.favorited = not item.favorited
    db.commit()

    return {
        "id": item.id,
        "favorited": item.favorited
    }


@router.delete("/{item_id}")
async def delete_from_library(
    item_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from library"""
    item = db.query(Library).filter(
        Library.id == item_id,
        Library.brand_id == user["brand_id"]
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"deleted": True}


@router.post("/{item_id}/download")
async def track_download(
    item_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track download count"""
    item = db.query(Library).filter(
        Library.id == item_id,
        Library.brand_id == user["brand_id"]
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.downloads += 1
    db.commit()

    return {"downloads": item.downloads}
