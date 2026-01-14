#!/bin/bash
# Quick image generation script

cd "$(dirname "$0")"

# Load .env from parent directory
if [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
fi

# Generate image
python3 -c "
from comfyui_serverless import ServerlessComfyUI
import sys

prompt = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'mountain landscape'

client = ServerlessComfyUI()
image_path = client.generate_image(
    prompt=prompt,
    steps=30,
    width=1024,
    height=1024
)
print(f'\n✅ Image saved: {image_path}')
" "$@"
