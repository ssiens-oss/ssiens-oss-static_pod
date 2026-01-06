#!/bin/bash

echo "======================================="
echo "🌐 RunPod Access URLs"
echo "======================================="
echo ""

# Try to get the RunPod ID from hostname or environment
POD_ID=$(hostname)
if [ -f /etc/machine-id ]; then
    MACHINE_ID=$(cat /etc/machine-id | head -c 12)
fi

echo "📝 Your pod hostname: $POD_ID"
echo ""
echo "🔗 To access your application on RunPod:"
echo ""
echo "1. In the RunPod web interface, click 'Connect' on your pod"
echo "2. Look for 'HTTP Service' or 'Connect to HTTP [Port]' options"
echo "3. You should expose these ports:"
echo "   - Port 3000 (Frontend/Main App)"
echo "   - Port 8000 (Backend API)"
echo ""
echo "Alternative - Use RunPod Proxy URLs:"
echo "   Frontend: https://${POD_ID}-3000.proxy.runpod.net"
echo "   Backend:  https://${POD_ID}-8000.proxy.runpod.net"
echo ""
echo "💡 If using RunPod's web-based interface:"
echo "   Click the 'Connect' button and select 'Connect to HTTP [3000]'"
echo ""
echo "Services Status:"
lsof -i :3000 -i :8000 2>/dev/null | grep LISTEN | awk '{print "   ✅ Port " $9 " - Listening"}'
echo ""
