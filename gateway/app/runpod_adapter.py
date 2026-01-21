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

    def submit_workflow(self, workflow: Dict[str, Any], client_id: str, timeout: int = 300, poll_interval: int = 2) -> Dict[str, Any]:
        """
        Submit a ComfyUI workflow to RunPod serverless endpoint (optimized for POD)

        Args:
            workflow: ComfyUI workflow dict
            client_id: Client identifier
            timeout: Request timeout in seconds (increased to 300 for complex POD workflows)
            poll_interval: Polling interval for async jobs in seconds

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

        logger.info(f"🚀 Submitting POD workflow to RunPod: {self.endpoint_url}")
        logger.debug(f"Payload keys: {list(payload.keys())}, input keys: {list(payload['input'].keys())}")

        try:
            # Submit workflow with extended timeout for POD
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"📡 RunPod response received")
            logger.debug(f"Response status: {result.get('status', 'unknown')}")

            # RunPod serverless returns: {"id": "...", "status": "COMPLETED", "output": {...}}
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                # Extract prompt_id from output if available
                prompt_id = output.get("prompt_id") or result.get("id")
                logger.info(f"✅ RunPod job completed successfully: {prompt_id}")
                return {
                    "prompt_id": prompt_id,
                    "status": "COMPLETED",
                    "output": output
                }
            elif result.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                # For async responses, poll until completion
                job_id = result.get("id")
                logger.info(f"⏳ RunPod job queued: {job_id}, polling for completion...")

                # Poll for completion (POD optimization: auto-poll)
                import time
                start_time = time.time()
                while time.time() - start_time < timeout:
                    time.sleep(poll_interval)
                    status_result = self.get_job_status(job_id, timeout=30)

                    if status_result.get("status") == "COMPLETED":
                        output = status_result.get("output", {})
                        prompt_id = output.get("prompt_id") or job_id
                        logger.info(f"✅ RunPod job completed after polling: {prompt_id}")
                        return {
                            "prompt_id": prompt_id,
                            "status": "COMPLETED",
                            "output": output
                        }
                    elif status_result.get("status") == "FAILED":
                        error_msg = status_result.get("error", "Job failed during execution")
                        logger.error(f"❌ RunPod job failed: {error_msg}")
                        raise Exception(error_msg)

                    logger.debug(f"Job {job_id} still {status_result.get('status')}, waiting...")

                # Timeout reached
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

            elif result.get("status") == "FAILED":
                # Job failed
                error_msg = result.get("error", "Unknown error from RunPod serverless")
                logger.error(f"❌ RunPod job failed: {error_msg}")
                raise Exception(error_msg)
            else:
                # Unknown status
                error_msg = result.get("error", f"Unknown status: {result.get('status')}")
                logger.error(f"⚠️ RunPod serverless error: {error_msg}")
                raise Exception(error_msg)

        except requests.HTTPError as e:
            status_code = e.response.status_code
            error_text = e.response.text

            if status_code == 401:
                logger.error(f"❌ RunPod authentication failed (401 Unauthorized)")
                logger.error(f"💡 Fix: Set RUNPOD_API_KEY in .env file")
                logger.error(f"   Example: RUNPOD_API_KEY=your-runpod-api-key-here")
                logger.error(f"   Get your key from: https://www.runpod.io/console/user/settings")
            elif status_code == 403:
                logger.error(f"❌ RunPod access forbidden (403)")
                logger.error(f"💡 Check: Endpoint ID and API key permissions")
            elif status_code == 404:
                logger.error(f"❌ RunPod endpoint not found (404)")
                logger.error(f"💡 Check: COMFYUI_API_URL endpoint ID is correct")
            else:
                logger.error(f"❌ RunPod HTTP error: {status_code} - {error_text}")

            raise
        except requests.Timeout as e:
            logger.error(f"⏱️ RunPod request timeout after {timeout}s")
            raise
        except requests.RequestException as e:
            logger.error(f"❌ RunPod serverless request failed: {e}")
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
