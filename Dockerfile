# Build stage - install dependencies
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/deps

# Production stage - minimal secure image
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/deps /app/deps

# Copy application source
COPY src/ /app/

# Set Python path to include dependencies
ENV PYTHONPATH=/app/deps

# Expose the application port
EXPOSE 8080

# Run the application
ENTRYPOINT ["python", "app.py"]
