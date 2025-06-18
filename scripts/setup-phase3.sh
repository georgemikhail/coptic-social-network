#!/bin/bash

# Phase 3: Media and Social Feeds Setup Script
# This script sets up the social media functionality including posts, comments, reactions, and feeds

echo "🚀 Setting up Phase 3: Media and Social Feeds..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")/.."

echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if database is ready
echo "🔍 Checking database connection..."
docker-compose exec -T backend python manage.py check --database default || {
    echo "❌ Database connection failed. Please check your configuration."
    exit 1
}

# Install new dependencies
echo "📚 Installing new dependencies..."
docker-compose exec -T backend pip install -r requirements.txt

# Run migrations for posts app
echo "🗄️ Running database migrations for posts..."
docker-compose exec -T backend python manage.py makemigrations posts
docker-compose exec -T backend python manage.py migrate

# Load sample posts data
echo "📝 Loading sample posts data..."
docker-compose exec -T backend python manage.py loaddata apps/posts/fixtures/sample_posts.json

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

# Check if services are healthy
echo "🏥 Checking service health..."

# Backend health check
backend_status=$(docker-compose exec -T backend python manage.py check 2>&1)
if [ $? -eq 0 ]; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service health check failed:"
    echo "$backend_status"
fi

# Database health check
db_status=$(docker-compose exec -T backend python -c "
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Database connection successful')
" 2>&1)

if [[ $db_status == *"successful"* ]]; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed:"
    echo "$db_status"
fi

# Frontend health check (if accessible)
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️ Frontend might still be starting up"
fi

echo ""
echo "🎉 Phase 3: Media and Social Feeds setup complete!"
echo ""
echo "📊 Phase 3 Features Implemented:"
echo "   ✅ Social Media Posts with text, images, videos, and documents"
echo "   ✅ Comments and nested replies system"
echo "   ✅ Reactions (Like, Love, Pray, Amen, Support, Celebrate)"
echo "   ✅ Post sharing and visibility controls"
echo "   ✅ Parish-specific and public feeds"
echo "   ✅ Post tags and categorization"
echo "   ✅ Media upload and processing"
echo "   ✅ Real-time engagement metrics"
echo "   ✅ Content moderation and approval system"
echo "   ✅ Feed customization and filtering"
echo ""
echo "🔗 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Admin Panel: http://localhost:8000/admin"
echo "   API Documentation: http://localhost:8000/api/docs"
echo ""
echo "🌟 New API Endpoints:"
echo "   Posts Feed: GET /api/posts/feed/"
echo "   Create Post: POST /api/posts/posts/"
echo "   React to Post: POST /api/posts/posts/{id}/react/"
echo "   Add Comment: POST /api/posts/posts/{id}/comments/"
echo "   Post Statistics: GET /api/posts/stats/"
echo "   Trending Posts: GET /api/posts/trending/"
echo ""
echo "📱 Sample Data Loaded:"
echo "   • 5 sample posts from different parishes"
echo "   • Mix of announcements, events, and community updates"
echo "   • Realistic engagement metrics"
echo ""
echo "🔧 Next Steps:"
echo "   1. Visit http://localhost:3000/feed to see the social feed"
echo "   2. Create new posts and test reactions"
echo "   3. Try commenting and engaging with content"
echo "   4. Explore the admin panel for content moderation"
echo ""
echo "⭐ Ready for Phase 4: Community Groups and Advanced Features!"

# Show running containers
echo ""
echo "🐳 Running containers:"
docker-compose ps 