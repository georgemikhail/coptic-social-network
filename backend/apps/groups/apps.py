"""
Groups app configuration - Phase 4
"""
from django.apps import AppConfig


class GroupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.groups'
    verbose_name = 'Groups'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.groups.signals 