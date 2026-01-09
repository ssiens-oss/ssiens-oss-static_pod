"""
Claude Prompt Generator
"""
import anthropic
import json
from typing import List, Dict

class PromptGenerator:
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate_prompts(
        self,
        theme: str = "general",
        style: str = "modern",
        niche: str = "general audience",
        count: int = 5,
        product_type: str = "tshirt"
    ) -> List[Dict]:
        """Generate creative POD prompts using Claude"""

        system_prompt = f"""You are an expert POD (Print-on-Demand) designer and AI art prompt engineer. Your role is to create highly effective prompts for AI image generation that will be used on {product_type}s.

Key requirements for POD designs:
- Designs must be visually striking and stand out in online marketplaces
- Prompts should generate images suitable for apparel printing
- Focus on clean, bold graphics that work well on fabric
- Avoid overly complex details that don't translate well to print
- Consider popular trends in POD marketplaces (minimalism, vintage, abstract, typography, nature, etc.)

Your output MUST be valid JSON with the following structure:
{{
  "prompts": [
    {{
      "prompt": "Detailed AI art generation prompt",
      "title": "Product title for marketplace",
      "tags": ["tag1", "tag2", "tag3"],
      "description": "Product description for customers"
    }}
  ]
}}

Make prompts specific, creative, and optimized for commercial appeal."""

        user_prompt = f"""Generate {count} creative and commercially viable POD design prompt{"s" if count > 1 else ""} with the following criteria:

Theme: {theme}
Style: {style}
Target Niche: {niche}

Each prompt should:
1. Be detailed enough for AI image generation (Stable Diffusion/SDXL)
2. Include artistic style, composition, colors, and mood
3. Be optimized for print-on-demand apparel
4. Have commercial appeal for the target niche
5. Include a catchy product title
6. Include relevant marketplace tags
7. Include a compelling product description

Return ONLY valid JSON as specified in the system prompt."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=1.0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            content = response.content[0].text

            # Parse JSON response
            prompts = self._parse_response(content)
            return prompts

        except Exception as e:
            print(f"Error generating prompts: {e}")
            raise

    def _parse_response(self, content: str) -> List[Dict]:
        """Parse Claude's response into structured prompts"""
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            parsed = json.loads(json_str)
            return parsed.get("prompts", [])

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Content: {content[:200]}")
            # Fallback
            return [{
                "prompt": content[:500],
                "title": "AI Generated Design",
                "tags": ["ai-art", "unique", "creative"],
                "description": "Unique AI-generated design"
            }]

    def refine_prompt(self, original_prompt: str, improvements: str) -> Dict:
        """Refine an existing prompt"""
        user_prompt = f"""Refine this POD design prompt to {improvements}:

Original prompt: {original_prompt}

Return a single improved prompt in the same JSON format as before."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            content = response.content[0].text
            prompts = self._parse_response(content)
            return prompts[0] if prompts else None

        except Exception as e:
            print(f"Error refining prompt: {e}")
            raise
