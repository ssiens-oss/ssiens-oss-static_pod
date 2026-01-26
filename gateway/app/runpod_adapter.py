"""
RunPod Serverless Adapter
Handles API calls to RunPod serverless endpoints with proper authentication and format
"""
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RunPodServerlessClient:
    """Client for RunPod serverless SDXL/image generation endpoints"""

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
        logger.info(f"RunPod serverless client initialized for: {endpoint_url}")

    def generate_image(self, prompt: str, timeout: int = 120, **kwargs) -> Dict[str, Any]:
        """
        Generate an image using RunPod SDXL template.

        Args:
            prompt: Text prompt for image generation
            timeout: Request timeout in seconds
            **kwargs: Additional parameters (seed, width, height, etc.)

        Returns:
            Response dict with status and output

        Raises:
            requests.RequestException: If request fails
        """
        # RunPod SDXL template expects: {"input": {"prompt": "...", ...}}
        input_params = {"prompt": prompt}

        # Add optional parameters if provided
        if kwargs.get("seed") is not None:
            input_params["seed"] = kwargs["seed"]
        if kwargs.get("width"):
            input_params["width"] = kwargs["width"]
        if kwargs.get("height"):
            input_params["height"] = kwargs["height"]
        if kwargs.get("num_inference_steps"):
            input_params["num_inference_steps"] = kwargs["num_inference_steps"]
        if kwargs.get("guidance_scale"):
            input_params["guidance_scale"] = kwargs["guidance_scale"]

        payload = {"input": input_params}

        logger.info(f"Calling RunPod SDXL: {self.endpoint_url}")
        logger.debug(f"Input params: {list(input_params.keys())}")

        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            status = result.get("status", "unknown")
            logger.info(f"RunPod response status: {status}")

            if status == "COMPLETED":
                output = result.get("output", {})
                prompt_id = f"sync-{result.get('id', 'unknown')}"
                logger.info(f"✓ RunPod job completed: {prompt_id}")
                logger.debug(f"Output keys: {list(output.keys()) if isinstance(output, dict) else type(output)}")
                return {
                    "prompt_id": prompt_id,
                    "status": "COMPLETED",
                    "output": output
                }
            elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                job_id = result.get("id")
                logger.info(f"RunPod job queued: {job_id}")
                return {
                    "prompt_id": job_id,
                    "status": status,
                    "job_id": job_id
                }
            elif status == "FAILED":
                error_msg = result.get("error", "Unknown error from RunPod")
                logger.error(f"RunPod job failed: {error_msg}")
                raise Exception(error_msg)
            else:
                error_msg = result.get("error", f"Unknown status: {status}")
                logger.error(f"RunPod error: {error_msg}")
                raise Exception(error_msg)

        except requests.HTTPError as e:
            logger.error(f"RunPod HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"RunPod request failed: {e}")
            raise

    def submit_workflow(self, workflow: Dict[str, Any], client_id: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Submit a ComfyUI workflow to RunPod serverless endpoint.

        NOTE: This is for ComfyUI-based endpoints. For SDXL templates, use generate_image().

        Args:
            workflow: ComfyUI workflow dict
            client_id: Client identifier
            timeout: Request timeout in seconds

        Returns:
            Response dict with prompt_id or error
        """
        # For ComfyUI endpoints: {"input": {"workflow": {...}}}
        payload = {
            "input": {
                "workflow": workflow,
                "client_id": client_id
            }
        }

        logger.info(f"Calling RunPod ComfyUI: {self.endpoint_url}")
        logger.debug(f"Payload keys: {list(payload['input'].keys())}")

        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            status = result.get("status", "unknown")
            logger.debug(f"Response status: {status}")

            if status == "COMPLETED":
                output = result.get("output", {})
                prompt_id = output.get("prompt_id") or result.get("id")
                logger.info(f"✓ RunPod job completed: {prompt_id}")
                return {
                    "prompt_id": prompt_id,
                    "status": "COMPLETED",
                    "output": output
                }
            elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                job_id = result.get("id")
                logger.info(f"RunPod job queued: {job_id}")
                return {
                    "prompt_id": job_id,
                    "status": status,
                    "job_id": job_id
                }
            elif status == "FAILED":
                error_msg = result.get("error", "Unknown error from RunPod")
                logger.error(f"RunPod job failed: {error_msg}")
                raise Exception(error_msg)
            else:
                error_msg = result.get("error", f"Unknown status: {status}")
                logger.error(f"RunPod error: {error_msg}")
                raise Exception(error_msg)

        except requests.HTTPError as e:
            logger.error(f"RunPod HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"RunPod request failed: {e}")
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
            result = response.json()
            logger.debug(f"Job {job_id} status: {result.get('status')}")
            return result

        except requests.RequestException as e:
            logger.error(f"RunPod status request failed: {e}")
            raise


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
            logger.error("RunPod API key is required for serverless endpoints!")
            raise ValueError("RUNPOD_API_KEY is required for RunPod serverless endpoints")

        logger.info("✓ Using RunPod serverless client")
        return RunPodServerlessClient(api_url, runpod_api_key)
    else:
        logger.info("✓ Using direct ComfyUI connection")
        return None
