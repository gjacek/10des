"""
Serializery dla API REST aplikacji kursowej.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer dla modelu CustomUser.
    Zwraca podstawowe informacje o użytkowniku.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_instructor']
        read_only_fields = ['id', 'is_instructor']


class LoginSerializer(serializers.Serializer):
    """
    Serializer dla żądania logowania.
    Waliduje email i hasło, zwraca token JWT oraz dane użytkownika.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Walidacja danych logowania.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Authenticate using email instead of username
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Django uses username field, but we use email
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    'Nieprawidłowy e-mail lub hasło.',
                    code='authorization'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'Konto użytkownika jest nieaktywne.',
                    code='authorization'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Wymagane są pola "email" i "password".',
                code='authorization'
            )


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer dla rejestracji nowego użytkownika.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def validate_email(self, value):
        """
        Sprawdza czy email jest unikalny.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ten adres e-mail jest już zarejestrowany.')
        return value

    def create(self, validated_data):
        """
        Tworzy nowego użytkownika z zahaszowanym hasłem.
        """
        user = CustomUser.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

