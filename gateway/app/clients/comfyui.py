"""
Direct ComfyUI Client

Handles API calls to a local or remote ComfyUI instance.
"""
import logging
import requests
from typing import Any, Dict

from app.clients.base import GenerationClient, GenerationResult, JobStatus

logger = logging.getLogger(__name__)


class ComfyUIClient(GenerationClient):
    """Client for direct ComfyUI API connections"""

    def __init__(self, api_url: str):
        """
        Initialize ComfyUI client.

        Args:
            api_url: ComfyUI API base URL (e.g., http://localhost:8188)
        """
        self.api_url = api_url.rstrip("/")
        logger.info(f"ComfyUI client initialized: {api_url}")

    @property
    def name(self) -> str:
        return "ComfyUI Direct"

    def submit_workflow(
        self,
        workflow: Dict[str, Any],
        client_id: str,
        timeout: int = 120
    ) -> GenerationResult:
        """Submit workflow to ComfyUI /prompt endpoint."""
        payload = {
            "prompt": workflow,
            "client_id": client_id
        }

        logger.info(f"Submitting workflow to ComfyUI: {self.api_url}/prompt")

        try:
            response = requests.post(
                f"{self.api_url}/prompt",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()

            prompt_id = result.get("prompt_id", "")
            logger.info(f"Workflow submitted successfully: {prompt_id}")

            return GenerationResult(
                job_id=prompt_id,
                status=JobStatus.QUEUED,
                prompt_id=prompt_id
            )

        except requests.HTTPError as e:
            logger.error(f"ComfyUI HTTP error: {e.response.status_code} - {e.response.text}")
            return GenerationResult(
                job_id="",
                status=JobStatus.FAILED,
                error=f"HTTP {e.response.status_code}: {e.response.text}"
            )
        except requests.RequestException as e:
            logger.error(f"ComfyUI request failed: {e}")
            return GenerationResult(
                job_id="",
                status=JobStatus.FAILED,
                error=str(e)
            )

    def get_job_status(self, job_id: str, timeout: int = 30) -> GenerationResult:
        """Check status via ComfyUI /history endpoint."""
        logger.info(f"Checking ComfyUI history for: {job_id}")

        try:
            response = requests.get(
                f"{self.api_url}/history/{job_id}",
                timeout=timeout
            )
            response.raise_for_status()
            history = response.json()

            prompt_entry = history.get(job_id, {})
            status_info = prompt_entry.get("status", {})
            outputs = prompt_entry.get("outputs", {})

            # Determine status from history
            if status_info.get("completed"):
                images = self._extract_images_from_history(outputs)
                return GenerationResult(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    prompt_id=job_id,
                    output=outputs,
                    images=images
                )
            elif status_info.get("status_str") == "error":
                return GenerationResult(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    prompt_id=job_id,
                    error=status_info.get("messages", ["Unknown error"])[0]
                )
            else:
                return GenerationResult(
                    job_id=job_id,
                    status=JobStatus.IN_PROGRESS,
                    prompt_id=job_id
                )

        except requests.RequestException as e:
            logger.error(f"ComfyUI status check failed: {e}")
            return GenerationResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                error=str(e)
            )

    def _extract_images_from_history(self, outputs: Dict[str, Any]) -> list:
        """Extract image metadata from ComfyUI history outputs."""
        images = []
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img in node_output["images"]:
                    images.append({
                        "filename": img.get("filename"),
                        "subfolder": img.get("subfolder", ""),
                        "type": img.get("type", "output")
                    })
        return images

    def download_image(
        self,
        filename: str,
        subfolder: str = "",
        image_type: str = "output",
        timeout: int = 60
    ) -> bytes | None:
        """
        Download an image from ComfyUI.

        Args:
            filename: Image filename
            subfolder: Optional subfolder
            image_type: Image type (output, temp, input)
            timeout: Request timeout

        Returns:
            Image bytes or None on failure
        """
        try:
            response = requests.get(
                f"{self.api_url}/view",
                params={
                    "filename": filename,
                    "subfolder": subfolder,
                    "type": image_type
                },
                timeout=timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to download image {filename}: {e}")
            return None
