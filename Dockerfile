# Use Python 3.12.3 slim image as base
FROM python:3.12.3-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    vim \
    libpq-dev \
    python-dev \
    python3-psycopg2 \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]