"""
StaticWaves Forge - Jobs Routes (Redis Implementation)
Endpoints for tracking job status with Redis
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import redis
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../packages'))

from common.schemas import (
    GenerationResult,
    JobStatus,
    AssetMetadata
)

router = APIRouter()

# Redis connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


@router.get("/{job_id}", response_model=GenerationResult)
async def get_job_status(job_id: str):
    """Get the status of a generation job"""
    job_key = f"jobs:{job_id}"

    if not redis_client.exists(job_key):
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = redis_client.hgetall(job_key)

    # Parse metadata and output files if they exist
    metadata = None
    if job_data.get('metadata'):
        metadata_dict = json.loads(job_data['metadata'])
        metadata = AssetMetadata(**metadata_dict)

    output_files = {}
    if job_data.get('output_files'):
        output_files = json.loads(job_data['output_files'])

    return GenerationResult(
        job_id=job_id,
        status=job_data.get('status', 'unknown'),
        progress=float(job_data.get('progress', 0.0)),
        asset_metadata=metadata,
        output_files=output_files,
        error_message=job_data.get('error_message')
    )


@router.get("/")
async def list_jobs(
    status: str = None,
    limit: int = 100,
    offset: int = 0
):
    """List all jobs"""
    # Get all job keys
    job_keys = redis_client.keys("jobs:*")

    jobs = []
    for key in job_keys[offset:offset+limit]:
        job_data = redis_client.hgetall(key)
        job_id = key.split(':', 1)[1]

        if status and job_data.get('status') != status:
            continue

        jobs.append({
            'job_id': job_id,
            'status': job_data.get('status'),
            'progress': float(job_data.get('progress', 0.0)),
            'created_at': job_data.get('created_at'),
            'updated_at': job_data.get('updated_at')
        })

    return {
        'jobs': jobs,
        'total': len(job_keys),
        'limit': limit,
        'offset': offset
    }


@router.delete("/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a pending or processing job"""
    job_key = f"jobs:{job_id}"

    if not redis_client.exists(job_key):
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = redis_client.hgetall(job_key)
    current_status = job_data.get('status')

    if current_status in ['completed', 'failed', 'cancelled']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in {current_status} state"
        )

    # Update job status
    redis_client.hset(job_key, mapping={
        'status': JobStatus.CANCELLED,
        'updated_at': __import__('time').strftime("%Y-%m-%dT%H:%M:%SZ")
    })

    return {'job_id': job_id, 'status': 'cancelled'}


@router.websocket("/{job_id}/stream")
async def job_progress_stream(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates

    Client can connect to ws://api/jobs/{job_id}/stream
    and receive real-time progress updates as they happen
    """
    await websocket.accept()

    job_key = f"jobs:{job_id}"

    if not redis_client.exists(job_key):
        await websocket.send_json({'error': 'Job not found'})
        await websocket.close()
        return

    # Send initial status
    job_data = redis_client.hgetall(job_key)
    await websocket.send_json({
        'job_id': job_id,
        'status': job_data.get('status'),
        'progress': float(job_data.get('progress', 0.0)),
        'message': job_data.get('message', '')
    })

    # Subscribe to progress updates
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"job_progress:{job_id}")

    try:
        while True:
            # Check for messages from Redis pubsub
            message = pubsub.get_message(timeout=1.0)

            if message and message['type'] == 'message':
                progress_data = json.loads(message['data'])
                await websocket.send_json(progress_data)

                # Close connection if job is complete
                if progress_data.get('status') in ['completed', 'failed', 'cancelled']:
                    break

            # Also check if client disconnected
            try:
                # Try to receive (this will fail if client disconnected)
                await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                break

    except Exception as e:
        print(f"WebSocket error for job {job_id}: {e}")
    finally:
        pubsub.unsubscribe(f"job_progress:{job_id}")
        pubsub.close()
        await websocket.close()


@router.get("/stats/overview")
async def get_job_stats():
    """Get overall job statistics"""
    all_jobs = redis_client.keys("jobs:*")

    stats = {
        'total_jobs': len(all_jobs),
        'queued': 0,
        'processing': 0,
        'completed': 0,
        'failed': 0,
        'cancelled': 0
    }

    for job_key in all_jobs:
        job_data = redis_client.hgetall(job_key)
        status = job_data.get('status', 'unknown')

        if status in stats:
            stats[status] += 1

    return stats


@router.get("/workers/list")
async def list_workers():
    """List all active workers"""
    worker_keys = redis_client.keys("workers:*")

    workers = []
    for key in worker_keys:
        worker_data = redis_client.hgetall(key)
        worker_id = key.split(':', 1)[1]

        workers.append({
            'worker_id': worker_id,
            'worker_type': worker_data.get('worker_type'),
            'status': worker_data.get('status'),
            'current_job': worker_data.get('current_job'),
            'jobs_completed': int(worker_data.get('jobs_completed', 0)),
            'jobs_failed': int(worker_data.get('jobs_failed', 0)),
            'started_at': worker_data.get('started_at'),
            'last_updated': worker_data.get('last_updated')
        })

    return {'workers': workers, 'total': len(workers)}
