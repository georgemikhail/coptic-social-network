"""
Groups models for Coptic Social Network - Phase 4
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class GroupType(models.TextChoices):
    """Types of groups available in the system"""
    MINISTRY = 'ministry', _('Ministry')
    COMMITTEE = 'committee', _('Committee')
    INTEREST = 'interest', _('Interest Group')
    AGE_BASED = 'age_based', _('Age-based Group')
    STUDY = 'study', _('Study Group')
    SERVICE = 'service', _('Service Group')
    PRAYER = 'prayer', _('Prayer Group')
    SOCIAL = 'social', _('Social Group')


class GroupPrivacy(models.TextChoices):
    """Privacy levels for groups"""
    PUBLIC = 'public', _('Public')
    PARISH_ONLY = 'parish_only', _('Parish Members Only')
    PRIVATE = 'private', _('Private')
    INVITE_ONLY = 'invite_only', _('Invite Only')


class GroupRole(models.TextChoices):
    """Roles within a group"""
    ADMIN = 'admin', _('Administrator')
    MODERATOR = 'moderator', _('Moderator')
    MEMBER = 'member', _('Member')


class JoinRequestStatus(models.TextChoices):
    """Status of join requests"""
    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')


class Group(models.Model):
    """
    Main Group model for community groups, ministries, committees, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    group_type = models.CharField(
        _('group type'),
        max_length=20,
        choices=GroupType.choices,
        default=GroupType.INTEREST
    )
    privacy = models.CharField(
        _('privacy'),
        max_length=20,
        choices=GroupPrivacy.choices,
        default=GroupPrivacy.PARISH_ONLY
    )
    
    # Relationships
    parish = models.ForeignKey(
        'parishes.Parish',
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name=_('parish')
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name=_('created by')
    )
    members = models.ManyToManyField(
        'users.User',
        through='GroupMembership',
        related_name='community_groups',
        verbose_name=_('members')
    )
    
    # Media and settings
    cover_image = models.ImageField(
        _('cover image'),
        upload_to='group_covers/',
        blank=True,
        null=True
    )
    icon = models.ImageField(
        _('icon'),
        upload_to='group_icons/',
        blank=True,
        null=True
    )
    
    # Group settings
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    allow_member_posts = models.BooleanField(_('allow member posts'), default=True)
    require_approval = models.BooleanField(_('require approval to join'), default=False)
    
    # Limits and metrics
    member_count = models.PositiveIntegerField(_('member count'), default=0)
    max_members = models.PositiveIntegerField(
        _('maximum members'),
        null=True,
        blank=True,
        help_text=_('Leave empty for unlimited members')
    )
    post_count = models.PositiveIntegerField(_('post count'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parish', '-created_at']),
            models.Index(fields=['group_type', 'is_active']),
            models.Index(fields=['privacy', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.parish.name})"
    
    @property
    def is_full(self):
        """Check if group has reached maximum capacity"""
        if self.max_members is None:
            return False
        return self.member_count >= self.max_members
    
    def can_user_join(self, user):
        """Check if a user can join this group"""
        if not self.is_active:
            return False
        if self.is_full:
            return False
        if user.parish != self.parish and self.privacy != GroupPrivacy.PUBLIC:
            return False
        return True
    
    def get_user_role(self, user):
        """Get user's role in this group"""
        try:
            membership = self.memberships.get(user=user, is_active=True)
            return membership.role
        except GroupMembership.DoesNotExist:
            return None


class GroupMembership(models.Model):
    """
    Through model for Group-User relationship with roles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('group')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='group_memberships',
        verbose_name=_('user')
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=GroupRole.choices,
        default=GroupRole.MEMBER
    )
    
    # Status and settings
    is_active = models.BooleanField(_('is active'), default=True)
    notifications_enabled = models.BooleanField(_('notifications enabled'), default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Group Membership')
        verbose_name_plural = _('Group Memberships')
        unique_together = ['group', 'user']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['group', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.group.name} ({self.role})"


class GroupJoinRequest(models.Model):
    """
    Model for handling group join requests
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='join_requests',
        verbose_name=_('group')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='group_join_requests',
        verbose_name=_('user')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=JoinRequestStatus.choices,
        default=JoinRequestStatus.PENDING
    )
    message = models.TextField(
        _('message'),
        blank=True,
        help_text=_('Optional message from the user')
    )
    
    # Processing info
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_join_requests',
        verbose_name=_('processed by')
    )
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    admin_notes = models.TextField(_('admin notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Group Join Request')
        verbose_name_plural = _('Group Join Requests')
        unique_together = ['group', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} -> {self.group.name} ({self.status})"


class GroupInvitation(models.Model):
    """
    Model for group invitations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name=_('group')
    )
    invited_user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='group_invitations',
        verbose_name=_('invited user')
    )
    invited_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sent_group_invitations',
        verbose_name=_('invited by')
    )
    
    # Invitation details
    message = models.TextField(
        _('message'),
        blank=True,
        help_text=_('Optional message from the inviter')
    )
    is_accepted = models.BooleanField(_('is accepted'), default=False)
    is_declined = models.BooleanField(_('is declined'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    responded_at = models.DateTimeField(_('responded at'), null=True, blank=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Group Invitation')
        verbose_name_plural = _('Group Invitations')
        unique_together = ['group', 'invited_user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group', 'is_accepted', 'is_declined']),
            models.Index(fields=['invited_user', 'is_accepted', 'is_declined']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.invited_user.full_name} invited to {self.group.name}"
    
    @property
    def is_pending(self):
        """Check if invitation is still pending"""
        return not self.is_accepted and not self.is_declined
    
    @property
    def is_expired(self):
        """Check if invitation has expired"""
        if self.expires_at is None:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class GroupPost(models.Model):
    """
    Posts specific to groups (extends the main Post model concept)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('group')
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='group_posts',
        verbose_name=_('author')
    )
    
    # Content
    title = models.CharField(_('title'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    
    # Post settings
    is_announcement = models.BooleanField(_('is announcement'), default=False)
    is_pinned = models.BooleanField(_('is pinned'), default=False)
    is_approved = models.BooleanField(_('is approved'), default=True)
    is_deleted = models.BooleanField(_('is deleted'), default=False)
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(_('likes count'), default=0)
    comments_count = models.PositiveIntegerField(_('comments count'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Group Post')
        verbose_name_plural = _('Group Posts')
        ordering = ['-is_pinned', '-published_at']
        indexes = [
            models.Index(fields=['group', '-published_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['is_announcement', '-published_at']),
            models.Index(fields=['is_pinned', '-published_at']),
        ]
    
    def __str__(self):
        return f"{self.title or self.content[:50]} - {self.group.name}"


class GroupEvent(models.Model):
    """
    Events specific to groups
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('group')
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_group_events',
        verbose_name=_('created by')
    )
    
    # Event details
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    location = models.CharField(_('location'), max_length=200, blank=True)
    
    # Timing
    start_datetime = models.DateTimeField(_('start date and time'))
    end_datetime = models.DateTimeField(_('end date and time'))
    is_all_day = models.BooleanField(_('is all day'), default=False)
    
    # Settings
    max_attendees = models.PositiveIntegerField(
        _('maximum attendees'),
        null=True,
        blank=True
    )
    require_rsvp = models.BooleanField(_('require RSVP'), default=False)
    is_public = models.BooleanField(_('is public'), default=False)
    
    # Metrics
    attendee_count = models.PositiveIntegerField(_('attendee count'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Group Event')
        verbose_name_plural = _('Group Events')
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['group', 'start_datetime']),
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['is_public', 'start_datetime']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.group.name}" 