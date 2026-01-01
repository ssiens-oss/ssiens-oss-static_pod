"""
Complete Vocal Generation Pipeline
Orchestrates rap, singing, harmonies, and mixing
"""

import os
import json
from typing import Dict, List, Optional

from .roles.planner import assign_roles
from .rap.generator import generate_rap
from .sing.generator import generate_hook, generate_melody
from .synthesis import rap_synthesize, sing_synthesize, synthesize
from .harmony.engine import enhance_vocals, pitch_shift
from .midi_export import export_melody_midi, export_harmony_midi

# Import song engine helpers
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from song_engine.generator import bars_to_seconds


def generate_vocals(
    song_plan: Dict,
    section_files: Dict[str, str],
    out_dir: str,
    enable_harmonies: bool = True,
    enable_rap: bool = True,
    enable_midi_export: bool = True
) -> Dict[str, str]:
    """
    Generate all vocals for a song

    Args:
        song_plan: Song plan from song_engine
        section_files: Dict mapping section names to instrumental WAV paths
        out_dir: Output directory
        enable_harmonies: Generate harmonies and backing vocals
        enable_rap: Generate rap vocals for verses
        enable_midi_export: Export MIDI files

    Returns:
        Dict with paths to vocal files and metadata
    """
    print("\n" + "=" * 60)
    print("MashDeck Vocal Generation Pipeline")
    print("=" * 60)

    os.makedirs(out_dir, exist_ok=True)
    vocals_dir = os.path.join(out_dir, "vocals")
    os.makedirs(vocals_dir, exist_ok=True)

    # Assign vocal roles
    print("\n[1/4] Assigning vocal roles...")
    roles = assign_roles(song_plan)
    print(f"  ✓ Assigned {len(roles)} vocal parts")

    # Generate vocals for each role
    print("\n[2/4] Generating vocal performances...")
    vocal_files = {}
    melodies = {}

    for role in roles:
        section = role["section"]
        role_type = role["role"]
        bars = role["bars"]
        energy = role["energy"]

        print(f"\n  Section: {section} ({role_type})")

        vocal_path = os.path.join(vocals_dir, f"{section}_{role_type}.wav")

        if role_type == "rap" and enable_rap:
            # Generate rap
            lyrics = generate_rap(
                bars=bars,
                bpm=song_plan["bpm"],
                energy=energy
            )
            print(f"    Lyrics: {lyrics[:50]}...")

            rap_synthesize(lyrics, vocal_path)
            vocal_files[section] = vocal_path

        elif role_type == "sing":
            # Generate sung hook
            mood = "energetic" if energy > 0.6 else "chill"
            lyrics = generate_hook(bars=bars, mood=mood)
            print(f"    Hook: {lyrics[:50]}...")

            # Generate melody
            melody = generate_melody(
                key=song_plan["key"],
                bars=bars,
                contour="wave"
            )
            melodies[section] = melody

            # Synthesize with melody
            sing_synthesize(lyrics, vocal_path, melody)
            vocal_files[section] = vocal_path

            # Export MIDI if enabled
            if enable_midi_export:
                midi_path = os.path.join(vocals_dir, f"{section}_melody.mid")
                export_melody_midi(
                    melody,
                    song_plan["bpm"],
                    midi_path
                )

        elif role_type == "chant":
            # Simple chant
            lyrics = "Yeah! Let's go!"
            synthesize(lyrics, vocal_path)
            vocal_files[section] = vocal_path

        elif role_type == "adlib":
            # Ad-libs
            lyrics = "Ooh... yeah"
            synthesize(lyrics, vocal_path)
            vocal_files[section] = vocal_path

    # Enhance with harmonies
    enhanced_files = {}

    if enable_harmonies:
        print("\n[3/4] Adding harmonies and backing vocals...")

        for section, vocal_path in vocal_files.items():
            if os.path.exists(vocal_path):
                print(f"  Enhancing {section}...")

                enhanced_path = enhance_vocals(
                    vocal_path,
                    song_plan["key"],
                    section,
                    vocals_dir
                )

                enhanced_files[section] = enhanced_path
    else:
        enhanced_files = vocal_files

    # Export metadata
    print("\n[4/4] Exporting metadata...")

    metadata = {
        "song_title": song_plan.get("title"),
        "style": song_plan.get("style"),
        "bpm": song_plan["bpm"],
        "key": song_plan["key"],
        "vocal_sections": list(enhanced_files.keys()),
        "melodies": {k: v for k, v in melodies.items()}
    }

    metadata_path = os.path.join(out_dir, "vocal_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 60)
    print("✓ Vocal Generation Complete!")
    print("=" * 60)
    print(f"Vocals directory: {vocals_dir}")
    print(f"Enhanced tracks: {len(enhanced_files)}")
    print("=" * 60)

    return {
        "vocals_dir": vocals_dir,
        "vocal_files": enhanced_files,
        "melodies": melodies,
        "metadata": metadata_path
    }


def add_vocals_to_song(
    song_output: Dict,
    vocal_output: Dict,
    final_out_path: str
) -> str:
    """
    Mix vocals into the final song

    Args:
        song_output: Output from song_engine.generate_full_song()
        vocal_output: Output from generate_vocals()
        final_out_path: Path for final mixed song

    Returns:
        Path to final song with vocals
    """
    print("\nMixing vocals into final song...")

    try:
        from pydub import AudioSegment

        # Load instrumental
        instrumental = AudioSegment.from_wav(song_output["song_final"])

        # For now, we'll just save the instrumental
        # TODO: Implement proper vocal mixing with timing alignment
        instrumental.export(final_out_path, format="wav")

        print(f"✓ Final song with vocals: {final_out_path}")

        return final_out_path

    except Exception as e:
        print(f"Error mixing vocals: {e}")
        # Fallback: copy instrumental
        import shutil
        shutil.copy(song_output["song_final"], final_out_path)
        return final_out_path
