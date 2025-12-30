"""
POD Studio - Simplified Autonomous Backend
Multi-LLM integration using direct API clients
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import anthropic
from groq import Groq

# Load environment
load_dotenv('.env.pod')

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pod_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

@dataclass
class Config:
    """Application configuration"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    comfyui_url: Optional[str] = None
    printify_api_key: Optional[str] = None
    printify_shop_id: Optional[str] = None
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None

    @classmethod
    def load_from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            groq_api_key=os.getenv('GROQ_API_KEY'),
            comfyui_url=os.getenv('COMFYUI_URL'),
            printify_api_key=os.getenv('PRINTIFY_API_KEY'),
            printify_shop_id=os.getenv('PRINTIFY_SHOP_ID'),
            instagram_username=os.getenv('INSTAGRAM_USERNAME'),
            instagram_password=os.getenv('INSTAGRAM_PASSWORD'),
        )

class MultiLLMGenerator:
    """Generate content using multiple LLM providers"""

    def __init__(self, config: Config):
        self.config = config

        # Initialize clients
        if config.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=config.openai_api_key)
            logger.info("✅ OpenAI client initialized")
        else:
            self.openai_client = None
            logger.warning("⚠️  OpenAI API key not set")

        if config.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
            logger.info("✅ Anthropic client initialized")
        else:
            self.anthropic_client = None
            logger.warning("⚠️  Anthropic API key not set")

        if config.groq_api_key:
            self.groq_client = Groq(api_key=config.groq_api_key)
            logger.info("✅ Groq client initialized")
        else:
            self.groq_client = None
            logger.warning("⚠️  Groq API key not set")

    def generate_trend_analysis(self, theme: str) -> str:
        """Generate trend analysis using Groq (fastest, free tier)"""
        if not self.groq_client:
            logger.warning("Groq not available, skipping trend analysis")
            return f"Trending: {theme} streetwear aesthetic"

        try:
            prompt = f"""Analyze current streetwear trends for: {theme}

Provide:
1. Popular color palettes
2. Key design elements
3. Target audience preferences
4. Viral hashtag suggestions

Keep it concise (3-4 sentences)."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a streetwear trend analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )

            result = response.choices[0].message.content
            logger.info(f"✅ Trend analysis generated via Groq")
            return result

        except Exception as e:
            logger.error(f"Groq trend analysis failed: {e}")
            return f"Trending: {theme} with bold graphics and vibrant colors"

    def generate_design_prompt(self, trend_analysis: str) -> str:
        """Generate ComfyUI prompt using Claude (best for technical prompts)"""
        if not self.anthropic_client:
            logger.warning("Claude not available, using fallback prompt generation")
            return self._fallback_prompt(trend_analysis)

        try:
            prompt = f"""Based on this trend analysis:
{trend_analysis}

Create a detailed ComfyUI prompt for generating a streetwear t-shirt design.
Include: style, colors, composition, quality modifiers.
Format as a single optimized prompt (max 75 words)."""

            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            result = message.content[0].text
            logger.info(f"✅ Design prompt generated via Claude")
            return result

        except Exception as e:
            logger.error(f"Claude prompt generation failed: {e}")
            return self._fallback_prompt(trend_analysis)

    def generate_caption(self, design_concept: str) -> Dict[str, any]:
        """Generate social media caption using GPT-4"""
        if not self.openai_client:
            logger.warning("OpenAI not available, using fallback caption")
            return self._fallback_caption(design_concept)

        try:
            prompt = f"""Create an Instagram caption for this design:
{design_concept}

Format:
- Main caption (1-2 sentences, engaging)
- 10-15 relevant hashtags
- Call-to-action

Keep it authentic and trendy."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a social media expert for streetwear brands."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )

            caption_text = response.choices[0].message.content
            logger.info(f"✅ Caption generated via GPT-4")

            return {
                "caption": caption_text,
                "platform": "instagram",
                "hashtags": self._extract_hashtags(caption_text)
            }

        except Exception as e:
            logger.error(f"GPT-4 caption generation failed: {e}")
            return self._fallback_caption(design_concept)

    def _fallback_prompt(self, trend_analysis: str) -> str:
        """Fallback prompt generation"""
        return f"High quality streetwear t-shirt design, {trend_analysis[:100]}, professional digital art, trending on artstation"

    def _fallback_caption(self, design_concept: str) -> Dict[str, any]:
        """Fallback caption generation"""
        return {
            "caption": f"New drop alert! 🔥\n\n{design_concept[:80]}...\n\nLink in bio 👆",
            "platform": "instagram",
            "hashtags": ["#streetwear", "#fashion", "#newdrop", "#clothing", "#style"]
        }

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags[:15] if hashtags else ["#streetwear", "#fashion"]

class PODWorkflow:
    """Complete POD automation workflow"""

    def __init__(self, config: Config):
        self.config = config
        self.llm_gen = MultiLLMGenerator(config)

    def run_complete_workflow(self, theme: str = "cyberpunk") -> Dict[str, any]:
        """Execute complete design workflow"""
        logger.info(f"🚀 Starting workflow for theme: {theme}")

        # Step 1: Trend Analysis
        logger.info("📊 Step 1: Analyzing trends...")
        trend_analysis = self.llm_gen.generate_trend_analysis(theme)

        # Step 2: Design Prompt
        logger.info("🎨 Step 2: Generating design prompt...")
        design_prompt = self.llm_gen.generate_design_prompt(trend_analysis)

        # Step 3: Social Caption
        logger.info("📱 Step 3: Creating social media caption...")
        caption_data = self.llm_gen.generate_caption(design_prompt)

        result = {
            "theme": theme,
            "timestamp": datetime.now().isoformat(),
            "trend_analysis": trend_analysis,
            "design_prompt": design_prompt,
            "caption": caption_data["caption"],
            "hashtags": caption_data["hashtags"],
            "status": "success"
        }

        logger.info("✅ Workflow completed successfully")
        return result

# Flask Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    config = Config.load_from_env()

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "openai": bool(config.openai_api_key),
            "anthropic": bool(config.anthropic_api_key),
            "groq": bool(config.groq_api_key),
            "comfyui": bool(config.comfyui_url),
            "printify": bool(config.printify_api_key)
        }
    })

@app.route('/test/workflow', methods=['POST'])
def test_workflow():
    """Test complete workflow"""
    try:
        data = request.get_json() or {}
        theme = data.get('theme', 'cyberpunk')

        config = Config.load_from_env()
        workflow = PODWorkflow(config)

        result = workflow.run_complete_workflow(theme)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/webhook/printify', methods=['POST'])
def printify_webhook():
    """Handle Printify webhooks"""
    try:
        event_type = request.headers.get('X-Printify-Event')
        payload = request.get_json()

        logger.info(f"📥 Received Printify webhook: {event_type}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_design():
    """Generate design concept"""
    try:
        data = request.get_json() or {}
        theme = data.get('theme', 'streetwear')

        config = Config.load_from_env()
        llm_gen = MultiLLMGenerator(config)

        trend_analysis = llm_gen.generate_trend_analysis(theme)
        design_prompt = llm_gen.generate_design_prompt(trend_analysis)

        return jsonify({
            "theme": theme,
            "trend_analysis": trend_analysis,
            "design_prompt": design_prompt,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Design generation failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting POD Studio Backend (Simplified)")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")

    # Load config and check services
    config = Config.load_from_env()

    if not any([config.openai_api_key, config.anthropic_api_key, config.groq_api_key]):
        logger.warning("⚠️  No LLM API keys configured! Add at least one to .env.pod")

    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(os.getenv('FLASK_ENV') == 'development')
    )
