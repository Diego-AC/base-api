#!/bin/sh

set -e

export FLASK_CONFIG=production
export FLASK_APP=app:create_app

echo "Running database migrations..."
flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5050} \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    "app:create_app()"
