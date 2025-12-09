from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.contrib.auth import logout
from .models import Enrollment, Course, CourseEdition
from .serializers import CourseSerializer, CourseEditionSerializer

def begin(request):
    return HttpResponse("Hello world!")

def login_view(request):
    """
    Widok logowania - strona główna aplikacji.
    Renderuje formularz logowania z integracją Alpine.js.
    """
    return render(request, 'registration/login.html')

def logout_view(request):
    """
    Wylogowuje użytkownika i przekierowuje na stronę główną.
    """
    logout(request)
    return redirect('login')

class StudentMyCoursesView(LoginRequiredMixin, TemplateView):
    """
    Widok 'Moje Kursy' dla studenta.
    Wyświetla listę kursów, na które student jest zapisany i ma status 'approved'.
    """
    template_name = 'my_courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pobieranie zatwierdzonych zapisów dla zalogowanego użytkownika
        enrollments = Enrollment.objects.filter(
            student=self.request.user, 
            status='approved'
        ).select_related('course', 'course__edition', 'course__instructor')
        
        courses = [enrollment.course for enrollment in enrollments]
        context['courses'] = courses
        return context

class InstructorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Widok Dashboardu Prowadzącego.
    Wyświetla listę kursów prowadzonych przez zalogowanego instruktora
    wraz z licznikiem oczekujących zapisów.
    """
    template_name = 'instructor_dashboard.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Course.objects.filter(instructor=self.request.user).annotate(
            pending_count=Count('enrollments', filter=Q(enrollments__status='pending'))
        ).select_related('edition')
        context['courses'] = courses
        return context

class InstructorCourseMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin sprawdzający uprawnienia instruktora.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor

class CourseCreateView(InstructorCourseMixin, TemplateView):
    """
    Widok tworzenia nowego kursu.
    """
    template_name = 'instructor/course_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        editions = CourseEdition.objects.all()
        editions_data = CourseEditionSerializer(editions, many=True).data
        context['editions_data'] = editions_data
        context['initial_data'] = {}
        context['page_title'] = 'Tworzenie kursu'
        return context

class CourseUpdateView(InstructorCourseMixin, TemplateView):
    """
    Widok edycji kursu.
    """
    template_name = 'instructor/course_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        
        editions = CourseEdition.objects.all()
        editions_data = CourseEditionSerializer(editions, many=True).data
        course_data = CourseSerializer(course).data
        
        context['editions_data'] = editions_data
        context['initial_data'] = course_data
        context['page_title'] = f'Edycja kursu: {course.name}'
        return context

class EnrollmentManagerView(InstructorCourseMixin, TemplateView):
    """
    Widok zarządzania zapisami na kurs.
    """
    template_name = 'instructor/enrollment_manager.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        
        context['course'] = course
        return context
