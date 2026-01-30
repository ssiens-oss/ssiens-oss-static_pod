"""
API Request/Response Schemas

Dataclasses for API request validation and response formatting.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class GenerateRequest:
    """Request schema for image generation"""
    prompt: str
    style: str = ""
    genre: str = ""
    seed: Optional[int] = None
    width: int = 1024
    height: int = 1024
    steps: int = 20
    cfg_scale: float = 7.0
    client_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerateRequest":
        """Create from request JSON with defaults"""
        return cls(
            prompt=(data.get("prompt") or "").strip(),
            style=(data.get("style") or "").strip(),
            genre=(data.get("genre") or "").strip(),
            seed=data.get("seed"),
            width=data.get("width", 1024),
            height=data.get("height", 1024),
            steps=data.get("steps", 20),
            cfg_scale=data.get("cfg_scale", 7.0),
            client_id=data.get("client_id")
        )

    def validate(self) -> Optional[str]:
        """Validate request fields. Returns error message or None."""
        if not self.prompt:
            return "Prompt is required"
        if self.width < 64 or self.width > 4096:
            return "Width must be between 64 and 4096"
        if self.height < 64 or self.height > 4096:
            return "Height must be between 64 and 4096"
        if self.steps < 1 or self.steps > 150:
            return "Steps must be between 1 and 150"
        if self.cfg_scale < 1.0 or self.cfg_scale > 30.0:
            return "CFG scale must be between 1.0 and 30.0"
        return None


@dataclass
class PublishRequest:
    """Request schema for publishing an image"""
    title: str
    description: Optional[str] = None
    price_cents: int = 3499
    blueprint_id: int = 77
    provider_id: int = 39

    @classmethod
    def from_dict(cls, data: Dict[str, Any], default_title: str = "") -> "PublishRequest":
        """Create from request JSON with defaults"""
        return cls(
            title=data.get("title", default_title),
            description=data.get("description"),
            price_cents=data.get("price_cents", 3499),
            blueprint_id=data.get("blueprint_id", 77),
            provider_id=data.get("provider_id", 39)
        )


@dataclass
class ImageResponse:
    """Response schema for an image"""
    id: str
    filename: str
    status: str
    path: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    error_message: Optional[str] = None
    product_id: Optional[str] = None
    title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class GenerationResponse:
    """Response schema for generation request"""
    prompt_id: Optional[str] = None
    job_id: Optional[str] = None
    status: str = ""
    prompt: str = ""
    source: str = ""
    images: List[Dict[str, str]] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "status": self.status,
            "prompt": self.prompt,
            "source": self.source,
            "images": self.images
        }
        if self.prompt_id:
            result["prompt_id"] = self.prompt_id
        if self.job_id:
            result["job_id"] = self.job_id
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class PublishResponse:
    """Response schema for publish request"""
    success: bool
    status: str = ""
    product_id: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"success": self.success}
        if self.status:
            result["status"] = self.status
        if self.product_id:
            result["product_id"] = self.product_id
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class StatsResponse:
    """Response schema for statistics"""
    total: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    publishing: int = 0
    published: int = 0
    failed: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary"""
        return asdict(self)
