"""
Enhanced MashDeck GUI API with improved error handling, validation, and features
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import asyncio
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from song_engine.pipeline import generate_full_song
from vocals.pipeline import generate_vocals
from live.freestyle import LiveFreestyleEngine
from live.battle.engine import BattleEngine
from release.pipeline import AutoReleaser
from marketplace.store import MarketplaceStore, Asset


app = FastAPI(
    title="MashDeck GUI API",
    description="Professional web interface for MashDeck AI Music Production System",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enhanced CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Enhanced Models with Validation =====

class SongGenerateRequest(BaseModel):
    style: str = Field(..., description="Music style")
    bpm: Optional[int] = Field(None, ge=60, le=200, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key")
    title: Optional[str] = Field(None, max_length=100, description="Song title")
    create_variants: bool = Field(False, description="Create platform variants")

    @validator('style')
    def validate_style(cls, v):
        valid_styles = ['edm', 'lofi', 'trap', 'hiphop', 'ambient', 'rock']
        if v not in valid_styles:
            raise ValueError(f'Style must be one of {valid_styles}')
        return v


class VocalGenerateRequest(BaseModel):
    song_dir: str
    enable_harmonies: bool = True
    enable_midi: bool = True


class FreestyleRequest(BaseModel):
    bars: int = 4
    style: str = "aggressive"


class BattleStartRequest(BaseModel):
    rounds: int = 3
    bars: int = 4


class ChatMessageRequest(BaseModel):
    side: str = Field(..., description="A or B")
    username: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)

    @validator('side')
    def validate_side(cls, v):
        if v not in ['A', 'B']:
            raise ValueError('Side must be A or B')
        return v.upper()


class ReleaseRequest(BaseModel):
    audio_path: str = Field(..., description="Path to audio file")
    title: str = Field(..., min_length=1, max_length=200)
    artist: str = Field("MashDeck AI", max_length=100)
    genre: str = Field("Electronic", max_length=50)
    platforms: List[str] = Field(default_factory=lambda: ["spotify", "tiktok", "youtube"])

    @validator('platforms')
    def validate_platforms(cls, v):
        valid = ['spotify', 'tiktok', 'youtube']
        for platform in v:
            if platform not in valid:
                raise ValueError(f'Invalid platform: {platform}')
        return v


class SettingsUpdate(BaseModel):
    theme: Optional[str] = Field(None, description="UI theme")
    notifications_enabled: Optional[bool] = None
    auto_save: Optional[bool] = None
    default_style: Optional[str] = None
    default_bpm: Optional[int] = Field(None, ge=60, le=200)


# ===== Enhanced State Management =====

class AppState:
    def __init__(self):
        self.freestyle_engine: Optional[LiveFreestyleEngine] = None
        self.battle_engine: Optional[BattleEngine] = None
        self.marketplace = MarketplaceStore()
        self.active_generations: Dict[str, dict] = {}
        self.websocket_connections: List[WebSocket] = []
        self.settings: Dict[str, Any] = {
            "theme": "dark",
            "notifications_enabled": True,
            "auto_save": True,
            "default_style": "edm",
            "default_bpm": 120
        }
        self.projects: Dict[str, dict] = {}

    def add_generation(self, job_id: str, data: dict):
        self.active_generations[job_id] = {
            **data,
            "created_at": datetime.utcnow().isoformat(),
            "status": "queued"
        }

    def update_generation(self, job_id: str, updates: dict):
        if job_id in self.active_generations:
            self.active_generations[job_id].update(updates)
            self.active_generations[job_id]["updated_at"] = datetime.utcnow().isoformat()


state = AppState()


# ===== Exception Handlers =====

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    logger.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    logger.error(f"FileNotFoundError: {exc}")
    return JSONResponse(
        status_code=404,
        content={"error": "File Not Found", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Check server logs."
        }
    )


# ===== Enhanced WebSocket Manager =====

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint with enhanced error handling"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await manager.broadcast({"type": "message", "data": message})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ===== Song Generation Endpoints (Enhanced) =====

@app.post("/api/generate/song", tags=["Generation"])
async def generate_song_endpoint(
    request: SongGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a full-length AI song with structure and vocals

    Returns job_id for status tracking via WebSocket or polling
    """
    job_id = f"song_{len(state.active_generations)}_{int(datetime.utcnow().timestamp())}"

    state.add_generation(job_id, {"request": request.dict()})

    async def generate_task():
        try:
            await manager.broadcast({
                "type": "generation_started",
                "job_id": job_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            state.update_generation(job_id, {"status": "generating", "progress": 0.1})

            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                generate_full_song,
                request.style,
                request.bpm,
                request.key,
                request.title,
                f"output/{job_id}",
                request.create_variants
            )

            state.update_generation(job_id, {
                "status": "completed",
                "progress": 1.0,
                "output": output
            })

            await manager.broadcast({
                "type": "generation_completed",
                "job_id": job_id,
                "output": output,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Generation failed for {job_id}: {e}\n{traceback.format_exc()}")
            state.update_generation(job_id, {
                "status": "failed",
                "error": str(e)
            })

            await manager.broadcast({
                "type": "generation_failed",
                "job_id": job_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    background_tasks.add_task(generate_task)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Song generation started",
        "estimated_duration": "2-5 minutes"
    }


@app.get("/api/generate/status/{job_id}")
async def get_generation_status(job_id: str):
    """Get generation job status"""
    if job_id not in state.active_generations:
        raise HTTPException(status_code=404, detail="Job not found")

    return state.active_generations[job_id]


@app.get("/api/styles")
async def get_styles():
    """Get available music styles"""
    return {
        "styles": [
            {"id": "edm", "name": "EDM", "description": "Electronic Dance Music"},
            {"id": "lofi", "name": "Lo-Fi", "description": "Chill Lo-Fi Beats"},
            {"id": "trap", "name": "Trap", "description": "Hard Trap"},
            {"id": "hiphop", "name": "Hip-Hop", "description": "Classic Hip-Hop"},
            {"id": "ambient", "name": "Ambient", "description": "Atmospheric Ambient"},
            {"id": "rock", "name": "Rock", "description": "Rock Music"}
        ]
    }


# ===== Freestyle Endpoints =====

@app.post("/api/freestyle/start")
async def start_freestyle():
    """Start freestyle mode"""
    if state.freestyle_engine is None:
        state.freestyle_engine = LiveFreestyleEngine(output_dir="freestyle_output")

    return {"status": "freestyle_started"}


@app.post("/api/freestyle/generate")
async def generate_freestyle(request: FreestyleRequest):
    """Generate a freestyle rap"""
    if state.freestyle_engine is None:
        raise HTTPException(status_code=400, detail="Freestyle mode not started")

    result = state.freestyle_engine.generate_from_chat(
        bars=request.bars,
        style=request.style,
        force=True
    )

    await broadcast_update({
        "type": "freestyle_generated",
        "audio_path": result
    })

    return {"audio_path": result}


@app.post("/api/freestyle/chat")
async def add_freestyle_chat(message: str):
    """Add chat message to freestyle engine"""
    if state.freestyle_engine is None:
        raise HTTPException(status_code=400, detail="Freestyle mode not started")

    state.freestyle_engine.add_chat_message("user", message)
    return {"status": "message_added"}


# ===== Battle Endpoints =====

@app.post("/api/battle/start")
async def start_battle(request: BattleStartRequest):
    """Start AI rapper battle"""
    state.battle_engine = BattleEngine(output_dir="battles")
    state.battle_engine.start_battle()

    await broadcast_update({
        "type": "battle_started",
        "rounds": request.rounds,
        "bars": request.bars
    })

    return {
        "status": "battle_started",
        "rounds": request.rounds,
        "bars": request.bars
    }


@app.post("/api/battle/round")
async def execute_battle_round(bars: int = 4):
    """Execute one battle round"""
    if state.battle_engine is None:
        raise HTTPException(status_code=400, detail="Battle not started")

    round_result = state.battle_engine.execute_round(bars=bars)

    await broadcast_update({
        "type": "battle_round_completed",
        "round": round_result.__dict__
    })

    return {"round": round_result.__dict__}


@app.post("/api/battle/chat")
async def add_battle_chat(request: ChatMessageRequest):
    """Add chat message to battle"""
    if state.battle_engine is None:
        raise HTTPException(status_code=400, detail="Battle not started")

    if request.side == "A":
        state.battle_engine.add_message_a(request.username, request.message)
    else:
        state.battle_engine.add_message_b(request.username, request.message)

    return {"status": "message_added"}


@app.post("/api/battle/end")
async def end_battle():
    """End battle and declare winner"""
    if state.battle_engine is None:
        raise HTTPException(status_code=400, detail="Battle not started")

    winner = state.battle_engine.end_battle()

    await broadcast_update({
        "type": "battle_ended",
        "winner": winner
    })

    return {"winner": winner}


# ===== Release Endpoints =====

@app.post("/api/release")
async def release_track(request: ReleaseRequest):
    """Auto-release track to platforms"""
    releaser = AutoReleaser()

    metadata = {
        "title": request.title,
        "artist": request.artist,
        "genre": request.genre
    }

    results = releaser.release_everywhere(
        request.audio_path,
        metadata,
        platforms=request.platforms
    )

    return {"results": results}


# ===== Marketplace Endpoints =====

@app.get("/api/marketplace/assets")
async def list_marketplace_assets(asset_type: Optional[str] = None):
    """List marketplace assets"""
    assets = state.marketplace.list_assets(asset_type=asset_type)
    return {"assets": [asset.__dict__ for asset in assets]}


@app.get("/api/marketplace/asset/{asset_id}")
async def get_marketplace_asset(asset_id: str):
    """Get specific marketplace asset"""
    asset = state.marketplace.get_asset(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return {"asset": asset.__dict__}


@app.post("/api/marketplace/purchase/{asset_id}")
async def purchase_asset(asset_id: str, user_id: str, balance: int):
    """Purchase marketplace asset"""
    result = state.marketplace.purchase_asset(user_id, asset_id, balance)
    return result


# ===== Health Check =====

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "MashDeck GUI API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "active_generations": len(state.active_generations),
        "websocket_connections": len(state.websocket_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# ===== Settings Endpoints =====

@app.get("/api/settings", tags=["Settings"])
async def get_settings():
    """Get current user settings"""
    return state.settings


@app.patch("/api/settings", tags=["Settings"])
async def update_settings(settings: SettingsUpdate):
    """Update user settings"""
    updates = settings.dict(exclude_unset=True)
    state.settings.update(updates)
    await manager.broadcast({"type": "settings_updated", "settings": state.settings})
    return {"settings": state.settings, "message": "Settings updated"}


@app.get("/api/stats", tags=["System"])
async def get_stats():
    """Get system statistics"""
    jobs = state.active_generations.values()
    return {
        "total_generations": len(jobs),
        "completed": len([j for j in jobs if j["status"] == "completed"]),
        "failed": len([j for j in jobs if j["status"] == "failed"]),
        "in_progress": len([j for j in jobs if j["status"] in ["queued", "generating"]]),
        "websocket_connections": len(manager.active_connections)
    }
