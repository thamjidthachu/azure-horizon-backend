FROM python:3.12.3-slim AS base

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    vim \
    libpq-dev \
    python3-dev \
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

# Create non-root user first
RUN useradd -m appuser

# Create directories and set permissions
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/staticfiles && \
    chmod -R 755 /app/media && \
    chmod +x /app/entrypoint.sh

USER appuser

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
