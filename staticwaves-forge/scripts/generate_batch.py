#!/usr/bin/env python3
"""
StaticWaves Forge - Batch Asset Generator
Generate multiple assets at once for creating asset packs
"""

import sys
import json
import argparse
from pathlib import Path
import subprocess
from typing import List, Dict

def generate_asset_batch(
    asset_type: str,
    count: int,
    style: str = "low-poly",
    base_seed: int = 42,
    output_dir: str = "./output/batch"
):
    """
    Generate a batch of assets

    Args:
        asset_type: Type of asset to generate
        count: Number of assets to generate
        style: Visual style
        base_seed: Base seed (each asset gets base_seed + index)
        output_dir: Where to save outputs
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🔥 Generating {count} {asset_type} assets in {style} style")
    print(f"   Output: {output_path}")
    print("━" * 60)

    results = []

    for i in range(count):
        seed = base_seed + i
        asset_name = f"{asset_type}_{seed}"
        asset_output = output_path / f"{asset_name}.glb"

        print(f"\n[{i+1}/{count}] Generating {asset_name}...")

        try:
            # Run Blender generation script
            cmd = [
                "blender",
                "--background",
                "--python", "packages/blender/generate_asset.py",
                "--",
                str(seed),
                asset_type,
                str(asset_output),
                style
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print(f"   ✅ Success: {asset_output}")
                results.append({
                    "name": asset_name,
                    "path": str(asset_output),
                    "seed": seed,
                    "status": "success"
                })
            else:
                print(f"   ❌ Failed: {result.stderr[:200]}")
                results.append({
                    "name": asset_name,
                    "seed": seed,
                    "status": "failed",
                    "error": result.stderr[:200]
                })

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "name": asset_name,
                "seed": seed,
                "status": "error",
                "error": str(e)
            })

    # Save manifest
    manifest_path = output_path / "batch_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump({
            "asset_type": asset_type,
            "style": style,
            "total_count": count,
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] != "success"]),
            "results": results
        }, f, indent=2)

    print("\n" + "━" * 60)
    print(f"✅ Batch complete!")
    print(f"   Success: {len([r for r in results if r['status'] == 'success'])}/{count}")
    print(f"   Manifest: {manifest_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate batches of 3D assets for asset packs"
    )
    parser.add_argument("asset_type", help="Type of asset (creature, prop, weapon, etc.)")
    parser.add_argument("count", type=int, help="Number of assets to generate")
    parser.add_argument("--style", default="low-poly", help="Visual style")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    parser.add_argument("--output", default="./output/batch", help="Output directory")

    args = parser.parse_args()

    generate_asset_batch(
        asset_type=args.asset_type,
        count=args.count,
        style=args.style,
        base_seed=args.seed,
        output_dir=args.output
    )

if __name__ == "__main__":
    main()
