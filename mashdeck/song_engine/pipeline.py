"""
Full Song Pipeline - End-to-end song generation orchestration
Combines planning, generation, arrangement, and mastering
"""

import json
import os
from typing import Dict, List, Optional

from .planner import plan_song, export_song_plan
from .generator import generate_section
from .arranger import arrange
from .master import master, create_loudness_variants


def generate_full_song(
    style: str = "edm",
    bpm: Optional[int] = None,
    key: Optional[str] = None,
    title: Optional[str] = None,
    out_dir: str = "output",
    create_variants: bool = False
) -> Dict[str, str]:
    """
    Generate a complete full-length song from scratch

    Args:
        style: Music style (edm, lofi, trap, hiphop, ambient, rock)
        bpm: BPM (auto-selected if None)
        key: Musical key (auto-selected if None)
        title: Song title (auto-generated if None)
        out_dir: Output directory
        create_variants: Create platform-specific loudness variants

    Returns:
        Dict with paths to generated files
    """
    print("=" * 60)
    print("MashDeck Full Song Generation Pipeline")
    print("=" * 60)

    # Create output directories
    os.makedirs(out_dir, exist_ok=True)
    sections_dir = os.path.join(out_dir, "sections")
    os.makedirs(sections_dir, exist_ok=True)

    # Step 1: Plan the song
    print("\n[1/5] Planning song structure...")
    plan = plan_song(style=style, bpm=bpm, key=key, title=title)

    print(f"  Title: {plan['title']}")
    print(f"  Style: {plan['style']}")
    print(f"  BPM: {plan['bpm']}")
    print(f"  Key: {plan['key']}")
    print(f"  Sections: {len(plan['structure'])}")

    # Save plan
    plan_path = os.path.join(out_dir, "song_plan.json")
    export_song_plan(plan, plan_path)

    # Step 2: Generate sections
    print("\n[2/5] Generating song sections...")
    section_files = []

    for i, section in enumerate(plan["structure"]):
        print(f"  Section {i+1}/{len(plan['structure'])}: {section['section']} "
              f"({section['bars']} bars, energy={section['energy']})")

        path = generate_section(section, plan, sections_dir)
        section_files.append(path)

    # Step 3: Arrange sections
    print("\n[3/5] Arranging sections with crossfades...")
    raw_path = os.path.join(out_dir, "song_raw.wav")
    arranged_path = arrange(section_files, raw_path, crossfade_ms=4000)

    # Step 4: Master the track
    print("\n[4/5] Mastering...")
    final_path = os.path.join(out_dir, "song_final.wav")
    master(arranged_path, final_path)

    # Step 5: Create variants (optional)
    variant_paths = {}
    if create_variants:
        print("\n[5/5] Creating platform variants...")
        variants_dir = os.path.join(out_dir, "variants")
        variant_paths = create_loudness_variants(final_path, variants_dir)

    # Prepare output
    output = {
        "song_final": final_path,
        "song_raw": arranged_path,
        "song_plan": plan_path,
        "sections_dir": sections_dir,
        "metadata": {
            "title": plan["title"],
            "style": plan["style"],
            "bpm": plan["bpm"],
            "key": plan["key"],
            "sections": len(plan["structure"])
        }
    }

    if variant_paths:
        output["variants"] = variant_paths

    # Save metadata
    metadata_path = os.path.join(out_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("✓ Song Generation Complete!")
    print("=" * 60)
    print(f"Final Song: {final_path}")
    print(f"Metadata: {metadata_path}")
    print("=" * 60)

    return output


def generate_song_batch(
    count: int = 5,
    style: Optional[str] = None,
    base_dir: str = "batch_output"
) -> List[Dict]:
    """
    Generate multiple songs in batch

    Args:
        count: Number of songs to generate
        style: Style (random if None)
        base_dir: Base output directory

    Returns:
        List of output dicts from each generation
    """
    import random

    styles = ["edm", "lofi", "trap", "hiphop", "ambient", "rock"]

    outputs = []

    for i in range(count):
        selected_style = style or random.choice(styles)
        song_dir = os.path.join(base_dir, f"song_{i+1:02d}")

        print(f"\n{'=' * 60}")
        print(f"Generating Song {i+1}/{count}")
        print(f"{'=' * 60}\n")

        output = generate_full_song(
            style=selected_style,
            out_dir=song_dir
        )

        outputs.append(output)

    return outputs


if __name__ == "__main__":
    # Example usage
    import sys

    style = sys.argv[1] if len(sys.argv) > 1 else "edm"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "my_song"

    generate_full_song(style=style, out_dir=out_dir, create_variants=True)
