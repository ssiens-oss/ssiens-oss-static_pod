"""Uncertainty modeling and disagreement detection."""

from statistics import variance, mean
from antigravity.types import ModelResponse
from typing import List


def disagreement_score(responses: List[ModelResponse]) -> float:
    """
    Calculate disagreement score based on confidence variance.
    Higher score = more disagreement between models.
    """
    if len(responses) < 2:
        return 0.0

    confidences = [r.confidence for r in responses]
    return variance(confidences)


def confidence_mean(responses: List[ModelResponse]) -> float:
    """Calculate mean confidence across all responses."""
    if not responses:
        return 0.0
    return mean([r.confidence for r in responses])


def should_escalate(
    responses: List[ModelResponse],
    disagreement_threshold: float = 0.05,
    confidence_threshold: float = 0.7
) -> tuple[bool, str]:
    """
    Determine if human escalation is needed.

    Returns:
        (should_escalate, reason)
    """
    if not responses:
        return True, "No model responses received"

    disagreement = disagreement_score(responses)
    avg_confidence = confidence_mean(responses)

    if disagreement > disagreement_threshold:
        return True, f"High disagreement detected (score: {disagreement:.3f})"

    if avg_confidence < confidence_threshold:
        return True, f"Low confidence (avg: {avg_confidence:.3f})"

    # Check for conflicting safety blocks
    safety_blocks = [r for r in responses if r.role.value == "safety" and "BLOCK" in r.content.upper()]
    non_safety = [r for r in responses if r.role.value != "safety"]

    if safety_blocks and non_safety:
        return True, "Safety model conflicts with other models"

    return False, "Confidence and agreement acceptable"
