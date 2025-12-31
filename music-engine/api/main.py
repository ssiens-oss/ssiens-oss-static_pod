"""
StaticWaves Music API - FastAPI Backend
Main API endpoints for music generation
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import redis.asyncio as redis
import uuid
import json
import os
from typing import Dict
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.music_spec import MusicSpec, JobStatus
from shared.utils import spec_to_prompt, calculate_credits, generate_job_id


app = FastAPI(
    title="StaticWaves Music API",
    description="Real-time AI music generation with user controls",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


async def get_redis():
    """Get Redis connection"""
    return await redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "StaticWaves Music API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/generate", response_model=Dict[str, str])
async def generate_music(spec: MusicSpec):
    """
    Generate music from MusicSpec

    This is the main endpoint for music generation.
    It validates the spec, calculates credits, and queues the job.
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Calculate credit cost
    credits_needed = calculate_credits(spec.dict())

    # TODO: Validate user has enough credits
    # user = await get_current_user()
    # if user["credits"] < credits_needed:
    #     raise HTTPException(status_code=402, detail="Insufficient credits")

    # Convert spec to prompt
    prompt = spec_to_prompt(spec.dict())

    # Queue the job
    r = await get_redis()
    job_data = {
        "job_id": job_id,
        "spec": spec.dict(),
        "prompt": prompt,
        "credits": credits_needed,
        "status": "pending"
    }

    # Add to Redis queue
    await r.lpush("music_jobs", json.dumps(job_data))
    await r.set(f"job:{job_id}:status", "pending")
    await r.set(f"job:{job_id}:data", json.dumps(job_data))

    # TODO: Charge credits
    # await charge_credits(user["id"], credits_needed)

    return {
        "job_id": job_id,
        "status": "queued",
        "credits_charged": str(credits_needed),
        "estimated_time": f"{spec.duration}s"
    }


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """
    Get status of a music generation job

    Returns current status, progress, and output URLs when complete
    """
    r = await get_redis()

    # Get job data
    job_data_str = await r.get(f"job:{job_id}:data")
    if not job_data_str:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = json.loads(job_data_str)

    # Get current status
    status = await r.get(f"job:{job_id}:status") or "pending"
    progress = float(await r.get(f"job:{job_id}:progress") or 0.0)

    # Get output URLs if completed
    output_urls = None
    if status == "completed":
        output_str = await r.get(f"job:{job_id}:outputs")
        if output_str:
            output_urls = json.loads(output_str)

    return JobStatus(
        job_id=job_id,
        status=status,
        progress=progress,
        output_urls=output_urls
    )


@app.get("/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """
    Download generated music or stems

    file_type: mix, bass, lead, pad, drums, etc.
    """
    # Construct file path
    output_dir = os.getenv("OUTPUT_DIR", "/data/output")
    file_path = f"{output_dir}/{job_id}/{file_type}.wav"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=f"{job_id}_{file_type}.wav"
    )


@app.websocket("/live")
async def live_mode(websocket: WebSocket):
    """
    WebSocket endpoint for live/streaming music generation

    This is the Magenta RT streaming mode - music evolves in real-time
    based on user vibe adjustments
    """
    await websocket.accept()

    try:
        while True:
            # Receive vibe update from client
            data = await websocket.receive_json()

            # TODO: Generate audio chunk based on vibe
            # For now, echo back the vibe
            # In production, this would call Magenta RT or streaming MusicGen

            response = {
                "type": "audio_chunk",
                "vibe": data,
                "message": "Live mode - audio chunk would be sent here"
            }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        print("WebSocket disconnected")


@app.get("/health")
async def health():
    """Health check endpoint"""
    r = await get_redis()

    try:
        await r.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"

    return {
        "api": "healthy",
        "redis": redis_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
