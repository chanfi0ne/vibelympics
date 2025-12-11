# PURPOSE: Chainguard-based Python backend - minimal attack surface, near-zero CVEs
# Build stage - use dev variant that includes pip
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage - minimal Chainguard Python image
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy installed packages from builder
# Chainguard Python uses /home/nonroot/.local for user packages
COPY --from=builder /home/nonroot/.local /home/nonroot/.local

# Copy application code
COPY --chown=nonroot:nonroot . .

# Set Python path to include user packages
ENV PATH="/home/nonroot/.local/bin:$PATH"
ENV PYTHONPATH="/home/nonroot/.local/lib/python3.12/site-packages"

# Expose port
EXPOSE 8000

# Expose port
ENV PORT=8000

# Run uvicorn server - exec form (Chainguard has no shell)
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]
