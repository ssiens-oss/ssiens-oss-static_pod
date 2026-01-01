"""
Harmony and Backing Vocal Engine
Auto-generates harmonies, doubles, and stacked vocals
"""

import os
import random
from typing import List, Optional

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available, harmony features limited")


# Harmony interval rules (music theory-based)
HARMONY_INTERVALS = {
    "minor": [3, 7, 12],   # Minor 3rd, Perfect 5th, Octave
    "major": [4, 7, 12]    # Major 3rd, Perfect 5th, Octave
}


def get_harmony_intervals(key: str, intensity: str = "medium") -> List[int]:
    """
    Get harmony intervals based on key and intensity

    Args:
        key: Musical key (e.g., "F minor")
        intensity: low, medium, high

    Returns:
        List of semitone intervals
    """
    mode = "minor" if "minor" in key.lower() else "major"
    intervals = HARMONY_INTERVALS[mode]

    if intensity == "low":
        return [intervals[0]]  # Just 3rd
    elif intensity == "high":
        return intervals  # All harmonies
    else:
        return intervals[:2]  # 3rd and 5th


def pitch_shift(audio: AudioSegment, semitones: int) -> AudioSegment:
    """
    Pitch shift audio by semitones

    Args:
        audio: Input audio
        semitones: Semitones to shift (positive = up, negative = down)

    Returns:
        Pitch-shifted audio
    """
    if not PYDUB_AVAILABLE:
        return audio

    # Calculate new frame rate
    new_frame_rate = int(audio.frame_rate * (2 ** (semitones / 12)))

    # Pitch shift by changing frame rate then resampling
    shifted = audio._spawn(
        audio.raw_data,
        overrides={"frame_rate": new_frame_rate}
    ).set_frame_rate(audio.frame_rate)

    return shifted


def generate_harmonies(
    lead_wav: str,
    intervals: List[int],
    out_dir: str,
    base_name: str
) -> List[str]:
    """
    Generate harmony parts from lead vocal

    Args:
        lead_wav: Lead vocal WAV file
        intervals: List of semitone intervals
        out_dir: Output directory
        base_name: Base filename

    Returns:
        List of harmony file paths
    """
    if not PYDUB_AVAILABLE:
        print("Warning: Cannot generate harmonies without pydub")
        return []

    os.makedirs(out_dir, exist_ok=True)

    lead = AudioSegment.from_wav(lead_wav)
    outputs = []

    for i, semitone in enumerate(intervals):
        # Pitch shift for harmony
        harmony = pitch_shift(lead, semitone)

        # Reduce volume slightly
        harmony = harmony.apply_gain(-6)

        # Export
        path = os.path.join(out_dir, f"{base_name}_harmony_{i+1}.wav")
        harmony.export(path, format="wav")
        outputs.append(path)

        print(f"  ✓ Generated harmony +{semitone}st: {path}")

    return outputs


def backing_double(
    lead_wav: str,
    out_path: str,
    detune_cents: float = 10.0
) -> str:
    """
    Create backing vocal double with slight detune

    Args:
        lead_wav: Lead vocal
        out_path: Output path
        detune_cents: Detune amount in cents (100 cents = 1 semitone)

    Returns:
        Path to backing double
    """
    if not PYDUB_AVAILABLE:
        import shutil
        shutil.copy(lead_wav, out_path)
        return out_path

    audio = AudioSegment.from_wav(lead_wav)

    # Slight detune for width
    detune_semitones = random.choice([-detune_cents, detune_cents]) / 100.0
    shifted = pitch_shift(audio, detune_semitones)

    # Reduce volume
    shifted = shifted.apply_gain(-9)

    shifted.export(out_path, format="wav")
    print(f"  ✓ Generated backing double: {out_path}")

    return out_path


def chant_stack(
    lead_wav: str,
    out_path: str,
    count: int = 4,
    spread_ms: int = 20
) -> str:
    """
    Create stacked chant effect (EDM-style)

    Args:
        lead_wav: Lead vocal
        out_path: Output path
        count: Number of layers
        spread_ms: Timing spread between layers

    Returns:
        Path to stacked chant
    """
    if not PYDUB_AVAILABLE:
        import shutil
        shutil.copy(lead_wav, out_path)
        return out_path

    lead = AudioSegment.from_wav(lead_wav)
    lead = lead.apply_gain(-10)  # Reduce volume per layer

    stack = lead

    for i in range(count - 1):
        # Slightly offset each layer
        stack = stack.overlay(lead, position=i * spread_ms)

    stack.export(out_path, format="wav")
    print(f"  ✓ Generated chant stack: {out_path}")

    return out_path


def mix_vocal_bus(
    tracks: List[str],
    out_path: str,
    pan_tracks: bool = True
) -> str:
    """
    Mix multiple vocal tracks into bus

    Args:
        tracks: List of track paths
        out_path: Output path
        pan_tracks: Apply stereo panning

    Returns:
        Path to mixed bus
    """
    if not PYDUB_AVAILABLE or not tracks:
        return ""

    bus = None

    for i, track_path in enumerate(tracks):
        if not os.path.exists(track_path):
            continue

        audio = AudioSegment.from_wav(track_path)

        # Pan alternating tracks
        if pan_tracks:
            pan_value = -0.5 if i % 2 == 0 else 0.5
            audio = audio.pan(pan_value)

        # Mix
        if bus is None:
            bus = audio
        else:
            bus = bus.overlay(audio)

    if bus is None:
        return ""

    bus.export(out_path, format="wav")
    print(f"✓ Mixed vocal bus: {out_path}")

    return out_path


def enhance_vocals(
    lead_vocal: str,
    key: str,
    section: str,
    out_dir: str
) -> str:
    """
    Full vocal enhancement: harmonies + backing + mix

    Args:
        lead_vocal: Lead vocal path
        key: Musical key
        section: Section name
        out_dir: Output directory

    Returns:
        Path to enhanced vocal bus
    """
    os.makedirs(out_dir, exist_ok=True)

    print(f"Enhancing vocals for {section}...")

    # Determine intensity
    intensity = "high" if "chorus" in section else "medium"

    # Get harmony intervals
    intervals = get_harmony_intervals(key, intensity)

    # Generate harmonies
    harmonies = generate_harmonies(
        lead_vocal,
        intervals,
        out_dir,
        section
    )

    # Generate backing double
    backing = backing_double(
        lead_vocal,
        os.path.join(out_dir, f"{section}_double.wav")
    )

    # Collect all tracks
    tracks = [lead_vocal] + harmonies + [backing]

    # Add chant stack for choruses
    if "chorus" in section or "drop" in section:
        chant = chant_stack(
            lead_vocal,
            os.path.join(out_dir, f"{section}_chant.wav")
        )
        tracks.append(chant)

    # Mix to bus
    bus_path = os.path.join(out_dir, f"{section}_vocal_bus.wav")
    mix_vocal_bus(tracks, bus_path)

    return bus_path
