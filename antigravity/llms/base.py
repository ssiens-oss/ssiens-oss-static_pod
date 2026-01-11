"""Base utilities for LLM integration."""

from typing import Tuple


def normalize_response(text: str, base_confidence: float = 0.85) -> Tuple[str, float]:
    """
    Normalize and clean LLM response.

    Returns:
        (cleaned_text, confidence_score)
    """
    if not text:
        return "", 0.0

    cleaned = text.strip()

    # Adjust confidence based on response quality indicators
    confidence = base_confidence

    # Lower confidence for very short responses
    if len(cleaned) < 20:
        confidence *= 0.8

    # Lower confidence for uncertain language
    uncertainty_markers = ["maybe", "might", "possibly", "unsure", "unclear"]
    if any(marker in cleaned.lower() for marker in uncertainty_markers):
        confidence *= 0.9

    # Higher confidence for decisive language
    decisive_markers = ["definitely", "clearly", "certainly", "confirmed"]
    if any(marker in cleaned.lower() for marker in decisive_markers):
        confidence *= 1.05

    # Cap confidence at 0.95
    confidence = min(confidence, 0.95)

    return cleaned, confidence


def extract_reasoning(response: str) -> Tuple[str, str]:
    """
    Extract main content and reasoning from response.

    Returns:
        (content, reasoning)
    """
    # Look for reasoning markers
    reasoning_markers = [
        "\n\nReasoning:",
        "\n\nExplanation:",
        "\n\nBecause:",
    ]

    for marker in reasoning_markers:
        if marker in response:
            parts = response.split(marker, 1)
            return parts[0].strip(), parts[1].strip()

    return response.strip(), ""
