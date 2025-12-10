from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from kursy.models import Course, CourseEdition, Lesson, Enrollment

User = get_user_model()

class StudentCourseDetailViewTests(TestCase):
    def setUp(self):
        # Users
        self.instructor = User.objects.create_user(
            username='instructor', password='password', is_instructor=True
        )
        self.student_approved = User.objects.create_user(
            username='student_approved', password='password'
        )
        self.student_pending = User.objects.create_user(
            username='student_pending', password='password'
        )
        self.student_rejected = User.objects.create_user(
            username='student_rejected', password='password'
        )
        self.student_no_enrollment = User.objects.create_user(
            username='student_no_enrollment', password='password'
        )

        # Course Edition
        self.edition = CourseEdition.objects.create(name='Edycja 1')

        # Course
        self.course = Course.objects.create(
            name='Kurs Testowy',
            description='Opis kursu',
            instructor=self.instructor,
            edition=self.edition,
            is_visible=True
        )

        self.hidden_course = Course.objects.create(
            name='Kurs Ukryty',
            instructor=self.instructor,
            edition=self.edition,
            is_visible=False
        )

        # Enrollments
        Enrollment.objects.create(student=self.student_approved, course=self.course, status='approved')
        Enrollment.objects.create(student=self.student_pending, course=self.course, status='pending')
        Enrollment.objects.create(student=self.student_rejected, course=self.course, status='rejected')
        
        # Enrollment for hidden course
        Enrollment.objects.create(student=self.student_approved, course=self.hidden_course, status='approved')

        # Lessons
        self.lesson_published_1 = Lesson.objects.create(
            title='B Lekcja', course=self.course, is_published=True, description='Opis'
        )
        self.lesson_published_2 = Lesson.objects.create(
            title='A Lekcja', course=self.course, is_published=True, description='Opis'
        )
        self.lesson_draft = Lesson.objects.create(
            title='C Lekcja (Draft)', course=self.course, is_published=False, description='Opis'
        )

        self.url = reverse('student_course_detail', args=[self.course.id])
        self.hidden_url = reverse('student_course_detail', args=[self.hidden_course.id])
        self.client = Client()

    def test_access_unauthenticated(self):
        """Niezalogowany użytkownik jest przekierowywany."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_access_unauthorized_student(self):
        """Student bez zapisu dostaje 403 Forbidden."""
        self.client.force_login(self.student_no_enrollment)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_pending_enrollment(self):
        """Student ze statusem pending dostaje 403 Forbidden."""
        self.client.force_login(self.student_pending)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_rejected_enrollment(self):
        """Student ze statusem rejected dostaje 403 Forbidden."""
        self.client.force_login(self.student_rejected)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_hidden_course(self):
        """Kurs ukryty zwraca 404 nawet dla zapisanego studenta."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.hidden_url)
        self.assertEqual(response.status_code, 404)

    def test_access_success(self):
        """Student z zatwierdzonym zapisem ma dostęp (200)."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/course_detail.html')

    def test_lessons_visibility_and_order(self):
        """Student widzi tylko opublikowane lekcje, posortowane alfabetycznie."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.url)
        
        lessons = list(response.context['lessons'])
        
        # Powinny być 2 lekcje (draft ukryty)
        self.assertEqual(len(lessons), 2)
        
        # Sortowanie alfabetyczne po tytule: 'A Lekcja', potem 'B Lekcja'
        self.assertEqual(lessons[0], self.lesson_published_2)
        self.assertEqual(lessons[1], self.lesson_published_1)
        
        # Draft nie powinien być w ogóle na liście
        self.assertNotIn(self.lesson_draft, lessons)

    def test_course_details_in_context(self):
        """Szczegóły kursu są w kontekście."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.url)
        self.assertEqual(response.context['course'], self.course)
        self.assertContains(response, self.course.name)
        self.assertContains(response, self.course.description)
        self.assertContains(response, self.instructor.last_name)

