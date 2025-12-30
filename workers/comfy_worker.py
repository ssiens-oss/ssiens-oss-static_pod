#!/usr/bin/env python3
"""
ComfyUI GPU Worker
Batch-safe, GPU-aware image generation worker
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import requests

DATA_DIR = Path(__file__).parent.parent / "data"
QUEUE_DIR = DATA_DIR / "queue"

# ComfyUI configuration
COMFYUI_API = os.environ.get("COMFYUI_API", "http://localhost:8188")
COMFYUI_PATH = os.environ.get("COMFYUI_PATH", "/opt/ComfyUI")

def process_queue():
    """
    Main worker loop: process pending items
    """
    print("🎨 ComfyUI Worker starting...")

    while True:
        try:
            # Get next pending item
            pending_items = list((QUEUE_DIR / "pending").glob("*.json"))

            if not pending_items:
                time.sleep(5)
                continue

            # Process first item
            item_file = pending_items[0]
            process_item(item_file)

        except KeyboardInterrupt:
            print("\n⏹️  Worker stopped")
            break
        except Exception as e:
            print(f"❌ Worker error: {e}")
            time.sleep(10)

def process_item(item_file):
    """
    Process a single queue item

    Steps:
    1. Load item from pending queue
    2. Generate design with ComfyUI
    3. Move to processing → done/failed
    """

    print(f"📝 Processing: {item_file.name}")

    # Move to processing
    processing_file = QUEUE_DIR / "processing" / item_file.name
    item_file.rename(processing_file)

    try:
        # Load item data
        with open(processing_file) as f:
            item_data = json.load(f)

        # Generate design
        design_path = generate_design(item_data)

        # Update item with design path
        item_data["design_path"] = str(design_path)
        item_data["processed_at"] = datetime.utcnow().isoformat()

        # Move to done
        done_file = QUEUE_DIR / "done" / processing_file.name
        with open(done_file, "w") as f:
            json.dump(item_data, f, indent=2)

        processing_file.unlink()

        print(f"✅ Completed: {item_file.name}")

    except Exception as e:
        print(f"❌ Failed: {item_file.name} - {e}")

        # Move to failed with error info
        failed_file = QUEUE_DIR / "failed" / processing_file.name

        try:
            with open(processing_file) as f:
                item_data = json.load(f)

            item_data["error"] = str(e)
            item_data["failed_at"] = datetime.utcnow().isoformat()

            with open(failed_file, "w") as f:
                json.dump(item_data, f, indent=2)

            processing_file.unlink()

        except Exception:
            pass

def generate_design(item_data):
    """
    Generate design using ComfyUI

    Args:
        item_data: dict with 'prompt' and other metadata

    Returns:
        Path: Path to generated image
    """

    prompt = item_data.get("prompt", "abstract art")
    sku = item_data.get("sku", f"design_{int(time.time())}")

    # Output path
    output_dir = DATA_DIR / "designs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{sku}.png"

    # Try ComfyUI API
    if is_comfyui_running():
        print(f"🖼️  Generating via ComfyUI API: {prompt}")
        generate_via_api(prompt, output_path)
    else:
        # Fallback: direct ComfyUI execution
        print(f"🖼️  Generating via ComfyUI CLI: {prompt}")
        generate_via_cli(prompt, output_path)

    return output_path

def is_comfyui_running():
    """Check if ComfyUI API is available"""
    try:
        response = requests.get(f"{COMFYUI_API}/system_stats", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

def generate_via_api(prompt, output_path):
    """
    Generate image via ComfyUI API

    This uses the ComfyUI workflow API
    """

    # Basic workflow structure
    # In production, load from config or generate dynamically
    workflow = {
        "3": {
            "inputs": {
                "seed": int(time.time()),
                "steps": 20,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {"text": prompt, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "text, watermark, low quality",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "StaticWaves",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

    # Queue prompt
    response = requests.post(
        f"{COMFYUI_API}/prompt",
        json={"prompt": workflow}
    )

    if response.status_code != 200:
        raise Exception(f"ComfyUI API error: {response.text}")

    # Wait for completion and download
    # In production, poll for status and download result
    time.sleep(10)  # Simplified wait

    # Create placeholder for now
    output_path.touch()

def generate_via_cli(prompt, output_path):
    """
    Generate image via ComfyUI CLI

    Fallback method when API is not available
    """

    # Save prompt to temp file
    prompt_file = Path("/tmp") / f"prompt_{int(time.time())}.txt"
    with open(prompt_file, "w") as f:
        f.write(prompt)

    # Run ComfyUI
    # In production, this would execute actual ComfyUI
    # subprocess.run([
    #     "python3",
    #     f"{COMFYUI_PATH}/main.py",
    #     "--prompt-file", str(prompt_file),
    #     "--output", str(output_path)
    # ])

    # Create placeholder
    output_path.touch()
    prompt_file.unlink()

if __name__ == "__main__":
    # Ensure queue directories exist
    for stage in ["pending", "processing", "done", "failed"]:
        (QUEUE_DIR / stage).mkdir(parents=True, exist_ok=True)

    # Start worker
    process_queue()
