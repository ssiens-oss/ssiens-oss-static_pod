"""
Listing Generator - Claude-powered marketing copy generation
Generates SEO-optimized titles, descriptions, hashtags, and social media content
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import anthropic
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ListingGenerator:
    """Generates marketplace listings using Claude AI"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.claude.api_key)
        self.model = config.claude.model
        self.max_tokens = config.claude.max_tokens

    def generate_listing(
        self,
        asset_type: str,
        theme: str,
        style: str,
        usage: str,
        prompts: List[str],
        additional_context: Optional[str] = None
    ) -> Dict:
        """Generate complete marketplace listing"""
        logger.info(f"Generating listing for: {theme} {asset_type}")

        system_prompt = """You are an expert digital asset marketer specializing in game assets, UI kits, and creative tools.

Your task is to generate compelling, SEO-optimized marketplace listings that:
- Use emotional, benefit-driven language
- Include relevant keywords naturally
- Appeal to indie game developers and creators
- Highlight time-saving and quality benefits
- Use power words and urgency when appropriate

Generate output in valid JSON format only."""

        user_prompt = f"""Generate a complete marketplace listing for the following digital asset:

**Asset Type:** {asset_type}
**Theme:** {theme}
**Style:** {style}
**Usage:** {usage}
**Generation Prompts:** {', '.join(prompts)}
{f'**Additional Context:** {additional_context}' if additional_context else ''}

Generate the following in JSON format:

1. **seo_title**: An SEO-optimized product title (max 60 chars) that includes theme, type, and key benefit
2. **short_description**: A punchy 1-2 sentence hook (max 150 chars) for search results
3. **long_description**: A detailed 3-4 paragraph description covering:
   - What's included
   - Key benefits and use cases
   - Quality and uniqueness
   - Who it's perfect for
4. **tags**: 15 relevant tags for discoverability (single words or 2-word phrases)
5. **hashtags**: 10 hashtags for social media (include # symbol)
6. **tiktok_hook**: A 1-sentence attention-grabbing hook for TikTok (max 100 chars)
7. **auto_replies**: 3 pre-written friendly replies to common customer questions
8. **pricing_suggestion**: Recommended price range (low, mid, high) in USD
9. **marketing_angles**: 3 different marketing angles to test in ads

Return ONLY valid JSON with these exact keys."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Extract JSON from response
            content = response.content[0].text

            # Try to parse JSON from code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            listing_data = json.loads(content)

            logger.info("Listing generated successfully")
            return listing_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.debug(f"Raw response: {content}")
            return {}
        except Exception as e:
            logger.error(f"Failed to generate listing: {e}")
            return {}

    def generate_from_template(self, template_path: Path) -> Dict:
        """Generate listing from JSON template file"""
        logger.info(f"Loading template: {template_path}")

        try:
            with open(template_path, 'r') as f:
                template = json.load(f)

            return self.generate_listing(
                asset_type=template.get("asset_type", "Asset Pack"),
                theme=template.get("theme", "Generic"),
                style=template.get("style", "Modern"),
                usage=template.get("usage", "Game Development"),
                prompts=template.get("prompts", []),
                additional_context=template.get("additional_context")
            )

        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return {}

    def save_listing(self, listing_data: Dict, output_path: Path):
        """Save generated listing to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(listing_data, f, indent=2)
            logger.info(f"Listing saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save listing: {e}")

    def generate_batch(self, templates: List[Path]) -> Dict[str, Dict]:
        """Generate listings for multiple templates"""
        results = {}

        for template_path in templates:
            listing = self.generate_from_template(template_path)
            if listing:
                results[template_path.stem] = listing

                # Save individual listing
                output_path = template_path.parent / f"{template_path.stem}_listing.json"
                self.save_listing(listing, output_path)

        logger.info(f"Generated {len(results)} listings")
        return results


class QualityScorer:
    """Uses Claude to score and rank asset quality"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.claude.api_key)
        self.model = config.claude.model

    def score_asset(
        self,
        asset_name: str,
        description: str,
        revenue: float,
        views: int,
        downloads: int,
        age_days: int
    ) -> Dict:
        """Score an asset's quality and potential"""
        logger.info(f"Scoring asset: {asset_name}")

        prompt = f"""Analyze this digital asset's performance and provide a quality score:

**Asset Name:** {asset_name}
**Description:** {description}
**Revenue:** ${revenue}
**Views:** {views:,}
**Downloads:** {downloads}
**Age:** {age_days} days

Provide a JSON response with:
1. **overall_score**: 0-10 rating of asset quality and market fit
2. **revenue_score**: 0-10 rating of revenue performance
3. **engagement_score**: 0-10 rating of view-to-download conversion
4. **longevity_score**: 0-10 rating of sustainable revenue potential
5. **recommendation**: "keep", "optimize", or "kill"
6. **reasoning**: 2-3 sentences explaining the recommendation
7. **optimization_tips**: List of 3 actionable improvements (if applicable)

Return ONLY valid JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,  # Lower temperature for more consistent scoring
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            score_data = json.loads(content)
            logger.info(f"Score: {score_data.get('overall_score', 0)}/10 - {score_data.get('recommendation', 'unknown')}")

            return score_data

        except Exception as e:
            logger.error(f"Failed to score asset: {e}")
            return {}

    def batch_score(self, assets: List[Dict]) -> List[Dict]:
        """Score multiple assets and rank them"""
        results = []

        for asset in assets:
            score = self.score_asset(
                asset_name=asset.get("name", "Unknown"),
                description=asset.get("description", ""),
                revenue=asset.get("revenue", 0),
                views=asset.get("views", 0),
                downloads=asset.get("downloads", 0),
                age_days=asset.get("age_days", 0)
            )

            if score:
                results.append({
                    **asset,
                    "claude_score": score
                })

        # Sort by overall score
        results.sort(key=lambda x: x.get("claude_score", {}).get("overall_score", 0), reverse=True)

        logger.info(f"Scored {len(results)} assets")
        return results


def main():
    """Example usage"""
    generator = ListingGenerator()

    # Example: Generate listing
    listing = generator.generate_listing(
        asset_type="2D Icon Pack",
        theme="Fantasy Potions",
        style="Hand-painted, Vibrant",
        usage="RPG UI, Game Development",
        prompts=[
            "fantasy potion icons, vibrant colors, game UI style",
            "magical elixirs, glowing effects, transparent bottles"
        ],
        additional_context="32 unique icons, PNG format, 512x512px"
    )

    if listing:
        print("\n" + "=" * 60)
        print("GENERATED LISTING")
        print("=" * 60)
        print(f"\nTitle: {listing.get('seo_title')}")
        print(f"\nShort: {listing.get('short_description')}")
        print(f"\nTags: {', '.join(listing.get('tags', []))}")
        print(f"\nPrice: {listing.get('pricing_suggestion')}")
        print("\n" + "=" * 60)

        # Save listing
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        generator.save_listing(listing, output_dir / "fantasy_potions_listing.json")

    # Example: Score assets
    scorer = QualityScorer()

    test_assets = [
        {
            "name": "Fantasy Potion Icons",
            "description": "32 magical potion icons",
            "revenue": 145.50,
            "views": 2340,
            "downloads": 87,
            "age_days": 45
        }
    ]

    scored = scorer.batch_score(test_assets)

    if scored:
        print("\n" + "=" * 60)
        print("ASSET SCORING")
        print("=" * 60)
        for asset in scored:
            score = asset.get("claude_score", {})
            print(f"\n{asset['name']}")
            print(f"  Score: {score.get('overall_score')}/10")
            print(f"  Recommendation: {score.get('recommendation')}")
            print(f"  Reasoning: {score.get('reasoning')}")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
