"""
Views for Users app
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)
from apps.parishes.models import Parish


class UserViewSet(ModelViewSet):
    """
    ViewSet for user management
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Users can only see their own profile and parish members
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(parish=user.parish)


@extend_schema(
    operation_id='auth_register',
    summary='User Registration',
    description='Register a new user with parish assignment',
    request=UserRegistrationSerializer,
    responses={201: UserSerializer}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register a new user
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Send welcome email (optional)
        send_welcome_email(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful! Please check your email for verification.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='auth_login',
    summary='User Login',
    description='Authenticate user and return JWT tokens',
    request=LoginSerializer,
    responses={200: {'access': 'string', 'refresh': 'string', 'user': UserSerializer}}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """
    User login
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        return Response({
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': UserSerializer(user).data,
            'message': 'Login successful!'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='auth_logout',
    summary='User Logout',
    description='Logout user and blacklist refresh token'
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """
    User logout
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Logout successful!'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    """
    Update user profile
    """
    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change user password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully!'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='parishes_list',
    summary='List Parishes',
    description='Get list of all parishes for registration'
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_parishes(request):
    """
    List all parishes for registration
    """
    from apps.parishes.serializers import ParishListSerializer
    parishes = Parish.objects.filter(is_active=True).select_related('diocese')
    serializer = ParishListSerializer(parishes, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='auth_password_reset',
    summary='Password Reset Request',
    description='Send password reset email',
    request=PasswordResetSerializer
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """
    Request password reset
    """
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
            
            return Response({
                'message': 'Password reset email sent!'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            return Response({
                'message': 'If an account with this email exists, a password reset email has been sent.'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='auth_password_reset_confirm',
    summary='Password Reset Confirmation',
    description='Confirm password reset with token',
    request=PasswordResetConfirmSerializer
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """
    Confirm password reset
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Decode token and get user
            # Implementation depends on your token strategy
            # This is a simplified version
            uid = urlsafe_base64_decode(token).decode()
            user = User.objects.get(pk=uid)
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password reset successful!'
            }, status=status.HTTP_200_OK)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Helper functions
def send_welcome_email(user):
    """
    Send welcome email to new user
    """
    subject = 'Welcome to Coptic Social Network!'
    message = render_to_string('emails/welcome.html', {
        'user': user,
        'parish': user.parish
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True
    )


def send_password_reset_email(user):
    """
    Send password reset email
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    subject = 'Password Reset - Coptic Social Network'
    message = render_to_string('emails/password_reset.html', {
        'user': user,
        'token': uid,  # Simplified - use proper token in production
        'domain': settings.FRONTEND_URL
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True
    ) 