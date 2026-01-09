# POD Pipeline - Quick Start Guide

## ✅ Pipeline is RUNNING

Your POD (Print-on-Demand) pipeline is currently active with **3 designs** indexed.

---

## 🚀 Access Points

| Service | URL | Status |
|---------|-----|--------|
| **Web Gallery** | http://localhost:8088/view-gallery.html | ✅ ONLINE |
| **API** | http://localhost:8099 | ✅ ONLINE |
| **API Docs** | http://localhost:8099/docs | ✅ ONLINE |

---

## 💡 Quick Commands (Run from ANY directory)

```bash
# Check status
pod status

# Start pipeline
pod start

# Stop pipeline
pod stop

# View logs
pod logs

# Add an image
pod add /path/to/image.png

# Export all designs as ZIP
pod export
```

---

## 📂 Test Files Already Added

Three test images have been created in `output/`:
- `ComfyUI_00001_.png`
- `test-design-001.png`
- `test-design-002.png`

View them at: http://localhost:8088/view-gallery.html

---

## 🔥 Common Tasks

### Add New Designs

**From anywhere:**
```bash
pod add /path/to/your-design.png
```

**Or directly:**
```bash
cp your-design.png /home/user/ssiens-oss-static_pod/output/
```

The gallery will update automatically within 1 second.

### Export All Designs

```bash
# Quick export
pod export

# Or via API
curl -O http://localhost:8099/export
```

### Check What's Indexed

```bash
curl http://localhost:8099/designs | python3 -m json.tool
```

### Publish to Printify (when configured)

```bash
curl -X POST http://localhost:8099/publish/ComfyUI_00001_.png
```

### Delete a Design

```bash
curl -X DELETE http://localhost:8099/designs/ComfyUI_00001_.png
```

---

## 🎨 Connect ComfyUI

If you have ComfyUI installed, configure it to output to:

```
/home/user/ssiens-oss-static_pod/output/
```

Or the pipeline will auto-detect these paths:
- `/workspace/ssiens-oss-static_pod/ComfyUI/output`
- `/home/user/ssiens-oss-static_pod/ComfyUI/output`
- `/home/user/ssiens-oss-static_pod/output` ✅ (current)

---

## 📡 API Examples

### List All Designs
```bash
curl http://localhost:8099/designs
```

### Live Stream (SSE)
```bash
curl http://localhost:8099/stream
```

### Service Info
```bash
curl http://localhost:8099/
```

---

## 🐛 Troubleshooting

### Pipeline Not Running

```bash
pod start
```

### Can't See Designs

```bash
# Check if files exist
ls /home/user/ssiens-oss-static_pod/output/

# Check API response
curl http://localhost:8099/designs
```

### Check Logs

```bash
pod logs
# or
tail -f /home/user/ssiens-oss-static_pod/gallery.log
```

### Reset Everything

```bash
pod stop
rm /home/user/ssiens-oss-static_pod/output/*.png
pod start
```

---

## 📖 Full Documentation

See `POD_PIPELINE_README.md` for:
- Complete API reference
- Integration guides (Printify, ComfyUI)
- Auto-restart configuration
- Advanced usage

---

## 🎯 Current State

```
✅ Gallery Bridge: RUNNING on port 8099
✅ Web UI: RUNNING on port 8088
✅ Designs Indexed: 3
✅ Auto-refresh: ENABLED (SSE)
✅ Export: ENABLED
✅ Publish Hook: READY
✅ Delete: ENABLED
```

---

## 🚀 Next Steps

1. ✅ **Pipeline running** - You're here!
2. 🖼️  **View gallery** - Open http://localhost:8088/view-gallery.html
3. 📦 **Add designs** - Use `pod add` or copy to `output/`
4. 🎨 **Connect ComfyUI** - Configure output path
5. 🚀 **Wire Printify** - Edit `gallery/server.py` (line 112)

---

**Need help?** Run `pod` for command list.
