# PURPOSE: Multi-platform Python backend container using Chainguard base image
# Build stage - use -dev variant for pip
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

# Production stage - minimal runtime
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /app/deps /app/deps

# Copy application code
COPY . .

# Set Python path to include deps
ENV PYTHONPATH=/app/deps

# Expose port
EXPOSE 8000

# Run uvicorn server (full path since no shell in distroless)
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
