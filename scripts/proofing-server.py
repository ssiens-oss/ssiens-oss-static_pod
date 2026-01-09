#!/usr/bin/env python3
"""
Web-based proofing server for ComfyUI outputs
Provides UI to review, delete, and publish designs
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn
import os
import shutil
import requests
from pathlib import Path
from PIL import Image
import io
import time
from typing import List

app = FastAPI(title="Design Proofing System")

# Configuration
COMFYUI_OUTPUT = Path(os.getenv("COMFYUI_OUTPUT_DIR", "./ComfyUI/output"))
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
GALLERY_DIR = Path("data/gallery")
PUBLISHED_DIR = Path("data/published")

GALLERY_DIR.mkdir(parents=True, exist_ok=True)
PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the proofing interface"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/api/images")
async def list_images():
    """Get list of all images in ComfyUI output"""
    if not COMFYUI_OUTPUT.exists():
        return {"images": []}

    images = []
    for img_path in COMFYUI_OUTPUT.glob("*.png"):
        stat = img_path.stat()
        images.append({
            "filename": img_path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "url": f"/api/image/{img_path.name}"
        })

    # Also check jpg/jpeg
    for img_path in list(COMFYUI_OUTPUT.glob("*.jpg")) + list(COMFYUI_OUTPUT.glob("*.jpeg")):
        stat = img_path.stat()
        images.append({
            "filename": img_path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "url": f"/api/image/{img_path.name}"
        })

    # Sort by modified time (newest first)
    images.sort(key=lambda x: x["modified"], reverse=True)

    return {"images": images}

@app.get("/api/image/{filename}")
async def get_image(filename: str):
    """Serve an image"""
    img_path = COMFYUI_OUTPUT / filename

    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(img_path)

@app.delete("/api/image/{filename}")
async def delete_image(filename: str):
    """Delete an image"""
    img_path = COMFYUI_OUTPUT / filename

    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    # Move to trash instead of permanent delete
    trash_dir = Path("data/trash")
    trash_dir.mkdir(parents=True, exist_ok=True)

    shutil.move(str(img_path), str(trash_dir / filename))

    return {"success": True, "message": f"Deleted {filename}"}

@app.post("/api/publish")
async def publish_images(data: dict):
    """Publish selected images to Printify"""
    filenames = data.get("filenames", [])

    if not filenames:
        raise HTTPException(status_code=400, detail="No images selected")

    if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
        raise HTTPException(status_code=400, detail="Printify credentials not configured")

    results = []

    for filename in filenames:
        img_path = COMFYUI_OUTPUT / filename

        if not img_path.exists():
            results.append({
                "filename": filename,
                "success": False,
                "error": "File not found"
            })
            continue

        try:
            # Upload to Printify
            product = upload_to_printify(img_path)

            if product:
                # Copy to published directory
                published_path = PUBLISHED_DIR / filename
                shutil.copy(str(img_path), str(published_path))

                results.append({
                    "filename": filename,
                    "success": True,
                    "product_id": product["id"],
                    "title": product["title"]
                })
            else:
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": "Upload failed"
                })

        except Exception as e:
            results.append({
                "filename": filename,
                "success": False,
                "error": str(e)
            })

    return {"results": results}

@app.post("/api/download-selected")
async def download_selected(data: dict):
    """Create a zip of selected images for download"""
    import zipfile
    from io import BytesIO

    filenames = data.get("filenames", [])

    if not filenames:
        raise HTTPException(status_code=400, detail="No images selected")

    # Create zip in memory
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename in filenames:
            img_path = COMFYUI_OUTPUT / filename
            if img_path.exists():
                zip_file.write(img_path, filename)

    zip_buffer.seek(0)

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=designs_{int(time.time())}.zip"
        }
    )

def upload_to_printify(image_path: Path, price: float = 39.99):
    """Upload image to Printify and create product"""

    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}

    # Upload image
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        response = requests.post(
            "https://api.printify.com/v1/uploads/images.json",
            headers=headers,
            files=files
        )

        if response.status_code != 200:
            return None

        image_id = response.json()["id"]

    # Create product
    title = image_path.stem.replace("_", " ").title()[:50]

    product_data = {
        "title": title,
        "description": f"Unique AI-generated design: {title}",
        "blueprint_id": 77,
        "print_provider_id": 99,
        "variants": [
            {"id": vid, "price": int(price * 100), "is_enabled": True}
            for vid in [45740, 45741, 45742, 45743, 45744]
        ],
        "print_areas": [{
            "variant_ids": [45740, 45741, 45742, 45743, 45744],
            "placeholders": [{
                "position": "front",
                "images": [{
                    "id": image_id,
                    "x": 0.5,
                    "y": 0.5,
                    "scale": 1.0,
                    "angle": 0
                }]
            }]
        }]
    }

    response = requests.post(
        f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP_ID}/products.json",
        headers={**headers, "Content-Type": "application/json"},
        json=product_data
    )

    if response.status_code == 200:
        return response.json()

    return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Design Proofing System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .toolbar {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-publish {
            background: #10b981;
            color: white;
        }

        .btn-publish:hover:not(:disabled) {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
        }

        .btn-delete {
            background: #ef4444;
            color: white;
        }

        .btn-delete:hover:not(:disabled) {
            background: #dc2626;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(239, 68, 68, 0.4);
        }

        .btn-download {
            background: #3b82f6;
            color: white;
        }

        .btn-download:hover:not(:disabled) {
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
        }

        .btn-select {
            background: #8b5cf6;
            color: white;
        }

        .btn-select:hover {
            background: #7c3aed;
        }

        .selection-info {
            margin-left: auto;
            color: #666;
            font-weight: 600;
            font-size: 1.1em;
        }

        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .image-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
        }

        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .image-card.selected {
            outline: 4px solid #10b981;
            outline-offset: 2px;
        }

        .image-card img {
            width: 100%;
            height: 300px;
            object-fit: cover;
        }

        .image-info {
            padding: 15px;
        }

        .image-filename {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
            word-break: break-all;
        }

        .image-meta {
            font-size: 0.9em;
            color: #666;
        }

        .checkbox {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 30px;
            height: 30px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        }

        .checkbox input {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        .loading {
            text-align: center;
            padding: 60px;
            color: white;
            font-size: 1.5em;
        }

        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #333;
            color: white;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s;
        }

        .toast.success {
            background: #10b981;
        }

        .toast.error {
            background: #ef4444;
        }

        @keyframes slideIn {
            from { transform: translateX(400px); }
            to { transform: translateX(0); }
        }

        .empty-state {
            text-align: center;
            padding: 100px 20px;
            color: white;
        }

        .empty-state h2 {
            font-size: 2em;
            margin-bottom: 20px;
        }

        .empty-state p {
            font-size: 1.2em;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎨 Design Proofing System</h1>
            <p class="subtitle">Review, approve, and publish your ComfyUI designs</p>
        </header>

        <div class="toolbar">
            <button class="btn btn-select" onclick="selectAll()">
                ☑️ Select All
            </button>
            <button class="btn btn-select" onclick="deselectAll()">
                ☐ Deselect All
            </button>
            <button class="btn btn-publish" id="publishBtn" onclick="publishSelected()" disabled>
                🚀 Publish to Printify
            </button>
            <button class="btn btn-download" id="downloadBtn" onclick="downloadSelected()" disabled>
                💾 Download Selected
            </button>
            <button class="btn btn-delete" id="deleteBtn" onclick="deleteSelected()" disabled>
                🗑️ Delete Selected
            </button>
            <span class="selection-info" id="selectionInfo">0 selected</span>
        </div>

        <div id="gallery" class="gallery">
            <div class="loading">
                <div class="spinner"></div>
                Loading designs...
            </div>
        </div>
    </div>

    <script>
        let images = [];
        let selected = new Set();

        async function loadImages() {
            try {
                const response = await fetch('/api/images');
                const data = await response.json();
                images = data.images;
                renderGallery();
            } catch (error) {
                showToast('Failed to load images', 'error');
            }
        }

        function renderGallery() {
            const gallery = document.getElementById('gallery');

            if (images.length === 0) {
                gallery.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <h2>No designs found</h2>
                        <p>Generate some designs with ComfyUI first!</p>
                    </div>
                `;
                return;
            }

            gallery.innerHTML = images.map(img => `
                <div class="image-card ${selected.has(img.filename) ? 'selected' : ''}"
                     onclick="toggleSelect('${img.filename}')">
                    <div class="checkbox">
                        <input type="checkbox"
                               ${selected.has(img.filename) ? 'checked' : ''}
                               onclick="event.stopPropagation(); toggleSelect('${img.filename}')">
                    </div>
                    <img src="${img.url}" alt="${img.filename}">
                    <div class="image-info">
                        <div class="image-filename">${img.filename}</div>
                        <div class="image-meta">
                            ${(img.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                    </div>
                </div>
            `).join('');

            updateToolbar();
        }

        function toggleSelect(filename) {
            if (selected.has(filename)) {
                selected.delete(filename);
            } else {
                selected.add(filename);
            }
            renderGallery();
        }

        function selectAll() {
            images.forEach(img => selected.add(img.filename));
            renderGallery();
        }

        function deselectAll() {
            selected.clear();
            renderGallery();
        }

        function updateToolbar() {
            const count = selected.size;
            document.getElementById('selectionInfo').textContent = `${count} selected`;
            document.getElementById('publishBtn').disabled = count === 0;
            document.getElementById('downloadBtn').disabled = count === 0;
            document.getElementById('deleteBtn').disabled = count === 0;
        }

        async function publishSelected() {
            if (selected.size === 0) return;

            if (!confirm(`Publish ${selected.size} design(s) to Printify?`)) return;

            const btn = document.getElementById('publishBtn');
            btn.disabled = true;
            btn.textContent = '⏳ Publishing...';

            try {
                const response = await fetch('/api/publish', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filenames: Array.from(selected)})
                });

                const data = await response.json();
                const successful = data.results.filter(r => r.success).length;

                showToast(`✅ Published ${successful}/${selected.size} designs`, 'success');

                // Download published images
                await downloadSelected();

                selected.clear();
                await loadImages();

            } catch (error) {
                showToast('Failed to publish: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '🚀 Publish to Printify';
            }
        }

        async function downloadSelected() {
            if (selected.size === 0) return;

            try {
                const response = await fetch('/api/download-selected', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filenames: Array.from(selected)})
                });

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `designs_${Date.now()}.zip`;
                a.click();

                showToast(`📥 Downloaded ${selected.size} design(s)`, 'success');

            } catch (error) {
                showToast('Failed to download: ' + error.message, 'error');
            }
        }

        async function deleteSelected() {
            if (selected.size === 0) return;

            if (!confirm(`Delete ${selected.size} design(s)? They will be moved to trash.`)) return;

            try {
                for (const filename of selected) {
                    await fetch(`/api/image/${filename}`, {method: 'DELETE'});
                }

                showToast(`🗑️ Deleted ${selected.size} design(s)`, 'success');

                selected.clear();
                await loadImages();

            } catch (error) {
                showToast('Failed to delete: ' + error.message, 'error');
            }
        }

        function showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);

            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        // Load images on page load
        loadImages();

        // Refresh every 30 seconds
        setInterval(loadImages, 30000);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("🎨 Starting Design Proofing Server...")
    print(f"📁 ComfyUI Output: {COMFYUI_OUTPUT}")
    print(f"✅ Printify: {'Configured' if PRINTIFY_API_KEY else 'Not configured'}")
    print("\n🌐 Server will be available at: http://localhost:8888")
    print("   Use RunPod port forwarding to access\n")

    uvicorn.run(app, host="0.0.0.0", port=8888)
