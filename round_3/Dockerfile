# PURPOSE: Dockerfile for PARANOID - SBOM Roast Generator
# Using Chainguard images for maximum paranoia (no shell, minimal attack surface)

FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

# Production image - distroless, no shell
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /app/deps /app/deps

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY run.py /app/

# Set Python path to include deps and backend
ENV PYTHONPATH=/app/deps:/app/backend

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Run via run.py which handles import paths
ENTRYPOINT ["python", "/app/run.py"]
