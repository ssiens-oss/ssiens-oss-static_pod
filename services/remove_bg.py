#!/usr/bin/env python3
"""
Background Removal Service
Removes background from images using rembg (U²-Net model)
"""

import sys
import os

# Force CPU-only mode to avoid cuDNN dependencies on RunPod
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from rembg import remove
from PIL import Image


def remove_background(input_path: str, output_path: str):
    """
    Remove background from image and save as transparent PNG

    Args:
        input_path: Path to input image
        output_path: Path to save transparent PNG
    """
    # Load image
    img = Image.open(input_path).convert("RGBA")

    # Remove background
    out = remove(img)

    # Save result
    out.save(output_path, "PNG")

    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python remove_bg.py <input_image> <output_image>")
        print("Example: python remove_bg.py design.png design_transparent.png")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Validate input
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Remove background
    try:
        result = remove_background(input_path, output_path)
        print(f"Background removed successfully: {result}")
    except Exception as e:
        print(f"Error removing background: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
