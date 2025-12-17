# PURPOSE: Dockerfile for PARANOID - SBOM Roast Generator
# Using Chainguard images: dev for building, distroless for runtime

# === BUILDER STAGE ===
# Chainguard dev image has pip and build tools
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /build

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install dependencies - let pip build from source if needed
# Set environment to allow forward compatibility builds
ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

RUN pip install --no-cache-dir -r requirements.txt --target /build/deps

# === RUNTIME STAGE ===
# Chainguard distroless: no shell, minimal attack surface, maximum paranoia
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy only the wheel artifacts from builder (no build tools)
COPY --from=builder --chown=nonroot:nonroot /build/deps /app/deps

# Copy application code (chown for nonroot user to write memes)
COPY --chown=nonroot:nonroot backend/ /app/backend/
COPY --chown=nonroot:nonroot frontend/ /app/frontend/
COPY --chown=nonroot:nonroot run.py /app/

# Set Python path to include deps and backend
ENV PYTHONPATH=/app/deps:/app/backend

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Chainguard runs as nonroot by default (UID 65532)
# No shell available - maximum security

# Run via run.py which handles import paths
ENTRYPOINT ["python", "/app/run.py"]
