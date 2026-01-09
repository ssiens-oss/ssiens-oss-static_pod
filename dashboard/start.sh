#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Run ./install_runpod.sh first"
    exit 1
fi

source .venv/bin/activate
python app/main.py
