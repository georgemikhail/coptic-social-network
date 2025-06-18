"""
Serializers for Users app
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile
from apps.parishes.models import Parish


class ParishSerializer(serializers.ModelSerializer):
    """
    Basic Parish serializer for user registration
    """
    diocese_name = serializers.CharField(source='diocese.name', read_only=True)
    location = serializers.CharField(source='location_display', read_only=True)
    
    class Meta:
        model = Parish
        fields = ['id', 'name', 'diocese_name', 'location', 'priest_name', 'address']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User Profile serializer
    """
    class Meta:
        model = UserProfile
        fields = [
            'custom_fields', 'email_notifications', 'push_notifications',
            'parish_notifications', 'show_email', 'show_phone', 'show_social_links'
        ]


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for references and lists
    """
    full_name = serializers.CharField(read_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'profile_picture', 'is_verified'
        ]
        read_only_fields = ['id', 'email', 'is_verified']
    
    def get_profile_picture(self, obj):
        """
        Handle empty profile_picture fields
        """
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for profile management
    """
    profile = UserProfileSerializer(read_only=True)
    parish = ParishSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'gender', 'bio',
            'profile_picture', 'linkedin_url', 'facebook_url', 'instagram_url',
            'parish', 'profile_visibility', 'is_verified', 'email_verified',
            'created_at', 'profile'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'email_verified', 'created_at']
    
    def get_profile_picture(self, obj):
        """
        Handle empty profile_picture fields
        """
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    parish_id = serializers.IntegerField(write_only=True)
    terms_accepted = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'parish_id', 'gender', 'date_of_birth', 'phone_number',
            'terms_accepted'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError("You must accept the terms and conditions.")
        
        # Validate parish exists
        try:
            parish = Parish.objects.get(id=attrs['parish_id'])
            attrs['parish'] = parish
        except Parish.DoesNotExist:
            raise serializers.ValidationError("Invalid parish selected.")
        
        return attrs
    
    def create(self, validated_data):
        # Remove non-model fields
        validated_data.pop('password_confirm')
        validated_data.pop('terms_accepted')
        parish = validated_data.pop('parish')
        
        # Create user
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.parish = parish
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    User login serializer
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer
    """
    current_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Update user profile serializer
    """
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'bio', 'profile_picture', 'linkedin_url',
            'facebook_url', 'instagram_url', 'profile_visibility', 'profile'
        ]
    
    def update(self, instance, validated_data):
        # Handle profile data separately
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class PasswordResetSerializer(serializers.Serializer):
    """
    Password reset request serializer
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Password reset confirmation serializer
    """
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs 