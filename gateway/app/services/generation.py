"""
Generation Service

Handles image generation workflow using the configured backend (RunPod or ComfyUI).
"""
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.clients import GenerationClient, GenerationResult, JobStatus
from app.models.schemas import GenerateRequest, GenerationResponse
from app.utils.workflow import build_comfyui_workflow, build_prompt_text

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for managing image generation"""

    def __init__(
        self,
        client: Optional[GenerationClient],
        image_service: Optional["ImageService"] = None
    ):
        """
        Initialize generation service.

        Args:
            client: Generation client (RunPod or ComfyUI)
            image_service: Optional image service for saving generated images
        """
        self.client = client
        self.image_service = image_service

    @property
    def is_available(self) -> bool:
        """Check if generation client is available"""
        return self.client is not None

    @property
    def backend_name(self) -> str:
        """Get the name of the configured backend"""
        if self.client:
            return self.client.name
        return "None"

    def generate(self, request: GenerateRequest) -> GenerationResponse:
        """
        Generate an image from a prompt.

        Args:
            request: Generation request with prompt and parameters

        Returns:
            GenerationResponse with job status and results
        """
        if not self.client:
            return GenerationResponse(
                status="error",
                error="Generation client not configured"
            )

        # Build full prompt with style/genre
        full_prompt = build_prompt_text(request.prompt, request.style, request.genre)
        logger.info(f"Generating with {self.backend_name}: {full_prompt[:50]}...")

        # Build ComfyUI workflow
        workflow = build_comfyui_workflow(
            prompt=full_prompt,
            seed=request.seed,
            width=request.width,
            height=request.height,
            steps=request.steps,
            cfg_scale=request.cfg_scale
        )

        # Generate client_id if not provided
        client_id = request.client_id or f"pod-gateway-{uuid.uuid4().hex[:8]}"

        # Submit workflow
        result = self.client.submit_workflow(workflow, client_id)

        # Process result
        return self._build_response(result, full_prompt)

    def check_status(self, job_id: str) -> GenerationResponse:
        """
        Check the status of a generation job.

        Args:
            job_id: Job identifier

        Returns:
            GenerationResponse with current status
        """
        if not self.client:
            return GenerationResponse(
                status="error",
                error="Generation client not configured"
            )

        result = self.client.get_job_status(job_id)
        return self._build_response(result, "")

    def _build_response(
        self,
        result: GenerationResult,
        prompt: str
    ) -> GenerationResponse:
        """Build API response from generation result."""
        saved_images: List[Dict[str, str]] = []

        # If completed and we have image service, save images
        if result.is_complete() and self.image_service and result.images:
            for img_data in result.images:
                saved = self._save_image(img_data)
                if saved:
                    saved_images.append(saved)

        return GenerationResponse(
            prompt_id=result.prompt_id,
            job_id=result.job_id,
            status=result.status.value,
            prompt=prompt,
            source="runpod" if self.client and self.client.is_serverless() else "comfyui",
            images=saved_images,
            error=result.error
        )

    def _save_image(self, img_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Save an image from generation result."""
        if not self.image_service:
            return None

        # Try different image data formats
        image_data = (
            img_data.get("url") or
            img_data.get("data") or
            img_data.get("image") or
            img_data.get("base64")
        )

        if image_data:
            result = self.image_service.save_from_data(image_data)
            if result:
                return {"id": result[0], "path": result[1]}

        # Handle ComfyUI filename reference
        if img_data.get("filename"):
            result = self.image_service.save_from_comfyui(
                filename=img_data["filename"],
                subfolder=img_data.get("subfolder", ""),
                image_type=img_data.get("type", "output")
            )
            if result:
                return {"id": result[0], "path": result[1]}

        return None
