from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from kursy.models import Course, CourseEdition, Lesson

User = get_user_model()

class CourseLessonsViewTests(TestCase):
    def setUp(self):
        # Create users
        self.instructor = User.objects.create_user(
            username='instructor', 
            password='password',
            email='inst@test.com',
            is_instructor=True
        )
        self.other_instructor = User.objects.create_user(
            username='other_instructor', 
            password='password',
            email='other@test.com',
            is_instructor=True
        )
        self.student = User.objects.create_user(
            username='student', 
            password='password',
            email='student@test.com',
            is_instructor=False
        )
        
        # Create course edition
        self.edition = CourseEdition.objects.create(name='Edycja 1')
        
        # Create courses
        self.course = Course.objects.create(
            name='Kurs Testowy',
            description='Opis',
            instructor=self.instructor,
            edition=self.edition
        )
        self.other_course = Course.objects.create(
            name='Kurs Innego Instruktora',
            description='Opis',
            instructor=self.other_instructor,
            edition=self.edition
        )
        
        # Create lessons
        self.lesson1 = Lesson.objects.create(
            title='Lekcja 1',
            description='Opis 1',
            course=self.course,
            is_published=True
        )
        self.lesson2 = Lesson.objects.create(
            title='Lekcja 2',
            description='Opis 2',
            course=self.course,
            is_published=False
        )

        self.url = reverse('instructor_course_lessons', args=[self.course.id])
        self.client = Client()

    def test_instructor_can_access_own_course_lessons(self):
        """Instruktor powinien mieć dostęp do widoku swoich lekcji."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/course_lessons.html')
        self.assertIn('lessons', response.context)
        self.assertEqual(len(response.context['lessons']), 2)
        
        # Sprawdzenie czy adnotacja files_count istnieje
        first_lesson = response.context['lessons'][0]
        self.assertTrue(hasattr(first_lesson, 'files_count'))

    def test_instructor_cannot_access_other_course_lessons(self):
        """Instruktor nie powinien widzieć lekcji innego instruktora (powinien dostać 404)."""
        self.client.force_login(self.other_instructor)
        response = self.client.get(self.url)
        
        # Oczekujemy 404, ponieważ w widoku używamy get_object_or_404 z filtrem na instruktora
        self.assertEqual(response.status_code, 404)

    def test_student_cannot_access_lessons_view(self):
        """Student nie powinien mieć dostępu do widoku zarządzania lekcjami (403)."""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        
        # UserPassesTestMixin powinien zwrócić 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_redirect(self):
        """Niezalogowany użytkownik powinien zostać przekierowany do logowania."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_context_contains_correct_data(self):
        """Kontekst powinien zawierać poprawne dane kursu i lekcji."""
        self.client.force_login(self.instructor)
        response = self.client.get(self.url)
        
        self.assertEqual(response.context['course'], self.course)
        lessons = list(response.context['lessons'])
        self.assertIn(self.lesson1, lessons)
        self.assertIn(self.lesson2, lessons)

