#!/usr/bin/env python3
"""
StaticWaves Gallery Proofing Server
Serves a web UI for reviewing designs before publishing to Printify
"""

import os
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
import subprocess

# Configuration
IMG_DIR = os.getenv("PRINTIFY_OUTPUT_DIR", "/workspace/printify_ready")
PORT = int(os.getenv("GALLERY_PORT", "8080"))
HOST = os.getenv("GALLERY_HOST", "0.0.0.0")

class GalleryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        # Serve gallery HTML
        if parsed_path.path == '/' or parsed_path.path == '/gallery':
            self.serve_gallery()

        # API: Get list of designs
        elif parsed_path.path == '/api/designs':
            self.serve_designs_list()

        # Serve image files
        elif parsed_path.path.startswith('/images/'):
            self.serve_image(parsed_path.path)

        else:
            self.send_error(404)

    def do_POST(self):
        parsed_path = urlparse(self.path)

        # API: Publish selected designs
        if parsed_path.path == '/api/publish':
            self.handle_publish()
        else:
            self.send_error(404)

    def serve_gallery(self):
        """Serve the gallery HTML page"""
        gallery_html = Path(__file__).parent / 'gallery-proof.html'

        try:
            with open(gallery_html, 'r') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, f"Error loading gallery: {e}")

    def serve_designs_list(self):
        """Return JSON list of all designs"""
        try:
            if not os.path.exists(IMG_DIR):
                designs = []
            else:
                designs = []
                for filename in sorted(os.listdir(IMG_DIR)):
                    if filename.lower().endswith('.png'):
                        # Generate readable name from filename
                        name = filename.replace('.png', '').replace('staticwaves_', '').replace('_', ' ').title()

                        designs.append({
                            'filename': filename,
                            'name': name,
                            'url': f'/images/{filename}',
                            'path': os.path.join(IMG_DIR, filename)
                        })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(designs).encode())

        except Exception as e:
            self.send_error(500, f"Error listing designs: {e}")

    def serve_image(self, path):
        """Serve an image file"""
        try:
            filename = path.split('/images/')[-1]
            filepath = os.path.join(IMG_DIR, filename)

            if not os.path.exists(filepath):
                self.send_error(404, f"Image not found: {filename}")
                return

            with open(filepath, 'rb') as f:
                content = f.read()

            self.send_response(200)
            mimetype, _ = mimetypes.guess_type(filepath)
            self.send_header('Content-Type', mimetype or 'image/png')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_error(500, f"Error serving image: {e}")

    def handle_publish(self):
        """Handle publish request"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            selected_designs = data.get('designs', [])

            if not selected_designs:
                self.send_error(400, "No designs selected")
                return

            # Create temp file with selected designs
            temp_list = Path('/tmp/selected_designs.txt')
            with open(temp_list, 'w') as f:
                for design in selected_designs:
                    f.write(f"{os.path.join(IMG_DIR, design)}\n")

            # Call publish script
            script_path = Path(__file__).parent / 'push-to-printify.py'
            result = subprocess.run(
                [
                    'python3',
                    str(script_path),
                    '--files', str(temp_list)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                response = {
                    'success': True,
                    'published': len(selected_designs) * 2,  # Hoodie + Tee per design
                    'message': 'Successfully published to Printify'
                }
                self.send_response(200)
            else:
                response = {
                    'success': False,
                    'error': result.stderr or 'Unknown error'
                }
                self.send_response(500)

            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Error publishing: {e}")

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[Gallery] {self.address_string()} - {format % args}")


def main():
    print("╔════════════════════════════════════════════════════╗")
    print("║  StaticWaves Gallery Proofing Server             ║")
    print("╚════════════════════════════════════════════════════╝")
    print("")
    print(f"📁 Image directory: {IMG_DIR}")
    print(f"🌐 Server: http://{HOST}:{PORT}")
    print("")

    # Check if image directory exists
    if not os.path.exists(IMG_DIR):
        print(f"⚠️  Warning: Image directory not found: {IMG_DIR}")
        print("Creating directory...")
        os.makedirs(IMG_DIR, exist_ok=True)

    # Count existing images
    image_count = len([f for f in os.listdir(IMG_DIR) if f.lower().endswith('.png')]) if os.path.exists(IMG_DIR) else 0
    print(f"🖼️  Found {image_count} designs ready to proof")
    print("")
    print("🚀 Starting server...")
    print("")
    print("Open in your browser:")
    print(f"   → http://localhost:{PORT}")
    print(f"   → http://<pod-ip>:{PORT}")
    print("")
    print("Press Ctrl+C to stop")
    print("")

    try:
        server = HTTPServer((HOST, PORT), GalleryHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gallery server...")
        server.shutdown()


if __name__ == "__main__":
    main()
