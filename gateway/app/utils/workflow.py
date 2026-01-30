"""
ComfyUI Workflow Utilities

Functions for building ComfyUI workflows.
"""
import os
from typing import Any, Dict, Optional


def build_prompt_text(prompt: str, style: str = "", genre: str = "") -> str:
    """
    Build the full prompt text with optional style and genre.

    Args:
        prompt: Base prompt text
        style: Optional style descriptor
        genre: Optional genre descriptor

    Returns:
        Combined prompt string
    """
    parts = [prompt.strip()]
    if style:
        parts.append(f"{style} style")
    if genre:
        parts.append(f"{genre} genre")
    return ", ".join(part for part in parts if part)


def build_comfyui_workflow(
    prompt: str,
    seed: Optional[int] = None,
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    cfg_scale: float = 7.0,
    negative_prompt: str = "text, watermark, low quality, worst quality",
    checkpoint: str = "flux1-dev-fp8.safetensors"
) -> Dict[str, Any]:
    """
    Build a ComfyUI workflow for image generation.

    Args:
        prompt: Positive prompt text
        seed: Random seed (auto-generated if None)
        width: Image width in pixels
        height: Image height in pixels
        steps: Number of sampling steps
        cfg_scale: Classifier-free guidance scale
        negative_prompt: Negative prompt text
        checkpoint: Model checkpoint filename

    Returns:
        ComfyUI workflow dictionary
    """
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder="little")

    return {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": checkpoint
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": negative_prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
