#!/bin/sh
set -e

echo "========================================="
echo "StaticWaves POD Studio - RunPod Startup"
echo "========================================="

# Display environment info
echo "Pod ID: ${RUNPOD_POD_ID:-not-set}"
echo "GPU ID: ${RUNPOD_GPU_ID:-not-set}"
echo "Node Environment: ${NODE_ENV:-production}"
echo "Beta Mode: ${BETA_MODE:-true}"

# Create necessary directories
mkdir -p /var/log/nginx
mkdir -p /var/cache/nginx

# Set proper permissions
chown -R nginx:nginx /var/log/nginx
chown -R nginx:nginx /var/cache/nginx
chown -R nginx:nginx /usr/share/nginx/html

# Display startup banner
cat << "EOF"
  ____  _        _   _   __        __
 / ___|| |_ __ _| |_(_)__\ \      / /_ ___   _____  ___
 \___ \| __/ _` | __| / __\ \ /\ / / _` \ \ / / _ \/ __|
  ___) | || (_| | |_| \__ \\ V  V / (_| |\ V /  __/\__ \
 |____/ \__\__,_|\__|_|___/ \_/\_/ \__,_| \_/ \___||___/

       POD Studio v6.0 - Beta Deployment Ready
EOF

# Validate nginx configuration
echo ""
echo "Validating nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration failed validation"
    exit 1
fi

# Start nginx
echo ""
echo "Starting nginx server..."
nginx -g "daemon off;" &
NGINX_PID=$!

echo "✓ Nginx started with PID: $NGINX_PID"
echo ""
echo "========================================="
echo "Server is ready!"
echo "Health check: http://localhost/health.json"
echo "Application: http://localhost/"
echo "========================================="

# Wait for nginx process
wait $NGINX_PID
