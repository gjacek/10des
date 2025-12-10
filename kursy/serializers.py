from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Course, CourseEdition, Enrollment, Lesson, Attachment


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


class CourseEditionSerializer(serializers.ModelSerializer):
    """
    Serializer dla edycji kursu.
    """
    class Meta:
        model = CourseEdition
        fields = ['id', 'name']


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer dla modelu Course.
    """
    edition = CourseEditionSerializer(read_only=True)
    edition_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseEdition.objects.all(), source='edition', write_only=True
    )
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'is_visible', 'edition', 'edition_id', 'instructor']
        read_only_fields = ['id', 'instructor']

    def create(self, validated_data):
        # Assign instructor from context request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['instructor'] = request.user
        return super().create(validated_data)


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer dla modelu Lesson.
    """
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'is_published', 'course']
        read_only_fields = ['id', 'course']

    def create(self, validated_data):
        # Course ID should be passed in context or managed by view
        # Here we rely on the view to set the course, or we expect it in data?
        # Typically the view logic handles setting the course based on URL param.
        return super().create(validated_data)


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer dla modelu Attachment.
    """
    file_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'original_filename', 'file', 'file_url', 'download_count', 'size']
        extra_kwargs = {'file': {'write_only': True}}

    def get_file_url(self, obj):
        return obj.file.url

    def get_size(self, obj):
        try:
            return obj.file.size
        except:
            return 0


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer dla zapisów na kurs.
    """
    student = UserSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'status', 'student']
