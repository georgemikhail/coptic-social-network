"""
Signals for Posts app
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Post, Comment, Reaction, Share


@receiver(post_save, sender=Comment)
def update_post_comment_count(sender, instance, created, **kwargs):
    """Update comment count when a comment is created"""
    if created and instance.is_approved and not instance.is_deleted:
        post = instance.post
        post.comments_count = post.comments.filter(
            is_approved=True,
            is_deleted=False
        ).count()
        post.save(update_fields=['comments_count'])


@receiver(post_delete, sender=Comment)
def decrease_post_comment_count(sender, instance, **kwargs):
    """Decrease comment count when a comment is deleted"""
    post = instance.post
    post.comments_count = post.comments.filter(
        is_approved=True,
        is_deleted=False
    ).count()
    post.save(update_fields=['comments_count'])


@receiver(post_save, sender=Reaction)
def update_reaction_count(sender, instance, created, **kwargs):
    """Update reaction count when a reaction is created"""
    if created:
        content_object = instance.content_object
        if isinstance(content_object, Post):
            # Update post likes count
            post = content_object
            post.likes_count = Reaction.objects.filter(
                content_type=ContentType.objects.get_for_model(Post),
                object_id=post.id
            ).count()
            post.save(update_fields=['likes_count'])
        elif isinstance(content_object, Comment):
            # Update comment likes count
            comment = content_object
            comment.likes_count = Reaction.objects.filter(
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id
            ).count()
            comment.save(update_fields=['likes_count'])


@receiver(post_delete, sender=Reaction)
def decrease_reaction_count(sender, instance, **kwargs):
    """Decrease reaction count when a reaction is deleted"""
    content_object = instance.content_object
    if isinstance(content_object, Post):
        # Update post likes count
        post = content_object
        post.likes_count = Reaction.objects.filter(
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id
        ).count()
        post.save(update_fields=['likes_count'])
    elif isinstance(content_object, Comment):
        # Update comment likes count
        comment = content_object
        comment.likes_count = Reaction.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=comment.id
        ).count()
        comment.save(update_fields=['likes_count'])


@receiver(post_save, sender=Share)
def update_post_share_count(sender, instance, created, **kwargs):
    """Update share count when a post is shared"""
    if created:
        post = instance.post
        post.shares_count = post.shares.count()
        post.save(update_fields=['shares_count'])


@receiver(post_delete, sender=Share)
def decrease_post_share_count(sender, instance, **kwargs):
    """Decrease share count when a share is deleted"""
    post = instance.post
    post.shares_count = post.shares.count()
    post.save(update_fields=['shares_count']) 