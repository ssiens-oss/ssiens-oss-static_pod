"""
StaticWaves Forge - Common Data Schemas
Shared data models and types across the platform
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class AssetType(str, Enum):
    """Types of 3D assets that can be generated"""
    CREATURE = "creature"
    CHARACTER = "character"
    PROP = "prop"
    WEAPON = "weapon"
    BUILDING = "building"
    ENVIRONMENT = "environment"
    VEHICLE = "vehicle"

class AssetStyle(str, Enum):
    """Visual styles for generated assets"""
    LOW_POLY = "low-poly"
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    VOXEL = "voxel"
    TOON = "toon"
    ROBLOX = "roblox-safe"

class TargetEngine(str, Enum):
    """Target game engines for export"""
    UNITY = "unity"
    UNREAL = "unreal"
    ROBLOX = "roblox"
    GODOT = "godot"
    GENERIC = "generic"

class ExportFormat(str, Enum):
    """Export file formats"""
    GLB = "glb"
    FBX = "fbx"
    OBJ = "obj"
    GLTF = "gltf"
    BLEND = "blend"

class AnimationType(str, Enum):
    """Types of animations to generate"""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    ATTACK = "attack"
    EMOTE = "emote"
    CUSTOM = "custom"

class JobStatus(str, Enum):
    """Asset generation job statuses"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GenerationRequest(BaseModel):
    """Request to generate a 3D asset"""
    prompt: str = Field(..., description="Text description of the asset to generate")
    asset_type: AssetType = Field(default=AssetType.PROP)
    style: AssetStyle = Field(default=AssetStyle.LOW_POLY)
    target_engine: TargetEngine = Field(default=TargetEngine.UNITY)
    export_formats: List[ExportFormat] = Field(default=[ExportFormat.GLB, ExportFormat.FBX])
    poly_budget: Optional[int] = Field(default=10000, description="Target polygon count")
    include_rig: bool = Field(default=False)
    include_animations: List[AnimationType] = Field(default=[])
    generate_lods: bool = Field(default=True)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    class Config:
        use_enum_values = True

class AssetMetadata(BaseModel):
    """Metadata about a generated asset"""
    asset_id: str
    name: str
    asset_type: AssetType
    style: AssetStyle
    poly_count: int
    vertex_count: int
    has_rig: bool
    animations: List[str]
    file_size_mb: float
    created_at: str
    seed: int

class GenerationResult(BaseModel):
    """Result of an asset generation job"""
    job_id: str
    status: JobStatus
    asset_metadata: Optional[AssetMetadata] = None
    output_files: Dict[str, str] = Field(default={}, description="Format -> file path")
    error_message: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)

    class Config:
        use_enum_values = True

class AssetPackMetadata(BaseModel):
    """Metadata for an asset pack"""
    pack_id: str
    name: str
    description: str
    price: float
    asset_count: int
    tags: List[str]
    version: str
    created_at: str
    formats: List[str]
    total_size_mb: float

class WorkerStatus(BaseModel):
    """Status of a Blender worker instance"""
    worker_id: str
    status: str
    current_job: Optional[str] = None
    jobs_completed: int = 0
    uptime_seconds: float = 0
    gpu_name: Optional[str] = None
    gpu_utilization: Optional[float] = None
