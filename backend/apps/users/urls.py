"""
URL patterns for Users app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/password-reset/', views.password_reset_request, name='password-reset'),
    path('auth/password-reset/confirm/', views.password_reset_confirm, name='password-reset-confirm'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Parishes for registration
    path('parishes/', views.list_parishes, name='parishes-list'),
    
    # User management
    path('', include(router.urls)),
] 