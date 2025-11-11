#!/bin/bash
# Production startup script for File Gallery Viewer

set -e

echo "=== File Gallery Viewer - Production Startup ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default values
export FLASK_ENV=${FLASK_ENV:-production}
export DATA_DIR=${DATA_DIR:-$(pwd)/data}
export PORT=${PORT:-9000}
export GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
export GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
export PYTHONPATH=$(pwd)/backend

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

echo ""
echo "Configuration:"
echo "  Environment: $FLASK_ENV"
echo "  Data Directory: $DATA_DIR"
echo "  Port: $PORT"
echo "  Workers: $GUNICORN_WORKERS"
echo "  Timeout: ${GUNICORN_TIMEOUT}s"
echo ""

# Start gunicorn
echo "Starting File Gallery Viewer with Gunicorn..."
echo ""

exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers $GUNICORN_WORKERS \
    --timeout $GUNICORN_TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --chdir backend \
    app:app
