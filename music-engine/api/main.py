"""
StaticWaves Music API - FastAPI Backend
Main API endpoints for music generation
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import redis.asyncio as redis
import uuid
import json
import os
from typing import Dict, List, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.music_spec import MusicSpec, JobStatus
from shared.utils import spec_to_prompt, calculate_credits, generate_job_id
from shared.genres import GENRES, get_genre_names, get_sub_genres, get_genre_profile
from shared.song_structure import get_structure_names, create_song_structure
from shared.auto_generator import (
    auto_generator,
    generate_automatic_song,
    generate_playlist,
    get_smart_preset
)
from shared.lyrics_generator import generate_lyrics_with_claude


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


# ===== AUTOMATIC GENERATION ENDPOINTS =====

@app.get("/genres")
async def list_genres():
    """Get list of all available genres"""
    return {
        "genres": [
            {
                "name": name,
                "display_name": GENRES[name].name,
                "description": GENRES[name].description,
                "sub_genres": GENRES[name].sub_genres,
                "bpm_range": GENRES[name].default_bpm_range
            }
            for name in get_genre_names()
        ]
    }


@app.get("/genres/{genre}/sub-genres")
async def list_sub_genres(genre: str):
    """Get sub-genres for a specific genre"""
    sub_genres = get_sub_genres(genre)
    if not sub_genres:
        raise HTTPException(status_code=404, detail="Genre not found")

    return {"genre": genre, "sub_genres": sub_genres}


@app.get("/structures")
async def list_structures():
    """Get list of available song structures"""
    return {"structures": get_structure_names()}


@app.get("/presets")
async def list_presets():
    """Get list of smart presets"""
    presets = [
        {"name": "morning_motivation", "description": "Uplifting indie electronic for starting your day"},
        {"name": "deep_focus", "description": "Lo-fi beats for concentration and study"},
        {"name": "workout_energy", "description": "High-energy trap for intense workouts"},
        {"name": "sleep_ambient", "description": "Peaceful ambient soundscapes for sleep"},
        {"name": "party_vibes", "description": "Euphoric house music for celebrations"},
        {"name": "gaming_intensity", "description": "Aggressive dubstep for gaming sessions"},
        {"name": "meditation", "description": "Calming ambient for mindfulness"},
        {"name": "creative_flow", "description": "Dreamy chillwave for creative work"}
    ]
    return {"presets": presets}


@app.post("/generate/auto")
async def generate_automatic(
    genre: Optional[str] = Query(None, description="Genre (optional, random if not specified)"),
    mood: Optional[str] = Query(None, description="Mood (optional)"),
    duration: Optional[int] = Query(None, ge=30, le=600, description="Duration in seconds"),
    include_lyrics: bool = Query(False, description="Generate AI lyrics with Claude")
):
    """
    🎵 Automatically generate a complete song!

    No configuration needed - just click and get a full song.
    Optionally specify genre, mood, or duration for more control.
    """
    # Generate song spec
    spec = generate_automatic_song(
        duration=duration,
        genre=genre,
        mood=mood,
        include_lyrics=False  # Will add lyrics separately if requested
    )

    # Generate lyrics if requested
    if include_lyrics:
        try:
            structure_types = [s["type"] for s in spec.get("structure", {}).get("sections", [])]
            lyrics = await generate_lyrics_with_claude(
                genre=spec.get("genre", "electronic"),
                mood=spec.get("mood", "chill"),
                theme=spec.get("theme"),
                structure=structure_types
            )
            spec["lyrics"] = lyrics
        except Exception as e:
            print(f"Error generating lyrics: {e}")
            spec["lyrics"] = None

    # Queue generation
    job_id = str(uuid.uuid4())
    credits_needed = calculate_credits(spec)

    r = await get_redis()
    job_data = {
        "job_id": job_id,
        "spec": spec,
        "prompt": spec_to_prompt(spec),
        "credits": credits_needed,
        "status": "pending"
    }

    await r.lpush("music_jobs", json.dumps(job_data))
    await r.set(f"job:{job_id}:status", "pending")
    await r.set(f"job:{job_id}:data", json.dumps(job_data))

    return {
        "job_id": job_id,
        "status": "queued",
        "song_info": {
            "title": spec.get("title"),
            "genre": spec.get("genre"),
            "mood": spec.get("mood"),
            "duration": spec.get("duration"),
            "bpm": spec.get("bpm")
        },
        "credits_charged": str(credits_needed)
    }


@app.post("/generate/preset/{preset_name}")
async def generate_from_preset(preset_name: str):
    """
    Generate a song from a smart preset

    Available presets:
    - morning_motivation
    - deep_focus
    - workout_energy
    - sleep_ambient
    - party_vibes
    - gaming_intensity
    - meditation
    - creative_flow
    """
    try:
        spec = get_smart_preset(preset_name)
    except:
        raise HTTPException(status_code=404, detail="Preset not found")

    # Queue generation
    job_id = str(uuid.uuid4())
    credits_needed = calculate_credits(spec)

    r = await get_redis()
    job_data = {
        "job_id": job_id,
        "spec": spec,
        "prompt": spec_to_prompt(spec),
        "credits": credits_needed,
        "status": "pending"
    }

    await r.lpush("music_jobs", json.dumps(job_data))
    await r.set(f"job:{job_id}:status", "pending")
    await r.set(f"job:{job_id}:data", json.dumps(job_data))

    return {
        "job_id": job_id,
        "status": "queued",
        "preset": preset_name,
        "song_info": {
            "title": spec.get("title"),
            "duration": spec.get("duration")
        }
    }


@app.post("/generate/playlist")
async def generate_playlist_endpoint(
    mood: str = Query(..., description="Playlist mood (energetic, chill, dark, etc.)"),
    count: int = Query(5, ge=1, le=20, description="Number of songs"),
    duration_per_song: int = Query(120, ge=30, le=300, description="Duration per song")
):
    """
    🎶 Generate a complete playlist!

    Creates multiple songs with a cohesive mood.
    Perfect for workout mixes, study sessions, or themed playlists.
    """
    # Generate playlist
    playlist_songs = generate_playlist(mood, count)

    # Queue all songs
    job_ids = []

    r = await get_redis()

    for i, spec in enumerate(playlist_songs):
        # Override duration if specified
        if duration_per_song:
            spec["duration"] = duration_per_song

        job_id = str(uuid.uuid4())
        credits_needed = calculate_credits(spec)

        job_data = {
            "job_id": job_id,
            "spec": spec,
            "prompt": spec_to_prompt(spec),
            "credits": credits_needed,
            "status": "pending",
            "playlist_index": i,
            "playlist_mood": mood
        }

        await r.lpush("music_jobs", json.dumps(job_data))
        await r.set(f"job:{job_id}:status", "pending")
        await r.set(f"job:{job_id}:data", json.dumps(job_data))

        job_ids.append(job_id)

    return {
        "playlist_id": str(uuid.uuid4()),
        "mood": mood,
        "song_count": count,
        "job_ids": job_ids,
        "message": f"Generating {count} {mood} songs..."
    }


@app.post("/generate/variations")
async def generate_variations(
    base_job_id: str = Query(..., description="Base job ID to create variations from"),
    count: int = Query(3, ge=1, le=10, description="Number of variations")
):
    """
    Create variations of an existing song

    Takes a generated song and creates similar but unique versions
    """
    r = await get_redis()

    # Get original spec
    job_data_str = await r.get(f"job:{base_job_id}:data")
    if not job_data_str:
        raise HTTPException(status_code=404, detail="Base job not found")

    base_job_data = json.loads(job_data_str)
    base_spec = base_job_data["spec"]

    # Generate variations
    variation_ids = []

    for i in range(count):
        # Create variation by tweaking vibe
        var_spec = base_spec.copy()
        var_spec["vibe"] = base_spec["vibe"].copy()

        # Slightly modify vibe (±0.15)
        import random
        for key in var_spec["vibe"]:
            var_spec["vibe"][key] = max(0.0, min(1.0,
                var_spec["vibe"][key] + random.uniform(-0.15, 0.15)
            ))

        # New seed
        var_spec["seed"] = base_spec.get("seed", 12345) + i + 1
        var_spec["title"] = f"{base_spec.get('title', 'Track')} - Variation {i+1}"

        # Queue
        job_id = str(uuid.uuid4())
        credits_needed = calculate_credits(var_spec)

        job_data = {
            "job_id": job_id,
            "spec": var_spec,
            "prompt": spec_to_prompt(var_spec),
            "credits": credits_needed,
            "status": "pending",
            "variation_of": base_job_id,
            "variation_index": i
        }

        await r.lpush("music_jobs", json.dumps(job_data))
        await r.set(f"job:{job_id}:status", "pending")
        await r.set(f"job:{job_id}:data", json.dumps(job_data))

        variation_ids.append(job_id)

    return {
        "base_job_id": base_job_id,
        "variation_count": count,
        "variation_ids": variation_ids
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
