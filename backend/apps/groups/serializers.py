"""
Serializers for Groups app - Phase 4
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Group, GroupMembership, GroupJoinRequest, 
    GroupInvitation, GroupPost, GroupEvent
)
from apps.users.serializers import UserBasicSerializer
from apps.parishes.serializers import ParishBasicSerializer

User = get_user_model()


class GroupBasicSerializer(serializers.ModelSerializer):
    """Basic group serializer for lists and references"""
    
    parish = ParishBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'group_type', 'privacy',
            'parish', 'created_by', 'cover_image', 'icon',
            'is_active', 'is_featured', 'member_count', 'post_count',
            'created_at'
        ]
        read_only_fields = ['id', 'member_count', 'post_count', 'created_at']


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group memberships"""
    
    user = UserBasicSerializer(read_only=True)
    group = GroupBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = [
            'id', 'group', 'user', 'role', 'is_active',
            'notifications_enabled', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']


class GroupDetailSerializer(serializers.ModelSerializer):
    """Detailed group serializer with memberships and stats"""
    
    parish = ParishBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    memberships = GroupMembershipSerializer(many=True, read_only=True)
    user_role = serializers.SerializerMethodField()
    user_membership = serializers.SerializerMethodField()
    can_user_join = serializers.SerializerMethodField()
    recent_posts = serializers.SerializerMethodField()
    upcoming_events = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'group_type', 'privacy',
            'parish', 'created_by', 'cover_image', 'icon',
            'is_active', 'is_featured', 'allow_member_posts', 'require_approval',
            'member_count', 'max_members', 'post_count',
            'memberships', 'user_role', 'user_membership', 'can_user_join',
            'recent_posts', 'upcoming_events',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'member_count', 'post_count', 'memberships',
            'user_role', 'user_membership', 'can_user_join',
            'recent_posts', 'upcoming_events',
            'created_at', 'updated_at'
        ]
    
    def get_user_role(self, obj):
        """Get current user's role in this group"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_user_role(request.user)
        return None
    
    def get_user_membership(self, obj):
        """Get current user's membership details"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = obj.memberships.get(user=request.user, is_active=True)
                return GroupMembershipSerializer(membership).data
            except GroupMembership.DoesNotExist:
                return None
        return None
    
    def get_can_user_join(self, obj):
        """Check if current user can join this group"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_user_join(request.user)
        return False
    
    def get_recent_posts(self, obj):
        """Get recent posts from this group"""
        recent_posts = obj.posts.filter(
            is_approved=True, 
            is_deleted=False
        ).order_by('-published_at')[:5]
        
        # Return basic post data without using serializer to avoid circular import
        return [{
            'id': str(post.id),
            'title': post.title,
            'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
            'is_announcement': post.is_announcement,
            'is_pinned': post.is_pinned,
            'published_at': post.published_at,
            'author': {
                'id': post.author.id,
                'full_name': post.author.full_name
            }
        } for post in recent_posts]
    
    def get_upcoming_events(self, obj):
        """Get upcoming events from this group"""
        upcoming_events = obj.events.filter(
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:3]
        
        # Return basic event data without using serializer to avoid circular import
        return [{
            'id': str(event.id),
            'title': event.title,
            'description': event.description[:100] + '...' if len(event.description) > 100 else event.description,
            'start_datetime': event.start_datetime,
            'end_datetime': event.end_datetime,
            'location': event.location,
            'is_public': event.is_public
        } for event in upcoming_events]


class CreateGroupSerializer(serializers.ModelSerializer):
    """Serializer for creating groups"""
    
    class Meta:
        model = Group
        fields = [
            'name', 'description', 'group_type', 'privacy',
            'parish', 'cover_image', 'icon',
            'allow_member_posts', 'require_approval', 'max_members'
        ]
    
    def validate_parish(self, value):
        """Validate that user belongs to the parish"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.parish != value:
                raise serializers.ValidationError(
                    "You can only create groups in your own parish."
                )
        return value
    
    def create(self, validated_data):
        """Create group and add creator as admin"""
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        
        group = super().create(validated_data)
        
        # Add creator as admin
        GroupMembership.objects.create(
            group=group,
            user=request.user,
            role='admin'
        )
        
        # Update member count
        group.member_count = 1
        group.save()
        
        return group


class GroupJoinRequestSerializer(serializers.ModelSerializer):
    """Serializer for group join requests"""
    
    user = UserBasicSerializer(read_only=True)
    group = GroupBasicSerializer(read_only=True)
    processed_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupJoinRequest
        fields = [
            'id', 'group', 'user', 'status', 'message',
            'processed_by', 'processed_at', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'processed_by', 'processed_at',
            'admin_notes', 'created_at', 'updated_at'
        ]


class CreateJoinRequestSerializer(serializers.ModelSerializer):
    """Serializer for creating join requests"""
    
    class Meta:
        model = GroupJoinRequest
        fields = ['group', 'message']
    
    def validate_group(self, value):
        """Validate join request"""
        request = self.context.get('request')
        user = request.user
        
        # Check if user can join
        if not value.can_user_join(user):
            raise serializers.ValidationError(
                "You cannot join this group."
            )
        
        # Check if already a member
        if value.memberships.filter(user=user, is_active=True).exists():
            raise serializers.ValidationError(
                "You are already a member of this group."
            )
        
        # Check if already has pending request
        if value.join_requests.filter(user=user, status='pending').exists():
            raise serializers.ValidationError(
                "You already have a pending request for this group."
            )
        
        return value
    
    def create(self, validated_data):
        """Create join request"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class GroupInvitationSerializer(serializers.ModelSerializer):
    """Serializer for group invitations"""
    
    group = GroupBasicSerializer(read_only=True)
    invited_user = UserBasicSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupInvitation
        fields = [
            'id', 'group', 'invited_user', 'invited_by', 'message',
            'is_accepted', 'is_declined', 'is_pending', 'is_expired',
            'created_at', 'responded_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'invited_by', 'is_pending', 'is_expired',
            'created_at', 'responded_at'
        ]


class CreateInvitationSerializer(serializers.ModelSerializer):
    """Serializer for creating invitations"""
    
    invited_user_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = GroupInvitation
        fields = ['group', 'invited_user_email', 'message']
    
    def validate(self, attrs):
        """Validate invitation"""
        request = self.context.get('request')
        group = attrs['group']
        
        # Check if user has permission to invite
        user_role = group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            raise serializers.ValidationError(
                "You don't have permission to invite users to this group."
            )
        
        # Get invited user
        try:
            invited_user = User.objects.get(email=attrs['invited_user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this email does not exist."
            )
        
        # Check if already a member
        if group.memberships.filter(user=invited_user, is_active=True).exists():
            raise serializers.ValidationError(
                "User is already a member of this group."
            )
        
        # Check if already invited
        if group.invitations.filter(
            invited_user=invited_user,
            is_accepted=False,
            is_declined=False
        ).exists():
            raise serializers.ValidationError(
                "User has already been invited to this group."
            )
        
        attrs['invited_user'] = invited_user
        return attrs
    
    def create(self, validated_data):
        """Create invitation"""
        request = self.context.get('request')
        validated_data['invited_by'] = request.user
        validated_data.pop('invited_user_email')  # Remove email field
        
        # Set expiration (30 days from now)
        validated_data['expires_at'] = timezone.now() + timezone.timedelta(days=30)
        
        return super().create(validated_data)


class GroupPostBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for group posts"""
    
    author = UserBasicSerializer(read_only=True)
    group = GroupBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupPost
        fields = [
            'id', 'group', 'author', 'title', 'content',
            'is_announcement', 'is_pinned',
            'likes_count', 'comments_count',
            'published_at'
        ]
        read_only_fields = [
            'id', 'author', 'likes_count', 'comments_count', 'published_at'
        ]


class GroupPostDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for group posts"""
    
    author = UserBasicSerializer(read_only=True)
    group = GroupBasicSerializer(read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupPost
        fields = [
            'id', 'group', 'author', 'title', 'content',
            'is_announcement', 'is_pinned', 'is_approved',
            'likes_count', 'comments_count', 'user_has_liked',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'author', 'is_approved', 'likes_count', 'comments_count',
            'user_has_liked', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_user_has_liked(self, obj):
        """Check if current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # This would integrate with the posts app reaction system
            return False  # Placeholder
        return False


class CreateGroupPostSerializer(serializers.ModelSerializer):
    """Serializer for creating group posts"""
    
    class Meta:
        model = GroupPost
        fields = ['group', 'title', 'content', 'is_announcement']
    
    def validate_group(self, value):
        """Validate that user can post in this group"""
        request = self.context.get('request')
        user = request.user
        
        # Check if user is a member
        if not value.memberships.filter(user=user, is_active=True).exists():
            raise serializers.ValidationError(
                "You must be a member to post in this group."
            )
        
        # Check if group allows member posts
        if not value.allow_member_posts:
            user_role = value.get_user_role(user)
            if user_role not in ['admin', 'moderator']:
                raise serializers.ValidationError(
                    "Only admins and moderators can post in this group."
                )
        
        return value
    
    def validate_is_announcement(self, value):
        """Validate announcement permission"""
        if value:
            request = self.context.get('request')
            group = self.initial_data.get('group')
            if group:
                try:
                    group_obj = Group.objects.get(id=group)
                    user_role = group_obj.get_user_role(request.user)
                    if user_role not in ['admin', 'moderator']:
                        raise serializers.ValidationError(
                            "Only admins and moderators can create announcements."
                        )
                except Group.DoesNotExist:
                    pass
        return value
    
    def create(self, validated_data):
        """Create group post"""
        request = self.context.get('request')
        validated_data['author'] = request.user
        
        post = super().create(validated_data)
        
        # Update group post count
        post.group.post_count += 1
        post.group.save()
        
        return post


class GroupEventBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for group events"""
    
    group = GroupBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupEvent
        fields = [
            'id', 'group', 'created_by', 'title', 'description', 'location',
            'start_datetime', 'end_datetime', 'is_all_day',
            'max_attendees', 'attendee_count', 'require_rsvp', 'is_public',
            'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'attendee_count', 'created_at']


class GroupEventDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for group events"""
    
    group = GroupBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    user_is_attending = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupEvent
        fields = [
            'id', 'group', 'created_by', 'title', 'description', 'location',
            'start_datetime', 'end_datetime', 'is_all_day',
            'max_attendees', 'attendee_count', 'require_rsvp', 'is_public',
            'user_is_attending',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'attendee_count', 'user_is_attending',
            'created_at', 'updated_at'
        ]
    
    def get_user_is_attending(self, obj):
        """Check if current user is attending this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # This would integrate with event attendance system
            return False  # Placeholder
        return False


class CreateGroupEventSerializer(serializers.ModelSerializer):
    """Serializer for creating group events"""
    
    class Meta:
        model = GroupEvent
        fields = [
            'group', 'title', 'description', 'location',
            'start_datetime', 'end_datetime', 'is_all_day',
            'max_attendees', 'require_rsvp', 'is_public'
        ]
    
    def validate_group(self, value):
        """Validate that user can create events in this group"""
        request = self.context.get('request')
        user = request.user
        
        # Check if user is a member with appropriate role
        user_role = value.get_user_role(user)
        if user_role not in ['admin', 'moderator']:
            raise serializers.ValidationError(
                "Only admins and moderators can create events."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate event timing"""
        if attrs['start_datetime'] >= attrs['end_datetime']:
            raise serializers.ValidationError(
                "End time must be after start time."
            )
        
        if attrs['start_datetime'] < timezone.now():
            raise serializers.ValidationError(
                "Event cannot be scheduled in the past."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create group event"""
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data) 