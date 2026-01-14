"""
RunPod Serverless ComfyUI Client
Generates images using RunPod serverless endpoints
"""
import requests
import time
import os
import json
import copy
from pathlib import Path
from typing import Optional, Dict, Any


class ServerlessComfyUI:
    """Client for RunPod Serverless ComfyUI"""

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY")
        self.endpoint_id = endpoint_id or os.environ.get("RUNPOD_ENDPOINT_ID")

        if not self.api_key or not self.endpoint_id:
            raise ValueError(
                "Missing RunPod credentials. Set RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID in .env"
            )

        self.base_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"

        # Load default workflow (Flux Dev)
        workflow_path = Path(__file__).parent / "workflows" / "flux_dev.json"
        with open(workflow_path) as f:
            self.default_workflow = json.load(f)

    def _headers(self) -> Dict[str, str]:
        """Get request headers with auth"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 30,
        cfg_scale: float = 7.0,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate an image using serverless ComfyUI

        Args:
            prompt: Text description of image
            negative_prompt: What to avoid in image
            steps: Number of sampling steps
            cfg_scale: Classifier-free guidance scale
            width: Image width
            height: Image height
            seed: Random seed (-1 for random)
            output_path: Where to save image (auto-generated if None)

        Returns:
            Path to saved image
        """
        print(f"🎨 Generating image: {prompt[:50]}...")
        print(f"   Steps: {steps}, Size: {width}x{height}")

        # Prepare workflow with parameters
        workflow = copy.deepcopy(self.default_workflow)

        # Update workflow parameters for Flux
        workflow["17"]["inputs"]["steps"] = steps  # Scheduler steps
        workflow["25"]["inputs"]["noise_seed"] = seed if seed > 0 else int(time.time())  # Random seed
        workflow["5"]["inputs"]["width"] = width  # Latent width
        workflow["5"]["inputs"]["height"] = height  # Latent height
        workflow["6"]["inputs"]["text"] = prompt  # Positive prompt

        # Submit job with full workflow
        payload = {
            "input": {
                "workflow": workflow
            }
        }

        response = requests.post(
            f"{self.base_url}/run",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        job_id = response.json()["id"]
        print(f"   Job ID: {job_id}")
        print(f"   ⏳ Waiting for generation...")

        # Poll for completion
        image_url = self._wait_for_completion(job_id)

        # Download image
        if not output_path:
            output_path = f"./images/{job_id}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"   📥 Downloading image...")
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(img_response.content)

        print(f"   ✅ Saved to: {output_path}")
        return output_path

    def _wait_for_completion(self, job_id: str, timeout: int = 300) -> str:
        """
        Poll job status until completion

        Args:
            job_id: RunPod job ID
            timeout: Max wait time in seconds

        Returns:
            URL of generated image
        """
        start_time = time.time()
        status_url = f"{self.base_url}/status/{job_id}"

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} timed out after {timeout}s")

            response = requests.get(status_url, headers=self._headers(), timeout=30)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")

            if status == "COMPLETED":
                output = data.get("output", {})

                # Handle different output formats
                if isinstance(output, dict):
                    images = output.get("images", output.get("image", []))
                elif isinstance(output, list):
                    images = output
                else:
                    images = []

                if images:
                    # Return first image URL
                    image = images[0] if isinstance(images, list) else images
                    return image if isinstance(image, str) else image.get("url", image.get("image"))

                raise ValueError(f"No images in completed job output. Output: {output}")

            elif status == "FAILED":
                error = data.get("error", "Unknown error")
                raise Exception(f"Job failed: {error}")

            elif status == "IN_QUEUE":
                print(f"   ⏸️  In queue...")

            elif status == "IN_PROGRESS":
                print(f"   🔄 Generating...")

            time.sleep(3)

    def health_check(self) -> Dict[str, Any]:
        """Check if endpoint is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=self._headers(),
                timeout=10
            )
            return {
                "status": "healthy" if response.ok else "unhealthy",
                "endpoint_id": self.endpoint_id,
                "response": response.json() if response.ok else None
            }
        except Exception as e:
            return {
                "status": "error",
                "endpoint_id": self.endpoint_id,
                "error": str(e)
            }


def main():
    """Test the serverless client"""
    import sys

    # Load .env
    from dotenv import load_dotenv
    load_dotenv("../.env")

    client = ServerlessComfyUI()

    # Health check
    print("🔍 Checking endpoint health...")
    health = client.health_check()
    print(f"   Status: {health['status']}")

    if health['status'] != 'healthy':
        print("   ❌ Endpoint not healthy. Check your credentials.")
        sys.exit(1)

    # Generate test image
    print("\n🎨 Generating test image...")
    image_path = client.generate_image(
        prompt="minimalist mountain landscape at sunset, flat colors, vector art",
        negative_prompt="realistic, photo, detailed",
        steps=25,
        width=1024,
        height=1024
    )

    print(f"\n✅ Success! Image saved to: {image_path}")
    print(f"   View it in your gateway at: http://localhost:8099")


if __name__ == "__main__":
    main()
