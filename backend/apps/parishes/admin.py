"""
Django admin configuration for Parishes app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Diocese, Parish, ParishEvent


@admin.register(Diocese)
class DioceseAdmin(admin.ModelAdmin):
    """
    Diocese admin configuration
    """
    list_display = ('name', 'bishop_name', 'country', 'parish_count', 'is_active', 'created_at')
    list_filter = ('country', 'is_active', 'created_at')
    search_fields = ('name', 'bishop_name', 'country', 'city')
    filter_horizontal = ('admins',)
    readonly_fields = ('created_at', 'updated_at', 'parish_count')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Bishop Information'), {
            'fields': ('bishop_name', 'bishop_title', 'bishop_photo')
        }),
        (_('Contact Information'), {
            'fields': ('address', 'phone_number', 'email', 'website')
        }),
        (_('Location'), {
            'fields': ('country', 'state_province', 'city')
        }),
        (_('Administration'), {
            'fields': ('admins',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def parish_count(self, obj):
        return obj.parish_count
    parish_count.short_description = 'Number of Parishes'


@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    """
    Parish admin configuration
    """
    list_display = ('name', 'diocese', 'priest_name', 'member_count', 'is_active', 'created_at')
    list_filter = ('diocese', 'is_active', 'enable_donations', 'allow_public_posts', 'created_at')
    search_fields = ('name', 'priest_name', 'diocese__name', 'address')
    filter_horizontal = ('admins',)
    readonly_fields = ('created_at', 'updated_at', 'member_count', 'location_display')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'diocese', 'is_active')
        }),
        (_('Clergy Information'), {
            'fields': ('priest_name', 'priest_title', 'priest_photo', 'deacons')
        }),
        (_('Contact Information'), {
            'fields': ('address', 'phone_number', 'email', 'website')
        }),
        (_('Media'), {
            'fields': ('cover_image', 'logo')
        }),
        (_('Services'), {
            'fields': ('service_schedule',)
        }),
        (_('Social Media'), {
            'fields': ('facebook_page', 'youtube_channel', 'whatsapp_group', 'telegram_group')
        }),
        (_('Location Details'), {
            'fields': ('latitude', 'longitude', 'timezone', 'location_display')
        }),
        (_('Settings'), {
            'fields': ('allow_public_posts', 'allow_member_posts', 'require_admin_approval')
        }),
        (_('Donations'), {
            'fields': ('enable_donations', 'donation_goal', 'donation_description')
        }),
        (_('Administration'), {
            'fields': ('admins',)
        }),
        (_('Statistics'), {
            'fields': ('member_count',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Number of Members'
    
    def location_display(self, obj):
        return obj.location_display
    location_display.short_description = 'Location'


@admin.register(ParishEvent)
class ParishEventAdmin(admin.ModelAdmin):
    """
    Parish Event admin configuration
    """
    list_display = ('title', 'parish', 'event_type', 'start_datetime', 'is_public', 'requires_registration', 'created_by')
    list_filter = ('event_type', 'is_public', 'requires_registration', 'is_all_day', 'start_datetime', 'parish')
    search_fields = ('title', 'description', 'parish__name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        (_('Event Information'), {
            'fields': ('title', 'description', 'parish', 'event_type')
        }),
        (_('Timing'), {
            'fields': ('start_datetime', 'end_datetime', 'is_all_day')
        }),
        (_('Details'), {
            'fields': ('location', 'event_image')
        }),
        (_('Registration'), {
            'fields': ('requires_registration', 'max_attendees', 'registration_deadline')
        }),
        (_('Visibility'), {
            'fields': ('is_public',)
        }),
        (_('Creator'), {
            'fields': ('created_by',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parish', 'created_by') 