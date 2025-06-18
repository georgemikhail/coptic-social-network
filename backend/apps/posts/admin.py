"""
Admin configuration for Posts app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Post, PostMedia, Comment, Reaction, Share, PostTag, 
    PostTagging, Feed, FeedPost
)


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'colored_name', 'is_official', 'posts_count', 'created_at']
    list_filter = ['is_official', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['posts_count', 'created_at']
    
    def colored_name(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">#{}</span>',
            obj.color,
            obj.name
        )
    colored_name.short_description = 'Tag'
    
    def posts_count(self, obj):
        return obj.tagged_posts.count()
    posts_count.short_description = 'Posts Count'


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0
    readonly_fields = ['file_size', 'content_type', 'media_type', 'is_processed']
    fields = ['file', 'filename', 'title', 'description', 'alt_text', 'media_type', 'file_size']


class PostTaggingInline(admin.TabularInline):
    model = PostTagging
    extra = 0
    readonly_fields = ['tagged_by', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'author', 'content_preview', 'post_type', 'visibility', 
        'parish', 'engagement_info', 'status_info', 'created_at'
    ]
    list_filter = [
        'post_type', 'visibility', 'is_announcement', 'is_pinned', 
        'is_featured', 'is_approved', 'is_deleted', 'created_at'
    ]
    search_fields = ['content', 'author__first_name', 'author__last_name', 'author__email']
    readonly_fields = [
        'id', 'likes_count', 'comments_count', 'shares_count', 
        'created_at', 'updated_at', 'published_at', 'parish'
    ]
    inlines = [PostMediaInline, PostTaggingInline]
    
    fieldsets = (
        ('Content', {
            'fields': ('author', 'content', 'post_type', 'target_parish')
        }),
        ('Visibility & Settings', {
            'fields': ('visibility', 'is_announcement', 'is_pinned', 'is_featured')
        }),
        ('Moderation', {
            'fields': ('requires_approval', 'is_approved', 'approved_by', 'approved_at')
        }),
        ('Engagement', {
            'fields': ('likes_count', 'comments_count', 'shares_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def engagement_info(self, obj):
        return format_html(
            '👍 {} | 💬 {} | 🔄 {}',
            obj.likes_count,
            obj.comments_count,
            obj.shares_count
        )
    engagement_info.short_description = 'Engagement'
    
    def status_info(self, obj):
        status_parts = []
        if obj.is_announcement:
            status_parts.append('📢 Announcement')
        if obj.is_pinned:
            status_parts.append('📌 Pinned')
        if obj.is_featured:
            status_parts.append('⭐ Featured')
        if not obj.is_approved:
            status_parts.append('⏳ Pending')
        if obj.is_deleted:
            status_parts.append('🗑️ Deleted')
        
        return ' | '.join(status_parts) if status_parts else '✅ Normal'
    status_info.short_description = 'Status'
    
    def parish(self, obj):
        return obj.target_parish.name if obj.target_parish else 'No Parish'
    parish.short_description = 'Parish'
    
    actions = ['approve_posts', 'feature_posts', 'pin_posts', 'soft_delete_posts']
    
    def approve_posts(self, request, queryset):
        updated = queryset.update(is_approved=True, approved_by=request.user)
        self.message_user(request, f'{updated} posts approved.')
    approve_posts.short_description = 'Approve selected posts'
    
    def feature_posts(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts featured.')
    feature_posts.short_description = 'Feature selected posts'
    
    def pin_posts(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} posts pinned.')
    pin_posts.short_description = 'Pin selected posts'
    
    def soft_delete_posts(self, request, queryset):
        for post in queryset:
            post.soft_delete()
        self.message_user(request, f'{queryset.count()} posts soft deleted.')
    soft_delete_posts.short_description = 'Soft delete selected posts'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post_link', 'content_preview', 'parent_info', 'likes_count', 'status_info', 'created_at']
    list_filter = ['is_approved', 'is_deleted', 'created_at']
    search_fields = ['content', 'author__first_name', 'author__last_name', 'post__content']
    readonly_fields = ['id', 'likes_count', 'created_at', 'updated_at']
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.post)[:50])
    post_link.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def parent_info(self, obj):
        if obj.parent:
            return format_html('↳ Reply to: {}', obj.parent.content[:30])
        return '💬 Main Comment'
    parent_info.short_description = 'Type'
    
    def status_info(self, obj):
        if obj.is_deleted:
            return '🗑️ Deleted'
        elif not obj.is_approved:
            return '⏳ Pending'
        else:
            return '✅ Approved'
    status_info.short_description = 'Status'


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'reaction_type', 'content_object_info', 'created_at']
    list_filter = ['reaction_type', 'content_type', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['id', 'created_at']
    
    def content_object_info(self, obj):
        return f"{obj.content_type.model}: {str(obj.content_object)[:50]}"
    content_object_info.short_description = 'Content'


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post_link', 'visibility', 'comment_preview', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'post__content', 'comment']
    readonly_fields = ['id', 'created_at']
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.post)[:50])
    post_link.short_description = 'Post'
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment or 'No comment'
    comment_preview.short_description = 'Share Comment'


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parish', 'created_by', 'posts_count', 'feed_type', 'created_at']
    list_filter = ['is_public', 'is_official', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['id', 'posts_count', 'created_at', 'updated_at']
    
    def posts_count(self, obj):
        return obj.feed_posts.count()
    posts_count.short_description = 'Posts Count'
    
    def feed_type(self, obj):
        types = []
        if obj.is_official:
            types.append('🏛️ Official')
        if obj.is_featured:
            types.append('⭐ Featured')
        if obj.is_public:
            types.append('🌍 Public')
        else:
            types.append('🔒 Private')
        
        return ' | '.join(types)
    feed_type.short_description = 'Type'


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_link', 'filename', 'media_type', 'file_size_display', 'is_processed', 'created_at']
    list_filter = ['media_type', 'is_processed', 'created_at']
    search_fields = ['filename', 'title', 'description', 'post__content']
    readonly_fields = ['id', 'file_size', 'content_type', 'created_at']
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.post)[:50])
    post_link.short_description = 'Post'
    
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'File Size' 