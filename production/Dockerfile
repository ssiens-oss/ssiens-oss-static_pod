# Production POD Engine Dockerfile

FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Install production dependencies only
COPY package*.json ./
RUN npm ci --production --ignore-scripts

# Copy built files from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/services ./services
COPY --from=builder /app/production ./production

# Create storage directory
RUN mkdir -p /app/storage

# Set environment
ENV NODE_ENV=production

# Expose API port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"

# Run the application
CMD ["node", "production/examples/worker-pool-api.ts"]
