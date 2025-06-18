#!/bin/bash

# Coptic Social Network - Development Preview Script
# This script starts the application using Docker so you can preview it in Cursor

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Coptic Social Network Development Preview...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker is not running. Please start Docker Desktop first.${NC}"
    exit 1
fi

# Build and start services
echo -e "${BLUE}📦 Building Docker containers...${NC}"
docker-compose -f docker-compose.dev.yml build

echo -e "${BLUE}🗄️  Starting database...${NC}"
docker-compose -f docker-compose.dev.yml up -d db-dev

# Wait for database to be ready
echo -e "${BLUE}⏳ Waiting for database to be ready...${NC}"
sleep 10

echo -e "${BLUE}🔧 Running database migrations...${NC}"
docker-compose -f docker-compose.dev.yml run --rm backend-dev python manage.py migrate

echo -e "${BLUE}👤 Creating superuser (if needed)...${NC}"
docker-compose -f docker-compose.dev.yml run --rm backend-dev python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@copticsocial.org').exists():
    User.objects.create_superuser('admin@copticsocial.org', 'admin123')
    print('Superuser created: admin@copticsocial.org / admin123')
else:
    print('Superuser already exists')
"

echo -e "${BLUE}📊 Loading sample data...${NC}"
if [ -f "backend/fixtures/sample_groups.json" ]; then
    docker-compose -f docker-compose.dev.yml run --rm backend-dev python manage.py loaddata fixtures/sample_groups.json
else
    echo -e "${YELLOW}⚠️  Sample data file not found, skipping...${NC}"
fi

echo -e "${BLUE}🌐 Starting all services...${NC}"
docker-compose -f docker-compose.dev.yml up -d

echo -e "${GREEN}✅ Development environment is starting up!${NC}"
echo ""
echo -e "${GREEN}🎉 Your Coptic Social Network is now running:${NC}"
echo -e "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "   Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "   Admin Panel: ${BLUE}http://localhost:8000/admin/${NC}"
echo ""
echo -e "${GREEN}👤 Login Credentials:${NC}"
echo -e "   Email: admin@copticsocial.org"
echo -e "   Password: admin123"
echo ""
echo -e "${BLUE}📋 Available Commands:${NC}"
echo -e "   View logs: ${YELLOW}docker-compose -f docker-compose.dev.yml logs -f${NC}"
echo -e "   Stop services: ${YELLOW}docker-compose -f docker-compose.dev.yml down${NC}"
echo -e "   Restart: ${YELLOW}./scripts/dev-preview.sh${NC}"
echo ""
echo -e "${GREEN}🔍 Open http://localhost:3000 in Cursor's browser or your web browser!${NC}" 