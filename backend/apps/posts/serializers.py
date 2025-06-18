"""
Serializers for Posts app
"""
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import (
    Post, PostMedia, Comment, Reaction, Share, PostTag, 
    PostTagging, Feed, FeedPost, PostVisibility, PostType, ReactionType
)
from apps.users.serializers import UserSerializer


class PostMediaSerializer(serializers.ModelSerializer):
    """
    Post Media serializer
    """
    file_url = serializers.CharField(source='file.url', read_only=True)
    
    class Meta:
        model = PostMedia
        fields = [
            'id', 'filename', 'file_url', 'file_size', 'content_type',
            'media_type', 'title', 'description', 'alt_text', 'duration',
            'width', 'height', 'is_processed', 'created_at'
        ]
        read_only_fields = ['id', 'file_size', 'content_type', 'is_processed', 'created_at']


class PostTagSerializer(serializers.ModelSerializer):
    """
    Post Tag serializer
    """
    posts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PostTag
        fields = ['id', 'name', 'description', 'color', 'is_official', 'posts_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReactionSerializer(serializers.ModelSerializer):
    """
    Reaction serializer
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user_name', 'reaction_type', 'created_at']
        read_only_fields = ['id', 'user_name', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer
    """
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author_name', 'author_avatar', 'content', 'parent', 'is_reply', 
            'likes_count', 'replies', 'user_reaction', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author_name', 'likes_count', 'created_at', 'updated_at']
    
    def get_author_avatar(self, obj):
        """Get author avatar URL safely"""
        if obj.author.profile_picture and hasattr(obj.author.profile_picture, 'url'):
            return obj.author.profile_picture.url
        return None
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(
                obj.replies.filter(is_approved=True, is_deleted=False)[:5], 
                many=True, 
                context=self.context
            ).data
        return []
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Comment)
            reaction = Reaction.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).first()
            return reaction.reaction_type if reaction else None
        return None


class PostListSerializer(serializers.ModelSerializer):
    """
    Simplified Post serializer for list views
    """
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    media_count = serializers.IntegerField(read_only=True)
    user_reaction = serializers.SerializerMethodField()
    parish_name = serializers.CharField(source='target_parish.name', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'author_name', 'author_avatar', 'content', 'post_type', 'visibility',
            'parish_name', 'is_announcement', 'is_pinned', 'is_featured',
            'likes_count', 'comments_count', 'shares_count', 'media_count',
            'user_reaction', 'created_at', 'updated_at'
        ]
    
    def get_author_avatar(self, obj):
        """Get author avatar URL safely"""
        if obj.author.profile_picture and hasattr(obj.author.profile_picture, 'url'):
            return obj.author.profile_picture.url
        return None
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Post)
            reaction = Reaction.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).first()
            return reaction.reaction_type if reaction else None
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Detailed Post serializer
    """
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    media = PostMediaSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    recent_reactions = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    parish_name = serializers.CharField(source='target_parish.name', read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author_name', 'author_avatar', 'content', 'post_type', 'visibility',
            'parish_name', 'is_announcement', 'is_pinned', 'is_featured',
            'likes_count', 'comments_count', 'shares_count',
            'media', 'comments', 'recent_reactions',
            'user_reaction', 'can_edit', 'can_delete',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_author_avatar(self, obj):
        """Get author avatar URL safely"""
        if obj.author.profile_picture and hasattr(obj.author.profile_picture, 'url'):
            return obj.author.profile_picture.url
        return None
    
    def get_comments(self, obj):
        comments = obj.comments.filter(
            is_approved=True, 
            is_deleted=False, 
            parent=None
        )[:10]
        return CommentSerializer(comments, many=True, context=self.context).data
    
    def get_recent_reactions(self, obj):
        content_type = ContentType.objects.get_for_model(Post)
        reactions = Reaction.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).select_related('user')[:5]
        return ReactionSerializer(reactions, many=True).data
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Post)
            reaction = Reaction.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).first()
            return reaction.reaction_type if reaction else None
        return None
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or request.user.is_staff
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or request.user.is_staff
        return False


class CreatePostSerializer(serializers.ModelSerializer):
    """
    Create Post serializer
    """
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'content', 'post_type', 'visibility', 'target_parish',
            'is_announcement', 'media_files'
        ]
    
    def validate(self, attrs):
        # Ensure content or media is provided
        if not attrs.get('content') and not attrs.get('media_files'):
            raise serializers.ValidationError("Post must have either content or media.")
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        # Extract non-model fields
        media_files = validated_data.pop('media_files', [])
        
        # Set author
        request = self.context.get('request')
        validated_data['author'] = request.user
        
        if not validated_data.get('target_parish'):
            validated_data['target_parish'] = request.user.parish
        
        # Create post
        post = Post.objects.create(**validated_data)
        
        # Create media attachments
        for media_file in media_files:
            PostMedia.objects.create(
                post=post,
                file=media_file,
                filename=media_file.name,
                file_size=media_file.size,
                content_type=media_file.content_type,
                media_type=self._get_media_type(media_file.content_type)
            )
        
        return post
    
    def _get_media_type(self, content_type):
        """Determine media type from content type"""
        if content_type.startswith('image/'):
            return 'image'
        elif content_type.startswith('video/'):
            return 'video'
        elif content_type.startswith('audio/'):
            return 'audio'
        else:
            return 'document'


class UpdatePostSerializer(serializers.ModelSerializer):
    """
    Update Post serializer
    """
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = ['content', 'visibility', 'is_announcement', 'tag_names']
    
    @transaction.atomic
    def update(self, instance, validated_data):
        # Extract tag names
        tag_names = validated_data.pop('tag_names', None)
        
        # Update post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_names is not None:
            # Remove existing tags
            PostTagging.objects.filter(post=instance).delete()
            
            # Add new tags
            request = self.context.get('request')
            for tag_name in tag_names:
                tag, created = PostTag.objects.get_or_create(
                    name=tag_name.lower().strip(),
                    defaults={'description': f'Tag for {tag_name}'}
                )
                PostTagging.objects.create(
                    post=instance,
                    tag=tag,
                    tagged_by=request.user
                )
        
        return instance


class CreateCommentSerializer(serializers.ModelSerializer):
    """
    Create Comment serializer
    """
    class Meta:
        model = Comment
        fields = ['content', 'parent']
    
    def validate_parent(self, value):
        if value:
            # Ensure parent belongs to the same post
            post_id = self.context.get('post_id')
            if value.post.id != post_id:
                raise serializers.ValidationError("Parent comment must belong to the same post.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        post_id = self.context.get('post_id')
        
        validated_data['author'] = request.user
        validated_data['post_id'] = post_id
        
        return Comment.objects.create(**validated_data)


class CreateReactionSerializer(serializers.ModelSerializer):
    """
    Create Reaction serializer
    """
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Reaction
        fields = ['reaction_type', 'content_type', 'object_id']
    
    def create(self, validated_data):
        request = self.context.get('request')
        content_type_name = validated_data.pop('content_type')
        object_id = validated_data.pop('object_id')
        
        # Get content type
        model_mapping = {
            'post': Post,
            'comment': Comment
        }
        model_class = model_mapping[content_type_name]
        content_type = ContentType.objects.get_for_model(model_class)
        
        # Create or update reaction
        reaction, created = Reaction.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={'reaction_type': validated_data['reaction_type']}
        )
        
        return reaction


class ShareSerializer(serializers.ModelSerializer):
    """
    Share serializer
    """
    user = UserSerializer(read_only=True)
    post = PostListSerializer(read_only=True)
    
    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'comment', 'visibility', 'created_at']
        read_only_fields = ['id', 'user', 'post', 'created_at']


class CreateShareSerializer(serializers.ModelSerializer):
    """
    Create Share serializer
    """
    post_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Share
        fields = ['post_id', 'comment', 'visibility']
    
    def validate_post_id(self, value):
        try:
            post = Post.objects.get(id=value, is_deleted=False, is_approved=True)
            return post
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found or not available for sharing.")
    
    def create(self, validated_data):
        request = self.context.get('request')
        post = validated_data.pop('post_id')
        
        validated_data['user'] = request.user
        validated_data['post'] = post
        
        return Share.objects.create(**validated_data)


class FeedSerializer(serializers.ModelSerializer):
    """
    Feed serializer
    """
    created_by = UserSerializer(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    parish_name = serializers.CharField(source='parish.name', read_only=True)
    
    class Meta:
        model = Feed
        fields = [
            'id', 'name', 'description', 'parish_name', 'created_by',
            'is_public', 'is_official', 'is_featured', 'allowed_post_types',
            'posts_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at'] 