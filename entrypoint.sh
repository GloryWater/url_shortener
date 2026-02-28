#!/bin/sh
set -e

echo "Waiting for database to be ready..."
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  sleep 0.1
done
echo "Database is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
