from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time, zipfile, os

# Check multiple possible output locations
POSSIBLE_OUTPUTS = [
    Path("/workspace/ssiens-oss-static_pod/ComfyUI/output"),
    Path("/home/user/ssiens-oss-static_pod/ComfyUI/output"),
    Path("/home/user/ssiens-oss-static_pod/output"),
    Path("output"),
]

COMFY_OUTPUT = None
for p in POSSIBLE_OUTPUTS:
    if p.exists():
        COMFY_OUTPUT = p
        break

if COMFY_OUTPUT is None:
    # Default to creating output directory in current location
    COMFY_OUTPUT = Path("/home/user/ssiens-oss-static_pod/output")
    COMFY_OUTPUT.mkdir(parents=True, exist_ok=True)

print(f"📂 Watching output directory: {COMFY_OUTPUT}")

app = FastAPI(title="POD Gallery Bridge")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve images
app.mount("/images", StaticFiles(directory=COMFY_OUTPUT), name="images")

def list_images():
    """Get all PNG images, excluding checkpoints and hidden files"""
    return sorted(
        [
            p for p in COMFY_OUTPUT.rglob("*.png")
            if ".ipynb_checkpoints" not in str(p) and not p.name.startswith(".")
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

@app.get("/")
def root():
    return {
        "service": "POD Gallery Bridge",
        "output_dir": str(COMFY_OUTPUT),
        "endpoints": {
            "designs": "/designs",
            "stream": "/stream",
            "export": "/export",
            "publish": "/publish/{image}"
        }
    }

@app.get("/designs")
def designs():
    """List all design images with metadata"""
    return [
        {
            "name": p.name,
            "url": f"/images/{p.relative_to(COMFY_OUTPUT)}",
            "timestamp": p.stat().st_mtime,
            "size": p.stat().st_size
        }
        for p in list_images()
    ]

@app.get("/stream")
def stream():
    """Server-Sent Events stream for live updates"""
    def gen():
        last = None
        while True:
            names = [p.name for p in list_images()]
            if names != last:
                last = names
                yield f"data: {len(names)}\n\n"
            time.sleep(1)
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/export")
def export():
    """Export all designs as a ZIP file"""
    zip_name = f"pod_designs_{int(time.time())}.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for p in list_images():
            z.write(p, p.name)
    return FileResponse(zip_name, filename=zip_name)

@app.post("/publish/{image}")
def publish(image: str):
    """Publish an image to Printify (hook for integration)"""
    target = next((p for p in list_images() if p.name == image), None)
    if not target:
        return {"error": "image not found"}

    # This is where you'd integrate with your existing Printify workflow
    # from gateway.app.printify_client import publish_design
    # result = publish_design(str(target))

    return {
        "status": "queued",
        "image": image,
        "path": str(target),
        "note": "Connect to Printify workflow via gateway.app.printify_client"
    }

@app.delete("/designs/{image}")
def delete_design(image: str):
    """Delete a design image"""
    target = next((p for p in list_images() if p.name == image), None)
    if not target:
        return {"error": "image not found"}

    target.unlink()
    return {"status": "deleted", "image": image}
