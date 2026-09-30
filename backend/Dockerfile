FROM python:3.11-slim

LABEL maintainer="Swaraj Karle"
LABEL description="ChurnSense AI — FastAPI Backend"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create artifact directories
RUN mkdir -p /data/uploads /data/models /data/logs

# Non-root user for security
RUN useradd --create-home --shell /bin/bash churnsense
RUN chown -R churnsense:churnsense /app /data
USER churnsense

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
