# PURPOSE: Dockerfile for PARANOID - SBOM Roast Generator
# Using python:3.12-slim for consistent builds across architectures
# Running as non-root for security

# === BUILDER STAGE ===
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install dependencies - pre-built wheels available for all platforms
RUN pip install --no-cache-dir -r requirements.txt --target /build/deps

# === RUNTIME STAGE ===
# Same Python version as builder for wheel compatibility
FROM python:3.12-slim

# Create non-root user (security hardening)
RUN useradd --create-home --uid 65532 --shell /usr/sbin/nologin nonroot

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /build/deps /app/deps

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY run.py /app/

# Create memes directory and set ownership
RUN mkdir -p /app/backend/static/memes && chown -R nonroot:nonroot /app

# Switch to non-root user
USER nonroot

# Set Python path
ENV PYTHONPATH=/app/deps:/app/backend

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "/app/run.py"]
