"""
Admin interface for Groups app - Phase 4
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import (
    Group, GroupMembership, GroupJoinRequest, 
    GroupInvitation, GroupPost, GroupEvent
)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin interface for Group model"""
    
    list_display = [
        'name', 'group_type', 'privacy', 'parish_link', 
        'member_count', 'post_count', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'group_type', 'privacy', 'is_active', 'is_featured',
        'parish__diocese', 'created_at'
    ]
    search_fields = ['name', 'description', 'parish__name', 'created_by__email']
    readonly_fields = ['id', 'member_count', 'post_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'name', 'description', 'group_type', 'privacy')
        }),
        (_('Relationships'), {
            'fields': ('parish', 'created_by')
        }),
        (_('Media'), {
            'fields': ('cover_image', 'icon'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': (
                'is_active', 'is_featured', 'allow_member_posts', 
                'require_approval', 'max_members'
            )
        }),
        (_('Statistics'), {
            'fields': ('member_count', 'post_count'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_groups', 'deactivate_groups', 'feature_groups', 'unfeature_groups']
    
    def parish_link(self, obj):
        """Link to parish admin page"""
        url = reverse('admin:parishes_parish_change', args=[obj.parish.pk])
        return format_html('<a href="{}">{}</a>', url, obj.parish.name)
    parish_link.short_description = _('Parish')
    
    def activate_groups(self, request, queryset):
        """Bulk activate groups"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} groups activated.')
    activate_groups.short_description = _('Activate selected groups')
    
    def deactivate_groups(self, request, queryset):
        """Bulk deactivate groups"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} groups deactivated.')
    deactivate_groups.short_description = _('Deactivate selected groups')
    
    def feature_groups(self, request, queryset):
        """Bulk feature groups"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} groups featured.')
    feature_groups.short_description = _('Feature selected groups')
    
    def unfeature_groups(self, request, queryset):
        """Bulk unfeature groups"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} groups unfeatured.')
    unfeature_groups.short_description = _('Unfeature selected groups')


class GroupMembershipInline(admin.TabularInline):
    """Inline for group memberships"""
    model = GroupMembership
    extra = 0
    readonly_fields = ['id', 'joined_at', 'updated_at']
    fields = ['user', 'role', 'is_active', 'notifications_enabled', 'joined_at']


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """Admin interface for GroupMembership model"""
    
    list_display = [
        'user_link', 'group_link', 'role', 'is_active', 
        'notifications_enabled', 'joined_at'
    ]
    list_filter = ['role', 'is_active', 'notifications_enabled', 'joined_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'group__name', 'group__parish__name'
    ]
    readonly_fields = ['id', 'joined_at', 'updated_at']
    
    fieldsets = (
        (_('Membership Details'), {
            'fields': ('id', 'group', 'user', 'role')
        }),
        (_('Settings'), {
            'fields': ('is_active', 'notifications_enabled')
        }),
        (_('Timestamps'), {
            'fields': ('joined_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['promote_to_admin', 'promote_to_moderator', 'demote_to_member']
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
    user_link.short_description = _('User')
    
    def group_link(self, obj):
        """Link to group admin page"""
        url = reverse('admin:groups_group_change', args=[obj.group.pk])
        return format_html('<a href="{}">{}</a>', url, obj.group.name)
    group_link.short_description = _('Group')
    
    def promote_to_admin(self, request, queryset):
        """Promote members to admin"""
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} members promoted to admin.')
    promote_to_admin.short_description = _('Promote to Admin')
    
    def promote_to_moderator(self, request, queryset):
        """Promote members to moderator"""
        updated = queryset.update(role='moderator')
        self.message_user(request, f'{updated} members promoted to moderator.')
    promote_to_moderator.short_description = _('Promote to Moderator')
    
    def demote_to_member(self, request, queryset):
        """Demote to regular member"""
        updated = queryset.update(role='member')
        self.message_user(request, f'{updated} users demoted to member.')
    demote_to_member.short_description = _('Demote to Member')


@admin.register(GroupJoinRequest)
class GroupJoinRequestAdmin(admin.ModelAdmin):
    """Admin interface for GroupJoinRequest model"""
    
    list_display = [
        'user_link', 'group_link', 'status', 'created_at', 
        'processed_by_link', 'processed_at'
    ]
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'group__name', 'message'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Request Details'), {
            'fields': ('id', 'group', 'user', 'status', 'message')
        }),
        (_('Processing'), {
            'fields': ('processed_by', 'processed_at', 'admin_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
    user_link.short_description = _('User')
    
    def group_link(self, obj):
        """Link to group admin page"""
        url = reverse('admin:groups_group_change', args=[obj.group.pk])
        return format_html('<a href="{}">{}</a>', url, obj.group.name)
    group_link.short_description = _('Group')
    
    def processed_by_link(self, obj):
        """Link to processed by user admin page"""
        if obj.processed_by:
            url = reverse('admin:users_user_change', args=[obj.processed_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.processed_by.full_name)
        return '-'
    processed_by_link.short_description = _('Processed By')
    
    def approve_requests(self, request, queryset):
        """Approve join requests"""
        updated = queryset.filter(status='pending').update(
            status='approved',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests approved.')
    approve_requests.short_description = _('Approve selected requests')
    
    def reject_requests(self, request, queryset):
        """Reject join requests"""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests rejected.')
    reject_requests.short_description = _('Reject selected requests')


@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    """Admin interface for GroupInvitation model"""
    
    list_display = [
        'invited_user_link', 'group_link', 'invited_by_link',
        'is_accepted', 'is_declined', 'created_at', 'responded_at'
    ]
    list_filter = ['is_accepted', 'is_declined', 'created_at', 'responded_at']
    search_fields = [
        'invited_user__email', 'invited_user__first_name', 'invited_user__last_name',
        'group__name', 'invited_by__email'
    ]
    readonly_fields = ['id', 'created_at', 'responded_at', 'expires_at']
    
    fieldsets = (
        (_('Invitation Details'), {
            'fields': ('id', 'group', 'invited_user', 'invited_by', 'message')
        }),
        (_('Status'), {
            'fields': ('is_accepted', 'is_declined')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'responded_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def invited_user_link(self, obj):
        """Link to invited user admin page"""
        url = reverse('admin:users_user_change', args=[obj.invited_user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.invited_user.full_name)
    invited_user_link.short_description = _('Invited User')
    
    def group_link(self, obj):
        """Link to group admin page"""
        url = reverse('admin:groups_group_change', args=[obj.group.pk])
        return format_html('<a href="{}">{}</a>', url, obj.group.name)
    group_link.short_description = _('Group')
    
    def invited_by_link(self, obj):
        """Link to inviter admin page"""
        url = reverse('admin:users_user_change', args=[obj.invited_by.pk])
        return format_html('<a href="{}">{}</a>', url, obj.invited_by.full_name)
    invited_by_link.short_description = _('Invited By')


@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    """Admin interface for GroupPost model"""
    
    list_display = [
        'title_or_content', 'author_link', 'group_link', 
        'is_announcement', 'is_pinned', 'is_approved', 
        'likes_count', 'comments_count', 'published_at'
    ]
    list_filter = [
        'is_announcement', 'is_pinned', 'is_approved', 'is_deleted',
        'group__group_type', 'published_at'
    ]
    search_fields = ['title', 'content', 'author__email', 'group__name']
    readonly_fields = [
        'id', 'likes_count', 'comments_count', 
        'created_at', 'updated_at', 'published_at'
    ]
    
    fieldsets = (
        (_('Post Details'), {
            'fields': ('id', 'group', 'author', 'title', 'content')
        }),
        (_('Settings'), {
            'fields': ('is_announcement', 'is_pinned', 'is_approved', 'is_deleted')
        }),
        (_('Engagement'), {
            'fields': ('likes_count', 'comments_count'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_posts', 'pin_posts', 'unpin_posts', 'mark_as_announcement']
    
    def title_or_content(self, obj):
        """Display title or truncated content"""
        if obj.title:
            return obj.title
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    title_or_content.short_description = _('Content')
    
    def author_link(self, obj):
        """Link to author admin page"""
        url = reverse('admin:users_user_change', args=[obj.author.pk])
        return format_html('<a href="{}">{}</a>', url, obj.author.full_name)
    author_link.short_description = _('Author')
    
    def group_link(self, obj):
        """Link to group admin page"""
        url = reverse('admin:groups_group_change', args=[obj.group.pk])
        return format_html('<a href="{}">{}</a>', url, obj.group.name)
    group_link.short_description = _('Group')
    
    def approve_posts(self, request, queryset):
        """Approve posts"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} posts approved.')
    approve_posts.short_description = _('Approve selected posts')
    
    def pin_posts(self, request, queryset):
        """Pin posts"""
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} posts pinned.')
    pin_posts.short_description = _('Pin selected posts')
    
    def unpin_posts(self, request, queryset):
        """Unpin posts"""
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} posts unpinned.')
    unpin_posts.short_description = _('Unpin selected posts')
    
    def mark_as_announcement(self, request, queryset):
        """Mark as announcement"""
        updated = queryset.update(is_announcement=True)
        self.message_user(request, f'{updated} posts marked as announcements.')
    mark_as_announcement.short_description = _('Mark as announcement')


@admin.register(GroupEvent)
class GroupEventAdmin(admin.ModelAdmin):
    """Admin interface for GroupEvent model"""
    
    list_display = [
        'title', 'group_link', 'start_datetime', 'end_datetime',
        'location', 'attendee_count', 'max_attendees', 'is_public'
    ]
    list_filter = [
        'is_public', 'is_all_day', 'require_rsvp',
        'group__group_type', 'start_datetime'
    ]
    search_fields = ['title', 'description', 'location', 'group__name']
    readonly_fields = ['id', 'attendee_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Event Details'), {
            'fields': ('id', 'group', 'created_by', 'title', 'description', 'location')
        }),
        (_('Timing'), {
            'fields': ('start_datetime', 'end_datetime', 'is_all_day')
        }),
        (_('Settings'), {
            'fields': ('max_attendees', 'require_rsvp', 'is_public')
        }),
        (_('Statistics'), {
            'fields': ('attendee_count',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def group_link(self, obj):
        """Link to group admin page"""
        url = reverse('admin:groups_group_change', args=[obj.group.pk])
        return format_html('<a href="{}">{}</a>', url, obj.group.name)
    group_link.short_description = _('Group')


# Add inlines to Group admin
GroupAdmin.inlines = [GroupMembershipInline] 