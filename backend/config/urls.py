"""
URL configuration for Coptic Social Network project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication (handled by users app)
    # path('api/auth/', include('dj_rest_auth.urls')),
    
    # App APIs
    path('api/users/', include('apps.users.urls')),
    path('api/parishes/', include('apps.parishes.urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/groups/', include('apps.groups.urls')),
    path('api/marketplace/', include('apps.marketplace.urls')),
    path('api/events/', include('apps.calendar_events.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 