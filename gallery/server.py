from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the interactive dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>POD Gallery Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      min-height: 100vh;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px;
    }

    header {
      border-bottom: 2px solid #2a2a3e;
      padding-bottom: 20px;
      margin-bottom: 30px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    h1 {
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #fff 0%, #888 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .header-right {
      display: flex;
      gap: 16px;
      align-items: center;
    }

    .stats {
      display: flex;
      gap: 24px;
      padding: 16px 24px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .stat-label {
      font-size: 12px;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: #fff;
    }

    .status {
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-weight: 500;
    }

    .status.live {
      background: rgba(16, 185, 129, 0.1);
      border-color: rgba(16, 185, 129, 0.3);
      color: #10b981;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    .controls {
      display: flex;
      gap: 12px;
      margin-bottom: 30px;
      flex-wrap: wrap;
    }

    button {
      background: linear-gradient(135deg, #2a2a3e 0%, #1a1a2e 100%);
      border: 1px solid #3a3a4e;
      color: #fff;
      padding: 12px 24px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    button:hover {
      background: linear-gradient(135deg, #3a3a4e 0%, #2a2a3e 100%);
      border-color: #4a4a5e;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    button:active {
      transform: translateY(0);
    }

    .btn-primary {
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
      border-color: #60a5fa;
    }

    .btn-primary:hover {
      background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
    }

    .btn-success {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      border-color: #34d399;
    }

    .btn-success:hover {
      background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
    }

    .btn-danger {
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      border-color: #f87171;
    }

    .btn-danger:hover {
      background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
    }

    #gallery {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;
    }

    .design-card {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.08);
      transition: all 0.3s;
      cursor: pointer;
    }

    .design-card:hover {
      transform: translateY(-8px);
      border-color: rgba(255, 255, 255, 0.2);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
    }

    .design-card img {
      width: 100%;
      display: block;
      aspect-ratio: 1;
      object-fit: cover;
      background: rgba(0, 0, 0, 0.3);
    }

    .design-info {
      padding: 20px;
    }

    .design-name {
      color: #fff;
      margin-bottom: 12px;
      font-weight: 600;
      font-size: 15px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .design-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #666;
      margin-bottom: 16px;
    }

    .design-actions {
      display: flex;
      gap: 8px;
    }

    .design-actions button {
      flex: 1;
      padding: 8px 16px;
      font-size: 12px;
    }

    .empty-state {
      text-align: center;
      padding: 80px 20px;
      color: #666;
    }

    .empty-state h3 {
      font-size: 24px;
      margin-bottom: 12px;
      color: #888;
    }

    .modal {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.95);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal.active {
      display: flex;
    }

    .modal img {
      max-width: 90%;
      max-height: 90%;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>
        <span>🎨</span>
        <span>POD Gallery Dashboard</span>
      </h1>
      <div class="header-right">
        <div class="stats">
          <div class="stat-item">
            <div class="stat-label">Designs</div>
            <div class="stat-value" id="count">0</div>
          </div>
        </div>
        <div class="status" id="status">⚡ Connecting...</div>
      </div>
    </header>

    <div class="controls">
      <button class="btn-primary" onclick="exportAll()">
        📦 Export All (ZIP)
      </button>
      <button class="btn-success" onclick="location.reload()">
        🔄 Refresh
      </button>
      <button onclick="window.open('/designs')">
        📡 API Data
      </button>
    </div>

    <div id="gallery"></div>

    <div class="modal" id="modal" onclick="closeModal()">
      <img id="modalImg" />
    </div>
  </div>

  <script>
    let designs = [];

    async function loadDesigns() {
      try {
        const res = await fetch('/designs');
        designs = await res.json();
        renderGallery();
      } catch (err) {
        console.error('Failed to load designs:', err);
      }
    }

    function renderGallery() {
      const galleryEl = document.getElementById('gallery');
      const countEl = document.getElementById('count');

      if (designs.length === 0) {
        galleryEl.innerHTML = `
          <div class="empty-state">
            <h3>No designs yet</h3>
            <p>Images from ComfyUI will appear here automatically</p>
          </div>
        `;
        countEl.textContent = '0';
        return;
      }

      countEl.textContent = designs.length;

      galleryEl.innerHTML = designs.map(d => {
        const date = new Date(d.timestamp * 1000);
        const size = (d.size / 1024).toFixed(0);

        return `
          <div class="design-card">
            <img
              src="${d.url}"
              alt="${d.name}"
              loading="lazy"
              onclick="openModal('${d.url}')"
            />
            <div class="design-info">
              <div class="design-name" title="${d.name}">${d.name}</div>
              <div class="design-meta">
                <span>${date.toLocaleDateString()}</span>
                <span>${size} KB</span>
              </div>
              <div class="design-actions">
                <button class="btn-success" onclick="event.stopPropagation(); publishDesign('${d.name}')">📤 Publish</button>
                <button class="btn-danger" onclick="event.stopPropagation(); deleteDesign('${d.name}')">🗑️ Delete</button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    async function publishDesign(name) {
      if (!confirm(`Publish "${name}" to Printify?`)) return;
      try {
        const res = await fetch(`/publish/${name}`, { method: 'POST' });
        const data = await res.json();
        alert(data.status === 'queued' ? 'Queued for publishing!' : JSON.stringify(data));
      } catch (err) {
        alert('Publish failed: ' + err.message);
      }
    }

    async function deleteDesign(name) {
      if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;
      try {
        await fetch(`/designs/${name}`, { method: 'DELETE' });
        await loadDesigns();
      } catch (err) {
        alert('Delete failed: ' + err.message);
      }
    }

    function exportAll() {
      window.open('/export', '_blank');
    }

    function openModal(url) {
      document.getElementById('modalImg').src = url;
      document.getElementById('modal').classList.add('active');
    }

    function closeModal() {
      document.getElementById('modal').classList.remove('active');
    }

    function connectLiveStream() {
      const statusEl = document.getElementById('status');
      try {
        const eventSource = new EventSource('/stream');
        eventSource.onopen = () => {
          statusEl.textContent = '⚡ Live';
          statusEl.className = 'status live';
        };
        eventSource.onmessage = () => {
          loadDesigns();
        };
        eventSource.onerror = () => {
          statusEl.textContent = '⚠ Reconnecting...';
          statusEl.className = 'status';
        };
      } catch (err) {
        console.error('SSE not supported, falling back to polling');
        setInterval(loadDesigns, 5000);
      }
    }

    loadDesigns();
    connectLiveStream();

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
      if (e.key === 'r' && e.ctrlKey) {
        e.preventDefault();
        loadDesigns();
      }
    });
  </script>
</body>
</html>
"""

@app.get("/api")
def api_info():
    """API information endpoint (JSON)"""
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
