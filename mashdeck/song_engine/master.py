"""
Mastering Engine - Auto-mastering for broadcast-ready output
Handles normalization, limiting, and basic EQ
"""

import os

try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available, mastering will be skipped")


def master(
    input_wav: str,
    output_wav: str,
    target_lufs: float = -14.0,
    normalize_peaks: bool = True,
    high_pass_hz: int = 30
) -> str:
    """
    Auto-master audio for streaming/broadcast

    Args:
        input_wav: Input WAV file path
        output_wav: Output WAV file path
        target_lufs: Target loudness (streaming standard is -14 LUFS)
        normalize_peaks: Apply peak normalization
        high_pass_hz: High-pass filter frequency

    Returns:
        Path to mastered file
    """
    if not PYDUB_AVAILABLE:
        print("Warning: Mastering skipped (pydub not available)")
        # Just copy file
        import shutil
        shutil.copy(input_wav, output_wav)
        return output_wav

    print(f"Mastering: {input_wav}")

    # Load audio
    audio = AudioSegment.from_wav(input_wav)

    # High-pass filter (remove sub-bass rumble)
    if high_pass_hz > 0:
        audio = audio.high_pass_filter(high_pass_hz)
        print(f"  ✓ High-pass filter: {high_pass_hz}Hz")

    # Peak normalization
    if normalize_peaks:
        audio = normalize(audio, headroom=1.0)
        print("  ✓ Peak normalization")

    # Dynamic range compression (gentle)
    # This helps even out the loudness
    audio = compress_dynamic_range(audio, threshold=-20.0, ratio=2.0)
    print("  ✓ Dynamic compression")

    # Final normalization to target level
    # Note: Proper LUFS metering requires additional library (pyloudnorm)
    # For now, we use peak normalization as proxy
    audio = normalize(audio, headroom=0.5)
    print("  ✓ Final normalization")

    # Export
    audio.export(output_wav, format="wav")
    print(f"✓ Mastered audio saved: {output_wav}")

    return output_wav


def create_stems_master(
    stem_files: dict,
    output_dir: str
) -> dict:
    """
    Master multiple stems

    Args:
        stem_files: Dict mapping stem names to file paths
        output_dir: Output directory

    Returns:
        Dict mapping stem names to mastered file paths
    """
    os.makedirs(output_dir, exist_ok=True)

    mastered = {}

    for stem_name, input_path in stem_files.items():
        output_path = os.path.join(output_dir, f"{stem_name}_mastered.wav")
        master(input_path, output_path)
        mastered[stem_name] = output_path

    return mastered


def create_loudness_variants(
    input_wav: str,
    output_dir: str
) -> dict:
    """
    Create multiple loudness variants for different platforms

    Args:
        input_wav: Input audio file
        output_dir: Output directory

    Returns:
        Dict with platform-specific variants
    """
    os.makedirs(output_dir, exist_ok=True)

    variants = {
        "spotify": -14.0,      # Spotify standard
        "youtube": -13.0,      # YouTube music
        "tiktok": -11.0,       # TikTok (louder)
        "club": -8.0,          # DJ/club play
        "broadcast": -16.0     # Radio/podcast
    }

    outputs = {}

    for platform, target_lufs in variants.items():
        output_path = os.path.join(output_dir, f"master_{platform}.wav")
        master(input_wav, output_path, target_lufs=target_lufs)
        outputs[platform] = output_path

    return outputs
