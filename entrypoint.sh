#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput
echo "Applied database migrations..."

echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Collected static files..."

echo "Starting Gunicorn server..."
exec gunicorn cyclone.wsgi:application --bind 0.0.0.0:8000 --workers 2
