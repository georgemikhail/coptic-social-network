# 🚀 Phase 3 API Access Guide

## Quick Start Testing

### 🔐 Authentication
```bash
# Login and get token
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"john@stmarkla.org","password":"password123"}' \
  http://localhost:8000/api/users/auth/login/
```

### 📝 Test Posts API
```bash
# Get all posts (requires token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/posts/posts/

# Get personalized feed
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/posts/feed/
```

### 🙏 Test Reactions (Coptic Features)
```bash
# Add a "pray" reaction
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reaction_type":"pray"}' \
  http://localhost:8000/api/posts/posts/550e8400-e29b-41d4-a716-446655440001/react/

# Add an "amen" reaction  
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reaction_type":"amen"}' \
  http://localhost:8000/api/posts/posts/550e8400-e29b-41d4-a716-446655440002/react/
```

## 👥 Test Users Available

| Email | Password | Parish | Role |
|-------|----------|--------|------|
| admin@copticsocial.com | admin123 | - | Superuser |
| john@stmarkla.org | password123 | St. Mark LA | Member |
| mary@stmarynj.org | password123 | St. Mary NJ | Member |
| peter@stmarysydney.org | password123 | St. Mary Sydney | Member |

## 🏢 Sample Data Loaded

### Dioceses & Parishes
- **Diocese of Los Angeles** → St. Mark Coptic Orthodox Church
- **Diocese of New York** → St. Mary and St. Athanasius Church  
- **Diocese of Sydney** → St. Mary and St. Mina Church

### Sample Posts
- 4 posts with various types (announcements, events, text)
- Realistic parish content (services, Bible study, meetings)
- Proper engagement metrics and parish scoping

## 🔗 Available Endpoints

### Core Posts
- `GET /api/posts/posts/` - List posts
- `POST /api/posts/posts/` - Create post
- `GET /api/posts/posts/{id}/` - Get post details
- `PATCH /api/posts/posts/{id}/` - Update post
- `DELETE /api/posts/posts/{id}/` - Delete post

### Engagement
- `POST /api/posts/posts/{id}/react/` - Add reaction
- `DELETE /api/posts/posts/{id}/unreact/` - Remove reaction  
- `POST /api/posts/posts/{id}/share/` - Share post

### Comments
- `GET /api/posts/posts/{id}/comments/` - Get comments
- `POST /api/posts/posts/{id}/comments/` - Add comment

### Discovery
- `GET /api/posts/feed/` - Personalized feed
- `GET /api/posts/trending/` - Trending posts
- `GET /api/posts/stats/` - Statistics

## 🎯 Reaction Types Available
- `like` - Standard like
- `love` - Love reaction
- `pray` - 🙏 Prayer reaction (Coptic-specific)
- `amen` - ✝️ Amen reaction (Coptic-specific)  
- `support` - Support reaction
- `celebrate` - Celebration reaction

## ⚡ Services Running
- **Backend API**: http://localhost:8000
- **Database**: PostgreSQL on port 5432
- **Admin Interface**: http://localhost:8000/admin (admin@copticsocial.com / admin123)
- **API Docs**: http://localhost:8000/api/docs/

## 🏆 Phase 3 Status: COMPLETE ✅ 