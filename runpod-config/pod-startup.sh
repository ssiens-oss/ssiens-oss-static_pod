#!/bin/bash
set -e

echo "========================================="
echo "StaticWaves POD Studio - RunPod Engine"
echo "Production Startup Script"
echo "========================================="

# Environment
export NODE_ENV="${NODE_ENV:-production}"
export RUNPOD_POD_ID="${RUNPOD_POD_ID:-local}"
export RUNPOD_GPU_ID="${RUNPOD_GPU_ID:-N/A}"

# Display environment info
echo "Environment: $NODE_ENV"
echo "Pod ID: $RUNPOD_POD_ID"
echo "GPU ID: $RUNPOD_GPU_ID"
echo "Beta Mode: ${BETA_MODE:-true}"
echo ""

# Step 1: Run system optimizations
echo "========================================="
echo "Step 1: System Optimization"
echo "========================================="

if [ -f "/runpod-config/optimize-pod.sh" ]; then
    bash /runpod-config/optimize-pod.sh
else
    echo "Optimization script not found, skipping..."
fi

echo ""

# Step 2: Validate configuration
echo "========================================="
echo "Step 2: Configuration Validation"
echo "========================================="

# Check nginx configuration
if [ -f "/etc/nginx/nginx.conf" ]; then
    echo "Validating nginx configuration..."
    nginx -t

    if [ $? -eq 0 ]; then
        echo "✓ Nginx configuration valid"
    else
        echo "✗ Nginx configuration invalid"
        exit 1
    fi
else
    echo "✗ Nginx configuration not found"
    exit 1
fi

# Check application files
if [ ! -d "/usr/share/nginx/html" ]; then
    echo "✗ Application directory not found"
    exit 1
fi

if [ ! -f "/usr/share/nginx/html/index.html" ]; then
    echo "✗ Application index.html not found"
    exit 1
fi

echo "✓ Application files present"

# Check health endpoint
if [ -f "/usr/share/nginx/html/health.json" ]; then
    echo "✓ Health check endpoint present"
else
    echo "⚠ Health check endpoint not found, creating..."
    cat > /usr/share/nginx/html/health.json << EOF
{
  "status": "healthy",
  "service": "staticwaves-pod-studio",
  "version": "6.0-beta.1",
  "environment": "$NODE_ENV",
  "pod_id": "$RUNPOD_POD_ID",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    echo "✓ Health check endpoint created"
fi

echo ""

# Step 3: Set permissions
echo "========================================="
echo "Step 3: Setting Permissions"
echo "========================================="

mkdir -p /var/log/nginx /var/cache/nginx
chown -R nginx:nginx /var/log/nginx /var/cache/nginx /usr/share/nginx/html || true
echo "✓ Permissions set"

echo ""

# Step 4: Start health monitoring (background)
echo "========================================="
echo "Step 4: Starting Health Monitor"
echo "========================================="

if [ -f "/runpod-config/health-monitor.sh" ]; then
    # Start health monitor in background
    nohup bash /runpod-config/health-monitor.sh monitor > /var/log/health-monitor.log 2>&1 &
    HEALTH_MONITOR_PID=$!
    echo "✓ Health monitor started (PID: $HEALTH_MONITOR_PID)"
else
    echo "⚠ Health monitor script not found"
fi

echo ""

# Step 5: Display startup banner
echo "========================================="
cat << "EOF"
  ____  _        _   _   __        __
 / ___|| |_ __ _| |_(_)__\ \      / /_ ___   _____  ___
 \___ \| __/ _` | __| / __\ \ /\ / / _` \ \ / / _ \/ __|
  ___) | || (_| | |_| \__ \\ V  V / (_| |\ V /  __/\__ \
 |____/ \__\__,_|\__|_|___/ \_/\_/ \__,_| \_/ \___||___/

       POD Studio v6.0-beta.1 - Production Engine
       RunPod Deployment
EOF
echo "========================================="
echo ""

# Step 6: Start nginx
echo "========================================="
echo "Step 6: Starting Nginx Server"
echo "========================================="

# Start nginx in foreground
echo "Starting nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

echo "✓ Nginx started (PID: $NGINX_PID)"

# Wait a moment for nginx to start
sleep 2

# Verify nginx is running
if ps -p $NGINX_PID > /dev/null; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx failed to start"
    exit 1
fi

echo ""

# Step 7: Final health check
echo "========================================="
echo "Step 7: Final Health Check"
echo "========================================="

sleep 2

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health.json || echo "failed")

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✓ Health check passed (HTTP 200)"
else
    echo "⚠ Health check returned: $HEALTH_CHECK"
fi

echo ""

# Step 8: Display access information
echo "========================================="
echo "🚀 Server Ready!"
echo "========================================="
echo ""
echo "Access Information:"
echo "  • Health Check: http://localhost/health.json"
echo "  • Application:  http://localhost/"
echo ""

if [ "$RUNPOD_POD_ID" != "local" ]; then
    echo "  • Public URL: https://${RUNPOD_POD_ID}-80.proxy.runpod.net"
    echo ""
fi

echo "Monitoring:"
echo "  • Health Monitor: Active"
echo "  • Logs: /var/log/nginx/access.log"
echo "  • Errors: /var/log/nginx/error.log"
echo ""
echo "Pod Information:"
echo "  • Pod ID: $RUNPOD_POD_ID"
echo "  • GPU ID: $RUNPOD_GPU_ID"
echo "  • Environment: $NODE_ENV"
echo "  • Beta Mode: ${BETA_MODE:-true}"
echo ""
echo "========================================="

# Keep script running and handle signals
trap 'echo "Shutting down..."; kill $NGINX_PID; exit 0' SIGTERM SIGINT

# Wait for nginx process
wait $NGINX_PID
