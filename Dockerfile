# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY tests/ tests/

# Create directories
RUN mkdir -p /opt/lef/archive \
    && mkdir -p /opt/lef/data \
    && mkdir -p /opt/lef/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LEF_ARCHIVE_PATH=/opt/lef/archive
ENV LEF_DATA_PATH=/opt/lef/data
ENV LEF_LOG_PATH=/opt/lef/logs
ENV LEF_LOG_LEVEL=INFO
ENV LEF_METRICS_INTERVAL=60
ENV LEF_HEALTH_CHECK_INTERVAL=30
ENV LEF_PORT=8000

# Expose port
EXPOSE ${LEF_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${LEF_PORT}/health || exit 1

# Run the application
CMD ["python", "-m", "lef.main"] 