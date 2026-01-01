"""
Arrangement Engine - Combines sections with transitions and crossfades
Creates final timeline from individual song sections
"""

import os
from typing import List, Optional

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available, arrangement will be limited")


def crossfade(a: AudioSegment, b: AudioSegment, ms: int = 4000) -> AudioSegment:
    """
    Crossfade between two audio segments

    Args:
        a: First audio segment
        b: Second audio segment
        ms: Crossfade duration in milliseconds

    Returns:
        Combined audio with crossfade
    """
    return a.append(b, crossfade=ms)


def arrange(
    section_files: List[str],
    out_path: str,
    crossfade_ms: int = 4000
) -> str:
    """
    Arrange song sections into final timeline

    Args:
        section_files: List of paths to section WAV files
        out_path: Output path for arranged song
        crossfade_ms: Crossfade duration between sections

    Returns:
        Path to final arranged WAV
    """
    if not PYDUB_AVAILABLE:
        print("Error: pydub not available for arrangement")
        return ""

    song = None

    print(f"Arranging {len(section_files)} sections...")

    for i, path in enumerate(section_files):
        if not os.path.exists(path):
            print(f"Warning: Section file not found: {path}")
            continue

        audio = AudioSegment.from_wav(path)

        if song is None:
            song = audio
        else:
            song = crossfade(song, audio, crossfade_ms)

        print(f"  Added section {i+1}/{len(section_files)}: {os.path.basename(path)}")

    if song is None:
        print("Error: No valid audio sections found")
        return ""

    # Export final arrangement
    song.export(out_path, format="wav")
    print(f"✓ Arranged song saved: {out_path}")

    return out_path


def create_stems_arrangement(
    sections_by_stem: dict,
    out_dir: str,
    crossfade_ms: int = 4000
) -> dict:
    """
    Arrange stems (bass, drums, melody, etc.) separately

    Args:
        sections_by_stem: Dict mapping stem names to lists of section files
        out_dir: Output directory for stem files
        crossfade_ms: Crossfade duration

    Returns:
        Dict mapping stem names to output file paths
    """
    os.makedirs(out_dir, exist_ok=True)

    stem_outputs = {}

    for stem_name, section_files in sections_by_stem.items():
        out_path = os.path.join(out_dir, f"{stem_name}.wav")
        result_path = arrange(section_files, out_path, crossfade_ms)

        if result_path:
            stem_outputs[stem_name] = result_path

    return stem_outputs


def add_silence(audio: AudioSegment, duration_ms: int, position: str = "end") -> AudioSegment:
    """
    Add silence to audio segment

    Args:
        audio: Audio segment
        duration_ms: Silence duration in milliseconds
        position: "start" or "end"

    Returns:
        Audio with added silence
    """
    if not PYDUB_AVAILABLE:
        return audio

    silence = AudioSegment.silent(duration=duration_ms)

    if position == "start":
        return silence + audio
    else:
        return audio + silence


def apply_fade(
    audio: AudioSegment,
    fade_in_ms: int = 0,
    fade_out_ms: int = 0
) -> AudioSegment:
    """
    Apply fade in/out to audio segment

    Args:
        audio: Audio segment
        fade_in_ms: Fade in duration
        fade_out_ms: Fade out duration

    Returns:
        Audio with fades applied
    """
    if not PYDUB_AVAILABLE:
        return audio

    if fade_in_ms > 0:
        audio = audio.fade_in(fade_in_ms)

    if fade_out_ms > 0:
        audio = audio.fade_out(fade_out_ms)

    return audio
