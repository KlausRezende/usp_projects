#!/bin/bash

echo "🚀 Starting Docker containers..."
chmod -R 777 docker-volume/db-data/ openmetadata-docker/docker-volume/db-data/
docker compose -f docker-compose.yaml up -d

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo "🗄️ Creating customer_db database..."
docker exec postgres_simple psql -U airflow -d airflow -c "CREATE DATABASE customer_db;"

echo "✅ Pipeline setup complete!"
echo "📊 Access Airflow at: http://localhost:8081 (admin/admin)"
echo "🔍 Access OpenMetadata at: http://localhost:8585"
