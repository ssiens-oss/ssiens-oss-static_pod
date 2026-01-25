#!/bin/bash
# Quick setup script to get latest changes and run gateway

echo "🔄 Pulling latest changes from git..."
git pull origin claude/fix-pod-engine-pipeline-kgDs9

echo ""
echo "✅ Latest changes pulled!"
echo ""
echo "📋 What's new:"
echo "  - RunPod Serverless integration"
echo "  - Gateway virtual environment setup"
echo "  - Fixed compilation issues"
echo "  - Test scripts for RunPod"
echo ""
echo "🚀 To start the gateway:"
echo "   cd gateway"
echo "   ./start.sh"
echo ""
echo "🧪 To test RunPod:"
echo "   ./test-runpod.sh"
echo "   ./test-runpod-async.sh"
echo ""
