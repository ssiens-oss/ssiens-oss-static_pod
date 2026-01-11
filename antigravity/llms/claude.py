"""Anthropic Claude integration."""

import os
from typing import Tuple
from antigravity.llms.base import normalize_response, extract_reasoning

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def call(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> Tuple[str, float]:
    """
    Call Anthropic Claude model.

    Args:
        prompt: The prompt to send
        model: Model to use (default: claude-3-5-sonnet-20241022)

    Returns:
        (response_text, confidence_score)
    """
    if not ANTHROPIC_AVAILABLE:
        raise RuntimeError("Anthropic package not installed. Install with: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    try:
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a safety-aware AI assistant for POD business operations. "
                   "Carefully evaluate risks, policy compliance, and potential issues. "
                   "Be thorough in identifying problems before they occur.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        if not message.content:
            return "", 0.0

        # Claude returns a list of content blocks
        content = message.content[0].text if message.content else ""

        # Extract reasoning if present
        main_content, reasoning = extract_reasoning(content)

        # Normalize response
        normalized, confidence = normalize_response(main_content)

        # Claude is typically more conservative, adjust confidence for safety
        if "BLOCK" in normalized.upper() or "RISK" in normalized.upper():
            confidence *= 1.1  # Higher confidence in safety warnings
            confidence = min(confidence, 0.95)

        return normalized, confidence

    except Exception as e:
        print(f"Claude API error: {e}")
        return f"ERROR: {str(e)}", 0.0
