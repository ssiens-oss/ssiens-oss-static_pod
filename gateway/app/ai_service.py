"""
AI Content Generation Service
Uses Claude API (Anthropic) for intelligent title, description, and tag generation
"""
import anthropic
import os
import logging
import base64
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProductMetadata:
    """Generated product metadata"""
    title: str
    description: str
    tags: List[str]
    keywords: List[str]
    suggested_price_cents: int
    style: str
    themes: List[str]


class AIContentGenerator:
    """
    AI-powered content generation for POD products

    Features:
    - Auto-generate SEO-optimized titles
    - Create compelling product descriptions
    - Extract visual themes and styles
    - Suggest relevant tags and keywords
    - Recommend pricing based on complexity
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI content generator

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required (set ANTHROPIC_API_KEY env var)")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("AI Content Generator initialized")

    def _encode_image(self, image_path: str) -> Tuple[str, str]:
        """
        Encode image as base64 for Claude API

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Determine media type
        suffix = path.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        media_type = media_types.get(suffix, "image/png")

        return image_data, media_type

    def generate_product_metadata(
        self,
        image_path: str,
        product_type: str = "hoodie",
        target_audience: str = "general",
        style_preference: Optional[str] = None
    ) -> ProductMetadata:
        """
        Generate comprehensive product metadata from image

        Args:
            image_path: Path to product image
            product_type: Type of product (hoodie, tshirt, poster, etc.)
            target_audience: Target audience (general, youth, professionals, etc.)
            style_preference: Optional style override (e.g., "vintage", "modern")

        Returns:
            ProductMetadata with all generated content
        """
        try:
            logger.info(f"Generating metadata for {image_path}")

            # Encode image
            image_data, media_type = self._encode_image(image_path)

            # Build prompt
            prompt = self._build_metadata_prompt(product_type, target_audience, style_preference)

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }],
            )

            # Parse response
            response_text = message.content[0].text
            metadata = self._parse_metadata_response(response_text, product_type)

            logger.info(f"Generated metadata: {metadata.title}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
            # Return fallback metadata
            return self._get_fallback_metadata(product_type)

    def _build_metadata_prompt(
        self,
        product_type: str,
        target_audience: str,
        style_preference: Optional[str]
    ) -> str:
        """Build the prompt for Claude API"""
        prompt = f"""Analyze this image for a print-on-demand {product_type} product and generate optimized marketing content.

Target Audience: {target_audience}
"""
        if style_preference:
            prompt += f"Style Preference: {style_preference}\n"

        prompt += """
Please provide:

1. TITLE (50-80 characters, SEO-optimized, captivating)
   - Include key visual elements
   - Make it searchable and appealing
   - Follow format: "[Main Theme] [Product Type] - [Style/Detail]"

2. DESCRIPTION (150-250 words, persuasive)
   - Start with emotional hook
   - Describe visual elements and style
   - Highlight quality and versatility
   - Include use cases
   - End with call to action

3. TAGS (10-15 relevant tags for search)
   - Mix of specific and broad terms
   - Include style, theme, audience, occasion

4. KEYWORDS (15-20 SEO keywords)
   - High-search-volume terms
   - Long-tail keywords
   - Related concepts

5. STYLE (single word: vintage, modern, minimalist, bold, artistic, etc.)

6. THEMES (3-5 main themes: nature, abstract, geometric, fantasy, etc.)

7. SUGGESTED_PRICE (in USD, consider complexity and appeal)
   - Basic designs: $25-35
   - Detailed designs: $35-45
   - Premium/Complex: $45-60

Format your response EXACTLY as follows:
TITLE: [your title here]
DESCRIPTION: [your description here]
TAGS: tag1, tag2, tag3, tag4, tag5
KEYWORDS: keyword1, keyword2, keyword3, keyword4
STYLE: [style]
THEMES: theme1, theme2, theme3
PRICE: [price in USD]
"""
        return prompt

    def _parse_metadata_response(self, response: str, product_type: str) -> ProductMetadata:
        """Parse Claude's response into ProductMetadata"""
        lines = response.strip().split('\n')
        data = {}

        current_key = None
        current_value = []

        for line in lines:
            if ':' in line and line.split(':')[0].strip().upper() in [
                'TITLE', 'DESCRIPTION', 'TAGS', 'KEYWORDS', 'STYLE', 'THEMES', 'PRICE'
            ]:
                # Save previous key
                if current_key:
                    data[current_key] = '\n'.join(current_value).strip()

                # Start new key
                parts = line.split(':', 1)
                current_key = parts[0].strip().upper()
                current_value = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Continue current value
                if current_key and line.strip():
                    current_value.append(line.strip())

        # Save last key
        if current_key:
            data[current_key] = '\n'.join(current_value).strip()

        # Extract and clean data
        title = data.get('TITLE', f'Premium {product_type.title()}')[:200]
        description = data.get('DESCRIPTION', f'High-quality {product_type} with unique design')

        tags = [t.strip() for t in data.get('TAGS', '').split(',') if t.strip()]
        keywords = [k.strip() for k in data.get('KEYWORDS', '').split(',') if k.strip()]
        themes = [t.strip() for t in data.get('THEMES', '').split(',') if t.strip()]

        style = data.get('STYLE', 'modern').strip()

        # Parse price
        price_str = data.get('PRICE', '35').strip()
        try:
            # Extract numeric value
            import re
            price_match = re.search(r'(\d+(?:\.\d+)?)', price_str)
            if price_match:
                price_usd = float(price_match.group(1))
                price_cents = int(price_usd * 100)
            else:
                price_cents = 3499  # Default $34.99
        except:
            price_cents = 3499

        # Ensure we have at least some tags/keywords
        if not tags:
            tags = [product_type, style, 'unique design', 'gift']
        if not keywords:
            keywords = [product_type, 'custom', 'print', style, 'apparel']
        if not themes:
            themes = ['custom design', 'artistic']

        return ProductMetadata(
            title=title,
            description=description,
            tags=tags[:15],  # Limit to 15 tags
            keywords=keywords[:20],  # Limit to 20 keywords
            suggested_price_cents=price_cents,
            style=style,
            themes=themes[:5]  # Limit to 5 themes
        )

    def _get_fallback_metadata(self, product_type: str) -> ProductMetadata:
        """Return fallback metadata if AI generation fails"""
        return ProductMetadata(
            title=f"Premium {product_type.title()} - Unique Design",
            description=f"High-quality {product_type} featuring a unique, eye-catching design. "
                       f"Perfect for everyday wear or as a thoughtful gift. "
                       f"Comfortable, durable, and stylish.",
            tags=[product_type, "custom", "unique", "gift", "style"],
            keywords=[product_type, "custom design", "unique", "fashion", "apparel"],
            suggested_price_cents=3499,  # $34.99
            style="modern",
            themes=["custom design"]
        )

    def generate_title_only(
        self,
        image_path: str,
        product_type: str = "hoodie",
        max_length: int = 80
    ) -> str:
        """
        Quick title generation without full metadata

        Args:
            image_path: Path to image
            product_type: Product type
            max_length: Maximum title length

        Returns:
            Generated title
        """
        try:
            metadata = self.generate_product_metadata(image_path, product_type)
            title = metadata.title[:max_length]
            return title
        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
            return f"Premium {product_type.title()}"

    def generate_description_only(
        self,
        image_path: str,
        product_type: str = "hoodie"
    ) -> str:
        """
        Quick description generation without full metadata

        Args:
            image_path: Path to image
            product_type: Product type

        Returns:
            Generated description
        """
        try:
            metadata = self.generate_product_metadata(image_path, product_type)
            return metadata.description
        except Exception as e:
            logger.error(f"Failed to generate description: {e}")
            return f"High-quality {product_type} with unique design"

    def batch_generate_metadata(
        self,
        image_paths: List[str],
        product_type: str = "hoodie"
    ) -> List[ProductMetadata]:
        """
        Generate metadata for multiple images

        Args:
            image_paths: List of image paths
            product_type: Product type

        Returns:
            List of ProductMetadata objects
        """
        results = []
        for image_path in image_paths:
            try:
                metadata = self.generate_product_metadata(image_path, product_type)
                results.append(metadata)
            except Exception as e:
                logger.error(f"Failed to generate metadata for {image_path}: {e}")
                results.append(self._get_fallback_metadata(product_type))

        return results
