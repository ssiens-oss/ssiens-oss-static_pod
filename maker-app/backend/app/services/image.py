"""
Image generation service - ComfyUI integration
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8188")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_POD_ID = os.getenv("RUNPOD_POD_ID")


def enqueue(job_id: int, prompt: str, style: Optional[str] = None):
    """
    Enqueue image generation job
    This is called asynchronously by the worker
    """
    logger.info(f"[IMAGE] Enqueuing job {job_id}: {prompt}")

    # In production, send to message queue (Redis/RabbitMQ)
    # For now, log the job
    # Worker will pick this up from database

    # Optional: Start RunPod pod if not running
    if RUNPOD_API_KEY and RUNPOD_POD_ID:
        try:
            start_runpod_pod()
        except Exception as e:
            logger.warning(f"Failed to start RunPod pod: {e}")

    return {"status": "queued"}


def generate(job_id: int, prompt: str, style: Optional[str] = None) -> str:
    """
    Actual generation logic (called by worker)
    Returns output URL
    """
    logger.info(f"[IMAGE] Generating job {job_id}")

    try:
        # Build ComfyUI workflow
        workflow = build_workflow(prompt, style)

        # Submit to ComfyUI
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={
                "prompt": workflow,
                "client_id": f"maker_{job_id}"
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")

            # Poll for completion (in production use websocket)
            output_url = poll_for_completion(prompt_id)

            logger.info(f"[IMAGE] Job {job_id} completed: {output_url}")
            return output_url
        else:
            raise Exception(f"ComfyUI error: {response.text}")

    except Exception as e:
        logger.error(f"[IMAGE] Job {job_id} failed: {e}")
        raise


def build_workflow(prompt: str, style: Optional[str] = None) -> dict:
    """Build ComfyUI workflow JSON"""
    # Simplified workflow - customize based on your ComfyUI setup
    return {
        "3": {
            "inputs": {
                "seed": -1,
                "steps": 20,
                "cfg": 7,
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
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": prompt + (f", {style}" if style else ""),
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, distorted",
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
                "filename_prefix": f"maker_",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }


def poll_for_completion(prompt_id: str, max_attempts: int = 60) -> str:
    """Poll ComfyUI for completion (simplified)"""
    import time

    for attempt in range(max_attempts):
        try:
            response = requests.get(
                f"{COMFYUI_URL}/history/{prompt_id}",
                timeout=5
            )

            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, output in outputs.items():
                        if "images" in output:
                            # Get first image
                            image = output["images"][0]
                            filename = image["filename"]
                            # Return CDN URL (upload to S3/CDN in production)
                            return f"{COMFYUI_URL}/view/{filename}"

        except Exception as e:
            logger.warning(f"Poll attempt {attempt} failed: {e}")

        time.sleep(2)

    raise Exception("Generation timeout")


def start_runpod_pod():
    """Start RunPod pod if not running"""
    if not RUNPOD_API_KEY or not RUNPOD_POD_ID:
        return

    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}

    response = requests.post(
        f"https://api.runpod.io/v1/pods/{RUNPOD_POD_ID}/start",
        headers=headers,
        timeout=30
    )

    if response.status_code == 200:
        logger.info("RunPod pod started")
    else:
        logger.warning(f"Failed to start RunPod pod: {response.text}")
