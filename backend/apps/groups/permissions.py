"""
Permissions for Groups app - Phase 4
"""
from rest_framework import permissions


class GroupPermissions(permissions.BasePermission):
    """
    Custom permissions for group operations
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific group"""
        user = request.user
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # For Group objects
        if hasattr(obj, 'privacy'):
            group = obj
        # For related objects (posts, events, etc.)
        elif hasattr(obj, 'group'):
            group = obj.group
        else:
            return False
        
        # Check based on action
        if view.action in ['retrieve', 'list']:
            return self._can_view_group(user, group)
        elif view.action in ['update', 'partial_update']:
            return self._can_edit_group(user, group)
        elif view.action == 'destroy':
            return self._can_delete_group(user, group)
        
        return False
    
    def _can_view_group(self, user, group):
        """Check if user can view the group"""
        if group.privacy == 'public':
            return True
        elif group.privacy == 'parish_only':
            return user.parish == group.parish
        elif group.privacy in ['private', 'invite_only']:
            return group.memberships.filter(user=user, is_active=True).exists()
        return False
    
    def _can_edit_group(self, user, group):
        """Check if user can edit the group"""
        # Only group admins can edit
        user_role = group.get_user_role(user)
        return user_role == 'admin'
    
    def _can_delete_group(self, user, group):
        """Check if user can delete the group"""
        # Only group creator or superuser can delete
        return user == group.created_by or user.is_superuser


class GroupMembershipPermissions(permissions.BasePermission):
    """
    Permissions for group membership operations
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific membership"""
        user = request.user
        membership = obj
        group = membership.group
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Users can view their own membership
        if view.action == 'retrieve' and membership.user == user:
            return True
        
        # Group admins and moderators can manage memberships
        user_role = group.get_user_role(user)
        if user_role in ['admin', 'moderator']:
            # Moderators cannot manage admin memberships
            if user_role == 'moderator' and membership.role == 'admin':
                return False
            return True
        
        return False


class GroupPostPermissions(permissions.BasePermission):
    """
    Permissions for group post operations
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific post"""
        user = request.user
        post = obj
        group = post.group
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Check if user can access the group
        if not self._can_access_group(user, group):
            return False
        
        # Authors can edit their own posts
        if view.action in ['update', 'partial_update', 'destroy']:
            if post.author == user:
                return True
            
            # Group admins and moderators can manage all posts
            user_role = group.get_user_role(user)
            return user_role in ['admin', 'moderator']
        
        return True
    
    def _can_access_group(self, user, group):
        """Check if user can access the group"""
        if group.privacy == 'public':
            return True
        elif group.privacy == 'parish_only':
            return user.parish == group.parish
        elif group.privacy in ['private', 'invite_only']:
            return group.memberships.filter(user=user, is_active=True).exists()
        return False


class GroupEventPermissions(permissions.BasePermission):
    """
    Permissions for group event operations
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific event"""
        user = request.user
        event = obj
        group = event.group
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Public events are viewable by all
        if view.action == 'retrieve' and event.is_public:
            return True
        
        # Check if user can access the group
        if not self._can_access_group(user, group):
            return False
        
        # Event creators can edit their own events
        if view.action in ['update', 'partial_update', 'destroy']:
            if event.created_by == user:
                return True
            
            # Group admins and moderators can manage all events
            user_role = group.get_user_role(user)
            return user_role in ['admin', 'moderator']
        
        return True
    
    def _can_access_group(self, user, group):
        """Check if user can access the group"""
        if group.privacy == 'public':
            return True
        elif group.privacy == 'parish_only':
            return user.parish == group.parish
        elif group.privacy in ['private', 'invite_only']:
            return group.memberships.filter(user=user, is_active=True).exists()
        return False 