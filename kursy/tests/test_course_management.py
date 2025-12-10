from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from kursy.models import Course, CourseEdition

User = get_user_model()

class CourseManagementTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor', password='password', is_instructor=True
        )
        self.student = User.objects.create_user(
            username='student', password='password', is_instructor=False
        )
        self.edition = CourseEdition.objects.create(name='Edycja 1')
        
        self.course = Course.objects.create(
            name='Stary Kurs',
            description='Stary Opis',
            instructor=self.instructor,
            edition=self.edition
        )
        
        self.create_url = reverse('course_create')
        self.edit_url = reverse('course_edit', args=[self.course.id])
        self.client = Client()

    # --- CREATE TESTS ---

    def test_create_course_access(self):
        """Instruktor może wejść na formularz tworzenia kursu."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/course_form.html')

    def test_create_course_student_forbidden(self):
        """Student nie może tworzyć kursów."""
        self.client.force_login(self.student)
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 403)

    def test_create_course_submit_success(self):
        """Poprawne utworzenie kursu."""
        self.client.force_login(self.instructor)
        data = {
            'name': 'Nowy Kurs',
            'description': 'Opis kursu',
            'edition': self.edition.id,
            'is_visible': True
        }
        response = self.client.post(self.create_url, data)
        
        # Powinno przekierować do dashboardu lub listy lekcji (zależnie od implementacji view)
        # Zazwyczaj success_url w CreateView
        self.assertEqual(response.status_code, 302)
        
        # Sprawdzenie czy kurs powstał
        new_course = Course.objects.filter(name='Nowy Kurs').first()
        self.assertIsNotNone(new_course)
        self.assertEqual(new_course.instructor, self.instructor)

    # --- EDIT TESTS ---

    def test_edit_course_access_owner(self):
        """Właściciel kursu może go edytować."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.course)

    def test_edit_course_access_other_instructor(self):
        """Inny instruktor nie może edytować cudzego kursu."""
        other_instructor = User.objects.create_user(
            username='other', password='password', is_instructor=True
        )
        self.client.force_login(other_instructor)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 403)

    def test_edit_course_submit(self):
        """Zmiana danych kursu."""
        self.client.force_login(self.instructor)
        data = {
            'name': 'Zaktualizowany Kurs',
            'description': 'Nowy opis',
            'edition': self.edition.id,
            'is_visible': False
        }
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Zaktualizowany Kurs')
        self.assertFalse(self.course.is_visible)

