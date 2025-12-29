# Multi-stage build for StaticWaves POD Studio
# Stage 1: Build the application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production --ignore-scripts && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production server with nginx
FROM nginx:alpine

# Install dependencies for RunPod engine
RUN apk add --no-cache \
    supervisor \
    curl \
    bash \
    jq \
    procps \
    coreutils

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy RunPod configuration and scripts
COPY runpod-config /runpod-config
RUN chmod +x /runpod-config/*.sh

# Copy startup scripts
COPY runpod-start.sh /usr/local/bin/runpod-start.sh
RUN chmod +x /usr/local/bin/runpod-start.sh

# Create log directory
RUN mkdir -p /var/log && touch /var/log/health-monitor.log

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health.json || exit 1

# Use RunPod engine startup script
CMD ["/runpod-config/pod-startup.sh"]
