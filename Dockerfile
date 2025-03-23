# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Create LEF directories
RUN mkdir -p /root/.lef/logs /root/.lef/data /root/.lef/state

# Set environment variables
ENV PYTHONPATH=/app
ENV LEF_ENV=production

# Expose ports
EXPOSE 8000

# Run the supervisor
CMD ["python", "-m", "src.lef.supervisor"] 