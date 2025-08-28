#!/bin/sh

# Exit on error
set -e

echo "Waiting for PostgreSQL..."

# Function to test PostgreSQL connection
postgres_ready() {
  python << END
import sys
import psycopg2
import os
from decouple import config

try:
    psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT', default=5432)
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready with a timeout
TIMEOUT=300  # 5 minutes timeout
ELAPSED=0
until postgres_ready; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "Timeout reached waiting for PostgreSQL"
        exit 1
    fi
done

echo "PostgreSQL is up - executing command"

# Create directories if they don't exist (with proper permissions)
mkdir -p /app/staticfiles
mkdir -p /app/media
chmod 755 /app/staticfiles
chmod 755 /app/media

# Run migrations
python manage.py migrate --noinput

# Collect static files 
python manage.py collectstatic --noinput --clear

# Start server
exec python manage.py runserver "0.0.0.0:${PORT:-8000}"
