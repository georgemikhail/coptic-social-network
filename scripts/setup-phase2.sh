#!/bin/bash

# Phase 2 Setup Script for Coptic Social Network
# This script sets up the development environment for Phase 2: User and Parish Core

set -e

echo "🚀 Setting up Coptic Social Network - Phase 2: User and Parish Core"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_section "Phase 2 Development Setup"

# Build and start containers
print_status "Building Docker containers..."
docker-compose down -v 2>/dev/null || true
docker-compose build

print_status "Starting services..."
docker-compose up -d db redis

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Run migrations
print_section "Setting up Database"
print_status "Running Django migrations..."
docker-compose run --rm backend python manage.py makemigrations users
docker-compose run --rm backend python manage.py makemigrations parishes
docker-compose run --rm backend python manage.py migrate

# Load sample data
print_status "Loading sample parishes and dioceses..."
docker-compose run --rm backend python manage.py loaddata apps/parishes/fixtures/initial_data.json

# Create superuser
print_section "Creating Admin User"
print_status "Creating Django superuser..."
print_warning "Please enter admin credentials when prompted:"
docker-compose run --rm backend python manage.py createsuperuser

# Install frontend dependencies
print_section "Setting up Frontend"
print_status "Installing Node.js dependencies..."
docker-compose run --rm frontend npm install

# Start all services
print_section "Starting Application"
print_status "Starting all services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 15

# Check service health
print_section "Service Health Check"

# Check backend
if curl -s http://localhost:8000/api/docs/ > /dev/null; then
    print_status "✅ Backend API is running at http://localhost:8000"
else
    print_warning "⚠️  Backend may still be starting..."
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    print_status "✅ Frontend is running at http://localhost:3000"
else
    print_warning "⚠️  Frontend may still be starting..."
fi

print_section "Phase 2 Setup Complete!"

echo "
🎉 Coptic Social Network - Phase 2 is ready!

📱 Frontend Application: http://localhost:3000
🔧 Backend API: http://localhost:8000/api/docs/
⚙️  Django Admin: http://localhost:8000/admin/

📚 Phase 2 Features:
• User registration with parish selection
• JWT authentication with automatic refresh
• User profile management
• Parish and diocese data
• Beautiful, responsive UI

🧪 Sample Data Loaded:
• 3 Dioceses (Los Angeles, New York, Sydney)
• 3 Parishes with realistic information
• Ready for user registration testing

🔍 Quick Test:
1. Visit http://localhost:3000/auth/login
2. Create a new account or login
3. Explore the user dashboard

📖 Documentation:
• API Documentation: http://localhost:8000/api/docs/
• Phase 2 Status: See PHASE_2_STATUS.md
• Setup Guide: See README.md

🚧 Next Phase:
Ready to proceed to Phase 3: Media and Social Feeds

Happy coding! 🚀
"

print_status "Use 'docker-compose logs -f' to view live logs"
print_status "Use 'docker-compose down' to stop all services" 