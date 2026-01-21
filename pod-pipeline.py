#!/usr/bin/env python3
"""
POD Pipeline - Automated Proof of Life Publisher
Generates, processes, and publishes POD designs with automated metadata
"""
import os
import sys
import logging
import argparse
import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PODPipeline:
    """Main POD automation pipeline with proof-of-life publishing"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gateway_url = config.get('gateway_url', 'http://localhost:5000')
        self.comfyui_url = config.get('comfyui_url', os.getenv('COMFYUI_API_URL', 'http://localhost:8188'))
        self.claude_api_key = config.get('claude_api_key', os.getenv('ANTHROPIC_API_KEY'))
        self.auto_publish = config.get('auto_publish', True)
        self.proof_of_life_mode = config.get('proof_of_life', True)

        logger.info("🚀 POD Pipeline initialized")
        logger.info(f"   Gateway: {self.gateway_url}")
        logger.info(f"   ComfyUI: {self.comfyui_url}")
        logger.info(f"   Auto-publish: {self.auto_publish}")
        logger.info(f"   Proof of Life: {self.proof_of_life_mode}")

    def generate_automated_metadata(self, theme: str = "abstract art") -> Dict[str, str]:
        """
        Generate automated title and description using Claude API

        Args:
            theme: Design theme for metadata generation

        Returns:
            Dict with title, description, tags
        """
        logger.info(f"📝 Generating automated metadata for theme: {theme}")

        if not self.claude_api_key or self.claude_api_key == "sk-ant-your-api-key-here":
            logger.warning("⚠️ Claude API key not configured, using fallback metadata")
            return {
                "title": f"POD Design - {datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "description": f"Unique AI-generated {theme} design for print-on-demand",
                "tags": ["ai-art", "pod", theme.replace(" ", "-")]
            }

        try:
            headers = {
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            prompt = f"""Generate a catchy product title and engaging description for a print-on-demand design with the theme: {theme}.

Return ONLY a JSON object with this exact structure:
{{
  "title": "A catchy, SEO-friendly title (3-10 words, under 200 characters)",
  "description": "An engaging product description (2-3 sentences, highlighting appeal and uniqueness)",
  "tags": ["tag1", "tag2", "tag3"]
}}

Make the title and description appealing for customers browsing t-shirts and hoodies."""

            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content_text = result['content'][0]['text']

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content_text)
            if json_match:
                metadata = json.loads(json_match.group(0))
                logger.info(f"✅ Generated metadata: {metadata['title']}")
                return metadata
            else:
                raise ValueError("No JSON found in Claude response")

        except Exception as e:
            logger.error(f"❌ Claude API error: {e}, using fallback")
            return {
                "title": f"POD Design - {datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "description": f"Unique AI-generated {theme} design for print-on-demand",
                "tags": ["ai-art", "pod", theme.replace(" ", "-")]
            }

    def build_pod_workflow(self, prompt: str, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Build optimized ComfyUI workflow for POD generation

        Args:
            prompt: Text prompt for image generation
            seed: Random seed (optional, auto-generated if not provided)

        Returns:
            ComfyUI workflow dict
        """
        if seed is None:
            seed = uuid.uuid4().int % (2**31)

        logger.info(f"🎨 Building POD workflow with seed: {seed}")

        # Optimized workflow for POD (1024x1024, high quality)
        workflow = {
            "1": {
                "inputs": {
                    "text": prompt,
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "8": {
                "inputs": {
                    "samples": ["13", 0],
                    "vae": ["10", 0]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"pod_design_{seed}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            },
            "10": {
                "inputs": {
                    "vae_name": "ae.sft"
                },
                "class_type": "VAELoader",
                "_meta": {"title": "Load VAE"}
            },
            "11": {
                "inputs": {
                    "clip_name": "t5xxl_fp8_e4m3fn.safetensors",
                    "type": "sd3"
                },
                "class_type": "CLIPLoader",
                "_meta": {"title": "Load CLIP"}
            },
            "12": {
                "inputs": {
                    "unet_name": "flux1-dev-fp8.safetensors",
                    "weight_dtype": "fp8_e4m3fn"
                },
                "class_type": "UNETLoader",
                "_meta": {"title": "Load Diffusion Model"}
            },
            "13": {
                "inputs": {
                    "seed": seed,
                    "steps": 25,  # Increased for POD quality
                    "cfg": 3.5,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["12", 0],
                    "positive": ["1", 0],
                    "negative": ["1", 0],  # Using same encoding for negative
                    "latent_image": ["25", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"}
            },
            "25": {
                "inputs": {
                    "width": 1024,  # POD standard size
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            }
        }

        return workflow

    def generate_design(self, theme: str = "vibrant abstract art") -> Optional[Dict[str, Any]]:
        """
        Generate a POD design using ComfyUI/RunPod

        Args:
            theme: Design theme/prompt

        Returns:
            Dict with generation results or None if failed
        """
        logger.info(f"🎨 Generating POD design: {theme}")

        try:
            # Generate metadata first
            metadata = self.generate_automated_metadata(theme)

            # Build enhanced prompt for POD
            enhanced_prompt = f"{theme}, high quality, vibrant colors, print-ready, professional design, centered composition"

            # Build workflow
            workflow = self.build_pod_workflow(enhanced_prompt)

            # Submit to gateway's generation endpoint
            # Gateway expects: prompt, style, genre, width, height, steps, cfg_scale
            response = requests.post(
                f"{self.gateway_url}/api/generate",
                json={
                    "prompt": enhanced_prompt,
                    "style": "professional, print-ready",
                    "genre": "abstract art",
                    "width": 1024,
                    "height": 1024,
                    "steps": 25,  # Higher quality for POD
                    "cfg_scale": 3.5
                },
                timeout=300  # 5 minutes for POD generation
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Design generated successfully: {result.get('prompt_id')}")

            # Extract image IDs if available (for RunPod serverless)
            images = result.get("images", [])
            image_id = images[0]["id"] if images else None

            return {
                "prompt_id": result.get("prompt_id"),
                "image_id": image_id,  # May be None if async
                "metadata": metadata,
                "theme": theme,
                "status": result.get("status", "pending")
            }

        except Exception as e:
            logger.error(f"❌ Design generation failed: {e}")
            return None

    def wait_for_generation(self, prompt_id: str, timeout: int = 300) -> Optional[str]:
        """
        Wait for generation to complete and return image ID

        Args:
            prompt_id: Generation job ID
            timeout: Maximum wait time in seconds

        Returns:
            Image ID if successful, None otherwise
        """
        logger.info(f"⏳ Waiting for generation {prompt_id} to complete...")

        import time
        start_time = time.time()
        poll_interval = 3

        while time.time() - start_time < timeout:
            try:
                # Check generation status
                response = requests.get(
                    f"{self.gateway_url}/api/generation_status",
                    params={"prompt_id": prompt_id},
                    timeout=10
                )

                if response.status_code == 200:
                    status = response.json()

                    if status.get("status") == "completed":
                        image_id = status.get("image_id")
                        logger.info(f"✅ Generation completed: {image_id}")
                        return image_id
                    elif status.get("status") == "failed":
                        logger.error(f"❌ Generation failed: {status.get('error')}")
                        return None

                time.sleep(poll_interval)

            except Exception as e:
                logger.warning(f"⚠️ Status check error: {e}")
                time.sleep(poll_interval)

        logger.error(f"⏱️ Generation timeout after {timeout}s")
        return None

    def publish_design(self, image_id: str, metadata: Dict[str, str]) -> Optional[str]:
        """
        Publish design to Printify with automated metadata

        Args:
            image_id: Image identifier from gateway
            metadata: Title, description, tags

        Returns:
            Product ID if successful, None otherwise
        """
        logger.info(f"📦 Publishing design {image_id}: {metadata['title']}")

        try:
            response = requests.post(
                f"{self.gateway_url}/api/publish/{image_id}",
                json={
                    "title": metadata["title"],
                    "description": metadata.get("description", ""),
                    "auto_approve": True  # Skip manual approval for proof of life
                },
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            product_id = result.get("product_id")

            logger.info(f"✅ Design published successfully: {product_id}")
            return product_id

        except Exception as e:
            logger.error(f"❌ Publishing failed: {e}")
            return None

    def run_proof_of_life(self, theme: str = "vibrant abstract art") -> Dict[str, Any]:
        """
        Run complete proof-of-life pipeline: generate, wait, publish

        Args:
            theme: Design theme

        Returns:
            Results dict with success status and details
        """
        logger.info("🚀 Starting POD Proof of Life pipeline...")
        logger.info("=" * 60)

        start_time = datetime.now()
        result = {
            "success": False,
            "theme": theme,
            "started_at": start_time.isoformat(),
            "metadata": None,
            "prompt_id": None,
            "image_id": None,
            "product_id": None,
            "errors": []
        }

        try:
            # Step 1: Generate design
            logger.info("Step 1/3: Generating design with automated metadata...")
            gen_result = self.generate_design(theme)

            if not gen_result:
                result["errors"].append("Design generation failed")
                return result

            result["metadata"] = gen_result["metadata"]
            result["prompt_id"] = gen_result["prompt_id"]

            # Step 2: Wait for completion (or use already-available image)
            if gen_result.get("image_id"):
                # Image already available (synchronous RunPod)
                logger.info("Step 2/3: Image ready immediately (sync mode)")
                image_id = gen_result["image_id"]
            else:
                # Wait for async generation
                logger.info("Step 2/3: Waiting for generation to complete...")
                image_id = self.wait_for_generation(gen_result["prompt_id"])

            if not image_id:
                result["errors"].append("Generation did not complete")
                return result

            result["image_id"] = image_id

            # Step 3: Auto-publish
            if self.auto_publish:
                logger.info("Step 3/3: Auto-publishing design...")
                product_id = self.publish_design(image_id, gen_result["metadata"])

                if product_id:
                    result["product_id"] = product_id
                    result["success"] = True
                else:
                    result["errors"].append("Publishing failed")
            else:
                logger.info("Step 3/3: Skipped (auto-publish disabled)")
                result["success"] = True

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            result["errors"].append(str(e))

        # Calculate duration
        end_time = datetime.now()
        result["completed_at"] = end_time.isoformat()
        result["duration_seconds"] = (end_time - start_time).total_seconds()

        # Summary
        logger.info("=" * 60)
        if result["success"]:
            logger.info("✅ POD Proof of Life SUCCESSFUL!")
            logger.info(f"   Title: {result['metadata']['title']}")
            logger.info(f"   Image ID: {result['image_id']}")
            if result.get("product_id"):
                logger.info(f"   Product ID: {result['product_id']}")
            logger.info(f"   Duration: {result['duration_seconds']:.1f}s")
        else:
            logger.error("❌ POD Proof of Life FAILED")
            logger.error(f"   Errors: {', '.join(result['errors'])}")

        return result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="POD Pipeline - Automated Proof of Life Publisher")
    parser.add_argument("--theme", default="vibrant abstract art", help="Design theme/prompt")
    parser.add_argument("--gateway-url", default="http://localhost:5000", help="Gateway URL")
    parser.add_argument("--no-publish", action="store_true", help="Skip auto-publishing")
    parser.add_argument("--output", help="Output results to JSON file")

    args = parser.parse_args()

    # Configuration
    config = {
        "gateway_url": args.gateway_url,
        "auto_publish": not args.no_publish,
        "proof_of_life": True
    }

    # Run pipeline
    pipeline = PODPipeline(config)
    result = pipeline.run_proof_of_life(args.theme)

    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(result, indent=2))
        logger.info(f"📄 Results saved to: {output_path}")

    # Exit code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
