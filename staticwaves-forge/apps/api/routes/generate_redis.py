"""
StaticWaves Forge - Generation Routes (Redis Queue Implementation)
Endpoints for creating new 3D assets with Redis job queue
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid
import time
import sys
import os
import json
import redis

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../packages'))

from common.schemas import (
    GenerationRequest,
    GenerationResult,
    JobStatus,
    AssetMetadata
)

router = APIRouter()

# Redis connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Queue names
QUEUE_HIGH = 'generation:high'
QUEUE_NORMAL = 'generation:normal'
QUEUE_LOW = 'generation:low'


def get_queue_name(priority: str = 'normal') -> str:
    """Get queue name based on priority"""
    queues = {
        'high': QUEUE_HIGH,
        'normal': QUEUE_NORMAL,
        'low': QUEUE_LOW
    }
    return queues.get(priority, QUEUE_NORMAL)


@router.post("/", response_model=GenerationResult)
async def create_generation_job(request: GenerationRequest, priority: str = 'normal'):
    """
    Create a new asset generation job

    This endpoint:
    1. Validates the request
    2. Generates a unique job ID
    3. Enqueues the job to Redis
    4. Returns immediately with job ID for tracking
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Set seed if not provided
    if request.seed is None:
        request.seed = int(time.time() * 1000) % 2147483647

    # Create job record
    job_data = {
        'job_id': job_id,
        'prompt': request.prompt,
        'asset_type': request.asset_type,
        'style': request.style,
        'target_engine': request.target_engine,
        'export_formats': request.export_formats,
        'poly_budget': request.poly_budget,
        'include_rig': request.include_rig,
        'include_animations': request.include_animations,
        'generate_lods': request.generate_lods,
        'seed': request.seed,
        'created_at': time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    # Save job to Redis
    job_key = f"jobs:{job_id}"
    redis_client.hset(job_key, mapping={
        'job_id': job_id,
        'status': JobStatus.QUEUED,
        'progress': 0.0,
        'data': json.dumps(job_data),
        'created_at': job_data['created_at'],
        'updated_at': job_data['created_at']
    })

    # Enqueue job
    queue_name = get_queue_name(priority)
    redis_client.rpush(queue_name, json.dumps(job_data))

    # Return job result
    return GenerationResult(
        job_id=job_id,
        status=JobStatus.QUEUED,
        progress=0.0
    )


@router.post("/batch", response_model=list[GenerationResult])
async def create_batch_generation(
    requests: list[GenerationRequest],
    priority: str = 'low'
):
    """
    Create multiple asset generation jobs at once
    Useful for generating entire asset packs
    """
    results = []

    for req in requests:
        result = await create_generation_job(req, priority)
        results.append(result)

    return results


@router.get("/quick", response_model=GenerationResult)
async def quick_generate(
    prompt: str,
    asset_type: str = "prop",
    priority: str = 'high'
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

    return await create_generation_job(request, priority)


@router.get("/queue/stats")
async def get_queue_stats():
    """Get queue statistics"""
    return {
        'high_priority': redis_client.llen(QUEUE_HIGH),
        'normal_priority': redis_client.llen(QUEUE_NORMAL),
        'low_priority': redis_client.llen(QUEUE_LOW),
        'total': (
            redis_client.llen(QUEUE_HIGH) +
            redis_client.llen(QUEUE_NORMAL) +
            redis_client.llen(QUEUE_LOW)
        )
    }


@router.delete("/queue/clear")
async def clear_queue(priority: Optional[str] = None):
    """Clear queue (admin endpoint)"""
    if priority:
        queue_name = get_queue_name(priority)
        count = redis_client.delete(queue_name)
        return {'cleared': queue_name, 'count': count}
    else:
        count = (
            redis_client.delete(QUEUE_HIGH) +
            redis_client.delete(QUEUE_NORMAL) +
            redis_client.delete(QUEUE_LOW)
        )
        return {'cleared': 'all', 'count': count}
