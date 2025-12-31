"""
Shared utilities for music generation
"""

import hashlib
import json
from typing import Dict


def spec_to_prompt(spec: Dict) -> str:
    """
    Convert MusicSpec to a text prompt for MusicGen

    This is critical - it translates user controls into AI prompts
    """
    # Extract vibe characteristics
    vibe = spec.get("vibe", {})
    genre_mix = spec.get("genre_mix", {})
    key = spec.get("key", "C minor")
    bpm = spec.get("bpm", 120)

    # Build genre string
    genres = ", ".join([f"{g} ({int(w*100)}%)" for g, w in genre_mix.items() if w > 0])

    # Build vibe descriptors
    vibe_words = []
    if vibe.get("energy", 0) > 0.6:
        vibe_words.append("energetic")
    if vibe.get("dark", 0) > 0.6:
        vibe_words.append("dark")
    if vibe.get("dreamy", 0) > 0.6:
        vibe_words.append("dreamy")
    if vibe.get("aggressive", 0) > 0.6:
        vibe_words.append("aggressive")

    vibe_str = ", ".join(vibe_words) if vibe_words else "balanced"

    # Construct prompt
    prompt = f"{key} {genres} music at {bpm} BPM, {vibe_str} vibe"

    return prompt


def calculate_credits(spec: Dict) -> int:
    """
    Calculate credit cost for a music generation job

    Pricing model:
    - Base: 1 credit per 10 seconds
    - Stems: +2 credits
    - Quality multiplier based on duration
    """
    duration = spec.get("duration", 30)
    stems = spec.get("stems", False)

    # Base cost: 1 credit per 10 seconds
    base_cost = max(1, duration // 10)

    # Stems add cost
    stem_cost = 2 if stems else 0

    total = base_cost + stem_cost

    return total


def generate_job_id(spec: Dict) -> str:
    """Generate a unique job ID from spec"""
    spec_json = json.dumps(spec, sort_keys=True)
    return hashlib.md5(spec_json.encode()).hexdigest()[:16]
