# PURPOSE: Dockerfile for PARANOID using Chainguard Wolfi base
# Zero CVE base image with Python 3.12

# === BUILDER STAGE ===
# Wolfi-base with build tools for pip install
FROM cgr.dev/chainguard/wolfi-base AS builder

# Install Python 3.12 and pip
RUN apk add --no-cache \
    python-3.12 \
    py3.12-pip \
    py3.12-pillow

WORKDIR /build

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
# Note: pillow comes from wolfi packages, skip in pip
RUN pip install --no-cache-dir \
    --target /build/deps \
    --ignore-installed pillow \
    -r requirements.txt

# === RUNTIME STAGE ===
# Minimal Wolfi image - no shell in production for security
FROM cgr.dev/chainguard/wolfi-base

# Install only runtime Python (no pip, no build tools)
RUN apk add --no-cache \
    python-3.12-base \
    py3.12-pillow \
    ca-certificates-bundle \
    && rm -rf /var/cache/apk/*

# Wolfi base already has nonroot user (UID 65532)
# No need to create - just use it

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder --chown=nonroot:nonroot /build/deps /app/deps

# Copy application code
COPY --chown=nonroot:nonroot backend/ /app/backend/
COPY --chown=nonroot:nonroot frontend/ /app/frontend/
COPY --chown=nonroot:nonroot run.py /app/

# Create memes directory
RUN mkdir -p /app/backend/static/memes && chown -R nonroot:nonroot /app

# Switch to non-root user
USER nonroot

# Set Python path
ENV PYTHONPATH=/app/deps:/app/backend
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the app
CMD ["python3.12", "/app/run.py"]
