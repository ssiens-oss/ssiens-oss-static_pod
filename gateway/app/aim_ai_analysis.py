"""
AIM AI Analysis Module
Uses Claude API to analyze images for commercial suitability
"""
import os
import base64
from typing import Dict, Optional
from pathlib import Path
import json


class AIImageAnalyzer:
    """
    AI-powered image analysis using Claude API
    Evaluates commercial suitability, quality, and generates descriptions
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI analyzer

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.enabled = True
            except ImportError:
                print("⚠️  anthropic package not installed. AI analysis disabled.")
                self.enabled = False
        else:
            print("⚠️  ANTHROPIC_API_KEY not set. AI analysis disabled.")
            self.enabled = False

    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """
        Analyze image using Claude Vision API

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with analysis results or None if disabled
        """
        if not self.enabled:
            return None

        try:
            # Read and encode image
            image_data = self._encode_image(image_path)

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": self._get_media_type(image_path),
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": self._get_analysis_prompt()
                            }
                        ]
                    }
                ]
            )

            # Parse response
            analysis_text = response.content[0].text

            # Try to extract JSON from response
            analysis = self._parse_analysis_response(analysis_text)

            return analysis

        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                "error": str(e),
                "commercial_suitability": 50,
                "content_safety": True,
                "quality_assessment": "unknown"
            }

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _get_media_type(self, image_path: str) -> str:
        """Get media type from file extension"""
        ext = Path(image_path).suffix.lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return media_types.get(ext, 'image/png')

    def _get_analysis_prompt(self) -> str:
        """Get analysis prompt for Claude"""
        return """Analyze this image for Print-on-Demand (POD) commercial suitability.

Please provide your analysis in JSON format with the following fields:

{
  "commercial_suitability": <score 0-100>,
  "content_safety": <true/false>,
  "quality_assessment": "<excellent/good/fair/poor>",
  "design_style": "<description of artistic style>",
  "target_audience": "<suggested target demographic>",
  "product_suitability": {
    "t_shirt": <score 0-100>,
    "hoodie": <score 0-100>,
    "poster": <score 0-100>,
    "mug": <score 0-100>
  },
  "strengths": [<list of design strengths>],
  "weaknesses": [<list of potential issues>],
  "suggested_title": "<catchy product title>",
  "suggested_description": "<marketing description>",
  "suggested_tags": [<list of relevant tags>],
  "recommendation": "<approve/review/reject>",
  "reasoning": "<brief explanation of recommendation>"
}

Evaluation criteria:
1. Commercial viability - Would people buy this?
2. Content safety - No offensive, copyrighted, or inappropriate content
3. Visual quality - Clear, well-composed, print-ready
4. Design appeal - Aesthetic value and uniqueness
5. Product fit - Suitable for POD products

Be honest and practical in your assessment."""

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse Claude's response into structured data"""
        try:
            # Try to find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback: basic parsing
                return {
                    "commercial_suitability": 70,
                    "content_safety": True,
                    "quality_assessment": "good",
                    "raw_response": response_text,
                    "recommendation": "review"
                }

        except json.JSONDecodeError:
            # Return raw response if JSON parsing fails
            return {
                "commercial_suitability": 70,
                "content_safety": True,
                "quality_assessment": "unknown",
                "raw_response": response_text,
                "recommendation": "review"
            }

    def generate_product_description(self, image_path: str, title: str) -> Optional[str]:
        """
        Generate marketing description for product

        Args:
            image_path: Path to image
            title: Product title

        Returns:
            Marketing description or None
        """
        if not self.enabled:
            return None

        try:
            image_data = self._encode_image(image_path)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": self._get_media_type(image_path),
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": f"""Write a compelling product description for this design titled "{title}".

The description should:
- Be 2-3 sentences
- Highlight the unique aspects of the design
- Appeal to potential buyers
- Include relevant style/theme keywords
- Be suitable for e-commerce listings

Write only the description, no extra commentary."""
                            }
                        ]
                    }
                ]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Description generation error: {e}")
            return None

    def batch_analyze(self, image_paths: list) -> Dict[str, Dict]:
        """
        Analyze multiple images in batch

        Args:
            image_paths: List of image file paths

        Returns:
            Dictionary mapping image paths to analysis results
        """
        results = {}

        for image_path in image_paths:
            try:
                analysis = self.analyze_image(image_path)
                results[image_path] = analysis
            except Exception as e:
                results[image_path] = {"error": str(e)}

        return results

    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.enabled
