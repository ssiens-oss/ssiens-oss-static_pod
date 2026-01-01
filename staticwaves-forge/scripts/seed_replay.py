#!/usr/bin/env python3
"""
StaticWaves Forge - Seed Replay System
Reproduce any previously generated asset using its seed
"""

import sys
import json
import argparse
from pathlib import Path
import subprocess

def replay_asset(seed: int, output_path: str = None):
    """
    Regenerate an asset from its seed

    Args:
        seed: The random seed used in original generation
        output_path: Where to save the regenerated asset
    """
    if output_path is None:
        output_path = f"./output/replay_{seed}.glb"

    print(f"🔄 Replaying asset generation with seed {seed}")
    print(f"   Output: {output_path}")

    # In production, this would:
    # 1. Look up the seed in database
    # 2. Retrieve original generation parameters
    # 3. Re-run generation with same parameters
    # 4. Output should be identical

    cmd = [
        "blender",
        "--background",
        "--python", "packages/blender/generate_asset.py",
        "--",
        str(seed),
        "prop",  # Would be retrieved from DB
        output_path,
        "low-poly"  # Would be retrieved from DB
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"✅ Asset regenerated successfully")
            print(f"   Saved to: {output_path}")
            return True
        else:
            print(f"❌ Generation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Reproduce assets from their generation seeds"
    )
    parser.add_argument("seed", type=int, help="Seed to replay")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    replay_asset(args.seed, args.output)

if __name__ == "__main__":
    main()
