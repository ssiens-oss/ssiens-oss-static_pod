#!/usr/bin/env python3
"""
ComfyUI Client - Interface for ComfyUI API
"""
import os
import sys
import json
import time
import uuid
import requests
import websocket
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import setup_logger

log = setup_logger("COMFY", "logs/comfy_client.log")

COMFY_API = os.getenv("COMFY_API", "http://127.0.0.1:8188")

class ComfyUIClient:
    """Client for interacting with ComfyUI API"""

    def __init__(self, api_url: str = COMFY_API):
        self.api_url = api_url
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """
        Queue a workflow for generation

        Args:
            workflow: ComfyUI workflow dictionary

        Returns:
            Prompt ID
        """
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }

        response = requests.post(
            f"{self.api_url}/prompt",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        prompt_id = result["prompt_id"]

        log.info(f"Queued prompt: {prompt_id}")
        return prompt_id

    def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get generation history for a prompt

        Args:
            prompt_id: Prompt ID to check

        Returns:
            History data or None
        """
        response = requests.get(
            f"{self.api_url}/history/{prompt_id}",
            timeout=10
        )
        response.raise_for_status()

        history = response.json()
        return history.get(prompt_id)

    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """
        Download generated image

        Args:
            filename: Image filename
            subfolder: Subfolder in output directory
            folder_type: Type of folder (output, input, temp)

        Returns:
            Image bytes
        """
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }

        response = requests.get(
            f"{self.api_url}/view",
            params=params,
            timeout=30
        )
        response.raise_for_status()

        return response.content

    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Wait for prompt to complete

        Args:
            prompt_id: Prompt ID to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Completed history data
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)

            if history and history.get("status", {}).get("completed", False):
                log.info(f"Prompt {prompt_id} completed")
                return history

            time.sleep(2)

        raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")

    def generate_and_save(
        self,
        workflow: Dict[str, Any],
        output_dir: Path,
        filename_prefix: str = "comfy"
    ) -> list[Path]:
        """
        Generate images and save to directory

        Args:
            workflow: ComfyUI workflow
            output_dir: Output directory path
            filename_prefix: Prefix for saved files

        Returns:
            List of saved file paths
        """
        log.info("Starting generation...")

        # Queue the prompt
        prompt_id = self.queue_prompt(workflow)

        # Wait for completion
        history = self.wait_for_completion(prompt_id)

        # Download generated images
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []

        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for image_info in node_output["images"]:
                    filename = image_info["filename"]
                    subfolder = image_info.get("subfolder", "")

                    # Download image
                    image_data = self.get_image(filename, subfolder)

                    # Save with custom prefix
                    save_path = output_dir / f"{filename_prefix}_{filename}"
                    save_path.write_bytes(image_data)

                    saved_files.append(save_path)
                    log.info(f"✅ Saved: {save_path}")

        return saved_files
