# PURPOSE: Dockerfile for PARANOID - SBOM Roast Generator
# Using Chainguard images for maximum paranoia (no shell, minimal attack surface)
# Pinned to Python 3.12 for wheel compatibility (3.14 lacks pre-built wheels)

FROM cgr.dev/chainguard/python:3.12-dev AS builder

WORKDIR /app

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

# Production image - distroless, no shell
FROM cgr.dev/chainguard/python:3.12

WORKDIR /app

# Copy installed dependencies
COPY --from=builder --chown=nonroot:nonroot /app/deps /app/deps

# Copy application code (chown for nonroot user to write memes)
COPY --chown=nonroot:nonroot backend/ /app/backend/
COPY --chown=nonroot:nonroot frontend/ /app/frontend/
COPY --chown=nonroot:nonroot run.py /app/

# Set Python path to include deps and backend
ENV PYTHONPATH=/app/deps:/app/backend

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Run via run.py which handles import paths
ENTRYPOINT ["python", "/app/run.py"]
