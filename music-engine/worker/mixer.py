"""
Mixer - Final mixing and export

This module:
1. Applies vibe-based effects (reverb, filters, etc.)
2. Mixes stems together
3. Exports final audio and individual stems
"""

import numpy as np
import soundfile as sf
import os
from pathlib import Path
from scipy import signal


def apply_vibe_effects(audio: np.ndarray, vibe: dict, sample_rate: int = 32000):
    """
    Apply effects based on vibe settings

    Vibe mapping:
    - energy → saturation, compression
    - dark → low-pass filter, detune
    - dreamy → reverb, chorus
    - aggressive → distortion, transient enhancement
    """
    processed = audio.copy()

    # Energy → Saturation
    energy = vibe.get("energy", 0.5)
    if energy > 0.5:
        # Soft clipping for saturation
        drive = 1 + (energy - 0.5) * 2
        processed = np.tanh(processed * drive) / drive

    # Dark → Low-pass filter
    dark = vibe.get("dark", 0.3)
    if dark > 0.3:
        # Cutoff frequency based on darkness
        cutoff = 8000 * (1 - dark * 0.7)  # 8kHz to 2.4kHz
        sos = signal.butter(4, cutoff, btype='low', fs=sample_rate, output='sos')
        processed = signal.sosfilt(sos, processed)

    # Dreamy → Simple reverb (delay + feedback)
    dreamy = vibe.get("dreamy", 0.4)
    if dreamy > 0.3:
        delay_samples = int(0.05 * sample_rate)  # 50ms delay
        wet = dreamy * 0.3

        reverb = np.zeros_like(processed)
        reverb[delay_samples:] = processed[:-delay_samples] * wet
        processed = processed + reverb

    # Aggressive → Transient enhancement
    aggressive = vibe.get("aggressive", 0.2)
    if aggressive > 0.3:
        # High-pass emphasis
        sos = signal.butter(2, 200, btype='high', fs=sample_rate, output='sos')
        transients = signal.sosfilt(sos, processed)
        processed = processed + transients * aggressive * 0.3

    return processed


def normalize_audio(audio: np.ndarray, target_db: float = -6.0):
    """
    Normalize audio to target dB level

    Prevents clipping and ensures consistent loudness
    """
    # Find peak
    peak = np.abs(audio).max()

    if peak == 0:
        return audio

    # Calculate gain to reach target
    target_linear = 10 ** (target_db / 20)
    gain = target_linear / peak

    # Apply gain
    normalized = audio * gain

    # Safety limiter
    normalized = np.clip(normalized, -1.0, 1.0)

    return normalized


def mix_and_export(job_id: str, stems: dict, spec: dict, output_dir: str):
    """
    Mix stems and export final audio

    Args:
        job_id: Unique job identifier
        stems: Dictionary of stem audio arrays
        spec: MusicSpec with mixing preferences
        output_dir: Directory to save outputs

    Returns:
        Dictionary of exported file paths
    """
    sample_rate = 32000
    vibe = spec.get("vibe", {})
    export_stems = spec.get("stems", True)

    # Create output directory for this job
    job_output_dir = Path(output_dir) / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Mixing {len(stems)} stems...")

    # Apply vibe effects to each stem
    processed_stems = {}
    for name, audio in stems.items():
        processed = apply_vibe_effects(audio, vibe, sample_rate)
        processed_stems[name] = processed

    # Mix all stems together
    max_length = max(len(audio) for audio in processed_stems.values())

    # Pad stems to same length
    for name, audio in processed_stems.items():
        if len(audio) < max_length:
            padded = np.zeros(max_length)
            padded[:len(audio)] = audio
            processed_stems[name] = padded

    # Sum all stems
    mix = sum(processed_stems.values()) / len(processed_stems)

    # Apply final vibe effects to mix
    mix = apply_vibe_effects(mix, vibe, sample_rate)

    # Normalize
    mix = normalize_audio(mix, target_db=-6.0)

    # Export files
    output_files = {}

    # Export mix
    mix_path = job_output_dir / "mix.wav"
    sf.write(str(mix_path), mix, sample_rate)
    output_files["mix"] = str(mix_path)
    print(f"✅ Exported mix: {mix_path}")

    # Export individual stems if requested
    if export_stems:
        for name, audio in processed_stems.items():
            normalized = normalize_audio(audio, target_db=-6.0)
            stem_path = job_output_dir / f"{name}.wav"
            sf.write(str(stem_path), normalized, sample_rate)
            output_files[name] = str(stem_path)
            print(f"✅ Exported stem: {stem_path}")

    print(f"\n🎵 Export complete! {len(output_files)} files")

    return output_files
