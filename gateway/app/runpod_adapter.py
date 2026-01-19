"""
RunPod Serverless Adapter
Adapts gateway requests to RunPod Serverless ComfyUI format
"""
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class RunPodServerlessAdapter:
    """Adapter for RunPod Serverless ComfyUI endpoints"""

    def __init__(self, endpoint_url: str, api_key: Optional[str] = None):
        """
        Initialize adapter

        Args:
            endpoint_url: RunPod serverless endpoint URL (e.g., https://api.runpod.ai/v2/xxx/runsync)
            api_key: RunPod API key (optional, for authentication)
        """
        self.endpoint_url = endpoint_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def is_serverless_endpoint(self) -> bool:
        """Check if this is a RunPod serverless endpoint"""
        return "api.runpod.ai/v2/" in self.endpoint_url or "api.runpod.io/v2/" in self.endpoint_url

    def _build_comfyui_workflow(
        self,
        prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: int,
        negative_prompt: str
    ) -> Dict[str, Any]:
        """
        Build a proper ComfyUI SDXL workflow

        Args:
            prompt: Positive prompt
            width: Image width
            height: Image height
            steps: Sampling steps
            cfg_scale: CFG scale
            seed: Random seed
            negative_prompt: Negative prompt

        Returns:
            ComfyUI workflow dictionary
        """
        return {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg_scale,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

    def generate_image(
        self,
        prompt: str,
        width: int = 1536,
        height: int = 1536,
        steps: int = 35,
        cfg_scale: float = 7.5,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image using RunPod Serverless

        Args:
            prompt: Text prompt for image generation
            width: Image width
            height: Image height
            steps: Number of diffusion steps
            cfg_scale: CFG scale
            seed: Random seed (optional)
            negative_prompt: Negative prompt (optional)

        Returns:
            Response from RunPod with image data
        """
        import os

        # Generate random seed if not provided
        if seed is None:
            seed = int.from_bytes(os.urandom(4), byteorder="little")

        # Use default negative prompt if not provided
        if not negative_prompt:
            negative_prompt = (
                "blurry, blur, blurred, out of focus, unfocused, low quality, "
                "worst quality, low resolution, lowres, pixelated, jpeg artifacts, "
                "compression artifacts, watermark, text, signature, username, "
                "low detail, unclear, soft, hazy, fuzzy, distorted, deformed, ugly, "
                "bad anatomy, disfigured, poorly drawn, bad proportions"
            )

        # Build proper ComfyUI workflow
        workflow = self._build_comfyui_workflow(
            prompt=prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            negative_prompt=negative_prompt
        )

        # RunPod serverless payload format
        # Based on the error logs, the handler expects nodes directly under input
        # without the "prompt" wrapper
        payload = {
            "input": workflow
        }

        logger.info(f"Calling RunPod serverless: {self.endpoint_url}")
        logger.debug(f"Payload structure: input with {len(workflow)} nodes directly")
        logger.debug(f"Node IDs: {list(workflow.keys())}")

        try:
            # Call RunPod serverless endpoint (runsync waits for completion)
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers,
                timeout=120  # Serverless can take longer on cold start
            )
            response.raise_for_status()
            result = response.json()

            logger.info("RunPod serverless generation completed")
            return result

        except requests.RequestException as e:
            logger.error(f"RunPod serverless request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    def get_output_url(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract output image URL from RunPod result

        Args:
            result: Response from RunPod

        Returns:
            URL to generated image, or None if not found
        """
        try:
            # Check if the request failed
            status = result.get("status")
            if status == "FAILED":
                error = result.get("error", "Unknown error")
                logger.error(f"RunPod job failed: {error}")
                return None

            # RunPod serverless returns output in result.output
            output = result.get("output", {})

            # Check for different possible output formats
            if isinstance(output, dict):
                # Format 1: direct image URL
                if "image_url" in output:
                    return output["image_url"]

                # Format 2: images array (URLs)
                if "images" in output and output["images"]:
                    img = output["images"][0]
                    if isinstance(img, str):
                        return img
                    elif isinstance(img, dict) and "url" in img:
                        return img["url"]

                # Format 3: message with URL
                if "message" in output:
                    msg = output["message"]
                    if isinstance(msg, str) and msg.startswith("http"):
                        return msg

                # Format 4: ComfyUI style output (from SaveImage node)
                # Structure: {"9": {"images": [{"filename": "...", "subfolder": "...", "type": "output"}]}}
                for node_id, node_output in output.items():
                    if isinstance(node_output, dict) and "images" in node_output:
                        images = node_output["images"]
                        if images and isinstance(images, list):
                            first_img = images[0]
                            if isinstance(first_img, dict):
                                # This is ComfyUI metadata format - need image URL
                                if "url" in first_img:
                                    return first_img["url"]
                                elif "filename" in first_img:
                                    # Some handlers return filename, need base URL
                                    logger.warning(f"Got filename without URL: {first_img}")

            # Format 5: output is the URL directly
            if isinstance(output, str) and output.startswith("http"):
                return output

            logger.warning(f"Could not extract image URL from result: {result}")
            return None

        except Exception as e:
            logger.error(f"Error extracting output URL: {e}")
            return None

    def download_image(self, url: str, output_path: str) -> bool:
        """
        Download generated image from URL

        Args:
            url: Image URL
            output_path: Local path to save image

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded image to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return False


def is_runpod_serverless_url(url: str) -> bool:
    """
    Check if URL is a RunPod serverless endpoint

    Args:
        url: URL to check

    Returns:
        True if RunPod serverless URL
    """
    return "api.runpod.ai/v2/" in url or "api.runpod.io/v2/" in url
