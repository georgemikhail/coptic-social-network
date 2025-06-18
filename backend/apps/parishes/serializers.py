"""
Serializers for Parishes app
"""
from rest_framework import serializers
from .models import Diocese, Parish, ParishEvent


class DioceseSerializer(serializers.ModelSerializer):
    """
    Diocese serializer
    """
    parish_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Diocese
        fields = [
            'id', 'name', 'description', 'bishop_name', 'bishop_title',
            'bishop_photo', 'address', 'phone_number', 'email', 'website',
            'country', 'state_province', 'city', 'is_active', 'parish_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ParishBasicSerializer(serializers.ModelSerializer):
    """
    Basic Parish serializer for references and lists
    """
    diocese_name = serializers.CharField(source='diocese.name', read_only=True)
    location = serializers.CharField(source='location_display', read_only=True)
    
    class Meta:
        model = Parish
        fields = [
            'id', 'name', 'diocese_name', 'location', 'priest_name',
            'address', 'phone_number', 'email', 'logo'
        ]
        read_only_fields = ['id']


class ParishListSerializer(serializers.ModelSerializer):
    """
    Simplified Parish serializer for lists
    """
    diocese_name = serializers.CharField(source='diocese.name', read_only=True)
    diocese_country = serializers.CharField(source='diocese.country', read_only=True)
    location = serializers.CharField(source='location_display', read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Parish
        fields = [
            'id', 'name', 'diocese_name', 'diocese_country', 'location',
            'priest_name', 'address', 'phone_number', 'email', 'website',
            'member_count', 'cover_image', 'logo'
        ]


class ParishDetailSerializer(serializers.ModelSerializer):
    """
    Detailed Parish serializer
    """
    diocese = DioceseSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    location = serializers.CharField(source='location_display', read_only=True)
    
    class Meta:
        model = Parish
        fields = [
            'id', 'name', 'description', 'diocese', 'priest_name', 'priest_title',
            'priest_photo', 'deacons', 'address', 'phone_number', 'email', 'website',
            'cover_image', 'logo', 'service_schedule', 'facebook_page', 'youtube_channel',
            'whatsapp_group', 'telegram_group', 'latitude', 'longitude', 'timezone',
            'location', 'is_active', 'allow_public_posts', 'allow_member_posts',
            'require_admin_approval', 'enable_donations', 'donation_goal',
            'donation_description', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'member_count', 'created_at', 'updated_at']


class ParishEventSerializer(serializers.ModelSerializer):
    """
    Parish Event serializer
    """
    parish_name = serializers.CharField(source='parish.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = ParishEvent
        fields = [
            'id', 'parish', 'parish_name', 'title', 'description',
            'start_datetime', 'end_datetime', 'is_all_day', 'location',
            'event_type', 'requires_registration', 'max_attendees',
            'registration_deadline', 'is_public', 'event_image',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CreateParishEventSerializer(serializers.ModelSerializer):
    """
    Create Parish Event serializer
    """
    class Meta:
        model = ParishEvent
        fields = [
            'title', 'description', 'start_datetime', 'end_datetime',
            'is_all_day', 'location', 'event_type', 'requires_registration',
            'max_attendees', 'registration_deadline', 'is_public', 'event_image'
        ]
    
    def create(self, validated_data):
        # Set the parish and creator from the request context
        user = self.context['request'].user
        validated_data['parish'] = user.parish
        validated_data['created_by'] = user
        return super().create(validated_data) 