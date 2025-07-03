# 🚀 Railway Deployment Guide for Coptic Social Network Backend

## 📋 Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- This repository pushed to GitHub

## 🔧 Step-by-Step Railway Deployment

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `coptic-social-network`
3. Make it **Public** (easier for deployment)
4. **Don't** initialize with README (we have existing code)
5. Copy the repository URL

### Step 2: Push Code to GitHub
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/coptic-social-network.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway

#### 3.1 Create Railway Account
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign in with GitHub

#### 3.2 Create New Project
1. Click "Deploy from GitHub repo"
2. Select your `coptic-social-network` repository
3. Railway will detect it's a Python project

#### 3.3 Configure Root Directory
**IMPORTANT**: Set the root directory to `/backend`
1. In project settings → "Root Directory"
2. Set to: `backend`
3. Save changes

#### 3.4 Add PostgreSQL Database
1. In your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Railway will automatically create and link the database

### Step 4: Set Environment Variables

In Railway dashboard → Settings → Variables, add:

```
DJANGO_SECRET_KEY=your-super-secret-key-change-this-in-production-make-it-50-chars-long
DEBUG=False
FRONTEND_URL=https://frontend-silk-five-31.vercel.app
ALLOWED_HOSTS=.railway.app
```

**Important**: Railway automatically provides:
- `DATABASE_URL` (from PostgreSQL service)
- `PORT` (for the web server)

### Step 5: Deploy & Verify

1. Railway will automatically deploy
2. You'll get a URL like: `https://your-project-name.up.railway.app`
3. Test endpoints:
   - Health check: `https://your-backend-url/health/`
   - API docs: `https://your-backend-url/api/docs/`
   - Admin: `https://your-backend-url/admin/`

## 🔄 After Deployment

### Update Frontend
1. Go to Vercel dashboard
2. Update environment variable:
   ```
   BACKEND_URL=https://your-backend-url.up.railway.app
   ```
3. Redeploy frontend

### Create Django Superuser
In Railway dashboard → Deployments → Select latest → View Logs:
```bash
python manage.py createsuperuser
```

## 🛠️ Configuration Files Included

- ✅ `railway.json` - Railway-specific configuration
- ✅ `nixpacks.toml` - Build optimization
- ✅ `Procfile` - Process commands
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies
- ✅ Production-ready Django settings

## 🌐 Expected URLs

After deployment:
- **Backend API**: `https://your-project-name.up.railway.app`
- **Health Check**: `https://your-project-name.up.railway.app/health/`
- **API Documentation**: `https://your-project-name.up.railway.app/api/docs/`
- **Admin Panel**: `https://your-project-name.up.railway.app/admin/`

## 🔧 Troubleshooting

### Common Issues:
1. **Build fails**: Check that root directory is set to `backend`
2. **Database errors**: Ensure PostgreSQL service is linked
3. **Static files**: Railway handles this automatically with our configuration
4. **CORS errors**: Frontend URL is configured in settings

### Useful Railway Commands:
- View logs: Railway dashboard → Deployments → View Logs
- Environment variables: Settings → Variables
- Database access: PostgreSQL service → Connect

## ✅ Production Checklist

- [ ] GitHub repository created and code pushed
- [ ] Railway project created with `/backend` root directory
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Deployment successful
- [ ] Health endpoint responding
- [ ] Frontend updated with backend URL
- [ ] API documentation accessible 