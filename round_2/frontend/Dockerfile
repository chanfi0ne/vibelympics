# PURPOSE: Multi-stage Docker build using Chainguard base images for minimal attack surface
# Build stage - use Node for building
FROM cgr.dev/chainguard/node:latest-dev AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage - Chainguard nginx
FROM cgr.dev/chainguard/nginx:latest

# Copy nginx configuration (Chainguard nginx uses /etc/nginx/nginx.conf)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 8080

# Chainguard nginx runs as non-root on port 8080 by default
