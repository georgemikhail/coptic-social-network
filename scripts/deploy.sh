#!/bin/bash

# Coptic Social Network - Production Deployment Script
# Usage: ./scripts/deploy.sh [railway|digitalocean|vps]

set -e

DEPLOYMENT_TYPE=${1:-railway}
DOMAIN=${2:-yourdomain.com}

echo "🚀 Starting Coptic Social Network deployment..."
echo "📋 Deployment type: $DEPLOYMENT_TYPE"
echo "🌐 Domain: $DOMAIN"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if required tools are installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Generate secure secrets
generate_secrets() {
    print_info "Generating secure secrets..."
    
    DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    NEXTAUTH_SECRET=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)
    
    print_status "Secrets generated"
}

# Create production environment file
create_env_file() {
    print_info "Creating production environment file..."
    
    cat > .env.production << EOF
# Production Environment Configuration
# Generated on $(date)

# Database Configuration
POSTGRES_DB=coptic_social_prod
POSTGRES_USER=coptic_admin
POSTGRES_PASSWORD=$DB_PASSWORD
DB_HOST=db
DB_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,*.railway.app,*.digitalocean.app

# Frontend Configuration
NEXTAUTH_URL=https://$DOMAIN
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
BACKEND_URL=https://api.$DOMAIN

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration (Update with your SMTP settings)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@$DOMAIN
EMAIL_HOST_PASSWORD=CHANGE_THIS_EMAIL_PASSWORD

# AWS S3 Configuration (Optional)
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=coptic-social-media
AWS_S3_REGION_NAME=us-east-1

# OAuth Configuration (Update with your OAuth keys)
GOOGLE_CLIENT_ID=your-production-google-client-id
GOOGLE_CLIENT_SECRET=your-production-google-client-secret
FACEBOOK_APP_ID=your-production-facebook-app-id
FACEBOOK_APP_SECRET=your-production-facebook-app-secret

# Domain Configuration
DOMAIN_NAME=$DOMAIN
EOF

    print_status "Production environment file created: .env.production"
    print_warning "Please update OAuth keys and email settings in .env.production"
}

# Railway deployment
deploy_railway() {
    print_info "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    print_info "Logging into Railway..."
    railway login
    
    print_info "Creating Railway project..."
    railway init coptic-social
    
    print_info "Adding PostgreSQL database..."
    railway add postgresql
    
    print_info "Deploying backend service..."
    railway service create backend
    railway service connect backend
    railway variables set DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY"
    railway variables set DEBUG=False
    railway variables set ALLOWED_HOSTS="*.railway.app,$DOMAIN"
    railway up --service backend
    
    print_info "Deploying frontend service..."
    railway service create frontend
    railway service connect frontend
    railway variables set NEXTAUTH_URL="https://$DOMAIN"
    railway variables set NEXTAUTH_SECRET="$NEXTAUTH_SECRET"
    railway up --service frontend
    
    print_status "Railway deployment initiated!"
    print_info "Check your Railway dashboard for deployment status"
}

# VPS deployment
deploy_vps() {
    print_info "Preparing for VPS deployment..."
    
    # Copy production environment
    cp .env.production .env
    
    print_info "Building production images..."
    docker-compose -f docker-compose.prod.yml build
    
    print_info "Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_status "VPS deployment completed!"
    print_info "Your application should be running on ports 80 (HTTP) and 443 (HTTPS)"
}

# Local production test
test_local() {
    print_info "Testing production build locally..."
    
    cp .env.production .env
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    
    print_info "Waiting for services to start..."
    sleep 30
    
    # Test backend health
    if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
        print_status "Backend is healthy"
    else
        print_error "Backend health check failed"
    fi
    
    # Test frontend
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        print_status "Frontend is accessible"
    else
        print_error "Frontend health check failed"
    fi
    
    print_status "Local production test completed"
    print_info "Access your application at http://localhost"
}

# Main deployment logic
main() {
    check_prerequisites
    generate_secrets
    create_env_file
    
    case $DEPLOYMENT_TYPE in
        railway)
            deploy_railway
            ;;
        digitalocean)
            print_info "DigitalOcean deployment requires manual setup using the App Platform"
            print_info "Please follow the guide in PRODUCTION_DEPLOYMENT_GUIDE.md"
            ;;
        vps)
            deploy_vps
            ;;
        test)
            test_local
            ;;
        *)
            print_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            echo "Usage: $0 [railway|digitalocean|vps|test] [domain]"
            exit 1
            ;;
    esac
    
    print_status "Deployment process completed!"
    
    # Display next steps
    echo ""
    echo "🎉 Next Steps:"
    echo "1. Configure your domain DNS settings"
    echo "2. Update OAuth credentials in your environment"
    echo "3. Set up email SMTP configuration"
    echo "4. Test your deployment thoroughly"
    echo "5. Set up monitoring and backups"
    echo ""
    echo "📖 For detailed instructions, see PRODUCTION_DEPLOYMENT_GUIDE.md"
}

# Run main function
main 