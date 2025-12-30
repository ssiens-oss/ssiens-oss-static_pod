"""
Autonomous POD Studio - Complete Multi-LLM Integration
Combines ComfyUI, Printify, Social Media Automation with AI Agents
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import hmac
import hashlib

# Multi-LLM Integration
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_xai import ChatXAI
from langchain_groq import ChatGroq
from langchain.chains import SequentialChain, LLMChain
from langchain.prompts import PromptTemplate

# Agent System
from crewai import Agent, Task, Crew, Process

# HTTP & APIs
import requests
from flask import Flask, request, jsonify

# Retry Logic
from tenacity import retry, stop_after_attempt, wait_exponential

# Social Media
try:
    from instagrapi import Client as InstaClient
except ImportError:
    InstaClient = None

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pod_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for all API keys and settings"""
    # LLM API Keys
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    xai_api_key: str = os.getenv('XAI_API_KEY', '')
    groq_api_key: str = os.getenv('GROQ_API_KEY', '')

    # Service APIs
    comfyui_url: str = os.getenv('COMFYUI_URL', 'http://localhost:8188')
    runpod_api_key: str = os.getenv('RUNPOD_API_KEY', '')
    printify_api_key: str = os.getenv('PRINTIFY_API_KEY', '')
    printify_shop_id: str = os.getenv('PRINTIFY_SHOP_ID', '')
    printify_webhook_secret: str = os.getenv('PRINTIFY_WEBHOOK_SECRET', '')

    # Social Media
    instagram_username: str = os.getenv('INSTAGRAM_USERNAME', '')
    instagram_password: str = os.getenv('INSTAGRAM_PASSWORD', '')
    tiktok_session_id: str = os.getenv('TIKTOK_SESSION_ID', '')

    # Processing Settings
    batch_size: int = 10
    max_retries: int = 3

    @classmethod
    def load_from_file(cls, path: str = '.env.pod'):
        """Load configuration from file"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = {}
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        data[key] = val.strip('"').strip("'")
                        os.environ[key] = data[key]
        return cls()


class MultiLLMPromptGenerator:
    """Generate design prompts using multiple LLMs in sequence"""

    def __init__(self, config: Config):
        self.config = config
        self._init_llms()
        self._init_chains()

    def _init_llms(self):
        """Initialize all LLM clients"""
        self.grok = ChatXAI(
            model="grok-4-0709",
            xai_api_key=self.config.xai_api_key,
            temperature=0.8
        ) if self.config.xai_api_key else None

        self.claude = ChatAnthropic(
            model="claude-3.5-sonnet-20241022",
            anthropic_api_key=self.config.anthropic_api_key,
            temperature=0.7
        ) if self.config.anthropic_api_key else None

        self.gpt = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=self.config.openai_api_key,
            temperature=0.6
        ) if self.config.openai_api_key else None

        self.llama = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=self.config.groq_api_key,
            temperature=0.9
        ) if self.config.groq_api_key else None

        logger.info(f"Initialized LLMs: Grok={bool(self.grok)}, Claude={bool(self.claude)}, GPT={bool(self.gpt)}, Llama={bool(self.llama)}")

    def _init_chains(self):
        """Create LangChain sequential chains"""

        # Step 1: Trend Analysis (Grok with DeepSearch)
        trend_prompt = PromptTemplate(
            input_variables=["theme"],
            template="""You are a 2025 streetwear trend analyst with access to real-time data.

Theme: {theme}

Analyze current streetwear trends, popular aesthetics, and viral design elements.
Focus on: Colors, Typography, Graphics, Cultural References, Platform virality (TikTok/IG).

Output: JSON with trend insights and 3 specific design directions.
"""
        )

        # Step 2: Prompt Refinement (Claude for precision)
        refine_prompt = PromptTemplate(
            input_variables=["trend_data"],
            template="""You are a ComfyUI prompt engineer. Refine this trend data into a technical prompt.

Trend Data: {trend_data}

Create a detailed ComfyUI/SDXL prompt with:
- Main subject and composition
- Art style and technique
- Color palette (specific hex codes)
- Mood and atmosphere
- Technical parameters (aspect ratio, quality tags)

Output: Optimized prompt for SDXL generation.
"""
        )

        # Step 3: Creative Variation (Llama for diversity)
        creative_prompt = PromptTemplate(
            input_variables=["base_prompt"],
            template="""Generate 3 creative variations of this design prompt.

Base Prompt: {base_prompt}

For each variation, maintain core concept but explore:
- Different artistic styles (minimalist, maximalist, neo-brutalist)
- Alternative color schemes
- Unique composition angles

Output: JSON array with 3 variations.
"""
        )

        # Step 4: Final Polish (GPT for marketing)
        final_prompt = PromptTemplate(
            input_variables=["variations"],
            template="""Select the best variation and add marketing metadata.

Variations: {variations}

Choose the most commercially viable design and add:
- Product title (catchy, SEO-friendly)
- Product description (2-3 sentences)
- Hashtags (10 trending tags)
- Price recommendation
- Target demographic

Output: Complete product package ready for Printify.
"""
        )

        # Build Sequential Chain
        self.chains = {}
        if self.grok:
            self.chains['trend'] = LLMChain(llm=self.grok, prompt=trend_prompt, output_key="trend_data")
        if self.claude:
            self.chains['refine'] = LLMChain(llm=self.claude, prompt=refine_prompt, output_key="base_prompt")
        if self.llama:
            self.chains['creative'] = LLMChain(llm=self.llama, prompt=creative_prompt, output_key="variations")
        if self.gpt:
            self.chains['final'] = LLMChain(llm=self.gpt, prompt=final_prompt, output_key="product_package")

        if len(self.chains) >= 2:
            chain_list = list(self.chains.values())
            input_vars = ["theme"]
            self.overall_chain = SequentialChain(
                chains=chain_list,
                input_variables=input_vars,
                output_variables=[chain_list[-1].output_key],
                verbose=True
            )
            logger.info(f"Created sequential chain with {len(self.chains)} LLMs")
        else:
            self.overall_chain = None
            logger.warning("Not enough LLMs configured for chain. Need at least 2.")

    def generate_design_concept(self, theme: str) -> Dict:
        """Generate complete design concept using LLM chain"""
        if not self.overall_chain:
            logger.error("LLM chain not initialized")
            return self._fallback_concept(theme)

        try:
            logger.info(f"Generating design concept for theme: {theme}")
            result = self.overall_chain.invoke({"theme": theme})

            # Parse the final output
            final_output = result.get(list(self.chains.values())[-1].output_key, "{}")
            try:
                concept = json.loads(final_output)
            except json.JSONDecodeError:
                concept = {"raw_output": final_output, "theme": theme}

            logger.info(f"Generated concept: {concept.get('title', 'Untitled')}")
            return concept

        except Exception as e:
            logger.error(f"LLM chain error: {e}")
            return self._fallback_concept(theme)

    def _fallback_concept(self, theme: str) -> Dict:
        """Fallback concept generation without LLMs"""
        return {
            "title": f"{theme.title()} Street Design",
            "prompt": f"urban streetwear design, {theme}, bold graphics, modern typography, trending 2025",
            "description": f"Bold {theme}-inspired streetwear design perfect for the modern fashion-forward audience.",
            "hashtags": ["#streetwear", "#fashion", "#design", f"#{theme}", "#trendy"],
            "price": 2999
        }


class CrewAIOrchestrator:
    """CrewAI agent system for autonomous workflow"""

    def __init__(self, config: Config, prompt_gen: MultiLLMPromptGenerator):
        self.config = config
        self.prompt_gen = prompt_gen
        self._init_agents()

    def _init_agents(self):
        """Initialize CrewAI agents"""

        # Agent 1: Trend Analyst
        self.trend_agent = Agent(
            role="Streetwear Trend Analyst",
            goal="Identify viral streetwear trends and aesthetics for 2025",
            backstory="""You monitor TikTok, Instagram, and fashion forums daily.
            You understand Gen-Z aesthetics, cultural movements, and viral design patterns.
            Your insights drive successful product launches.""",
            llm=self.prompt_gen.grok if self.prompt_gen.grok else self.prompt_gen.gpt,
            verbose=True,
            allow_delegation=False
        )

        # Agent 2: Prompt Engineer
        self.prompt_agent = Agent(
            role="ComfyUI Prompt Engineer",
            goal="Create technical prompts that generate commercially viable designs",
            backstory="""You are an expert in SDXL, ControlNet, and ComfyUI workflows.
            You understand negative prompts, quality tags, and artistic styles.
            Your prompts consistently produce sellable designs.""",
            llm=self.prompt_gen.claude if self.prompt_gen.claude else self.prompt_gen.gpt,
            verbose=True,
            allow_delegation=False
        )

        # Agent 3: Social Media Strategist
        self.caption_agent = Agent(
            role="Social Media Caption Writer",
            goal="Write viral captions and hashtags for product launches",
            backstory="""You understand TikTok and Instagram algorithms.
            You write hooks that stop scrolling and drive engagement.
            Your captions consistently generate sales.""",
            llm=self.prompt_gen.gpt if self.prompt_gen.gpt else self.prompt_gen.llama,
            verbose=True,
            allow_delegation=False
        )

        logger.info("Initialized 3 CrewAI agents")

    def run_autonomous_workflow(self, theme: str) -> Dict:
        """Run complete autonomous workflow with agents"""

        # Task 1: Analyze trends
        trend_task = Task(
            description=f"""Analyze current streetwear trends related to: {theme}

Provide:
1. Top 3 trending design elements
2. Viral color palettes
3. Popular graphic styles
4. Target demographic insights

Output format: JSON""",
            agent=self.trend_agent,
            expected_output="JSON with trend analysis"
        )

        # Task 2: Generate prompts
        prompt_task = Task(
            description="""Using the trend analysis, create 3 ComfyUI prompts.

Each prompt should include:
- Main subject and composition
- Artistic style
- Color palette (hex codes)
- Quality tags for SDXL
- Negative prompts

Output format: JSON array of prompts""",
            agent=self.prompt_agent,
            expected_output="JSON array with 3 design prompts"
        )

        # Task 3: Create social content
        caption_task = Task(
            description="""Create social media content for the top design.

Include:
- Instagram caption (hook + value + CTA)
- TikTok caption (trending audio reference)
- 10 hashtags (mix of trending + niche)
- Best posting time recommendation

Output format: JSON""",
            agent=self.caption_agent,
            expected_output="JSON with social media content"
        )

        # Create Crew
        crew = Crew(
            agents=[self.trend_agent, self.prompt_agent, self.caption_agent],
            tasks=[trend_task, prompt_task, caption_task],
            process=Process.sequential,
            verbose=True
        )

        try:
            logger.info(f"Starting autonomous workflow for: {theme}")
            result = crew.kickoff()

            # Parse results
            workflow_output = {
                "theme": theme,
                "timestamp": datetime.now().isoformat(),
                "trends": result.tasks_output[0] if len(result.tasks_output) > 0 else {},
                "prompts": result.tasks_output[1] if len(result.tasks_output) > 1 else [],
                "social": result.tasks_output[2] if len(result.tasks_output) > 2 else {}
            }

            logger.info("Autonomous workflow completed successfully")
            return workflow_output

        except Exception as e:
            logger.error(f"CrewAI workflow error: {e}")
            return {"theme": theme, "error": str(e)}


class ComfyUIClient:
    """ComfyUI API client for image generation"""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.comfyui_url

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def generate_image(self, prompt: str, negative_prompt: str = "") -> Optional[str]:
        """Generate image using ComfyUI"""

        workflow = {
            "3": {  # KSampler
                "inputs": {
                    "seed": int(time.time()),
                    "steps": 30,
                    "cfg": 7.5,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {  # Load Checkpoint
                "inputs": {"ckpt_name": "sdxl_base_1.0.safetensors"},
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {  # Empty Latent
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
                "class_type": "EmptyLatentImage"
            },
            "6": {  # Positive Prompt
                "inputs": {"text": prompt, "clip": ["4", 1]},
                "class_type": "CLIPTextEncode"
            },
            "7": {  # Negative Prompt
                "inputs": {
                    "text": negative_prompt or "nsfw, low quality, blurry, watermark",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {  # VAE Decode
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                "class_type": "VAEDecode"
            },
            "9": {  # Save Image
                "inputs": {"filename_prefix": "pod_design", "images": ["8", 0]},
                "class_type": "SaveImage"
            }
        }

        try:
            logger.info(f"Submitting to ComfyUI: {prompt[:50]}...")

            response = requests.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow},
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            prompt_id = result.get('prompt_id')

            if not prompt_id:
                logger.error("No prompt_id returned from ComfyUI")
                return None

            # Wait for completion
            image_url = self._wait_for_completion(prompt_id)
            logger.info(f"Generated image: {image_url}")
            return image_url

        except Exception as e:
            logger.error(f"ComfyUI generation error: {e}")
            return None

    def _wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Optional[str]:
        """Wait for ComfyUI to complete generation"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check history
                response = requests.get(f"{self.base_url}/history/{prompt_id}")
                history = response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get('outputs', {})
                    for node_id, node_output in outputs.items():
                        if 'images' in node_output:
                            filename = node_output['images'][0]['filename']
                            return f"{self.base_url}/view?filename={filename}"

                time.sleep(2)

            except Exception as e:
                logger.error(f"Error checking completion: {e}")
                time.sleep(5)

        logger.error(f"Timeout waiting for prompt {prompt_id}")
        return None


class PrintifyClient:
    """Printify API client"""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://api.printify.com/v1"
        self.headers = {
            "Authorization": f"Bearer {config.printify_api_key}",
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def upload_image(self, image_url: str, filename: str) -> Optional[str]:
        """Upload image to Printify"""

        try:
            # Download image first
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()

            # Upload to Printify
            upload_url = f"{self.base_url}/uploads/images.json"
            files = {'file': (filename, img_response.content, 'image/png')}

            response = requests.post(
                upload_url,
                headers={"Authorization": self.headers["Authorization"]},
                files=files
            )
            response.raise_for_status()

            upload_id = response.json().get('id')
            logger.info(f"Uploaded image to Printify: {upload_id}")
            return upload_id

        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def create_product(self, title: str, description: str, image_id: str, price: int = 2999) -> Optional[str]:
        """Create product on Printify"""

        product_data = {
            "title": title,
            "description": description,
            "blueprint_id": 6,  # T-shirt
            "print_provider_id": 1,
            "variants": [
                {"id": 1, "price": price, "is_enabled": True}  # S
            ],
            "print_areas": [
                {
                    "variant_ids": [1],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {"id": image_id, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}
                            ]
                        }
                    ]
                }
            ]
        }

        try:
            url = f"{self.base_url}/shops/{self.config.printify_shop_id}/products.json"
            response = requests.post(url, headers=self.headers, json=product_data)
            response.raise_for_status()

            product_id = response.json().get('id')
            logger.info(f"Created Printify product: {product_id}")
            return product_id

        except Exception as e:
            logger.error(f"Product creation error: {e}")
            return None

    def publish_product(self, product_id: str) -> bool:
        """Publish product to connected stores"""

        try:
            url = f"{self.base_url}/shops/{self.config.printify_shop_id}/products/{product_id}/publish.json"
            response = requests.post(url, headers=self.headers, json={"title": True, "description": True, "images": True, "variants": True, "tags": True})
            response.raise_for_status()

            logger.info(f"Published product {product_id}")
            return True

        except Exception as e:
            logger.error(f"Product publish error: {e}")
            return False


class SocialMediaPoster:
    """Social media automation"""

    def __init__(self, config: Config):
        self.config = config
        self.instagram = self._init_instagram()

    def _init_instagram(self):
        """Initialize Instagram client"""
        if not InstaClient or not self.config.instagram_username:
            logger.warning("Instagram not configured")
            return None

        try:
            client = InstaClient()
            client.login(self.config.instagram_username, self.config.instagram_password)
            logger.info("Instagram client initialized")
            return client
        except Exception as e:
            logger.error(f"Instagram init error: {e}")
            return None

    def post_to_instagram(self, image_url: str, caption: str, hashtags: List[str]) -> bool:
        """Post to Instagram"""
        if not self.instagram:
            logger.warning("Instagram not available")
            return False

        try:
            # Download image
            img_response = requests.get(image_url)
            temp_path = f"/tmp/ig_post_{int(time.time())}.png"
            with open(temp_path, 'wb') as f:
                f.write(img_response.content)

            # Build caption
            full_caption = f"{caption}\n\n{' '.join(hashtags)}"

            # Upload
            self.instagram.photo_upload(temp_path, full_caption)
            os.remove(temp_path)

            logger.info("Posted to Instagram")
            return True

        except Exception as e:
            logger.error(f"Instagram post error: {e}")
            return False


# Flask Webhook Server
app = Flask(__name__)
webhook_config = None

@app.route('/webhook/printify', methods=['POST'])
def printify_webhook():
    """Handle Printify webhooks"""

    # Verify signature
    payload = request.data.decode('utf-8')
    signature = request.headers.get('X-Pfy-Signature', '')

    if webhook_config and webhook_config.printify_webhook_secret:
        expected = hmac.new(
            webhook_config.printify_webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            logger.warning("Invalid webhook signature")
            return jsonify({"error": "Invalid signature"}), 401

    # Process event
    data = json.loads(payload)
    event_type = data.get('type')

    logger.info(f"Received webhook: {event_type}")

    if event_type == 'order:created':
        logger.info(f"New order: {data.get('resource', {}).get('id')}")
        # TODO: Trigger social post or notification

    elif event_type == 'order:shipped':
        logger.info(f"Order shipped: {data.get('resource', {}).get('id')}")

    return jsonify({"status": "received"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


def main():
    """Main execution"""
    global webhook_config

    # Load config
    config = Config.load_from_file()
    webhook_config = config

    # Initialize components
    prompt_gen = MultiLLMPromptGenerator(config)
    crew = CrewAIOrchestrator(config, prompt_gen)
    comfyui = ComfyUIClient(config)
    printify = PrintifyClient(config)
    social = SocialMediaPoster(config)

    # Example workflow
    theme = "cyberpunk streetwear"

    logger.info("=" * 80)
    logger.info("AUTONOMOUS POD STUDIO - FULL WORKFLOW")
    logger.info("=" * 80)

    # Step 1: Generate concept with agents
    concept = crew.run_autonomous_workflow(theme)

    # Step 2: Generate image
    if concept.get('prompts'):
        prompt = concept['prompts'][0] if isinstance(concept['prompts'], list) else concept['prompts']
        image_url = comfyui.generate_image(str(prompt))

        if image_url:
            # Step 3: Upload to Printify
            upload_id = printify.upload_image(image_url, f"{theme}_design.png")

            if upload_id:
                # Step 4: Create product
                product_id = printify.create_product(
                    title=concept.get('title', f"{theme} Design"),
                    description=concept.get('description', ''),
                    image_id=upload_id,
                    price=concept.get('price', 2999)
                )

                if product_id:
                    # Step 5: Publish
                    printify.publish_product(product_id)

                    # Step 6: Post to social
                    if concept.get('social'):
                        social.post_to_instagram(
                            image_url,
                            concept['social'].get('caption', ''),
                            concept['social'].get('hashtags', [])
                        )

    logger.info("Workflow complete!")

    # Start webhook server
    logger.info("Starting webhook server on port 5000...")
    app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()
