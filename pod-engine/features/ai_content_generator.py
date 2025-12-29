#!/usr/bin/env python3
"""
AI-Powered Content Generator
Uses Claude/GPT for product descriptions and SEO content
"""
import os
import json
import requests
from typing import Dict, List

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AIContentGenerator:
    """Generate product content using AI"""

    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self.api_key = ANTHROPIC_API_KEY if provider == "anthropic" else OPENAI_API_KEY

    def generate_product_content(
        self,
        image_description: str,
        product_type: str = "hoodie",
        style: str = "casual",
        target_audience: str = "young adults"
    ) -> Dict[str, any]:
        """Generate product title, description, tags, and keywords"""

        prompt = f"""Generate compelling e-commerce content for this product:

Product Type: {product_type}
Design: {image_description}
Style: {style}
Target Audience: {target_audience}

Create:
1. A catchy product title (50-70 chars)
2. Full product description (150-200 words, SEO-optimized)
3. Short description (40-60 words)
4. 10 relevant tags
5. 15 SEO keywords

Format as JSON with keys: title, description, short_description, tags, seo_keywords"""

        if self.provider == "anthropic":
            return self._generate_anthropic(prompt)
        else:
            return self._generate_openai(prompt)

    def _generate_anthropic(self, prompt: str) -> Dict:
        """Generate using Claude"""
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            response.raise_for_status()

            content = response.json()["content"][0]["text"]
            # Clean markdown if present
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)

        except Exception as e:
            return self._fallback_content()

    def _fallback_content(self) -> Dict:
        """Fallback content if AI fails"""
        return {
            "title": "Premium Custom Design Product",
            "description": "High-quality custom design featuring unique artwork. Perfect for standing out with style.",
            "short_description": "Unique custom design, premium quality.",
            "tags": ["custom", "design", "premium", "unique", "art"],
            "seo_keywords": ["custom design", "unique art", "premium quality"]
        }
