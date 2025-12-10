from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import Course, Enrollment, Lesson, Attachment
from .serializers import CourseSerializer, LoginSerializer, EnrollmentSerializer, LessonSerializer, AttachmentSerializer

# Custom permission check for Instructor
def is_instructor(user):
    return user.is_authenticated and user.is_instructor

@require_POST
def login_view_api(request):
    """
    Tradycyjny widok logowania API (bez DRF na razie, dla kompatybilności).
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if not user.is_active:
                return JsonResponse({'detail': 'Konto użytkownika jest nieaktywne.'}, status=401)
            
            login(request, user)
            return JsonResponse({
                'detail': 'Successfully logged in.',
                'user': {
                    'email': user.email,
                    'is_instructor': user.is_instructor
                }
            })
        else:
            return JsonResponse({'detail': 'Nieprawidłowy e-mail lub hasło.'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON.'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_api(request):
    """
    Inicjuje proces resetowania hasła (wysyłka email).
    """
    User = get_user_model()
    email = request.data.get('email')

    if not email:
         return Response({'email': ['To pole jest wymagane.']}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()

    if user:
        # Generowanie tokenu i linku (na razie logujemy link w konsoli, 
        # w produkcji wysyłamy email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Przykład linku (zakładamy frontend/widok do ustawienia nowego hasła)
        # reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
        
        # TODO: Skonfigurować SMTP i wysłać email
        # send_mail(
        #     'Reset hasła',
        #     f'Kliknij tutaj, aby zresetować hasło: {reset_link}',
        #     settings.DEFAULT_FROM_EMAIL,
        #     [email],
        #     fail_silently=False,
        # )
        
        # Dla celów deweloperskich/testowych (bez SMTP) - symulacja sukcesu
        pass
    else:
        # Zgodnie z planem: "Email not found" dla 400 Bad Request
        # (Chociaż bezpieczniej byłoby zawsze zwracać 200 OK)
        return Response({'message': 'Email not found.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Wysłano email z informacjami o resecie hasła.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view_api(request):
    """
    Rejestracja nowego użytkownika.
    """
    User = get_user_model()
    data = request.data
    
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    errors = {}
    
    if not email:
        errors.setdefault('email', []).append('This field is required.')
    elif User.objects.filter(email=email).exists():
        errors.setdefault('email', []).append('User with this email already exists.')
        
    if not password:
        errors.setdefault('password', []).append('This field is required.')
    elif len(password) < 8:
        errors.setdefault('password', []).append('Password must be at least 8 characters long.')
        
    if not first_name:
        errors.setdefault('first_name', []).append('This field is required.')
        
    if not last_name:
        errors.setdefault('last_name', []).append('This field is required.')
        
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        # Username is required by default User model, use email as username
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_list_create_api(request):
    """
    GET: Lista kursów (publiczna/zapisana).
    POST: Tworzenie nowego kursu (tylko instruktor).
    """
    if request.method == 'GET':
        # TODO: Implement filtering for students (public visible + enrolled)
        # For now, simplistic implementation for instructor/testing
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not is_instructor(request.user):
            return Response({'detail': 'Tylko instruktorzy mogą tworzyć kursy.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CourseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def course_detail_api(request, pk):
    """
    Obsługa pojedynczego kursu.
    """
    course = get_object_or_404(Course, pk=pk)

    # Check permissions for modification
    if request.method in ['PUT', 'PATCH', 'DELETE']:
        if request.user != course.instructor:
            return Response({'detail': 'Brak uprawnień do edycji tego kursu.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = CourseSerializer(course, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Optional: check if can delete (e.g. no students enrolled)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course_api(request, course_id):
    """
    Wysyłanie prośby o zapisanie na kurs przez studenta.
    """
    course = get_object_or_404(Course, pk=course_id)
    
    # Sprawdź czy kurs jest widoczny
    if not course.is_visible:
        return Response({'detail': 'Kurs nie jest dostępny.'}, status=status.HTTP_404_NOT_FOUND)
        
    # Sprawdź czy użytkownik jest studentem (nie instruktorem)
    if request.user.is_instructor:
        return Response({'detail': 'Instruktorzy nie mogą zapisywać się na kursy.'}, status=status.HTTP_403_FORBIDDEN)

    # Sprawdź czy już jest zapisany
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if enrollment:
        return Response({
            'detail': 'Już wysłano zgłoszenie lub jesteś zapisany.',
            'status': enrollment.status
        }, status=status.HTTP_400_BAD_REQUEST)
        
    # Utwórz zapis
    Enrollment.objects.create(
        student=request.user,
        course=course,
        status='pending'
    )
    
    return Response({
        'message': 'Enrollment request sent.',
        'status': 'pending'
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enrollment_list_api(request, course_id):
    """
    Pobiera listę zapisów na dany kurs (tylko dla instruktora).
    Parametr ?status=pending|approved|rejected filtruje wyniki.
    """
    course = get_object_or_404(Course, pk=course_id)
    
    if request.user != course.instructor:
        return Response({'detail': 'Brak uprawnień do przeglądania zapisów.'}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.query_params.get('status')
    queryset = course.enrollments.all()
    
    if status_filter in ['pending', 'approved', 'rejected']:
        queryset = queryset.filter(status=status_filter)
        
    serializer = EnrollmentSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enrollment_bulk_update_api(request, course_id):
    """
    Masowa aktualizacja statusów zapisów (approve, reject, delete, restore).
    """
    course = get_object_or_404(Course, pk=course_id)
    
    if request.user != course.instructor:
        return Response({'detail': 'Brak uprawnień do zarządzania zapisami.'}, status=status.HTTP_403_FORBIDDEN)
        
    action = request.data.get('action')
    enrollment_ids = request.data.get('enrollment_ids', [])
    
    if not enrollment_ids or not isinstance(enrollment_ids, list):
        return Response({'detail': 'Nieprawidłowa lista ID.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if action not in ['approve', 'reject', 'delete', 'restore']:
        return Response({'detail': 'Nieprawidłowa akcja.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            enrollments = Enrollment.objects.filter(
                id__in=enrollment_ids, 
                course=course
            ).select_for_update()
            
            # Weryfikacja czy wszystkie ID należą do tego kursu
            if enrollments.count() != len(enrollment_ids):
                # Można tu rzucić błąd albo zignorować brakujące. 
                # Bezpieczniej rzucić błąd spójności.
                 return Response({'detail': 'Niektóre zapisy nie należą do tego kursu lub nie istnieją.'}, status=status.HTTP_400_BAD_REQUEST)

            if action == 'approve':
                # Tylko z pending/rejected na approved? Zazwyczaj z pending.
                # Ale restore też robi to samo.
                enrollments.update(status='approved')
                
            elif action == 'reject':
                enrollments.update(status='rejected')
                
            elif action == 'restore':
                enrollments.update(status='approved')
                
            elif action == 'delete':
                # Usuwanie rekordów (np. wyrzucenie z kursu)
                enrollments.delete()
                
        return Response({'message': 'Operacja zakończona sukcesem.', 'updated_count': len(enrollment_ids)})
        
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lesson_list_create_api(request, course_id):
    """
    GET: Lista lekcji dla kursu.
    POST: Tworzenie lekcji (tylko instruktor).
    """
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'GET':
        # Dla instruktora kursu: wszystkie lekcje
        # Dla studenta: tylko opublikowane
        if request.user == course.instructor:
            lessons = course.lessons.all()
        else:
            # TODO: check enrollment status
            lessons = course.lessons.filter(is_published=True)
            
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user != course.instructor:
            return Response({'detail': 'Brak uprawnień do tworzenia lekcji w tym kursie.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course) # course is managed by URL, not payload usually
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def lesson_detail_api(request, course_id, pk):
    """
    Operacje na pojedynczej lekcji.
    """
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(Lesson, pk=pk, course=course)

    if request.method in ['PUT', 'PATCH', 'DELETE']:
        if request.user != course.instructor:
            return Response({'detail': 'Brak uprawnień do edycji tej lekcji.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if not lesson.is_published and request.user != course.instructor:
             return Response({'detail': 'Nie znaleziono lekcji.'}, status=status.HTTP_404_NOT_FOUND)
             
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = LessonSerializer(lesson, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def attachment_list_create_api(request, course_id, lesson_id):
    """
    GET: Lista załączników lekcji.
    POST: Dodanie załącznika (tylko instruktor).
    """
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)

    if request.method == 'GET':
        # Sprawdź dostęp (instruktor lub student zapisany)
        # TODO: check enrollment status for student
        if not lesson.is_published and request.user != course.instructor:
             return Response({'detail': 'Brak dostępu.'}, status=status.HTTP_403_FORBIDDEN)
        
        attachments = lesson.attachments.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user != course.instructor:
            return Response({'detail': 'Brak uprawnień do dodawania plików.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Limit liczby plików (max 10)
        if lesson.attachments.count() >= 10:
             return Response({'detail': 'Przekroczono limit 10 załączników dla tej lekcji.'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'detail': 'Brak pliku.'}, status=status.HTTP_400_BAD_REQUEST)

        # Limit rozmiaru (10MB)
        if file_obj.size > 10 * 1024 * 1024:
             return Response({'detail': 'Plik jest za duży (max 10MB).'}, status=status.HTTP_400_BAD_REQUEST)

        # Walidacja rozszerzenia
        import os
        allowed_extensions = ['.pdf', '.zip', '.pptx', '.docx', '.txt', '.jpg', '.jpeg']
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in allowed_extensions:
             return Response({'detail': f'Niedozwolone rozszerzenie: {ext}'}, status=status.HTTP_400_BAD_REQUEST)

        # Serializer save - pass file in data
        # Note: Model expects 'file' and 'original_filename'
        data = {'file': file_obj, 'original_filename': file_obj.name}
        serializer = AttachmentSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def attachment_detail_api(request, course_id, lesson_id, pk):
    """
    DELETE: Usunięcie załącznika.
    """
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
    attachment = get_object_or_404(Attachment, pk=pk, lesson=lesson)

    if request.user != course.instructor:
        return Response({'detail': 'Brak uprawnień do usuwania plików.'}, status=status.HTTP_403_FORBIDDEN)

    attachment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
