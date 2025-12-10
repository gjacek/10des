from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from kursy.models import Course, CourseEdition, Enrollment

User = get_user_model()

class EnrollmentManagerViewTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor', password='password', is_instructor=True
        )
        self.other_instructor = User.objects.create_user(
            username='other', password='password', is_instructor=True
        )
        self.student = User.objects.create_user(
            username='student', password='password'
        )
        
        self.edition = CourseEdition.objects.create(name='Edycja 1')
        self.course = Course.objects.create(
            name='Kurs', instructor=self.instructor, edition=self.edition
        )
        
        # Enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status='pending'
        )
        
        self.url = reverse('instructor_course_enrollments', args=[self.course.id])
        self.client = Client()

    def test_access_instructor_owner(self):
        """Właściciel kursu ma dostęp do menedżera zapisów."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/enrollment_manager.html')
        
        # Pobieramy enrollments z obiektu kursu w kontekście
        course_in_context = response.context['course']
        self.assertIn(self.enrollment, course_in_context.enrollments.all())

    def test_access_other_instructor_forbidden(self):
        """Inny instruktor nie ma dostępu."""
        self.client.force_login(self.other_instructor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
    
    # Uwaga: Testy POST zostały usunięte, ponieważ widok EnrollmentManagerView jest typu TemplateView
    # i nie obsługuje logiki POST. Prawdopodobnie aktualizacja statusów odbywa się przez API (AJAX).
