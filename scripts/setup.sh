#!/bin/bash

# Coptic Social Network - Development Setup Script
# Phase 1: Platform Architecture

set -e

echo "🏛️ Setting up Coptic Social Network Development Environment"
echo "================================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please update it with your configuration."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/logs
mkdir -p backend/media
mkdir -p backend/staticfiles
mkdir -p frontend/public/images
mkdir -p frontend/public/patterns

echo "🐳 Building Docker containers..."
docker-compose build

echo "🗄️ Setting up database..."
docker-compose up -d db
sleep 5

echo "🔄 Running database migrations..."
docker-compose run --rm backend python manage.py migrate

echo "👑 Creating superuser (optional)..."
read -p "Do you want to create a Django superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose run --rm backend python manage.py createsuperuser
fi

echo "📦 Installing frontend dependencies..."
cd frontend
if command -v npm &> /dev/null; then
    npm install
else
    echo "⚠️ npm not found. You'll need to install frontend dependencies manually."
fi
cd ..

echo "🎉 Setup complete!"
echo ""
echo "To start the development environment:"
echo "  docker-compose up"
echo ""
echo "Application URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/api/docs/"
echo "  Django Admin: http://localhost:8000/admin/"
echo ""
echo "Phase 1 (Platform Architecture) is now ready for development!"
echo "Next: Implement Phase 2 (User and Parish Core)" 