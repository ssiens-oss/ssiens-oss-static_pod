"""
RunPod Serverless Handler for ComfyUI
This handler receives ComfyUI workflows and returns generated images.

Deploy this to your RunPod Serverless endpoint.
"""

import runpod
import requests
import json
import time
import os
import base64
from io import BytesIO

# ComfyUI runs locally on the serverless worker
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")


def execute_comfyui_workflow(workflow):
    """Execute a ComfyUI workflow and return generated images."""

    # Generate client ID
    client_id = f"runpod-{int(time.time())}"

    # Submit workflow to ComfyUI
    prompt_response = requests.post(
        f"{COMFYUI_URL}/prompt",
        json={
            "prompt": workflow,
            "client_id": client_id
        }
    )

    if prompt_response.status_code != 200:
        return {
            "error": f"Failed to submit workflow: {prompt_response.text}"
        }

    prompt_id = prompt_response.json()["prompt_id"]

    # Poll for completion
    max_attempts = 300  # 5 minutes max (1s intervals)
    for attempt in range(max_attempts):
        time.sleep(1)

        # Check history
        history_response = requests.get(
            f"{COMFYUI_URL}/history/{prompt_id}"
        )

        if history_response.status_code != 200:
            continue

        history = history_response.json()

        if prompt_id not in history:
            continue

        job = history[prompt_id]

        # Check if completed
        if job.get("status", {}).get("completed", False):
            # Extract images
            images = []
            outputs = job.get("outputs", {})

            for node_id, output in outputs.items():
                if "images" in output:
                    for img_info in output["images"]:
                        # Get image data
                        filename = img_info["filename"]
                        subfolder = img_info.get("subfolder", "")
                        img_type = img_info.get("type", "output")

                        # Build image URL
                        img_url = f"{COMFYUI_URL}/view"
                        params = {
                            "filename": filename,
                            "type": img_type
                        }
                        if subfolder:
                            params["subfolder"] = subfolder

                        # Get image data
                        img_response = requests.get(img_url, params=params)

                        if img_response.status_code == 200:
                            # Convert to base64 for output
                            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                            img_data_url = f"data:image/png;base64,{img_base64}"
                            images.append(img_data_url)

            return {
                "images": images,
                "prompt_id": prompt_id,
                "execution_time": attempt
            }

        # Check if failed
        if job.get("status", {}).get("status_str") == "error":
            error_messages = []
            if "messages" in job.get("status", {}):
                error_messages = [msg[1] for msg in job["status"]["messages"] if msg[0] == "execution_error"]

            return {
                "error": "Workflow execution failed",
                "details": error_messages
            }

    return {
        "error": "Workflow execution timeout"
    }


def handler(event):
    """
    RunPod handler function.

    Expected input format:
    {
        "input": {
            "workflow": { ... ComfyUI workflow JSON ... },
            "images": [] // Optional: base64 encoded input images
        }
    }
    """

    try:
        # Extract workflow from input
        input_data = event.get("input", {})
        workflow = input_data.get("workflow")

        if not workflow:
            return {
                "error": "No workflow provided in input"
            }

        # Execute workflow
        result = execute_comfyui_workflow(workflow)

        return result

    except Exception as e:
        return {
            "error": str(e)
        }


# Start RunPod serverless handler
if __name__ == "__main__":
    runpod.serverless.start({
        "handler": handler
    })
