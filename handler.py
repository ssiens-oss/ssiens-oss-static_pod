"""
RunPod Serverless Handler for POD Pipeline
Processes design generation requests via serverless endpoint
"""
import runpod
import os
import json
import subprocess
import time
import requests
from pathlib import Path


def start_comfyui():
    """Start ComfyUI server if not already running"""
    try:
        # Check if ComfyUI is already running
        response = requests.get("http://localhost:8188/system_stats", timeout=2)
        if response.status_code == 200:
            print("ComfyUI already running")
            return True
    except:
        pass

    # Start ComfyUI
    print("Starting ComfyUI...")
    subprocess.Popen(
        ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"],
        cwd="/workspace/ComfyUI",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for ComfyUI to be ready
    for i in range(30):
        try:
            response = requests.get("http://localhost:8188/system_stats", timeout=2)
            if response.status_code == 200:
                print("ComfyUI started successfully")
                return True
        except:
            time.sleep(2)

    print("Failed to start ComfyUI")
    return False


def generate_design(job):
    """
    Process a design generation job

    Expected input:
    {
        "prompt": "Design prompt text",
        "style": "artistic|minimal|bold",
        "product_type": "tshirt|hoodie",
        "publish": true|false
    }
    """
    job_input = job.get('input', {})

    # Ensure ComfyUI is running
    if not start_comfyui():
        return {"error": "Failed to start ComfyUI"}

    try:
        # Extract parameters
        prompt = job_input.get('prompt', 'Abstract geometric design')
        style = job_input.get('style', 'artistic')
        product_type = job_input.get('product_type', 'tshirt')
        auto_publish = job_input.get('publish', False)

        print(f"Generating design: {prompt} ({style} style for {product_type})")

        # TODO: Implement actual ComfyUI workflow execution
        # This is a placeholder - replace with your ComfyUI workflow API call
        workflow = {
            "prompt": prompt,
            "style": style,
            "product": product_type
        }

        # Call ComfyUI API to generate design
        response = requests.post(
            "http://localhost:8188/prompt",
            json={"prompt": workflow},
            timeout=300  # 5 minute timeout for generation
        )

        if response.status_code != 200:
            return {"error": f"ComfyUI API error: {response.status_code}"}

        result = response.json()
        prompt_id = result.get('prompt_id')

        # Wait for generation to complete
        # Poll ComfyUI for completion
        max_wait = 300  # 5 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            history_response = requests.get(f"http://localhost:8188/history/{prompt_id}")
            if history_response.status_code == 200:
                history = history_response.json()
                if prompt_id in history and history[prompt_id].get('status', {}).get('completed'):
                    # Get output image path
                    outputs = history[prompt_id].get('outputs', {})
                    # Extract image path from outputs
                    # This depends on your ComfyUI workflow structure

                    return {
                        "status": "success",
                        "prompt_id": prompt_id,
                        "design": {
                            "prompt": prompt,
                            "style": style,
                            "product_type": product_type
                        },
                        "outputs": outputs
                    }
            time.sleep(2)

        return {"error": "Design generation timeout"}

    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}


def handler(job):
    """
    RunPod serverless handler function
    """
    print(f"Received job: {json.dumps(job, indent=2)}")

    # Get the operation type
    operation = job.get('input', {}).get('operation', 'generate')

    if operation == 'health':
        return {
            "status": "healthy",
            "comfyui_running": start_comfyui()
        }
    elif operation == 'generate':
        return generate_design(job)
    else:
        return {"error": f"Unknown operation: {operation}"}


if __name__ == "__main__":
    print("Starting RunPod Serverless Handler...")
    runpod.serverless.start({"handler": handler})
