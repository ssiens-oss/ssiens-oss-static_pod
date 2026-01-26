"""
RunPod Serverless Handler for ComfyUI
Processes ComfyUI workflows and returns generated images
"""
import runpod
import requests
import time
import base64
import os
from pathlib import Path

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
OUTPUT_DIR = Path("/workspace/ComfyUI/output")


def wait_for_comfyui(timeout=60):
    """Wait for ComfyUI to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
            if r.ok:
                return True
        except:
            pass
        time.sleep(2)
    return False


def submit_workflow(workflow, client_id="serverless"):
    """Submit workflow to ComfyUI and get prompt_id"""
    payload = {"prompt": workflow, "client_id": client_id}
    response = requests.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=30)
    response.raise_for_status()
    return response.json().get("prompt_id")


def wait_for_completion(prompt_id, timeout=300):
    """Poll ComfyUI history until job completes"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            if response.ok:
                history = response.json()
                if prompt_id in history:
                    entry = history[prompt_id]
                    status = entry.get("status", {})
                    if status.get("completed"):
                        return entry
                    if status.get("status_str") == "error":
                        raise Exception(f"ComfyUI error: {entry.get('status', {}).get('messages', 'Unknown')}")
        except requests.RequestException:
            pass
        time.sleep(2)
    raise TimeoutError(f"Job {prompt_id} did not complete within {timeout}s")


def get_output_images(history_entry):
    """Extract output images from ComfyUI history"""
    images = []
    outputs = history_entry.get("outputs", {})

    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for img_info in node_output["images"]:
                filename = img_info.get("filename")
                subfolder = img_info.get("subfolder", "")
                img_type = img_info.get("type", "output")

                # Build path to image
                if subfolder:
                    img_path = OUTPUT_DIR / subfolder / filename
                else:
                    img_path = OUTPUT_DIR / filename

                if img_path.exists():
                    # Read and base64 encode
                    with open(img_path, "rb") as f:
                        b64_data = base64.b64encode(f.read()).decode("utf-8")
                    images.append({
                        "filename": filename,
                        "data": b64_data,
                        "type": "image/png"
                    })

    return images


def handler(job):
    """
    RunPod serverless handler

    Expected input:
    {
        "input": {
            "workflow": { ... ComfyUI workflow ... },
            "client_id": "optional-client-id"
        }
    }

    Returns:
    {
        "images": [
            {"filename": "...", "data": "base64...", "type": "image/png"}
        ],
        "prompt_id": "..."
    }
    """
    job_input = job.get("input", {})
    workflow = job_input.get("workflow")
    client_id = job_input.get("client_id", "runpod-serverless")

    if not workflow:
        return {"error": "No workflow provided"}

    # Wait for ComfyUI
    if not wait_for_comfyui(timeout=30):
        return {"error": "ComfyUI not available"}

    try:
        # Submit workflow
        prompt_id = submit_workflow(workflow, client_id)

        # Wait for completion
        history = wait_for_completion(prompt_id, timeout=300)

        # Get output images
        images = get_output_images(history)

        return {
            "prompt_id": prompt_id,
            "images": images,
            "status": "success"
        }

    except Exception as e:
        return {"error": str(e)}


# Start the serverless handler
runpod.serverless.start({"handler": handler})
