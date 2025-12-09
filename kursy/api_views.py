from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.db import transaction
import json
from .models import Course, Enrollment
from .serializers import CourseSerializer, LoginSerializer, EnrollmentSerializer

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
