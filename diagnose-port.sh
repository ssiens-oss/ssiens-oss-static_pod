#!/bin/bash
# Port diagnostic script

echo "🔍 POD Pipeline Port Diagnostic"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1. Repository Location:"
echo "   Working directory: $(pwd)"
echo "   REPO_ROOT: ${REPO_ROOT:-not set}"
echo ""

echo "2. Script Locations:"
echo "   pod command: $(which pod 2>/dev/null || echo 'not found')"
echo "   run-pod-pipeline.sh: $(find / -name 'run-pod-pipeline.sh' 2>/dev/null | head -3)"
echo ""

echo "3. Running Processes:"
ps aux | grep -E "uvicorn|http.server" | grep -v grep | while read line; do
    echo "   $line"
done
echo ""

echo "4. Port Binding Check:"
for port in 8099 18099 8088; do
    if command -v ss >/dev/null 2>&1; then
        binding=$(ss -tulnp 2>/dev/null | grep ":$port " || echo "Not listening")
    elif command -v netstat >/dev/null 2>&1; then
        binding=$(netstat -tulnp 2>/dev/null | grep ":$port " || echo "Not listening")
    else
        binding=$(lsof -i :$port 2>/dev/null || echo "Not listening")
    fi
    echo "   Port $port: $binding"
done
echo ""

echo "5. Checking run-pod-pipeline.sh for port configuration:"
if [ -f "./run-pod-pipeline.sh" ]; then
    echo "   Found in current directory:"
    grep -n "port.*809" ./run-pod-pipeline.sh || echo "   No port 809X found"
fi
if [ -f "/home/user/ssiens-oss-static_pod/run-pod-pipeline.sh" ]; then
    echo "   Found in /home/user/ssiens-oss-static_pod:"
    grep -n "port.*809" /home/user/ssiens-oss-static_pod/run-pod-pipeline.sh || echo "   No port 809X found"
fi
if [ -f "/workspace/ssiens-oss-static_pod/run-pod-pipeline.sh" ]; then
    echo "   Found in /workspace/ssiens-oss-static_pod:"
    grep -n "port.*809" /workspace/ssiens-oss-static_pod/run-pod-pipeline.sh || echo "   No port 809X found"
fi
echo ""

echo "6. Environment Variables:"
env | grep -i port | while read line; do
    echo "   $line"
done || echo "   No PORT-related env vars"
echo ""

echo "7. Uvicorn Config Check:"
find /workspace /home/user -name "uvicorn.conf*" -o -name ".env" 2>/dev/null | while read file; do
    echo "   Found: $file"
    grep -i port "$file" 2>/dev/null
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
