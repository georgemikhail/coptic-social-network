"""
Signals for Groups app - Phase 4
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import GroupMembership, GroupPost, GroupJoinRequest, GroupInvitation


@receiver(post_save, sender=GroupMembership)
def update_group_member_count_on_save(sender, instance, created, **kwargs):
    """Update group member count when membership is created or updated"""
    if created or instance.is_active:
        # Recalculate member count
        active_count = instance.group.memberships.filter(is_active=True).count()
        instance.group.member_count = active_count
        instance.group.save(update_fields=['member_count'])


@receiver(post_delete, sender=GroupMembership)
def update_group_member_count_on_delete(sender, instance, **kwargs):
    """Update group member count when membership is deleted"""
    # Recalculate member count
    active_count = instance.group.memberships.filter(is_active=True).count()
    instance.group.member_count = active_count
    instance.group.save(update_fields=['member_count'])


@receiver(post_save, sender=GroupPost)
def update_group_post_count_on_save(sender, instance, created, **kwargs):
    """Update group post count when post is created"""
    if created and instance.is_approved and not instance.is_deleted:
        instance.group.post_count += 1
        instance.group.save(update_fields=['post_count'])


@receiver(pre_save, sender=GroupPost)
def update_group_post_count_on_status_change(sender, instance, **kwargs):
    """Update group post count when post status changes"""
    if instance.pk:  # Only for existing posts
        try:
            old_instance = GroupPost.objects.get(pk=instance.pk)
            
            # Check if post approval status changed
            old_counted = old_instance.is_approved and not old_instance.is_deleted
            new_counted = instance.is_approved and not instance.is_deleted
            
            if old_counted != new_counted:
                if new_counted:
                    instance.group.post_count += 1
                else:
                    instance.group.post_count -= 1
                instance.group.save(update_fields=['post_count'])
        except GroupPost.DoesNotExist:
            pass


@receiver(post_delete, sender=GroupPost)
def update_group_post_count_on_delete(sender, instance, **kwargs):
    """Update group post count when post is deleted"""
    if instance.is_approved and not instance.is_deleted:
        instance.group.post_count -= 1
        instance.group.save(update_fields=['post_count'])


@receiver(post_save, sender=GroupJoinRequest)
def handle_join_request_approval(sender, instance, created, **kwargs):
    """Handle automatic membership creation when join request is approved"""
    if not created and instance.status == 'approved':
        # Check if membership doesn't already exist
        if not GroupMembership.objects.filter(
            group=instance.group,
            user=instance.user,
            is_active=True
        ).exists():
            # Create membership
            GroupMembership.objects.create(
                group=instance.group,
                user=instance.user,
                role='member'
            )


@receiver(post_save, sender=GroupInvitation)
def handle_invitation_acceptance(sender, instance, created, **kwargs):
    """Handle automatic membership creation when invitation is accepted"""
    if not created and instance.is_accepted and not instance.is_declined:
        # Check if membership doesn't already exist
        if not GroupMembership.objects.filter(
            group=instance.group,
            user=instance.invited_user,
            is_active=True
        ).exists():
            # Create membership
            GroupMembership.objects.create(
                group=instance.group,
                user=instance.invited_user,
                role='member'
            )
            
            # Update responded_at timestamp
            if not instance.responded_at:
                instance.responded_at = timezone.now()
                instance.save(update_fields=['responded_at']) 