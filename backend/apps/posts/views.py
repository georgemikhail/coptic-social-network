"""
Views for Posts app
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count, Prefetch
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils import timezone
from datetime import timedelta

from .models import (
    Post, PostMedia, Comment, Reaction, Share, PostTag,
    Feed, PostVisibility, PostType, ReactionType
)
from .serializers import (
    PostListSerializer, PostDetailSerializer, CreatePostSerializer,
    CommentSerializer, CreateCommentSerializer, CreateReactionSerializer,
    ReactionSerializer, PostTagSerializer
)
from .filters import PostFilter


class PostViewSet(ModelViewSet):
    """
    ViewSet for managing posts
    """
    queryset = Post.objects.filter(is_deleted=False, is_approved=True)
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['content', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'likes_count', 'comments_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.select_related(
            'author', 'target_parish', 'target_parish__diocese'
        ).prefetch_related(
            'media', 'post_tags__tag'
        ).annotate(
            media_count=Count('media')
        )
        
        # Filter based on visibility and user's parish
        if not user.is_staff:
            queryset = queryset.filter(
                Q(visibility=PostVisibility.PUBLIC) |
                Q(visibility=PostVisibility.PARISH_ONLY, target_parish=user.parish) |
                Q(author=user)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'create':
            return CreatePostSerializer
        return PostDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'], parser_classes=[JSONParser])
    def react(self, request, pk=None):
        """Add or update reaction to a post"""
        post = self.get_object()
        serializer = CreateReactionSerializer(
            data={
                'reaction_type': request.data.get('reaction_type'),
                'content_type': 'post',
                'object_id': str(post.id)
            },
            context={'request': request}
        )
        
        if serializer.is_valid():
            reaction = serializer.save()
            return Response({
                'message': 'Reaction added successfully',
                'reaction_type': reaction.reaction_type
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def unreact(self, request, pk=None):
        """Remove reaction from a post"""
        post = self.get_object()
        content_type = ContentType.objects.get_for_model(Post)
        
        reaction = Reaction.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        ).first()
        
        if reaction:
            reaction.delete()
            return Response({'message': 'Reaction removed successfully'})
        
        return Response(
            {'error': 'No reaction found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['post'], parser_classes=[JSONParser])
    def share(self, request, pk=None):
        """Share a post"""
        post = self.get_object()
        
        # Check if already shared
        existing_share = Share.objects.filter(
            user=request.user,
            post=post
        ).first()
        
        if existing_share:
            return Response(
                {'error': 'You have already shared this post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        share = Share.objects.create(
            user=request.user,
            post=post,
            comment=request.data.get('comment', ''),
            visibility=request.data.get('visibility', PostVisibility.PARISH_ONLY)
        )
        
        # Update share count
        post.shares_count += 1
        post.save(update_fields=['shares_count'])
        
        return Response({
            'message': 'Post shared successfully',
            'share_id': str(share.id)
        })


class CommentViewSet(ModelViewSet):
    """
    ViewSet for managing comments
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.filter(
            post_id=post_id,
            is_approved=True,
            is_deleted=False
        ).select_related('author').order_by('created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCommentSerializer
        return CommentSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post_id'] = self.kwargs.get('post_pk')
        return context
    
    def perform_create(self, serializer):
        comment = serializer.save()
        
        # Update comment count on post
        post = comment.post
        post.comments_count = post.comments.filter(
            is_approved=True, 
            is_deleted=False
        ).count()
        post.save(update_fields=['comments_count'])
    
    @action(detail=True, methods=['post'], parser_classes=[JSONParser])
    def react(self, request, post_pk=None, pk=None):
        """Add or update reaction to a comment"""
        comment = self.get_object()
        serializer = CreateReactionSerializer(
            data={
                'reaction_type': request.data.get('reaction_type'),
                'content_type': 'comment',
                'object_id': str(comment.id)
            },
            context={'request': request}
        )
        
        if serializer.is_valid():
            reaction = serializer.save()
            return Response({
                'message': 'Reaction added successfully',
                'reaction_type': reaction.reaction_type
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='posts_feed',
    summary='Get personalized feed',
    description='Get posts for the user\'s personalized feed',
    parameters=[
        OpenApiParameter(name='feed_type', description='Type of feed', required=False),
        OpenApiParameter(name='limit', description='Number of posts', required=False),
    ]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_feed(request):
    """
    Get personalized feed for the user
    """
    user = request.user
    feed_type = request.GET.get('feed_type', 'parish')
    limit = int(request.GET.get('limit', 20))
    
    # Base queryset
    queryset = Post.objects.filter(
        is_deleted=False,
        is_approved=True
    ).select_related(
        'author', 'target_parish'
    ).prefetch_related(
        'media'
    ).annotate(
        media_count=Count('media')
    )
    
    if feed_type == 'parish':
        # Parish-specific feed
        queryset = queryset.filter(
            Q(target_parish=user.parish) |
            Q(visibility=PostVisibility.PUBLIC)
        )
    elif feed_type == 'public':
        # Public feed
        queryset = queryset.filter(visibility=PostVisibility.PUBLIC)
    elif feed_type == 'following':
        # Following feed (implement when friendship system is ready)
        queryset = queryset.filter(author=user)
    
    # Order by engagement and recency
    queryset = queryset.order_by('-is_pinned', '-created_at')[:limit]
    
    serializer = PostListSerializer(
        queryset, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'feed_type': feed_type,
        'posts': serializer.data,
        'total': queryset.count()
    })


@extend_schema(
    operation_id='posts_trending',
    summary='Get trending posts',
    description='Get trending posts based on engagement'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_trending_posts(request):
    """
    Get trending posts based on engagement
    """
    user = request.user
    limit = int(request.GET.get('limit', 10))
    
    queryset = Post.objects.filter(
        is_deleted=False,
        is_approved=True,
        target_parish=user.parish
    ).select_related(
        'author', 'target_parish'
    ).annotate(
        engagement_score=Count('reactions') + Count('comments') + Count('shares')
    ).order_by('-engagement_score', '-created_at')[:limit]
    
    serializer = PostListSerializer(
        queryset, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'trending_posts': serializer.data
    })


class PostTagListView(generics.ListAPIView):
    """
    List all post tags
    """
    serializer_class = PostTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        return PostTag.objects.annotate(
            posts_count=Count('tagged_posts')
        ).order_by('-posts_count', 'name')


@extend_schema(
    operation_id='posts_stats',
    summary='Get post statistics',
    description='Get statistics about posts in the user\'s parish'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_post_stats(request):
    """
    Get post statistics for the user's parish
    """
    user = request.user
    
    # Get stats for user's parish
    parish_posts = Post.objects.filter(
        target_parish=user.parish,
        is_deleted=False,
        is_approved=True
    )
    
    stats = {
        'total_posts': parish_posts.count(),
        'posts_this_week': parish_posts.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'total_reactions': Reaction.objects.filter(
            content_type=ContentType.objects.get_for_model(Post),
            object_id__in=parish_posts.values_list('id', flat=True)
        ).count(),
        'total_comments': Comment.objects.filter(
            post__in=parish_posts,
            is_approved=True,
            is_deleted=False
        ).count(),
        'most_popular_post_type': parish_posts.values('post_type').annotate(
            count=Count('id')
        ).order_by('-count').first(),
        'active_members': parish_posts.values('author').distinct().count()
    }
    
    return Response(stats)


# Media upload view
@extend_schema(
    operation_id='posts_upload_media',
    summary='Upload media for posts',
    description='Upload media files that can be attached to posts'
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_media(request):
    """
    Upload media files for posts
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Basic file validation
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size > max_size:
        return Response(
            {'error': 'File too large. Maximum size is 50MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For now, just return file info
    # In production, upload to S3 and return URL
    return Response({
        'filename': file.name,
        'size': file.size,
        'content_type': file.content_type,
        'message': 'File uploaded successfully'
    }) 