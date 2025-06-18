"""
Filters for Posts app
"""
import django_filters
from django.db.models import Q
from .models import Post, PostVisibility, PostType


class PostFilter(django_filters.FilterSet):
    """
    Filter for posts
    """
    visibility = django_filters.ChoiceFilter(
        choices=PostVisibility.choices,
        method='filter_visibility'
    )
    post_type = django_filters.ChoiceFilter(
        choices=PostType.choices
    )
    parish = django_filters.UUIDFilter(
        field_name='target_parish__id'
    )
    author = django_filters.UUIDFilter(
        field_name='author__id'
    )
    tag = django_filters.CharFilter(
        field_name='post_tags__tag__name',
        lookup_expr='icontains'
    )
    date_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    date_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Post
        fields = ['visibility', 'post_type', 'parish', 'author', 'tag', 'date_from', 'date_to']
    
    def filter_visibility(self, queryset, name, value):
        """
        Custom filter for post visibility
        """
        user = self.request.user
        
        if value == PostVisibility.PUBLIC:
            return queryset.filter(visibility=PostVisibility.PUBLIC)
        elif value == PostVisibility.PARISH_ONLY:
            return queryset.filter(
                visibility=PostVisibility.PARISH_ONLY,
                target_parish=user.parish
            )
        elif value == PostVisibility.PRIVATE:
            return queryset.filter(
                visibility=PostVisibility.PRIVATE,
                author=user
            )
        
        return queryset 