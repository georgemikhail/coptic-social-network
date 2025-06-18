# 🚀 Coptic Social Network - Production Deployment Guide

## 🎯 Overview

This guide will help you deploy the Coptic Social Network to production with a custom domain. We'll cover multiple deployment options from simple to enterprise-level.

---

## 🏗️ Deployment Options

### **Option 1: Railway (Recommended - Easiest)**
- **Cost**: $5-20/month
- **Setup Time**: 15 minutes
- **Best For**: Quick deployment, automatic scaling

### **Option 2: DigitalOcean App Platform**
- **Cost**: $12-25/month
- **Setup Time**: 30 minutes
- **Best For**: Managed deployment with good performance

### **Option 3: AWS (Enterprise)**
- **Cost**: $20-100+/month
- **Setup Time**: 1-2 hours
- **Best For**: Full control, enterprise features

### **Option 4: VPS (Advanced)**
- **Cost**: $10-50/month
- **Setup Time**: 2-3 hours
- **Best For**: Maximum control, custom configuration

---

## 🚂 Option 1: Railway Deployment (Recommended)

### **Step 1: Prepare for Railway**

First, let's create production-ready configuration:

```bash
# 1. Create production environment file
cp env.example .env.production

# 2. Update the production environment
```

Create `.env.production`:
```env
# Database (Railway will provide this)
DATABASE_URL=postgresql://user:password@host:port/database

# Django Configuration
DJANGO_SECRET_KEY=your-super-secret-production-key-generate-new-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,*.railway.app

# Frontend Configuration
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=your-production-nextauth-secret
BACKEND_URL=https://your-backend.railway.app

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://your-frontend.railway.app
```

### **Step 2: Deploy to Railway**

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
railway login
```

2. **Initialize Railway Project**:
```bash
railway init
railway link
```

3. **Deploy Backend**:
```bash
# Create backend service
railway service create backend
railway service connect backend

# Set environment variables
railway variables set DJANGO_SECRET_KEY="your-secret-key"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS="*.railway.app,yourdomain.com"

# Deploy
railway up --service backend
```

4. **Deploy Frontend**:
```bash
# Create frontend service
railway service create frontend
railway service connect frontend

# Set environment variables
railway variables set NEXTAUTH_URL="https://yourdomain.com"
railway variables set BACKEND_URL="https://your-backend.railway.app"

# Deploy
railway up --service frontend
```

5. **Add PostgreSQL Database**:
```bash
railway add postgresql
```

### **Step 3: Domain Configuration**

1. **Get Railway URLs**:
   - Backend: `https://your-backend.railway.app`
   - Frontend: `https://your-frontend.railway.app`

2. **Configure Custom Domain**:
   - Go to Railway dashboard
   - Select your frontend service
   - Add custom domain: `yourdomain.com`
   - Railway will provide DNS records

3. **DNS Setup** (at your domain registrar):
```
Type: CNAME
Name: @
Value: your-frontend.railway.app

Type: CNAME  
Name: api
Value: your-backend.railway.app
```

---

## 🌊 Option 2: DigitalOcean App Platform

### **Step 1: Prepare App Spec**

Create `.do/app.yaml`:
```yaml
name: coptic-social
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/coptic-social
    branch: main
  run_command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DJANGO_SECRET_KEY
    value: your-secret-key
  - key: DEBUG
    value: "False"
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}

- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/coptic-social
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NEXTAUTH_URL
    value: https://yourdomain.com
  - key: BACKEND_URL
    value: ${backend.PUBLIC_URL}

databases:
- name: db
  engine: PG
  version: "13"
  size_slug: db-s-dev-database

domains:
- domain: yourdomain.com
  type: PRIMARY
```

### **Step 2: Deploy**
```bash
# Install doctl
brew install doctl  # macOS
# or download from DigitalOcean

# Authenticate
doctl auth init

# Deploy
doctl apps create --spec .do/app.yaml
```

---

## ☁️ Option 3: AWS Deployment (Enterprise)

### **Step 1: AWS Infrastructure Setup**

Create `aws/docker-compose.prod.yml`:
```yaml
version: '3.9'

services:
  backend:
    image: your-account.dkr.ecr.region.amazonaws.com/coptic-social-backend:latest
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DEBUG=False
      - DATABASE_URL=${RDS_DATABASE_URL}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    ports:
      - "8000:8000"

  frontend:
    image: your-account.dkr.ecr.region.amazonaws.com/coptic-social-frontend:latest
    environment:
      - NEXTAUTH_URL=${NEXTAUTH_URL}
      - BACKEND_URL=${BACKEND_URL}
    ports:
      - "3000:3000"
```

### **Step 2: Build and Push Images**
```bash
# Build images
docker build -f Dockerfile.backend -t coptic-social-backend .
docker build -f Dockerfile.frontend -t coptic-social-frontend .

# Tag for ECR
docker tag coptic-social-backend:latest your-account.dkr.ecr.region.amazonaws.com/coptic-social-backend:latest
docker tag coptic-social-frontend:latest your-account.dkr.ecr.region.amazonaws.com/coptic-social-frontend:latest

# Push to ECR
aws ecr get-login-password --region region | docker login --username AWS --password-stdin your-account.dkr.ecr.region.amazonaws.com
docker push your-account.dkr.ecr.region.amazonaws.com/coptic-social-backend:latest
docker push your-account.dkr.ecr.region.amazonaws.com/coptic-social-frontend:latest
```

### **Step 3: ECS Deployment**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name coptic-social

# Deploy using ECS task definitions
aws ecs run-task --cluster coptic-social --task-definition coptic-social-task
```

---

## 🖥️ Option 4: VPS Deployment (Advanced)

### **Step 1: Server Setup**
```bash
# Connect to your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Nginx
apt install nginx -y
```

### **Step 2: Deploy Application**
```bash
# Clone repository
git clone https://github.com/your-username/coptic-social.git
cd coptic-social

# Create production environment
cp env.example .env
# Edit .env with production values

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### **Step 3: Nginx Configuration**

Create `/etc/nginx/sites-available/coptic-social`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /path/to/static/files/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/media/files/;
        expires 30d;
    }
}
```

### **Step 4: SSL Certificate**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Enable Nginx
systemctl enable nginx
systemctl restart nginx
```

---

## 🌐 Domain Configuration Guide

### **Step 1: Choose a Domain**
- **Recommended registrars**: Namecheap, Google Domains, Cloudflare
- **Suggested domains**: 
  - `copticsocial.org`
  - `yourparish.social`
  - `copticnetwork.com`

### **Step 2: DNS Configuration**

**For Railway/DigitalOcean/AWS:**
```
Type: A
Name: @
Value: [Platform-provided IP]

Type: CNAME
Name: www
Value: yourdomain.com

Type: CNAME
Name: api
Value: [Backend URL]
```

**For VPS:**
```
Type: A
Name: @
Value: [Your VPS IP]

Type: A
Name: www
Value: [Your VPS IP]
```

### **Step 3: Email Setup (Optional)**
```
Type: MX
Name: @
Value: [Email provider MX records]
Priority: 10
```

---

## 🔒 Production Security Checklist

### **Environment Variables**
- [ ] Generate new `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up proper `CORS_ALLOWED_ORIGINS`
- [ ] Enable SSL redirects

### **Database Security**
- [ ] Use strong database passwords
- [ ] Enable database SSL
- [ ] Configure database backups
- [ ] Restrict database access

### **Application Security**
- [ ] Enable HTTPS everywhere
- [ ] Configure security headers
- [ ] Set up rate limiting
- [ ] Enable CSRF protection
- [ ] Configure session security

---

## 📊 Production Monitoring

### **Health Checks**
Create `scripts/health-check.sh`:
```bash
#!/bin/bash
# Backend health check
curl -f http://localhost:8000/api/health/ || exit 1

# Frontend health check  
curl -f http://localhost:3000/ || exit 1

echo "All services healthy"
```

### **Logging Setup**
```python
# backend/config/settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/coptic-social/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 🚀 Quick Start (Railway - Fastest)

**For immediate deployment:**

1. **Sign up for Railway**: https://railway.app
2. **Connect GitHub repository**
3. **Deploy backend and frontend services**
4. **Add PostgreSQL database**
5. **Configure custom domain**
6. **Update DNS records**

**Total time**: 15-30 minutes
**Cost**: ~$10-20/month

---

## 🎯 Next Steps After Deployment

1. **Test all functionality**
2. **Set up monitoring and alerts**
3. **Configure automated backups**
4. **Set up CI/CD pipeline**
5. **Plan scaling strategy**
6. **Invite beta users from parishes**

---

## 🆘 Troubleshooting

### **Common Issues**
- **Build failures**: Check Node.js/Python versions
- **Database connection**: Verify DATABASE_URL
- **CORS errors**: Check CORS_ALLOWED_ORIGINS
- **SSL issues**: Verify certificate configuration
- **Static files**: Configure static file serving

### **Support Resources**
- Railway docs: https://docs.railway.app
- DigitalOcean docs: https://docs.digitalocean.com
- AWS ECS docs: https://aws.amazon.com/ecs/

---

**🎉 Your Coptic Social Network will be live at `https://yourdomain.com`!**

*Choose the deployment option that best fits your technical expertise and budget. Railway is recommended for quick deployment, while VPS gives you maximum control.* 