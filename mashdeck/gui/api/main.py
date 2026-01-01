"""
MashDeck GUI API - FastAPI backend for web interface
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import os
import sys

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
    description="Web interface for MashDeck AI Music Production System",
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


# ===== Models =====

class SongGenerateRequest(BaseModel):
    style: str = "edm"
    bpm: Optional[int] = None
    key: Optional[str] = None
    title: Optional[str] = None
    create_variants: bool = False


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
    side: str  # "A" or "B"
    username: str
    message: str


class ReleaseRequest(BaseModel):
    audio_path: str
    title: str
    artist: str = "MashDeck AI"
    genre: str = "Electronic"
    platforms: List[str] = ["spotify", "tiktok", "youtube"]


# ===== State =====

class AppState:
    def __init__(self):
        self.freestyle_engine: Optional[LiveFreestyleEngine] = None
        self.battle_engine: Optional[BattleEngine] = None
        self.marketplace = MarketplaceStore()
        self.active_generations: Dict[str, dict] = {}
        self.websocket_connections: List[WebSocket] = []


state = AppState()


# ===== WebSocket Manager =====

async def broadcast_update(message: dict):
    """Broadcast update to all connected clients"""
    dead_connections = []

    for ws in state.websocket_connections:
        try:
            await ws.send_json(message)
        except:
            dead_connections.append(ws)

    # Remove dead connections
    for ws in dead_connections:
        if ws in state.websocket_connections:
            state.websocket_connections.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    state.websocket_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        if websocket in state.websocket_connections:
            state.websocket_connections.remove(websocket)


# ===== Song Generation Endpoints =====

@app.post("/api/generate/song")
async def generate_song_endpoint(
    request: SongGenerateRequest,
    background_tasks: BackgroundTasks
):
    """Generate a full-length song"""

    job_id = f"song_{len(state.active_generations)}"

    # Track generation
    state.active_generations[job_id] = {
        "status": "queued",
        "progress": 0,
        "request": request.dict()
    }

    # Start generation in background
    async def generate_task():
        try:
            await broadcast_update({
                "type": "generation_started",
                "job_id": job_id
            })

            # Generate song (this runs sync code in executor)
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

            state.active_generations[job_id]["status"] = "completed"
            state.active_generations[job_id]["output"] = output

            await broadcast_update({
                "type": "generation_completed",
                "job_id": job_id,
                "output": output
            })

        except Exception as e:
            state.active_generations[job_id]["status"] = "failed"
            state.active_generations[job_id]["error"] = str(e)

            await broadcast_update({
                "type": "generation_failed",
                "job_id": job_id,
                "error": str(e)
            })

    background_tasks.add_task(generate_task)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Song generation started"
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
