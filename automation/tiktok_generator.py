"""
TikTok Generator - AI-powered TikTok content creation
Generates captions, hooks, comments, and engagement strategies
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


class TikTokGenerator:
    """Generates TikTok content using Claude AI"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.claude.api_key)
        self.model = config.claude.model

    def generate_video_script(
        self,
        asset_name: str,
        theme: str,
        key_features: List[str],
        target_audience: str = "indie game developers",
        video_length: int = 30  # seconds
    ) -> Dict:
        """Generate TikTok video script and content plan"""
        logger.info(f"Generating TikTok script for: {asset_name}")

        prompt = f"""Create a compelling TikTok video script for promoting a digital asset.

**Asset:** {asset_name}
**Theme:** {theme}
**Key Features:** {', '.join(key_features)}
**Target Audience:** {target_audience}
**Video Length:** {video_length} seconds

Generate a JSON response with:

1. **hook** (first 3 seconds): Attention-grabbing opening line that stops scrollers
2. **caption**: Full TikTok caption with emojis, line breaks, and hashtags
3. **script_breakdown**: Array of 5-7 script segments with:
   - timestamp (e.g., "0-3s")
   - visual_direction (what to show on screen)
   - voiceover (what to say)
   - text_overlay (on-screen text)

4. **trending_sounds**: 3 TikTok sound/music suggestions that fit the vibe
5. **hashtags**: 15-20 hashtags (mix of trending, niche, and broad)
6. **posting_tips**: 3 tips for maximizing reach
7. **call_to_action**: Clear CTA for viewers
8. **thumbnail_ideas**: 3 eye-catching thumbnail concepts

Use a casual, authentic tone. Avoid being too salesy. Focus on value and relatability.

Return ONLY valid JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.8,  # Higher temp for creative content
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

            script_data = json.loads(content)
            logger.info("TikTok script generated successfully")

            return script_data

        except Exception as e:
            logger.error(f"Failed to generate TikTok script: {e}")
            return {}

    def generate_comment_replies(
        self,
        asset_name: str,
        common_questions: Optional[List[str]] = None
    ) -> Dict:
        """Generate engaging comment replies"""
        logger.info("Generating TikTok comment replies")

        default_questions = [
            "What software did you use?",
            "How much does this cost?",
            "Can I use this for commercial projects?",
            "Do you have more packs like this?",
            "Is this compatible with Unity/Unreal?",
            "How long did this take to make?",
            "Can you make a tutorial?",
            "Link?"
        ]

        questions = common_questions or default_questions

        prompt = f"""Generate friendly, engaging TikTok comment replies for a digital asset: {asset_name}

Common questions/comments:
{chr(10).join(f'- {q}' for q in questions)}

For each question, provide:
1. A natural, friendly reply (1-2 sentences)
2. Include relevant emojis
3. Encourage engagement without being pushy
4. Add value where possible

Also generate:
- **hype_replies**: 5 replies to positive comments ("This is fire!", "Need this!", etc.)
- **objection_handling**: 3 replies to common objections ("Too expensive", "Looks basic", etc.)
- **engagement_boosters**: 3 replies that encourage discussion and boost comments

Return as JSON with keys: replies, hype_replies, objection_handling, engagement_boosters"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1536,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            replies_data = json.loads(content)
            logger.info(f"Generated {len(replies_data.get('replies', {}))} comment replies")

            return replies_data

        except Exception as e:
            logger.error(f"Failed to generate comment replies: {e}")
            return {}

    def generate_content_series(
        self,
        asset_name: str,
        theme: str,
        num_videos: int = 5
    ) -> List[Dict]:
        """Generate a content series/campaign for an asset"""
        logger.info(f"Generating {num_videos}-video TikTok series")

        prompt = f"""Create a {num_videos}-video TikTok content series to promote: {asset_name} ({theme})

Generate a cohesive series that builds momentum:
- Video 1: Teaser/Problem introduction
- Video 2-{num_videos-1}: Value demonstrations, use cases, behind-the-scenes
- Video {num_videos}: Launch/Call-to-action

For each video, provide JSON with:
1. **video_number**: 1-{num_videos}
2. **title**: Internal reference title
3. **hook**: Opening line (3 seconds)
4. **concept**: 2-sentence video concept
5. **key_message**: Main takeaway
6. **caption_template**: TikTok caption structure
7. **recommended_day**: Best day to post (e.g., "Monday - high engagement")
8. **content_type**: Category (tutorial, showcase, behind-the-scenes, storytelling, etc.)

Return as JSON array."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            series_data = json.loads(content)

            if isinstance(series_data, dict) and "videos" in series_data:
                series_data = series_data["videos"]

            logger.info(f"Generated {len(series_data)} video concepts")
            return series_data

        except Exception as e:
            logger.error(f"Failed to generate content series: {e}")
            return []

    def analyze_viral_potential(
        self,
        script: Dict,
        asset_type: str = "icons"
    ) -> Dict:
        """Analyze viral potential of a TikTok script"""
        logger.info("Analyzing viral potential")

        prompt = f"""Analyze the viral potential of this TikTok script for a {asset_type} digital asset:

{json.dumps(script, indent=2)}

Rate the following on a scale of 0-10:
1. **hook_strength**: How attention-grabbing is the hook?
2. **relatability**: How relatable is the content to the target audience?
3. **value_clarity**: How clearly is the value communicated?
4. **trend_alignment**: How well does it align with current TikTok trends?
5. **shareability**: How likely are viewers to share this?
6. **cta_effectiveness**: How compelling is the call-to-action?

Also provide:
- **overall_score**: Average of all scores
- **viral_probability**: "low", "medium", "high", or "very high"
- **strengths**: List of 3 strong points
- **weaknesses**: List of 3 areas for improvement
- **optimization_tips**: 3 specific ways to improve viral potential

Return as JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)
            logger.info(f"Viral potential: {analysis.get('viral_probability', 'unknown')}")

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze viral potential: {e}")
            return {}

    def save_content(self, content: Dict, output_path: Path):
        """Save generated TikTok content to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(content, f, indent=2)
            logger.info(f"Content saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save content: {e}")


def main():
    """Example usage"""
    generator = TikTokGenerator()

    # Generate video script
    script = generator.generate_video_script(
        asset_name="Fantasy Potion Icons Pack",
        theme="Hand-Painted RPG UI",
        key_features=[
            "32 unique icons",
            "Vibrant colors",
            "Transparent PNG",
            "Game-ready"
        ],
        target_audience="indie game developers and RPG makers",
        video_length=30
    )

    if script:
        print("\n" + "=" * 60)
        print("TIKTOK VIDEO SCRIPT")
        print("=" * 60)
        print(f"\nHook: {script.get('hook')}")
        print(f"\nCaption:\n{script.get('caption')}")
        print(f"\nHashtags: {' '.join(script.get('hashtags', [])[:10])}")
        print("\n" + "=" * 60)

        # Analyze viral potential
        analysis = generator.analyze_viral_potential(script, "icon pack")
        print("\nVIRAL POTENTIAL ANALYSIS")
        print("=" * 60)
        print(f"Overall Score: {analysis.get('overall_score')}/10")
        print(f"Probability: {analysis.get('viral_probability')}")
        print(f"\nStrengths:")
        for strength in analysis.get('strengths', []):
            print(f"  ✓ {strength}")
        print("\n" + "=" * 60)

        # Save script
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        generator.save_content(script, output_dir / "tiktok_script.json")

    # Generate comment replies
    replies = generator.generate_comment_replies(
        asset_name="Fantasy Potion Icons Pack"
    )

    if replies:
        print("\n" + "=" * 60)
        print("COMMENT REPLY TEMPLATES")
        print("=" * 60)
        for question, reply in list(replies.get('replies', {}).items())[:3]:
            print(f"\nQ: {question}")
            print(f"A: {reply}")
        print("\n" + "=" * 60)

    # Generate content series
    series = generator.generate_content_series(
        asset_name="Fantasy Potion Icons Pack",
        theme="Hand-Painted RPG UI",
        num_videos=5
    )

    if series:
        print("\n" + "=" * 60)
        print("CONTENT SERIES (5 VIDEOS)")
        print("=" * 60)
        for video in series:
            print(f"\nVideo {video.get('video_number')}: {video.get('title')}")
            print(f"  Hook: {video.get('hook')}")
            print(f"  Type: {video.get('content_type')}")
            print(f"  Post: {video.get('recommended_day')}")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
