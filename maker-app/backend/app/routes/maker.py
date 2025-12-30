"""
Maker API routes - Image, Video, Music, Book generation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.deps import get_current_user, charge_tokens, track_usage, TOKEN_COST
from app.models import GenerationJob
from app.services import image, video, music, book

router = APIRouter(prefix="/maker", tags=["maker"])


class GenerateRequest(BaseModel):
    prompt: str
    style: Optional[str] = None  # For advanced customization (paid tier)
    output_format: Optional[str] = None


class GenerateResponse(BaseModel):
    job_id: int
    status: str
    tokens_used: int
    estimated_completion: int  # seconds


@router.post("/generate/image", response_model=GenerateResponse)
async def generate_image(
    req: GenerateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an AI image from prompt"""
    cost = TOKEN_COST["image"]

    # Charge tokens
    balance = charge_tokens(db, user["brand_id"], cost)

    # Create job
    job = GenerationJob(
        brand_id=user["brand_id"],
        type="image",
        prompt=req.prompt,
        tokens_used=cost,
        output_format=req.output_format or "png"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Track usage
    track_usage(db, user["brand_id"], "image", cost)

    # Enqueue to worker
    image.enqueue(job.id, req.prompt, req.style)

    return {
        "job_id": job.id,
        "status": "queued",
        "tokens_used": cost,
        "estimated_completion": 15  # 15 seconds
    }


@router.post("/generate/video", response_model=GenerateResponse)
async def generate_video(
    req: GenerateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an AI video from prompt"""
    cost = TOKEN_COST["video"]

    balance = charge_tokens(db, user["brand_id"], cost)

    job = GenerationJob(
        brand_id=user["brand_id"],
        type="video",
        prompt=req.prompt,
        tokens_used=cost,
        output_format=req.output_format or "mp4"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    track_usage(db, user["brand_id"], "video", cost)

    # Enqueue to worker
    video.enqueue(job.id, req.prompt, req.style)

    return {
        "job_id": job.id,
        "status": "queued",
        "tokens_used": cost,
        "estimated_completion": 45  # 45 seconds
    }


@router.post("/generate/music", response_model=GenerateResponse)
async def generate_music(
    req: GenerateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI music from prompt"""
    cost = TOKEN_COST["music"]

    balance = charge_tokens(db, user["brand_id"], cost)

    job = GenerationJob(
        brand_id=user["brand_id"],
        type="music",
        prompt=req.prompt,
        tokens_used=cost,
        output_format=req.output_format or "mp3"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    track_usage(db, user["brand_id"], "music", cost)

    # Enqueue to worker
    music.enqueue(job.id, req.prompt, req.style)

    return {
        "job_id": job.id,
        "status": "queued",
        "tokens_used": cost,
        "estimated_completion": 30  # 30 seconds
    }


@router.post("/generate/book", response_model=GenerateResponse)
async def generate_book(
    req: GenerateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an AI book from prompt"""
    cost = TOKEN_COST["book"]

    balance = charge_tokens(db, user["brand_id"], cost)

    job = GenerationJob(
        brand_id=user["brand_id"],
        type="book",
        prompt=req.prompt,
        tokens_used=cost,
        output_format=req.output_format or "pdf"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    track_usage(db, user["brand_id"], "book", cost)

    # Enqueue to worker
    book.enqueue(job.id, req.prompt, req.output_format or "pdf")

    return {
        "job_id": job.id,
        "status": "queued",
        "tokens_used": cost,
        "estimated_completion": 90  # 90 seconds
    }


@router.get("/job/{job_id}")
async def get_job_status(
    job_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check generation job status"""
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id,
        GenerationJob.brand_id == user["brand_id"]
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "type": job.type,
        "status": job.status,
        "output_url": job.output_url,
        "output_format": job.output_format,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message
    }


@router.get("/queue")
async def get_queue(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get user's recent generation jobs"""
    jobs = db.query(GenerationJob).filter(
        GenerationJob.brand_id == user["brand_id"]
    ).order_by(GenerationJob.created_at.desc()).limit(limit).all()

    return {
        "jobs": [
            {
                "job_id": job.id,
                "type": job.type,
                "prompt": job.prompt[:100],  # Truncate long prompts
                "status": job.status,
                "output_url": job.output_url,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ]
    }
