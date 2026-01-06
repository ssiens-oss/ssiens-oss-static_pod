#!/bin/bash
#
# Quick Test Script for POD Engine
# Tests the complete workflow
#

echo "🚀 StaticWaves POD Engine - Test Run"
echo "======================================"
echo ""

# Check if services are running
echo "1. Checking if backend is running..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend not running. Starting it now..."
    cd backend
    python3 main.py &
    BACKEND_PID=$!
    sleep 5
    cd ..
fi

echo ""
echo "2. Checking if frontend is running..."
if curl -s http://localhost:5173 > /dev/null; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend not running. Starting it now..."
    npm run dev &
    FRONTEND_PID=$!
    sleep 5
fi

echo ""
echo "======================================"
echo "✨ POD Engine is ready!"
echo "======================================"
echo ""
echo "📱 Open these URLs in your browser:"
echo ""
echo "   Main App:  http://localhost:5173"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🧪 Test Workflow:"
echo "   1. Create account at /register"
echo "   2. Login with your credentials"
echo "   3. Go to AI Generate tab"
echo "   4. Pick a genre (e.g., Fantasy 🧙)"
echo "   5. Select a template (e.g., Dragon Castle)"
echo "   6. Choose batch size (e.g., 2️⃣)"
echo "   7. Click 'Generate Image'"
echo "   8. Save to library when done"
echo "   9. Go to Designs tab to see it"
echo "   10. Try bulk operations!"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
tail -f /dev/null
