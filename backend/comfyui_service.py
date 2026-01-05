"""
ComfyUI Service - Integration with ComfyUI for AI image generation
"""

import os
import json
import asyncio
import httpx
from typing import Dict, Any, Optional
from pathlib import Path


class ComfyUIService:
    """Service to interact with ComfyUI API"""

    def __init__(
        self,
        comfyui_url: str = "http://127.0.0.1:8188",
        output_dir: str = "/workspace/ComfyUI/output"
    ):
        self.comfyui_url = comfyui_url
        self.output_dir = Path(output_dir)
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 4500,
        height: int = 5400,
        steps: int = 30,
        cfg_scale: float = 7.5,
        seed: int = -1,
        style: str = "Photorealistic"
    ) -> Dict[str, Any]:
        """
        Generate an image using ComfyUI workflow

        Returns:
            dict: Job information including prompt_id for tracking
        """
        # Build the workflow based on style
        workflow = self._build_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            style=style
        )

        # Queue the prompt
        try:
            response = await self.client.post(
                f"{self.comfyui_url}/prompt",
                json={"prompt": workflow}
            )
            response.raise_for_status()
            result = response.json()

            return {
                "prompt_id": result.get("prompt_id"),
                "number": result.get("number"),
                "status": "queued"
            }
        except Exception as e:
            raise Exception(f"Failed to queue ComfyUI job: {str(e)}")

    async def get_job_status(self, prompt_id: str) -> Dict[str, Any]:
        """
        Check the status of a ComfyUI generation job

        Returns:
            dict: Status information including progress and completion
        """
        try:
            # Get history for this prompt
            response = await self.client.get(
                f"{self.comfyui_url}/history/{prompt_id}"
            )
            response.raise_for_status()
            history = response.json()

            if prompt_id not in history:
                return {"status": "queued", "progress": 0}

            job_data = history[prompt_id]

            # Check if completed
            if "outputs" in job_data:
                return {
                    "status": "completed",
                    "progress": 100,
                    "outputs": job_data["outputs"]
                }

            # Check for errors
            if job_data.get("status", {}).get("status_str") == "error":
                return {
                    "status": "failed",
                    "error": job_data.get("status", {}).get("messages", ["Unknown error"])
                }

            # Still processing
            return {
                "status": "processing",
                "progress": 50  # Could calculate from node execution progress
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def get_generated_image(self, prompt_id: str) -> Optional[str]:
        """
        Retrieve the generated image file path

        Returns:
            str: Path to generated image file
        """
        status = await self.get_job_status(prompt_id)

        if status.get("status") != "completed":
            return None

        outputs = status.get("outputs", {})

        # Find the image in outputs
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                images = node_output["images"]
                if images:
                    # Return the first image
                    filename = images[0].get("filename")
                    if filename:
                        return str(self.output_dir / filename)

        return None

    def _build_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: int,
        style: str
    ) -> Dict[str, Any]:
        """
        Build a ComfyUI workflow JSON based on parameters

        This is a simplified workflow. In production, you would load
        a template workflow and modify the parameters.
        """
        # Enhance prompt with style
        style_prompts = {
            "Photorealistic": "photorealistic, highly detailed, 8k uhd, professional photography",
            "Digital Art": "digital art, trending on artstation, highly detailed",
            "Oil Painting": "oil painting, classical art, brushstrokes, canvas texture",
            "Watercolor": "watercolor painting, soft colors, artistic",
            "Anime": "anime style, vibrant colors, manga art",
            "Cartoon": "cartoon style, colorful, illustrated",
            "Abstract": "abstract art, modern, artistic composition",
            "3D Render": "3d render, octane render, highly detailed, cgi",
            "Pixel Art": "pixel art, retro gaming style, 8-bit",
            "Sketch": "pencil sketch, hand drawn, artistic",
            "Pop Art": "pop art style, bold colors, andy warhol inspired",
            "Minimalist": "minimalist design, simple, clean",
            "Retro": "retro style, vintage, nostalgic",
            "Cyberpunk": "cyberpunk, neon lights, futuristic, sci-fi"
        }

        style_modifier = style_prompts.get(style, "")
        full_prompt = f"{prompt}, {style_modifier}" if style_modifier else prompt

        # Basic workflow structure
        # This is a simplified example - you would typically load from a template
        workflow = {
            "3": {
                "inputs": {
                    "seed": seed if seed >= 0 else -1,
                    "steps": steps,
                    "cfg": cfg_scale,
                    "sampler_name": "euler",
                    "scheduler": "normal",
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
                    "text": full_prompt,
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

        return workflow

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global service instance
_comfyui_service: Optional[ComfyUIService] = None


def get_comfyui_service() -> ComfyUIService:
    """Get or create the global ComfyUI service instance"""
    global _comfyui_service
    if _comfyui_service is None:
        comfyui_url = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
        output_dir = os.getenv("COMFYUI_OUTPUT_DIR", "/workspace/ComfyUI/output")
        _comfyui_service = ComfyUIService(
            comfyui_url=comfyui_url,
            output_dir=output_dir
        )
    return _comfyui_service
