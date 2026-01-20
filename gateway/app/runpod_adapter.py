"""
RunPod Serverless Adapter
Handles API calls to RunPod serverless endpoints with proper authentication and format
"""
import requests
import logging
from typing import Dict, Any, Optional

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
        logger.info(f"RunPod serverless client initialized for: {endpoint_url}")

    def submit_workflow(self, workflow: Dict[str, Any], client_id: str, timeout: int = 120, poll_for_completion: bool = True) -> Dict[str, Any]:
        """
        Submit a ComfyUI workflow to RunPod serverless endpoint

        Args:
            workflow: ComfyUI workflow dict
            client_id: Client identifier
            timeout: Request timeout in seconds
            poll_for_completion: If True, poll until job completes (default: True)

        Returns:
            Response dict with prompt_id or error

        Raises:
            requests.RequestException: If request fails
        """
        # CRITICAL: Wrap workflow in RunPod serverless format
        # RunPod handler expects: {"input": {"workflow": {...}}}
        payload = {
            "input": {
                "workflow": workflow,
                "client_id": client_id
            }
        }

        # Use /run endpoint for async submission instead of /runsync
        submit_url = self.endpoint_url.replace("/runsync", "/run")
        logger.info(f"Submitting to RunPod: {submit_url}")
        logger.debug(f"Payload keys: {list(payload.keys())}, input keys: {list(payload['input'].keys())}")

        try:
            response = requests.post(
                submit_url,
                json=payload,
                headers=self.headers,
                timeout=30  # Short timeout for submission
            )
            response.raise_for_status()

            result = response.json()
            job_id = result.get("id")
            if not job_id:
                raise Exception(f"No job ID in response: {result}")

            logger.info(f"✓ RunPod job submitted: {job_id}")

            # If polling is disabled, return immediately
            if not poll_for_completion:
                return {
                    "prompt_id": job_id,
                    "status": result.get("status", "IN_QUEUE"),
                    "job_id": job_id
                }

            # Poll for completion
            import time
            start_time = time.time()
            poll_interval = 3  # Start with 3 seconds
            max_poll_interval = 10  # Max 10 seconds between polls

            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.warning(f"Job {job_id} timed out after {timeout}s")
                    return {
                        "prompt_id": job_id,
                        "status": "TIMEOUT",
                        "job_id": job_id,
                        "error": f"Job did not complete within {timeout}s"
                    }

                # Poll job status
                status_result = self.get_job_status(job_id)
                status = status_result.get("status")

                logger.info(f"Job {job_id} status: {status} (elapsed: {int(elapsed)}s)")

                if status == "COMPLETED":
                    output = status_result.get("output", {})
                    logger.info(f"✓ Job {job_id} completed successfully")
                    return {
                        "prompt_id": job_id,
                        "status": "COMPLETED",
                        "output": output,
                        "job_id": job_id
                    }
                elif status == "FAILED":
                    error_msg = status_result.get("error", "Unknown error from RunPod")
                    logger.error(f"Job {job_id} failed: {error_msg}")
                    raise Exception(error_msg)
                elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                    # Continue polling
                    time.sleep(poll_interval)
                    # Gradually increase poll interval
                    poll_interval = min(poll_interval * 1.2, max_poll_interval)
                else:
                    logger.warning(f"Unknown job status: {status}")
                    time.sleep(poll_interval)

        except requests.HTTPError as e:
            logger.error(f"RunPod HTTP error: {e.response.status_code} - {e.response.text}")
            raise
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
        # Extract endpoint base URL (remove /runsync or /run)
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
        return None  # Use direct requests for standard ComfyUI
