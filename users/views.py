from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer
)

@api_view(['GET','POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'GET':
        return Response({
            'message': 'User registration endpoint',
            'method': 'POST',
            'required_fields': ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        })

    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        # Create the user
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Return user data and tokens
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    # Return errors if validation failed
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logs the user out by blacklisting their refresh token.

    Client sends: {"refresh": "<refresh_token>"}

    Important nuance to understand: JWT access tokens are stateless — they
    are validated by signature + expiry alone, with no database lookup.
    That means blacklisting only stops the refresh token from being used
    to mint new access tokens; the *current* access token stays valid
    until it naturally expires (up to ACCESS_TOKEN_LIFETIME, currently
    60 minutes in your settings). This is the standard trade-off with
    stateless auth. If you need "logout means instantly blocked", the
    options are: shorten ACCESS_TOKEN_LIFETIME, or check a blacklist on
    every request (which defeats the point of using stateless JWTs).
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response(
            {'error': 'Token is invalid or already expired/blacklisted.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {'message': 'Logged out successfully.'},
        status=status.HTTP_205_RESET_CONTENT
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user's profile

    Requires: JWT token in Authorization header
    Returns: user data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update current user's profile

    Requires: JWT token
    Accepts: Any of the updatable fields
    Returns: updated user data
    """
    serializer = UserUpdateSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)