"""
Widoki API dla autentykacji użytkowników.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


def get_tokens_for_user(user):
    """
    Generuje tokeny JWT dla użytkownika.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view_api(request):
    """
    API endpoint dla logowania użytkownika.
    
    POST /api/auth/login/
    Request: {"email": "user@example.com", "password": "password123"}
    Response: {"token": "jwt_token", "user": {...}}
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT token
        tokens = get_tokens_for_user(user)
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        return Response({
            'token': tokens['access'],  # Return only access token for simplicity
            'refresh': tokens['refresh'],  # Include refresh token as well
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    
    # Return validation errors
    return Response({
        'detail': serializer.errors.get('non_field_errors', ['Nieprawidłowe dane logowania.'])[0]
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view_api(request):
    """
    API endpoint dla rejestracji nowego użytkownika.
    
    POST /api/auth/register/
    Request: {"email": "...", "first_name": "...", "last_name": "...", "password": "..."}
    Response: {"id": ..., "email": "...", "first_name": "...", "last_name": "..."}
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        user_serializer = UserSerializer(user)
        
        return Response(
            user_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    # Return validation errors
    errors = serializer.errors
    if 'email' in errors:
        detail = errors['email'][0]
    else:
        detail = 'Błąd walidacji danych.'
    
    return Response({
        'detail': detail,
        'errors': errors
    }, status=status.HTTP_400_BAD_REQUEST)

