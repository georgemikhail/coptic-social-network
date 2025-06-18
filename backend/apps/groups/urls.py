"""
URL patterns for Groups app - Phase 4
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    GroupViewSet, GroupPostViewSet, GroupEventViewSet,
    GroupMembershipViewSet, GroupInvitationViewSet
)

# Main router
router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'group-posts', GroupPostViewSet, basename='grouppost')
router.register(r'group-events', GroupEventViewSet, basename='groupevent')
router.register(r'group-memberships', GroupMembershipViewSet, basename='groupmembership')
router.register(r'group-invitations', GroupInvitationViewSet, basename='groupinvitation')

# Nested routers for group-specific resources
groups_router = routers.NestedDefaultRouter(router, r'groups', lookup='group')
groups_router.register(r'posts', GroupPostViewSet, basename='group-posts')
groups_router.register(r'events', GroupEventViewSet, basename='group-events')
groups_router.register(r'members', GroupMembershipViewSet, basename='group-members')

app_name = 'groups'

urlpatterns = [
    path('', include(router.urls)),
    path('', include(groups_router.urls)),
] 