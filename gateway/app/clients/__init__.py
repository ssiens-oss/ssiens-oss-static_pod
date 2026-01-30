"""
Image Generation Clients

Provides a unified interface for interacting with different image generation backends:
- RunPod Serverless
- Direct ComfyUI
"""
from app.clients.base import GenerationClient, GenerationResult, JobStatus
from app.clients.runpod import RunPodClient
from app.clients.comfyui import ComfyUIClient
from app.clients.factory import create_generation_client

__all__ = [
    "GenerationClient",
    "GenerationResult",
    "JobStatus",
    "RunPodClient",
    "ComfyUIClient",
    "create_generation_client",
]
