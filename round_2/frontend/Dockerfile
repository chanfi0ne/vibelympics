# PURPOSE: Chainguard-based frontend build - minimal attack surface, near-zero CVEs
# Build stage - use dev variant that includes npm
FROM cgr.dev/chainguard/node:latest-dev AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage - minimal Chainguard nginx image
FROM cgr.dev/chainguard/nginx:latest

# Copy built application to nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration - replace the full nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 8080

# Chainguard nginx runs on port 8080 by default as nonroot
# No CMD needed - image has default entrypoint
