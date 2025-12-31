"""
MusicSpec - The core data model for user-generated music
This defines how users specify their music preferences
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional


class MusicSpec(BaseModel):
    """
    User-defined music specification
    This is the key to user-generated, reproducible, and remixable music
    """
    bpm: int = Field(default=120, ge=60, le=180, description="Beats per minute")
    key: str = Field(default="C minor", description="Musical key")
    duration: int = Field(default=30, ge=5, le=300, description="Duration in seconds")

    # Vibe controls - this is what makes it user-generated
    vibe: Dict[str, float] = Field(
        default={
            "energy": 0.5,
            "dark": 0.3,
            "dreamy": 0.4,
            "aggressive": 0.2
        },
        description="Emotional characteristics (0.0-1.0)"
    )

    # Genre mixing
    genre_mix: Dict[str, float] = Field(
        default={
            "synthwave": 0.6,
            "lofi": 0.3,
            "techno": 0.1
        },
        description="Genre blend ratios"
    )

    # Instrument selection
    instruments: Dict[str, str] = Field(
        default={
            "bass": "analog_mono",
            "lead": "supersaw",
            "pad": "granular_pad",
            "drums": "808"
        },
        description="Instrument preset per stem"
    )

    # Output options
    stems: bool = Field(default=True, description="Export separate stems")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    class Config:
        json_schema_extra = {
            "example": {
                "bpm": 120,
                "key": "C minor",
                "duration": 45,
                "vibe": {
                    "energy": 0.8,
                    "dark": 0.6,
                    "dreamy": 0.4,
                    "aggressive": 0.2
                },
                "genre_mix": {
                    "synthwave": 0.6,
                    "lofi": 0.3,
                    "techno": 0.1
                },
                "instruments": {
                    "bass": "analog_mono",
                    "lead": "supersaw",
                    "pad": "granular_pad",
                    "drums": "808"
                },
                "stems": True,
                "seed": 483920
            }
        }


class JobStatus(BaseModel):
    """Status of a music generation job"""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = 0.0
    message: Optional[str] = None
    output_urls: Optional[Dict[str, str]] = None
