"""
Abstract Base Client Interface

Defines the contract for image generation backends (RunPod, ComfyUI, etc.)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class JobStatus(Enum):
    """Job execution status"""
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class GenerationResult:
    """Result from an image generation request"""
    job_id: str
    status: JobStatus
    prompt_id: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    images: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if job completed successfully"""
        return self.status == JobStatus.COMPLETED

    def is_pending(self) -> bool:
        """Check if job is still running"""
        return self.status in (JobStatus.QUEUED, JobStatus.IN_PROGRESS)

    def has_failed(self) -> bool:
        """Check if job failed"""
        return self.status == JobStatus.FAILED


class GenerationClient(ABC):
    """Abstract base class for image generation backends"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this backend"""
        pass

    @abstractmethod
    def submit_workflow(
        self,
        workflow: Dict[str, Any],
        client_id: str,
        timeout: int = 120
    ) -> GenerationResult:
        """
        Submit a ComfyUI workflow for execution.

        Args:
            workflow: ComfyUI workflow dictionary
            client_id: Unique client identifier
            timeout: Request timeout in seconds

        Returns:
            GenerationResult with job status and any available output
        """
        pass

    @abstractmethod
    def get_job_status(self, job_id: str, timeout: int = 30) -> GenerationResult:
        """
        Check status of a submitted job.

        Args:
            job_id: Job identifier from submit_workflow
            timeout: Request timeout in seconds

        Returns:
            GenerationResult with current status
        """
        pass

    def is_serverless(self) -> bool:
        """Check if this is a serverless/async backend"""
        return False
