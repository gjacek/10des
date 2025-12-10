from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from kursy.models import Course, CourseEdition, Enrollment

User = get_user_model()

class InstructorDashboardViewTests(TestCase):
    def setUp(self):
        # Users
        self.instructor = User.objects.create_user(
            username='instructor', password='password', is_instructor=True
        )
        self.other_instructor = User.objects.create_user(
            username='other_instructor', password='password', is_instructor=True
        )
        self.student = User.objects.create_user(
            username='student', password='password', is_instructor=False
        )
        
        # Data setup
        self.edition = CourseEdition.objects.create(name='Edycja 1')
        
        # Course owned by instructor
        self.course_1 = Course.objects.create(
            name='Kurs 1', instructor=self.instructor, edition=self.edition
        )
        # Course owned by other instructor
        self.course_2 = Course.objects.create(
            name='Kurs 2', instructor=self.other_instructor, edition=self.edition
        )

        # Enrollments
        # Pending enrollment for instructor's course
        Enrollment.objects.create(student=self.student, course=self.course_1, status='pending')

        self.url = reverse('instructor_dashboard')
        self.client = Client()

    def test_access_unauthenticated(self):
        """Niezalogowany użytkownik jest przekierowywany."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_access_unauthorized_student(self):
        """Student nie ma dostępu do dashboardu instruktora."""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_success_instructor(self):
        """Instruktor ma dostęp do swojego dashboardu."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor_dashboard.html')

    def test_dashboard_context_data(self):
        """Dashboard pokazuje poprawne dane (kursy instruktora, liczba oczekujących)."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.url)
        
        # Sprawdź czy kursy są w kontekście
        courses = response.context['courses']
        self.assertIn(self.course_1, courses)
        self.assertNotIn(self.course_2, courses) # Nie powinien widzieć kursu innego instruktora

        # Sprawdź czy pending_enrollments_count jest poprawnie policzone
        # (Jeden enrollment pending dla course_1)
        self.assertEqual(courses[0].pending_count, 1)

    def test_dashboard_empty_for_new_instructor(self):
        """Nowy instruktor widzi pustą listę kursów."""
        new_instructor = User.objects.create_user(
            username='new_inst', password='password', is_instructor=True
        )
        self.client.force_login(new_instructor)
        response = self.client.get(self.url)
        
        self.assertEqual(len(response.context['courses']), 0)

