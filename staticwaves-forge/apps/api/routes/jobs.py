"""
StaticWaves Forge - Job Management Routes
Endpoints for tracking and managing generation jobs
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../packages'))

from common.schemas import GenerationResult, JobStatus

router = APIRouter()

# Import active jobs from generate module
from . import generate

@router.get("/{job_id}", response_model=GenerationResult)
async def get_job_status(job_id: str):
    """
    Get the status of a specific generation job

    Returns:
    - Job status (queued, processing, completed, failed)
    - Progress percentage (0.0 - 1.0)
    - Asset metadata (if completed)
    - Output file paths (if completed)
    - Error message (if failed)
    """
    if job_id not in generate.active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = generate.active_jobs[job_id]
    return GenerationResult(**job_data)

@router.get("/", response_model=List[GenerationResult])
async def list_jobs(
    status: Optional[JobStatus] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List all generation jobs

    Filters:
    - status: Filter by job status
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    jobs = list(generate.active_jobs.values())

    # Filter by status if provided
    if status:
        jobs = [j for j in jobs if j["status"] == status]

    # Pagination
    jobs = jobs[offset:offset + limit]

    return [GenerationResult(**j) for j in jobs]

@router.delete("/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a queued or processing job

    Note: Cannot cancel completed jobs
    """
    if job_id not in generate.active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = generate.active_jobs[job_id]

    if job["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in {job['status']} status"
        )

    # Update job status
    job["status"] = JobStatus.CANCELLED
    generate.active_jobs[job_id] = job

    return {"message": "Job cancelled successfully", "job_id": job_id}

@router.post("/{job_id}/retry", response_model=GenerationResult)
async def retry_failed_job(job_id: str):
    """
    Retry a failed generation job

    Only works for jobs in FAILED status
    """
    if job_id not in generate.active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = generate.active_jobs[job_id]

    if job["status"] != JobStatus.FAILED:
        raise HTTPException(
            status_code=400,
            detail="Can only retry failed jobs"
        )

    # Reset job status
    job["status"] = JobStatus.QUEUED
    job["progress"] = 0.0
    job["error_message"] = None

    generate.active_jobs[job_id] = job

    # TODO: Re-queue the job
    # background_tasks.add_task(process_generation_job, job_id, original_request)

    return GenerationResult(**job)

@router.get("/stats/summary")
async def get_job_stats():
    """
    Get summary statistics about all jobs
    """
    jobs = list(generate.active_jobs.values())

    stats = {
        "total": len(jobs),
        "queued": len([j for j in jobs if j["status"] == JobStatus.QUEUED]),
        "processing": len([j for j in jobs if j["status"] == JobStatus.PROCESSING]),
        "completed": len([j for j in jobs if j["status"] == JobStatus.COMPLETED]),
        "failed": len([j for j in jobs if j["status"] == JobStatus.FAILED]),
        "cancelled": len([j for j in jobs if j["status"] == JobStatus.CANCELLED])
    }

    return stats
