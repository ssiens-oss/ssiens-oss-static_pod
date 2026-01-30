"""
RunPod Serverless Client

Handles API calls to RunPod serverless endpoints for ComfyUI workflow execution.
"""
import logging
import requests
from typing import Any, Dict

from app.clients.base import GenerationClient, GenerationResult, JobStatus

logger = logging.getLogger(__name__)


class RunPodClient(GenerationClient):
    """Client for RunPod serverless ComfyUI endpoints"""

    def __init__(self, endpoint_url: str, api_key: str):
        """
        Initialize RunPod serverless client.

        Args:
            endpoint_url: RunPod endpoint URL (e.g., https://api.runpod.ai/v2/{id}/runsync)
            api_key: RunPod API key for authentication
        """
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"RunPod client initialized: {endpoint_url}")

    @property
    def name(self) -> str:
        return "RunPod Serverless"

    def is_serverless(self) -> bool:
        return True

    def submit_workflow(
        self,
        workflow: Dict[str, Any],
        client_id: str,
        timeout: int = 120
    ) -> GenerationResult:
        """Submit workflow to RunPod serverless endpoint."""
        # RunPod expects: {"input": {"workflow": {...}, "client_id": "..."}}
        payload = {
            "input": {
                "workflow": workflow,
                "client_id": client_id
            }
        }

        logger.info(f"Submitting workflow to RunPod: {self.endpoint_url}")
        logger.debug(f"Payload structure: input.workflow keys={list(workflow.keys())}")

        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self._headers,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()

            return self._parse_response(result)

        except requests.HTTPError as e:
            logger.error(f"RunPod HTTP error: {e.response.status_code} - {e.response.text}")
            return GenerationResult(
                job_id="",
                status=JobStatus.FAILED,
                error=f"HTTP {e.response.status_code}: {e.response.text}"
            )
        except requests.RequestException as e:
            logger.error(f"RunPod request failed: {e}")
            return GenerationResult(
                job_id="",
                status=JobStatus.FAILED,
                error=str(e)
            )

    def get_job_status(self, job_id: str, timeout: int = 30) -> GenerationResult:
        """Check status of a RunPod job."""
        # Build status URL from endpoint (remove /runsync or /run)
        base_url = self.endpoint_url.replace("/runsync", "").replace("/run", "")
        status_url = f"{base_url}/status/{job_id}"

        logger.info(f"Checking job status: {job_id}")

        try:
            response = requests.get(
                status_url,
                headers=self._headers,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()

            return self._parse_response(result)

        except requests.RequestException as e:
            logger.error(f"RunPod status check failed: {e}")
            return GenerationResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                error=str(e)
            )

    def _parse_response(self, result: Dict[str, Any]) -> GenerationResult:
        """Parse RunPod API response into GenerationResult."""
        status_str = result.get("status", "UNKNOWN")
        job_id = result.get("id", "")
        output = result.get("output", {})

        # Map RunPod status to JobStatus
        status_map = {
            "COMPLETED": JobStatus.COMPLETED,
            "IN_QUEUE": JobStatus.QUEUED,
            "IN_PROGRESS": JobStatus.IN_PROGRESS,
            "FAILED": JobStatus.FAILED,
        }
        status = status_map.get(status_str, JobStatus.FAILED)

        # Extract images from output if present
        images = self._extract_images(output)

        if status == JobStatus.COMPLETED:
            logger.info(f"Job {job_id} completed with {len(images)} images")
        elif status == JobStatus.FAILED:
            logger.error(f"Job {job_id} failed: {result.get('error')}")

        return GenerationResult(
            job_id=job_id,
            status=status,
            prompt_id=output.get("prompt_id") or job_id,
            output=output,
            images=images,
            error=result.get("error") if status == JobStatus.FAILED else None
        )

    def _extract_images(self, output: Any) -> list:
        """Extract image data from RunPod output (recursive search)."""
        images = []
        stack = [output]

        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                # Check for images array
                if "images" in current and isinstance(current["images"], list):
                    for item in current["images"]:
                        if isinstance(item, dict):
                            images.append(item)
                        elif isinstance(item, str):
                            images.append({"data": item})
                # Check for single image field
                if "image" in current and isinstance(current["image"], str):
                    images.append({"data": current["image"]})
                # Recurse into dict values
                for value in current.values():
                    stack.append(value)
            elif isinstance(current, list):
                stack.extend(current)

        return images
