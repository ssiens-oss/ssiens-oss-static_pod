#!/usr/bin/env bash
set -e

# Always run from repo root
cd "$(dirname "$(readlink -f "$0")")"

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# Start backend services
docker compose up -d

# Start GUI
npm run dev:music
