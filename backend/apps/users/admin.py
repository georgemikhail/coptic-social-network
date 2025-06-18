"""
Django admin configuration for Users app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with additional fields
    """
    list_display = ('email', 'first_name', 'last_name', 'parish', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'is_staff', 'parish__diocese', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'parish__name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'bio', 'profile_picture')
        }),
        (_('Social Links'), {
            'fields': ('linkedin_url', 'facebook_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        (_('Parish Information'), {
            'fields': ('parish',)
        }),
        (_('Privacy Settings'), {
            'fields': ('profile_visibility',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'email_verified', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'last_login_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'parish'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parish', 'parish__diocese')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin
    """
    list_display = ('user', 'email_notifications', 'push_notifications', 'parish_notifications', 'created_at')
    list_filter = ('email_notifications', 'push_notifications', 'parish_notifications', 'show_email', 'show_phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Custom Fields'), {'fields': ('custom_fields',)}),
        (_('Notification Preferences'), {
            'fields': ('email_notifications', 'push_notifications', 'parish_notifications')
        }),
        (_('Privacy Preferences'), {
            'fields': ('show_email', 'show_phone', 'show_social_links')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 