#!/bin/bash
set -e

# Migrations and collectstatic are handled by the 'migrate' init container.
# This script only starts the application server.

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3}
