"""
Section Generator - Generate individual song sections using MusicGen
Integrates with existing music-engine infrastructure
"""

import math
import os
import sys
from typing import Dict, Optional

# Add music-engine to path for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'music-engine'))

try:
    from worker.musicgen_engine import MusicGenEngine
    MUSICGEN_AVAILABLE = True
except ImportError:
    MUSICGEN_AVAILABLE = False
    print("Warning: MusicGen not available, using mock generation")


def bars_to_seconds(bars: int, bpm: int) -> float:
    """
    Convert musical bars to seconds

    Args:
        bars: Number of bars (4 beats per bar)
        bpm: Beats per minute

    Returns:
        Duration in seconds
    """
    return (60 / bpm) * 4 * bars


def generate_section(
    section: Dict,
    plan: Dict,
    out_dir: str,
    model_name: str = "facebook/musicgen-medium"
) -> str:
    """
    Generate a single song section using MusicGen

    Args:
        section: Section dict with 'section', 'bars', 'energy'
        plan: Full song plan with 'style', 'bpm', 'key'
        out_dir: Output directory for WAV file
        model_name: MusicGen model to use

    Returns:
        Path to generated WAV file
    """
    os.makedirs(out_dir, exist_ok=True)

    # Calculate duration
    seconds = math.ceil(bars_to_seconds(section["bars"], plan["bpm"]))
    energy = section["energy"]

    # Build descriptive prompt for this section
    energy_descriptors = {
        (0.0, 0.3): "minimal, sparse, atmospheric",
        (0.3, 0.5): "gentle, smooth, flowing",
        (0.5, 0.7): "driving, energetic, engaging",
        (0.7, 0.9): "powerful, intense, dynamic",
        (0.9, 1.1): "explosive, maximum energy, peak intensity"
    }

    energy_desc = "moderate"
    for (low, high), desc in energy_descriptors.items():
        if low <= energy < high:
            energy_desc = desc
            break

    prompt = (
        f"{plan['style']} music, {section['section']} section, "
        f"{energy_desc}, {plan['bpm']} bpm, "
        f"key {plan['key']}, instrumental"
    )

    print(f"Generating {section['section']}: {prompt}")

    # Generate audio
    path = f"{out_dir}/{section['section']}.wav"

    if MUSICGEN_AVAILABLE:
        try:
            # Use actual MusicGen engine
            engine = MusicGenEngine(model_name=model_name)
            audio = engine.generate(
                prompt=prompt,
                duration=seconds,
                temperature=0.8,
                top_k=250,
                top_p=0.9
            )

            # Save to file
            import soundfile as sf
            sf.write(path, audio, 32000)

        except Exception as e:
            print(f"MusicGen error: {e}, using mock file")
            _create_mock_audio(path, seconds)
    else:
        # Create mock audio file for testing
        _create_mock_audio(path, seconds)

    return path


def _create_mock_audio(path: str, duration: int):
    """Create a silent mock audio file for testing"""
    import numpy as np
    import soundfile as sf

    sample_rate = 32000
    samples = int(sample_rate * duration)
    audio = np.zeros(samples, dtype=np.float32)

    sf.write(path, audio, sample_rate)
    print(f"Created mock audio: {path}")


def generate_transition(
    from_section: str,
    to_section: str,
    bpm: int,
    style: str,
    out_dir: str
) -> str:
    """
    Generate a transition between two sections (riser, downlifter, etc.)

    Args:
        from_section: Source section name
        to_section: Destination section name
        bpm: Song BPM
        style: Music style
        out_dir: Output directory

    Returns:
        Path to transition audio file
    """
    os.makedirs(out_dir, exist_ok=True)

    # 2-4 bars for transitions
    duration = bars_to_seconds(2, bpm)

    prompt = f"{style} transition, riser sweep, build tension, {bpm} bpm"

    path = f"{out_dir}/transition_{from_section}_to_{to_section}.wav"

    # For now, create silent transition
    # TODO: Add actual AI-generated risers/downlifters
    _create_mock_audio(path, int(duration))

    return path
