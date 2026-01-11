"""Type definitions for Antigravity orchestration system."""

from pydantic import BaseModel
from typing import List, Literal, Any, Optional
from enum import Enum


class Role(str, Enum):
    """Task roles for model routing."""
    ANALYSIS = "analysis"
    COPY = "copy"
    SAFETY = "safety"
    PRICING = "pricing"
    EXECUTION = "execution"


class SubTask(BaseModel):
    """A decomposed subtask to be handled by a specific model."""
    role: Role
    prompt: str
    context: Optional[dict] = None


class ModelResponse(BaseModel):
    """Response from an LLM model."""
    model: str
    role: Role
    content: str
    confidence: float
    reasoning: Optional[str] = None


class ExecutionPlan(BaseModel):
    """Plan for executing actions."""
    actions: List[dict]
    metadata: Optional[dict] = None
    risk_level: Optional[str] = "medium"


class PODOffer(BaseModel):
    """A POD product offer variant."""
    price: float
    headline: str
    description: str
    tags: List[str]
    brand: str
    variant_id: Optional[str] = None


class DecisionRecord(BaseModel):
    """Record of a decision made by the system."""
    decision_id: str
    task: str
    subtasks: List[SubTask]
    responses: List[ModelResponse]
    plan: Optional[ExecutionPlan] = None
    outcome: Optional[str] = None
    timestamp: float
