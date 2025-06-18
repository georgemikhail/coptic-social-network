"""
Views for Groups app - Phase 4
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Group, GroupMembership, GroupJoinRequest, 
    GroupInvitation, GroupPost, GroupEvent
)
from .serializers import (
    GroupBasicSerializer, GroupDetailSerializer, CreateGroupSerializer,
    GroupMembershipSerializer, GroupJoinRequestSerializer, CreateJoinRequestSerializer,
    GroupInvitationSerializer, CreateInvitationSerializer,
    GroupPostBasicSerializer, GroupPostDetailSerializer, CreateGroupPostSerializer,
    GroupEventBasicSerializer, GroupEventDetailSerializer, CreateGroupEventSerializer
)
from .permissions import GroupPermissions


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing groups
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group_type', 'privacy', 'parish', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'member_count', 'post_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get groups based on user's permissions"""
        user = self.request.user
        
        # Base queryset with optimizations
        queryset = Group.objects.select_related(
            'parish', 'parish__diocese', 'created_by'
        ).prefetch_related(
            'memberships__user'
        ).filter(is_active=True)
        
        # Filter based on privacy and user's parish
        if user.is_superuser:
            return queryset
        
        # Regular users see:
        # - Public groups
        # - Parish-only groups from their parish
        # - Private groups they're members of
        return queryset.filter(
            Q(privacy='public') |
            Q(privacy='parish_only', parish=user.parish) |
            Q(privacy__in=['private', 'invite_only'], memberships__user=user, memberships__is_active=True)
        ).distinct()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CreateGroupSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return GroupDetailSerializer
        return GroupBasicSerializer
    
    def perform_create(self, serializer):
        """Create group with current user as creator"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a group directly or create join request"""
        group = self.get_object()
        user = request.user
        
        # Check if user can join
        if not group.can_user_join(user):
            return Response(
                {'error': 'You cannot join this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already a member
        if group.memberships.filter(user=user, is_active=True).exists():
            return Response(
                {'error': 'You are already a member of this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If group requires approval, create join request
        if group.require_approval:
            # Check if already has pending request
            if group.join_requests.filter(user=user, status='pending').exists():
                return Response(
                    {'error': 'You already have a pending request for this group'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            join_request = GroupJoinRequest.objects.create(
                group=group,
                user=user,
                message=request.data.get('message', '')
            )
            
            return Response(
                {'message': 'Join request submitted successfully'},
                status=status.HTTP_201_CREATED
            )
        
        # Join directly
        membership = GroupMembership.objects.create(
            group=group,
            user=user,
            role='member'
        )
        
        # Update member count
        group.member_count += 1
        group.save()
        
        return Response(
            GroupMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a group"""
        group = self.get_object()
        user = request.user
        
        try:
            membership = group.memberships.get(user=user, is_active=True)
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the only admin
        if membership.role == 'admin':
            admin_count = group.memberships.filter(role='admin', is_active=True).count()
            if admin_count == 1:
                return Response(
                    {'error': 'You cannot leave as you are the only admin. Please assign another admin first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Deactivate membership
        membership.is_active = False
        membership.save()
        
        # Update member count
        group.member_count -= 1
        group.save()
        
        return Response(
            {'message': 'Successfully left the group'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get group members"""
        group = self.get_object()
        
        # Check if user can view members
        if group.privacy == 'private':
            if not group.memberships.filter(user=request.user, is_active=True).exists():
                return Response(
                    {'error': 'You do not have permission to view members'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        memberships = group.memberships.filter(is_active=True).select_related('user')
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite a user to the group"""
        group = self.get_object()
        
        # Check permission
        user_role = group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to invite users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CreateInvitationSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def join_requests(self, request, pk=None):
        """Get pending join requests for the group"""
        group = self.get_object()
        
        # Check permission
        user_role = group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to view join requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        requests = group.join_requests.filter(status='pending').select_related('user')
        serializer = GroupJoinRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        """Approve a join request"""
        group = self.get_object()
        request_id = request.data.get('request_id')
        
        # Check permission
        user_role = group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to approve requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            join_request = group.join_requests.get(id=request_id, status='pending')
        except GroupJoinRequest.DoesNotExist:
            return Response(
                {'error': 'Join request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create membership
        membership = GroupMembership.objects.create(
            group=group,
            user=join_request.user,
            role='member'
        )
        
        # Update request status
        join_request.status = 'approved'
        join_request.processed_by = request.user
        join_request.processed_at = timezone.now()
        join_request.save()
        
        # Update member count
        group.member_count += 1
        group.save()
        
        return Response(
            {'message': 'Join request approved successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        """Reject a join request"""
        group = self.get_object()
        request_id = request.data.get('request_id')
        
        # Check permission
        user_role = group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to reject requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            join_request = group.join_requests.get(id=request_id, status='pending')
        except GroupJoinRequest.DoesNotExist:
            return Response(
                {'error': 'Join request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update request status
        join_request.status = 'rejected'
        join_request.processed_by = request.user
        join_request.processed_at = timezone.now()
        join_request.admin_notes = request.data.get('admin_notes', '')
        join_request.save()
        
        return Response(
            {'message': 'Join request rejected'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_groups(self, request):
        """Get current user's groups"""
        user = request.user
        memberships = GroupMembership.objects.filter(
            user=user, 
            is_active=True
        ).select_related('group', 'group__parish')
        
        groups = [membership.group for membership in memberships]
        serializer = GroupBasicSerializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured groups"""
        groups = self.get_queryset().filter(is_featured=True)[:10]
        serializer = GroupBasicSerializer(groups, many=True)
        return Response(serializer.data)


class GroupPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing group posts
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group', 'is_announcement', 'is_pinned']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at', 'likes_count']
    ordering = ['-is_pinned', '-published_at']
    
    def get_queryset(self):
        """Get posts based on user's group memberships"""
        user = self.request.user
        
        # Get groups user has access to
        accessible_groups = Group.objects.filter(
            Q(privacy='public') |
            Q(privacy='parish_only', parish=user.parish) |
            Q(privacy__in=['private', 'invite_only'], memberships__user=user, memberships__is_active=True)
        ).distinct()
        
        return GroupPost.objects.filter(
            group__in=accessible_groups,
            is_approved=True,
            is_deleted=False
        ).select_related('group', 'author')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CreateGroupPostSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return GroupPostDetailSerializer
        return GroupPostBasicSerializer
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a group post"""
        post = self.get_object()
        # This would integrate with the posts app reaction system
        return Response({'message': 'Like functionality to be integrated with posts app'})
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin a group post"""
        post = self.get_object()
        
        # Check permission
        user_role = post.group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to pin posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_pinned = True
        post.save()
        
        return Response({'message': 'Post pinned successfully'})
    
    @action(detail=True, methods=['post'])
    def unpin(self, request, pk=None):
        """Unpin a group post"""
        post = self.get_object()
        
        # Check permission
        user_role = post.group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to unpin posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_pinned = False
        post.save()
        
        return Response({'message': 'Post unpinned successfully'})


class GroupEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing group events
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group', 'is_public', 'require_rsvp']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_datetime', 'created_at']
    ordering = ['start_datetime']
    
    def get_queryset(self):
        """Get events based on user's group memberships"""
        user = self.request.user
        
        # Get groups user has access to
        accessible_groups = Group.objects.filter(
            Q(privacy='public') |
            Q(privacy='parish_only', parish=user.parish) |
            Q(privacy__in=['private', 'invite_only'], memberships__user=user, memberships__is_active=True)
        ).distinct()
        
        return GroupEvent.objects.filter(
            Q(group__in=accessible_groups) |
            Q(is_public=True)
        ).select_related('group', 'created_by').distinct()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CreateGroupEventSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return GroupEventDetailSerializer
        return GroupEventBasicSerializer
    
    @action(detail=True, methods=['post'])
    def rsvp(self, request, pk=None):
        """RSVP to an event"""
        event = self.get_object()
        # This would integrate with event attendance system
        return Response({'message': 'RSVP functionality to be implemented'})
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        events = self.get_queryset().filter(
            start_datetime__gte=timezone.now()
        )[:20]
        serializer = GroupEventBasicSerializer(events, many=True)
        return Response(serializer.data)


class GroupMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing group memberships
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupMembershipSerializer
    
    def get_queryset(self):
        """Get memberships for groups user has access to"""
        user = self.request.user
        
        # Get groups user is admin/moderator of
        admin_groups = Group.objects.filter(
            memberships__user=user,
            memberships__role__in=['admin', 'moderator'],
            memberships__is_active=True
        )
        
        return GroupMembership.objects.filter(
            group__in=admin_groups,
            is_active=True
        ).select_related('user', 'group')
    
    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """Promote a member"""
        membership = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in ['admin', 'moderator', 'member']:
            return Response(
                {'error': 'Invalid role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permission
        user_role = membership.group.get_user_role(request.user)
        if user_role != 'admin':
            return Response(
                {'error': 'Only admins can promote members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        membership.role = new_role
        membership.save()
        
        return Response(
            GroupMembershipSerializer(membership).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def remove(self, request, pk=None):
        """Remove a member from the group"""
        membership = self.get_object()
        
        # Check permission
        user_role = membership.group.get_user_role(request.user)
        if user_role not in ['admin', 'moderator']:
            return Response(
                {'error': 'You do not have permission to remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot remove admins (unless you're an admin)
        if membership.role == 'admin' and user_role != 'admin':
            return Response(
                {'error': 'You cannot remove an admin'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Deactivate membership
        membership.is_active = False
        membership.save()
        
        # Update member count
        membership.group.member_count -= 1
        membership.group.save()
        
        return Response(
            {'message': 'Member removed successfully'},
            status=status.HTTP_200_OK
        )


class GroupInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing group invitations (read-only for recipients)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupInvitationSerializer
    
    def get_queryset(self):
        """Get invitations for current user"""
        return GroupInvitation.objects.filter(
            invited_user=self.request.user,
            is_accepted=False,
            is_declined=False
        ).select_related('group', 'invited_by')
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a group invitation"""
        invitation = self.get_object()
        
        if invitation.is_expired:
            return Response(
                {'error': 'This invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user can still join
        if not invitation.group.can_user_join(invitation.invited_user):
            return Response(
                {'error': 'You can no longer join this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = GroupMembership.objects.create(
            group=invitation.group,
            user=invitation.invited_user,
            role='member'
        )
        
        # Update invitation
        invitation.is_accepted = True
        invitation.responded_at = timezone.now()
        invitation.save()
        
        # Update member count
        invitation.group.member_count += 1
        invitation.group.save()
        
        return Response(
            {'message': 'Invitation accepted successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline a group invitation"""
        invitation = self.get_object()
        
        invitation.is_declined = True
        invitation.responded_at = timezone.now()
        invitation.save()
        
        return Response(
            {'message': 'Invitation declined'},
            status=status.HTTP_200_OK
        ) 