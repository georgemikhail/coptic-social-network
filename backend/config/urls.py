"""
URL configuration for Coptic Social Network project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def health_check(request):
    """Health check endpoint for deployment platforms"""
    return JsonResponse({"status": "healthy", "message": "Coptic Social Network API is running"})

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication
    path('api/auth/', include('allauth.urls')),
    
    # API Endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/parishes/', include('apps.parishes.urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/groups/', include('apps.groups.urls')),
    path('api/marketplace/', include('apps.marketplace.urls')),
    path('api/calendar/', include('apps.calendar_events.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 