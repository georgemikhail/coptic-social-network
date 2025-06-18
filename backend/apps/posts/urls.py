"""
URL patterns for Posts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Main router
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='posts')

# Nested router for comments
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', views.CommentViewSet, basename='post-comments')

app_name = 'posts'

urlpatterns = [
    # Main endpoints
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    
    # Feed endpoints
    path('feed/', views.get_feed, name='feed'),
    path('trending/', views.get_trending_posts, name='trending'),
    
    # Tags
    path('tags/', views.PostTagListView.as_view(), name='tags'),
    
    # Statistics
    path('stats/', views.get_post_stats, name='stats'),
] 