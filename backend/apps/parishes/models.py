"""
Parish and Diocese models for Coptic Social Network
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Diocese(models.Model):
    """
    Diocese model representing a collection of parishes
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Bishop information
    bishop_name = models.CharField(max_length=200, blank=True, null=True)
    bishop_title = models.CharField(max_length=100, blank=True, null=True)
    bishop_photo = models.ImageField(upload_to='bishops/', blank=True, null=True)
    
    # Contact information
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Diocese admins
    admins = models.ManyToManyField(
        'users.User',
        related_name='administered_dioceses',
        blank=True
    )
    
    # Location
    country = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Diocese')
        verbose_name_plural = _('Dioceses')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def parish_count(self):
        return self.parishes.count()


class Parish(models.Model):
    """
    Parish model representing individual church communities
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Diocese relationship
    diocese = models.ForeignKey(
        Diocese,
        on_delete=models.CASCADE,
        related_name='parishes'
    )
    
    # Clergy information
    priest_name = models.CharField(max_length=200, blank=True, null=True)
    priest_title = models.CharField(max_length=100, blank=True, null=True)
    priest_photo = models.ImageField(upload_to='priests/', blank=True, null=True)
    
    # Additional clergy
    deacons = models.TextField(blank=True, null=True, help_text="List of deacons (one per line)")
    
    # Contact information
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Parish image and media
    cover_image = models.ImageField(upload_to='parishes/covers/', blank=True, null=True)
    logo = models.ImageField(upload_to='parishes/logos/', blank=True, null=True)
    
    # Service times
    service_schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Weekly service schedule in JSON format"
    )
    
    # Social media and communication
    facebook_page = models.URLField(blank=True, null=True)
    youtube_channel = models.URLField(blank=True, null=True)
    whatsapp_group = models.URLField(blank=True, null=True)
    telegram_group = models.URLField(blank=True, null=True)
    
    # Parish admins
    admins = models.ManyToManyField(
        'users.User',
        related_name='administered_parishes',
        blank=True
    )
    
    # Location details
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Settings
    is_active = models.BooleanField(default=True)
    allow_public_posts = models.BooleanField(default=True)
    allow_member_posts = models.BooleanField(default=True)
    require_admin_approval = models.BooleanField(default=False)
    
    # Donations
    enable_donations = models.BooleanField(default=False)
    donation_goal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    donation_description = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Parish')
        verbose_name_plural = _('Parishes')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.diocese.name}"
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def location_display(self):
        parts = [self.diocese.city, self.diocese.state_province, self.diocese.country]
        return ", ".join(filter(None, parts))


class ParishEvent(models.Model):
    """
    Events specific to a parish
    """
    parish = models.ForeignKey(
        Parish,
        on_delete=models.CASCADE,
        related_name='events'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Event timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    
    # Event details
    location = models.CharField(max_length=200, blank=True, null=True)
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('service', 'Church Service'),
            ('meeting', 'Meeting'),
            ('social', 'Social Event'),
            ('education', 'Educational'),
            ('youth', 'Youth Event'),
            ('charity', 'Charity Event'),
            ('other', 'Other'),
        ],
        default='other'
    )
    
    # Registration
    requires_registration = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    
    # Visibility
    is_public = models.BooleanField(default=True)
    
    # Media
    event_image = models.ImageField(upload_to='events/', blank=True, null=True)
    
    # Creator
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Parish Event')
        verbose_name_plural = _('Parish Events')
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.title} - {self.parish.name}" 