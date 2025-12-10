from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from kursy.models import Course, CourseEdition, Lesson, Enrollment, Attachment

User = get_user_model()

class StudentLessonDetailViewTests(TestCase):
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

        # Enrollments
        Enrollment.objects.create(student=self.student_approved, course=self.course, status='approved')
        Enrollment.objects.create(student=self.student_pending, course=self.course, status='pending')
        Enrollment.objects.create(student=self.student_rejected, course=self.course, status='rejected')

        # Lessons
        self.lesson = Lesson.objects.create(
            title='Lekcja 1', course=self.course, is_published=True, description='Opis lekcji'
        )
        self.lesson_unpublished = Lesson.objects.create(
            title='Lekcja Ukryta', course=self.course, is_published=False, description='Opis ukrytej'
        )
        
        # Another course lesson
        self.other_course = Course.objects.create(
            name='Inny Kurs',
            instructor=self.instructor,
            edition=self.edition,
            is_visible=True
        )
        self.other_lesson = Lesson.objects.create(
            title='Lekcja Inna', course=self.other_course, is_published=True
        )

        # Attachments
        self.attachment = Attachment.objects.create(
            lesson=self.lesson,
            file=SimpleUploadedFile("test.txt", b"content"),
            original_filename="test.txt"
        )

        self.url = reverse('student_lesson_detail', kwargs={'course_id': self.course.id, 'lesson_id': self.lesson.id})
        self.unpublished_url = reverse('student_lesson_detail', kwargs={'course_id': self.course.id, 'lesson_id': self.lesson_unpublished.id})
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

    def test_access_unpublished_lesson(self):
        """Nieopublikowana lekcja zwraca 404."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.unpublished_url)
        self.assertEqual(response.status_code, 404)

    def test_access_success(self):
        """Student z zatwierdzonym zapisem ma dostęp (200)."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/lesson_detail.html')
        self.assertContains(response, self.lesson.title)
        self.assertContains(response, self.lesson.description)

    def test_attachments_in_context(self):
        """Załączniki są w kontekście i wyświetlane."""
        self.client.force_login(self.student_approved)
        response = self.client.get(self.url)
        
        attachments = list(response.context['attachments'])
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0], self.attachment)
        self.assertContains(response, self.attachment.original_filename)

    def test_access_lesson_wrong_course(self):
        """Próba dostępu do lekcji z innego kursu przez URL (mismatch ID)."""
        # URL z ID kursu, który nie zawiera tej lekcji
        url_mismatch = reverse('student_lesson_detail', kwargs={'course_id': self.other_course.id, 'lesson_id': self.lesson.id})
        
        self.client.force_login(self.student_approved)
        # Powinno zwrócić 404, bo get_queryset filtruje po course_id
        response = self.client.get(url_mismatch)
        self.assertEqual(response.status_code, 404)

