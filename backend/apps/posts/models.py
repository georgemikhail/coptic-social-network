"""
Models for Posts app - Social Media Functionality
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator


class PostVisibility(models.TextChoices):
    """Post visibility options"""
    PUBLIC = 'public', 'Public'
    PARISH_ONLY = 'parish_only', 'Parish Only'
    FRIENDS_ONLY = 'friends_only', 'Friends Only'
    PRIVATE = 'private', 'Private'


class PostType(models.TextChoices):
    """Post type options"""
    TEXT = 'text', 'Text'
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Video'
    AUDIO = 'audio', 'Audio'
    DOCUMENT = 'document', 'Document'
    LINK = 'link', 'Link'
    EVENT = 'event', 'Event'
    ANNOUNCEMENT = 'announcement', 'Announcement'


class ReactionType(models.TextChoices):
    """Reaction types"""
    LIKE = 'like', '👍 Like'
    LOVE = 'love', '❤️ Love'
    PRAY = 'pray', '🙏 Pray'
    AMEN = 'amen', '✝️ Amen'
    SUPPORT = 'support', '🤝 Support'
    CELEBRATE = 'celebrate', '🎉 Celebrate'


def post_media_upload_path(instance, filename):
    """Generate upload path for post media"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"posts/{instance.post.author.parish.id}/{instance.post.id}/{filename}"


class Post(models.Model):
    """
    Main Post model for social media content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # Content
    content = models.TextField(blank=True)
    post_type = models.CharField(
        max_length=20,
        choices=PostType.choices,
        default=PostType.TEXT
    )
    
    # Visibility and targeting
    visibility = models.CharField(
        max_length=20,
        choices=PostVisibility.choices,
        default=PostVisibility.PARISH_ONLY
    )
    target_parish = models.ForeignKey(
        'parishes.Parish',
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
        help_text="Parish this post is targeted to. If null, uses author's parish."
    )
    
    # Metadata
    is_announcement = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_posts'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'posts_post'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['target_parish', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
            models.Index(fields=['is_approved', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.full_name}: {self.content[:50]}..."
    
    @property
    def parish(self):
        """Get the target parish or author's parish"""
        return self.target_parish or self.author.parish
    
    def save(self, *args, **kwargs):
        # Set published_at on first save if approved
        if not self.published_at and self.is_approved:
            self.published_at = timezone.now()
        
        # Set target_parish to author's parish if not specified
        if not self.target_parish:
            self.target_parish = self.author.parish
            
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Soft delete the post"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class PostMedia(models.Model):
    """
    Media attachments for posts
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    
    # File information
    file = models.FileField(upload_to=post_media_upload_path)
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    content_type = models.CharField(max_length=100)
    
    # Media type
    media_type = models.CharField(
        max_length=20,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('document', 'Document'),
        ]
    )
    
    # Metadata
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    alt_text = models.CharField(max_length=500, blank=True, help_text="For accessibility")
    
    # Media-specific fields
    duration = models.DurationField(null=True, blank=True, help_text="For audio/video")
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts_media'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.post.author.full_name} - {self.filename}"


class Comment(models.Model):
    """
    Comments on posts
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # Comment content
    content = models.TextField()
    
    # Nested comments
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts_comment'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.full_name}: {self.content[:50]}..."
    
    @property
    def is_reply(self):
        return self.parent is not None


class Reaction(models.Model):
    """
    Reactions to posts and comments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    
    # Generic foreign key for reactions on different models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reaction_type = models.CharField(
        max_length=20,
        choices=ReactionType.choices,
        default=ReactionType.LIKE
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts_reaction'
        unique_together = ['user', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} {self.reaction_type} {self.content_object}"


class Share(models.Model):
    """
    Post shares
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    
    # Share with additional comment
    comment = models.TextField(blank=True)
    
    # Share visibility
    visibility = models.CharField(
        max_length=20,
        choices=PostVisibility.choices,
        default=PostVisibility.PARISH_ONLY
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts_share'
        unique_together = ['post', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} shared {self.post}"


class PostTag(models.Model):
    """
    Tags for posts
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    is_official = models.BooleanField(default=False)  # Official parish tags
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts_tag'
        ordering = ['name']
    
    def __str__(self):
        return f"#{self.name}"


class PostTagging(models.Model):
    """
    Many-to-many relationship between posts and tags
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_tags')
    tag = models.ForeignKey(PostTag, on_delete=models.CASCADE, related_name='tagged_posts')
    tagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_taggings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts_tagging'
        unique_together = ['post', 'tag']
    
    def __str__(self):
        return f"{self.post} tagged with {self.tag}"


class Feed(models.Model):
    """
    Custom feeds for organizing posts
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Feed ownership
    parish = models.ForeignKey(
        'parishes.Parish',
        on_delete=models.CASCADE,
        related_name='feeds',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_feeds'
    )
    
    # Feed settings
    is_public = models.BooleanField(default=True)
    is_official = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Feed filters
    allowed_post_types = models.JSONField(
        default=list,
        help_text="List of allowed post types. Empty means all types allowed."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts_feed'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FeedPost(models.Model):
    """
    Posts included in custom feeds
    """
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='feed_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='in_feeds')
    
    # Ordering within feed
    order = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_additions'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts_feed_post'
        unique_together = ['feed', 'post']
        ordering = ['-is_pinned', 'order', '-added_at']
    
    def __str__(self):
        return f"{self.post} in {self.feed}" 