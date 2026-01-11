"""OpenAI GPT integration."""

import os
from typing import Tuple
from antigravity.llms.base import normalize_response, extract_reasoning

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def call(prompt: str, model: str = "gpt-4o") -> Tuple[str, float]:
    """
    Call OpenAI GPT model.

    Args:
        prompt: The prompt to send
        model: Model to use (default: gpt-4o)

    Returns:
        (response_text, confidence_score)
    """
    if not OPENAI_AVAILABLE:
        raise RuntimeError("OpenAI package not installed. Install with: pip install openai")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strategic AI assistant focused on POD business optimization. "
                               "Provide clear, actionable responses with reasoning."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        if not content:
            return "", 0.0

        # Extract reasoning if present
        main_content, reasoning = extract_reasoning(content)

        # Normalize response
        normalized, confidence = normalize_response(main_content)

        # Adjust confidence based on finish reason
        finish_reason = response.choices[0].finish_reason
        if finish_reason == "stop":
            confidence *= 1.0
        elif finish_reason == "length":
            confidence *= 0.9  # Response was cut off

        return normalized, confidence

    except Exception as e:
        print(f"GPT API error: {e}")
        return f"ERROR: {str(e)}", 0.0
