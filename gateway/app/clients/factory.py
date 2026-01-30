"""
Client Factory

Creates the appropriate generation client based on configuration.
"""
import logging
from typing import Optional

from app.clients.base import GenerationClient
from app.clients.runpod import RunPodClient
from app.clients.comfyui import ComfyUIClient

logger = logging.getLogger(__name__)


def is_runpod_url(url: str) -> bool:
    """Check if URL is a RunPod serverless endpoint."""
    return "api.runpod.ai" in url or "runsync" in url


def create_generation_client(
    api_url: str,
    runpod_api_key: Optional[str] = None
) -> GenerationClient:
    """
    Factory function to create the appropriate generation client.

    Args:
        api_url: ComfyUI or RunPod API URL
        runpod_api_key: RunPod API key (required for serverless)

    Returns:
        GenerationClient instance

    Raises:
        ValueError: If RunPod URL without API key
    """
    if is_runpod_url(api_url):
        if not runpod_api_key:
            raise ValueError("RUNPOD_API_KEY required for RunPod serverless endpoints")
        logger.info("Creating RunPod serverless client")
        return RunPodClient(api_url, runpod_api_key)
    else:
        logger.info("Creating direct ComfyUI client")
        return ComfyUIClient(api_url)
