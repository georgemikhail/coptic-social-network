"""
URL patterns for Parishes app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'parishes'

urlpatterns = [
    # Will be implemented in Phase 2
    path('', lambda request: None, name='placeholder'),
] 