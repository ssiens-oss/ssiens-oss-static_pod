#!/bin/bash
# Sync latest code to container
# Run this from your local repository root

set -e

echo "🔄 Syncing latest code to container..."

# If you're inside the container, run:
if [ -d "/workspace/pod/.git" ]; then
    echo "📦 Detected container environment"
    cd /workspace/pod

    # Fetch and pull latest changes
    echo "⬇️ Fetching latest changes..."
    git fetch origin claude/inject-http-adapter-Aiv7c

    echo "🔀 Checking out branch..."
    git checkout claude/inject-http-adapter-Aiv7c

    echo "📥 Pulling latest changes..."
    git pull origin claude/inject-http-adapter-Aiv7c

    echo "✅ Code synced successfully!"
    echo ""
    echo "📋 New files available:"
    echo "   - docs/PRINTIFY_BLUEPRINTS.md"
    echo "   - scripts/find_printify_blueprint.py"
    echo "   - scripts/set_product_template.sh"
    echo ""
    echo "🎯 Default template: Gildan 18500 Hoodie (Blueprint 165)"
    echo ""
    echo "Next steps:"
    echo "  1. python scripts/find_printify_blueprint.py --id 165 --providers"
    echo "  2. cd gateway && PYTHONPATH=. python -m flask run --host=0.0.0.0 --port=5000"
else
    echo "❌ Not in container environment (/workspace/pod not found)"
    echo ""
    echo "If you're on the host, copy files to container:"
    echo "  docker cp . CONTAINER_ID:/workspace/pod/"
    echo ""
    echo "Or rebuild the container with latest code"
fi
