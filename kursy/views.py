from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from .models import Course, Lesson, Enrollment, Attachment
from .forms import CourseForm, LessonCreateForm, LessonUpdateForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('begin')
    return render(request, 'registration/login.html')

def register_view(request):
    """
    Widok rejestracji nowego użytkownika.
    """
    if request.user.is_authenticated:
        return redirect('begin')
    return render(request, 'registration/register.html')

def password_reset_view(request):
    """
    Widok resetu hasła (formularz email).
    """
    if request.user.is_authenticated:
        return redirect('begin')
    return render(request, 'registration/password_reset.html')

def logout_view(request):
    """
    Wylogowuje użytkownika i przekierowuje do strony logowania.
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
            status='approved',
            course__is_visible=True
        ).select_related('course', 'course__edition', 'course__instructor')
        
        courses = [enrollment.course for enrollment in enrollments]
        context['courses'] = courses
        return context

class StudentAvailableCoursesView(LoginRequiredMixin, TemplateView):
    """
    Widok 'Dostępne Kursy' dla studenta (Katalog).
    Prezentuje listę wszystkich kursów w systemie, które mają status "Widoczny".
    """
    template_name = 'courses/student/available_courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Pobierz wszystkie widoczne kursy
        visible_courses = Course.objects.filter(is_visible=True).select_related('instructor', 'edition')
        
        # 2. Pobierz zapisy studenta
        student_enrollments = Enrollment.objects.filter(
            student=self.request.user
        ).values('course_id', 'status')
        
        enrollment_map = {e['course_id']: e['status'] for e in student_enrollments}
        
        # 3. Zbuduj strukturę danych dla szablonu
        courses_with_status = []
        for course in visible_courses:
            status = enrollment_map.get(course.id, 'none')
            courses_with_status.append({
                'course': course,
                'user_status': status
            })
            
        context['courses_with_status'] = courses_with_status
        return context

def begin(request):
    """
    Widok startowy po zalogowaniu.
    Przekierowuje na odpowiedni dashboard w zależności od roli użytkownika.
    """
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.user.is_instructor:
        return redirect('instructor_dashboard')
    else:
        return redirect('student_my_courses')

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

class CourseCreateView(InstructorCourseMixin, CreateView):
    """
    Widok tworzenia nowego kursu.
    """
    model = Course
    form_class = CourseForm
    template_name = 'instructor/course_form.html'
    success_url = reverse_lazy('instructor_dashboard')

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)

class CourseUpdateView(InstructorCourseMixin, TemplateView):
    """
    Widok edycji kursu (bez formularza na razie, jako placeholder lub prosty widok).
    W przyszłości można zmienić na UpdateView.
    """
    template_name = 'instructor/course_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id)
        
        # Sprawdzenie uprawnień (czy kurs należy do instruktora)
        if course.instructor != self.request.user:
            raise PermissionDenied("Nie masz uprawnień do edycji tego kursu.")

        context['form'] = CourseForm(instance=course)
        context['object'] = course # Dla kompatybilności z szablonem
        context['page_title'] = f'Edycja kursu: {course.name}'
        return context
    
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id)
        
        if course.instructor != self.request.user:
            raise PermissionDenied("Nie masz uprawnień do edycji tego kursu.")
            
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('instructor_dashboard')
            
        return render(request, self.template_name, {'form': form, 'object': course, 'page_title': f'Edycja kursu: {course.name}'})

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

class CourseLessonsView(InstructorCourseMixin, TemplateView):
    """
    Widok zarządzania lekcjami kursu.
    """
    template_name = 'instructor/course_lessons.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        
        context['course'] = course
        context['lessons'] = course.lessons.all().order_by('title')
        return context

class LessonUpdateView(InstructorCourseMixin, UpdateView):
    """
    Widok edycji lekcji.
    """
    model = Lesson
    form_class = LessonUpdateForm
    template_name = 'instructor/lesson_edit.html'
    pk_url_kwarg = 'lesson_id'
    context_object_name = 'lesson'

    def get_queryset(self):
        # Upewniamy się, że lekcja należy do kursu instruktora
        return Lesson.objects.filter(course__instructor=self.request.user)

    def get_success_url(self):
        return reverse('instructor_course_lessons', kwargs={'course_id': self.object.course.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context

class LessonCreateView(InstructorCourseMixin, CreateView):
    """
    Widok tworzenia lekcji.
    """
    model = Lesson
    form_class = LessonCreateForm
    template_name = 'instructor/lesson_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs.get('course_id'), instructor=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context

    def get_success_url(self):
        return reverse_lazy('instructor_lesson_edit', kwargs={'course_id': self.object.course.id, 'lesson_id': self.object.id})


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    """
    Widok szczegółów kursu dla studenta.
    Dostępny tylko dla zalogowanych studentów z zatwierdzonym zapisem.
    """
    model = Course
    template_name = 'student/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        # Pobieramy tylko widoczne kursy, optymalizujemy zapytania
        return Course.objects.filter(is_visible=True).select_related('instructor', 'edition')

    def get_object(self, queryset=None):
        course = super().get_object(queryset)
        
        # Sprawdzenie czy student jest zapisany i zatwierdzony
        has_enrollment = Enrollment.objects.filter(
            student=self.request.user,
            course=course,
            status='approved'
        ).exists()
        
        if not has_enrollment:
            raise PermissionDenied("Nie masz dostępu do tego kursu (wymagany zatwierdzony zapis).")
            
        return course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pobieranie tylko opublikowanych lekcji
        context['lessons'] = self.object.lessons.filter(is_published=True).order_by('title')
        return context


class StudentLessonDetailView(LoginRequiredMixin, DetailView):
    """
    Widok szczegółów lekcji dla studenta.
    Dostępny tylko dla studentów zapisanych na kurs (zatwierdzony zapis).
    Wyświetla treść lekcji i załączniki.
    """
    model = Lesson
    template_name = 'student/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_id'

    def get_queryset(self):
        # Pobieramy tylko opublikowane lekcje w ramach danego kursu
        course_id = self.kwargs.get('course_id')
        return Lesson.objects.filter(
            course_id=course_id,
            is_published=True
        ).select_related('course')

    def get_object(self, queryset=None):
        lesson = super().get_object(queryset)
        course = lesson.course

        # Sprawdzenie czy student jest zapisany i zatwierdzony na kurs
        has_enrollment = Enrollment.objects.filter(
            student=self.request.user,
            course=course,
            status='approved'
        ).exists()

        if not has_enrollment:
            raise PermissionDenied("Nie masz dostępu do tej lekcji (wymagany zatwierdzony zapis na kurs).")
        
        return lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Przekazujemy kurs do kontekstu (np. do nawigacji)
        context['course'] = self.object.course
        # Załączniki do lekcji
        context['attachments'] = self.object.attachments.all()
        return context
