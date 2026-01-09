#!/bin/bash
# Quick start script for POD Gateway

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Run ./install_runpod.sh first"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠ No .env file found, using defaults"
fi

source .venv/bin/activate
python app/main.py
