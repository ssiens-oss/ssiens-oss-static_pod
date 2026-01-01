"""
StaticWaves Forge - Generation Routes
Endpoints for creating new 3D assets
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import uuid
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../packages'))

from common.schemas import (
    GenerationRequest,
    GenerationResult,
    JobStatus,
    AssetMetadata
)

router = APIRouter()

# In-memory job storage (replace with Redis/DB in production)
active_jobs = {}

async def process_generation_job(job_id: str, request: GenerationRequest):
    """
    Background task to process asset generation
    In production, this would dispatch to RunPod workers via queue
    """
    try:
        # Update job status
        active_jobs[job_id]["status"] = JobStatus.PROCESSING
        active_jobs[job_id]["progress"] = 0.1

        # Simulate processing stages
        # In production:
        # 1. Push job to Redis queue
        # 2. RunPod worker picks up job
        # 3. Blender scripts execute
        # 4. Assets uploaded to S3/R2
        # 5. Job marked complete

        time.sleep(2)  # Simulate mesh generation
        active_jobs[job_id]["progress"] = 0.4

        time.sleep(1)  # Simulate rigging
        active_jobs[job_id]["progress"] = 0.6

        time.sleep(1)  # Simulate animation
        active_jobs[job_id]["progress"] = 0.8

        time.sleep(1)  # Simulate export
        active_jobs[job_id]["progress"] = 1.0

        # Create mock asset metadata
        asset_metadata = AssetMetadata(
            asset_id=job_id,
            name=f"asset_{job_id[:8]}",
            asset_type=request.asset_type,
            style=request.style,
            poly_count=request.poly_budget or 10000,
            vertex_count=(request.poly_budget or 10000) * 3,
            has_rig=request.include_rig,
            animations=[anim.value for anim in request.include_animations],
            file_size_mb=2.5,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            seed=request.seed or 42
        )

        # Mock output files
        output_files = {
            fmt.value: f"/output/{job_id}/{job_id}.{fmt.value}"
            for fmt in request.export_formats
        }

        # Update job as completed
        active_jobs[job_id]["status"] = JobStatus.COMPLETED
        active_jobs[job_id]["asset_metadata"] = asset_metadata
        active_jobs[job_id]["output_files"] = output_files

    except Exception as e:
        active_jobs[job_id]["status"] = JobStatus.FAILED
        active_jobs[job_id]["error_message"] = str(e)

@router.post("/", response_model=GenerationResult)
async def create_generation_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new asset generation job

    This endpoint:
    1. Validates the request
    2. Generates a unique job ID
    3. Queues the job for processing
    4. Returns immediately with job ID for tracking
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Set seed if not provided
    if request.seed is None:
        request.seed = int(time.time() * 1000) % 2147483647

    # Create job record
    job_result = GenerationResult(
        job_id=job_id,
        status=JobStatus.QUEUED,
        progress=0.0
    )

    active_jobs[job_id] = job_result.dict()

    # Queue background processing
    background_tasks.add_task(process_generation_job, job_id, request)

    return job_result

@router.post("/batch", response_model=list[GenerationResult])
async def create_batch_generation(
    requests: list[GenerationRequest],
    background_tasks: BackgroundTasks
):
    """
    Create multiple asset generation jobs at once
    Useful for generating entire asset packs
    """
    results = []

    for req in requests:
        job_id = str(uuid.uuid4())

        if req.seed is None:
            req.seed = int(time.time() * 1000) % 2147483647

        job_result = GenerationResult(
            job_id=job_id,
            status=JobStatus.QUEUED,
            progress=0.0
        )

        active_jobs[job_id] = job_result.dict()
        background_tasks.add_task(process_generation_job, job_id, req)

        results.append(job_result)

    return results

@router.get("/quick", response_model=GenerationResult)
async def quick_generate(
    prompt: str,
    asset_type: str = "prop",
    background_tasks: BackgroundTasks = None
):
    """
    Quick generation endpoint with minimal parameters
    Useful for demos and testing
    """
    request = GenerationRequest(
        prompt=prompt,
        asset_type=asset_type,
        style="low-poly",
        export_formats=["glb"]
    )

    return await create_generation_job(request, background_tasks)
