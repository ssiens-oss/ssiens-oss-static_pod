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
        # Build RunPod serverless payload
        payload = {
            "input": {
                "workflow": {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "cfg_scale": cfg_scale,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras"
                }
            }
        }

        if seed is not None:
            payload["input"]["workflow"]["seed"] = seed

        if negative_prompt:
            payload["input"]["workflow"]["negative_prompt"] = negative_prompt
        else:
            # Default negative prompt for quality
            payload["input"]["workflow"]["negative_prompt"] = (
                "blurry, blur, blurred, out of focus, unfocused, low quality, "
                "worst quality, low resolution, lowres, pixelated, jpeg artifacts, "
                "compression artifacts, watermark, text, signature"
            )

        logger.info(f"Calling RunPod serverless: {self.endpoint_url}")
        logger.debug(f"Payload: {payload}")

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
            # RunPod serverless returns output in result.output
            output = result.get("output", {})

            # Check for different possible output formats
            if isinstance(output, dict):
                # Format 1: direct image URL
                if "image_url" in output:
                    return output["image_url"]

                # Format 2: images array
                if "images" in output and output["images"]:
                    return output["images"][0]

                # Format 3: message with URL
                if "message" in output:
                    return output["message"]

            # Format 4: output is the URL directly
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
