#!/bin/bash

echo "🐳 Starting ICE Locator Docker Services"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the services
echo "🏗️ Building and starting services..."
docker-compose up -d --build

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is ready
echo "🔍 Checking PostgreSQL health..."
until docker-compose exec postgres pg_isready -U ice_user -d ice_locator; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Install required Python packages for the populator
echo "📦 Installing Python dependencies..."
pip install psycopg2-binary geopy

# Populate the database
echo "📊 Populating database with comprehensive facility data..."
python populate_docker_db.py

echo "🎉 Docker services are ready!"
echo "🌐 Heatmap API: http://localhost:8000"
echo "📋 API Documentation: http://localhost:8000/docs"
echo "🗄️ PostgreSQL: localhost:5432 (ice_user/ice_password/ice_locator)"

