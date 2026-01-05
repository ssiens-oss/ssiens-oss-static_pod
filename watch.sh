#!/bin/bash
# Development watcher - rebuilds on file changes

echo "🔍 Starting development watcher..."
echo "   Watching: *.ts files"
echo "   Press Ctrl+C to stop"
echo ""

# Install nodemon if not present
if ! command -v nodemon &> /dev/null; then
    echo "Installing nodemon..."
    npm install -g nodemon
fi

# Watch TypeScript files and rebuild
nodemon \
  --watch services \
  --watch . \
  --ext ts \
  --exec "echo '🔨 Rebuilding...' && tsc --noEmit && echo '✅ Build complete!'" \
  --delay 1
