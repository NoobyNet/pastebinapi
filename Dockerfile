# Multi-stage build for Pastebin API Wrapper
# Stage 1: Build stage with uv for dependency installation
FROM python:3.14-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Stage 2: Runtime stage
FROM python:3.14-slim

# Metadata labels
LABEL org.opencontainers.image.title="pastebinapi"
LABEL org.opencontainers.image.description="FastAPI-based wrapper for the Pastebin API"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.vendor="noobynet"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/noobynet/pastebinapi"
LABEL org.opencontainers.image.documentation="https://github.com/noobynet/pastebinapi/blob/main/README.md"
LABEL maintainer="noobynet"

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY config.py .
COPY exceptions.py .
COPY main.py .
COPY models/ ./models/
COPY routers/ ./routers/
COPY services/ ./services/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
