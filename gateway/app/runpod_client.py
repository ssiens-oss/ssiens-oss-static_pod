"""
RunPod Serverless Client
Handles API calls to RunPod serverless endpoints with proper authentication and format
"""
import requests
import logging
from typing import Dict, Any, Optional, List
import time
import base64
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class RunPodServerlessClient:
    """Client for RunPod serverless ComfyUI endpoints"""

    def __init__(self, endpoint_url: str, api_key: str):
        """
        Initialize RunPod serverless client

        Args:
            endpoint_url: RunPod serverless endpoint URL (e.g., https://api.runpod.ai/v2/{endpoint_id}/runsync)
            api_key: RunPod API key for authentication
        """
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def submit_workflow(self, workflow: Dict[str, Any], client_id: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Submit a ComfyUI workflow to RunPod serverless endpoint

        Args:
            workflow: ComfyUI workflow dict
            client_id: Client identifier
            timeout: Request timeout in seconds

        Returns:
            Response dict with prompt_id or error

        Raises:
            requests.RequestException: If request fails
        """
        # Wrap workflow in RunPod serverless format
        payload = {
            "input": {
                "workflow": workflow,
                "client_id": client_id
            }
        }

        logger.info(f"Submitting workflow to RunPod serverless: {self.endpoint_url}")

        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"RunPod serverless response: {result.get('status', 'unknown')}")

            # RunPod serverless returns: {"id": "...", "status": "COMPLETED", "output": {...}}
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                # Extract prompt_id from output if available
                prompt_id = output.get("prompt_id") or result.get("id")
                return {
                    "prompt_id": prompt_id,
                    "status": "COMPLETED",
                    "output": output
                }
            elif result.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                # For async responses, return the job ID
                return {
                    "prompt_id": result.get("id"),
                    "status": result.get("status"),
                    "job_id": result.get("id")
                }
            else:
                # Error or unknown status
                error_msg = result.get("error", "Unknown error from RunPod serverless")
                logger.error(f"RunPod serverless error: {error_msg}")
                raise Exception(error_msg)

        except requests.RequestException as e:
            logger.error(f"RunPod serverless request failed: {e}")
            raise

    def get_job_status(self, job_id: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Get status of a RunPod serverless job

        Args:
            job_id: RunPod job ID
            timeout: Request timeout in seconds

        Returns:
            Job status dict
        """
        # Extract endpoint base URL (remove /runsync)
        base_url = self.endpoint_url.replace("/runsync", "").replace("/run", "")
        status_url = f"{base_url}/status/{job_id}"

        logger.info(f"Checking RunPod job status: {status_url}")

        try:
            response = requests.get(
                status_url,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"RunPod status request failed: {e}")
            raise

    def download_images_from_output(self, output: Dict[str, Any], target_dir: Path) -> List[str]:
        """
        Download images from RunPod serverless output to local directory

        Args:
            output: RunPod output dict containing image data
            target_dir: Directory to save images

        Returns:
            List of saved image file paths
        """
        saved_images = []
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # RunPod ComfyUI typically returns images in output['images'] or output['files']
        images_data = output.get('images', []) or output.get('files', [])

        if not images_data:
            # Try to get from nested output structure
            if 'output' in output:
                images_data = output['output'].get('images', []) or output['output'].get('files', [])

        if not images_data:
            logger.warning("No images found in RunPod output")
            return saved_images

        logger.info(f"Found {len(images_data)} image(s) in RunPod output")

        for idx, image_data in enumerate(images_data):
            try:
                # Generate unique filename
                filename = f"generated_{uuid.uuid4().hex[:8]}_{idx}.png"
                filepath = target_dir / filename

                # Handle different image formats from RunPod
                if isinstance(image_data, dict):
                    # Option 1: Base64 encoded image
                    if 'data' in image_data or 'base64' in image_data:
                        base64_str = image_data.get('data') or image_data.get('base64')
                        # Remove data URL prefix if present
                        if ',' in base64_str:
                            base64_str = base64_str.split(',')[1]

                        image_bytes = base64.b64decode(base64_str)
                        filepath.write_bytes(image_bytes)
                        logger.info(f"Saved base64 image: {filename}")
                        saved_images.append(str(filepath))

                    # Option 2: URL to download
                    elif 'url' in image_data:
                        url = image_data['url']
                        response = requests.get(url, timeout=30)
                        response.raise_for_status()
                        filepath.write_bytes(response.content)
                        logger.info(f"Downloaded image from URL: {filename}")
                        saved_images.append(str(filepath))

                    # Option 3: Filename in ComfyUI output directory (RunPod specific)
                    elif 'filename' in image_data:
                        logger.warning(f"Image filename provided but cannot download: {image_data['filename']}")

                elif isinstance(image_data, str):
                    # String could be base64 or URL
                    if image_data.startswith('http'):
                        # It's a URL
                        response = requests.get(image_data, timeout=30)
                        response.raise_for_status()
                        filepath.write_bytes(response.content)
                        logger.info(f"Downloaded image from URL: {filename}")
                        saved_images.append(str(filepath))
                    else:
                        # Assume base64
                        if ',' in image_data:
                            image_data = image_data.split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                        filepath.write_bytes(image_bytes)
                        logger.info(f"Saved base64 image: {filename}")
                        saved_images.append(str(filepath))

            except Exception as e:
                logger.error(f"Failed to save image {idx}: {e}")
                continue

        logger.info(f"Successfully saved {len(saved_images)} image(s) to {target_dir}")
        return saved_images


def create_comfyui_client(api_url: str, runpod_api_key: Optional[str] = None):
    """
    Factory function to create appropriate client based on URL

    Args:
        api_url: ComfyUI or RunPod API URL
        runpod_api_key: RunPod API key (required for serverless)

    Returns:
        RunPodServerlessClient if serverless URL, None for direct ComfyUI
    """
    is_serverless = "api.runpod.ai" in api_url or "runsync" in api_url

    if is_serverless:
        if not runpod_api_key:
            raise ValueError("RUNPOD_API_KEY is required for RunPod serverless endpoints")

        logger.info("Using RunPod serverless client")
        return RunPodServerlessClient(api_url, runpod_api_key)
    else:
        logger.info("Using direct ComfyUI connection")
        return None  # Use direct requests for standard ComfyUI
