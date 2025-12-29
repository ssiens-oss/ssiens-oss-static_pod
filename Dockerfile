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

# Install supervisor for process management
RUN apk add --no-cache supervisor curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create health check endpoint
RUN echo '{"status":"healthy","service":"staticwaves-pod-studio"}' > /usr/share/nginx/html/health.json

# Copy startup script
COPY runpod-start.sh /usr/local/bin/runpod-start.sh
RUN chmod +x /usr/local/bin/runpod-start.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health.json || exit 1

# Use startup script
CMD ["/usr/local/bin/runpod-start.sh"]
