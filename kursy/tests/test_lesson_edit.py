from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from kursy.models import Course, CourseEdition, Lesson, Attachment
import json

User = get_user_model()

class LessonEditViewTests(TestCase):
    def setUp(self):
        # Create users
        self.instructor = User.objects.create_user(
            username='instructor', 
            email='inst@test.com', 
            password='password', 
            is_instructor=True
        )
        self.other_instructor = User.objects.create_user(
            username='other', 
            email='other@test.com', 
            password='password', 
            is_instructor=True
        )
        
        # Create course structure
        self.edition = CourseEdition.objects.create(name='Edycja 1')
        self.course = Course.objects.create(
            name='Kurs',
            description='Opis',
            instructor=self.instructor,
            edition=self.edition
        )
        self.lesson = Lesson.objects.create(
            title='Lekcja',
            description='Opis',
            course=self.course,
            is_published=False
        )
        
        self.url = reverse('instructor_lesson_edit', kwargs={
            'course_id': self.course.id, 
            'lesson_id': self.lesson.id
        })
        self.client = Client()

    def test_view_access(self):
        # Owner access
        self.client.force_login(self.instructor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/lesson_edit.html')

        # Other instructor access (should be 404 because queryset filters by user)
        self.client.force_login(self.other_instructor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_lesson_update(self):
        self.client.force_login(self.instructor)
        data = {
            'title': 'Nowy Tytuł',
            'description': 'Nowy Opis',
            'is_published': 'on'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302) # Redirect after success
        
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Nowy Tytuł')
        self.assertTrue(self.lesson.is_published)


class AttachmentAPITests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor', email='inst@test.com', password='password', is_instructor=True
        )
        self.other_instructor = User.objects.create_user(
            username='other', email='other@test.com', password='password', is_instructor=True
        )
        self.student = User.objects.create_user(
            username='student', email='student@test.com', password='password', is_instructor=False
        )
        
        self.edition = CourseEdition.objects.create(name='Edycja 1')
        self.course = Course.objects.create(
            name='Kurs', instructor=self.instructor, edition=self.edition
        )
        self.lesson = Lesson.objects.create(
            title='Lekcja', course=self.course
        )
        
        self.list_create_url = reverse('api_attachment_list_create', kwargs={
            'course_id': self.course.id, 'lesson_id': self.lesson.id
        })

    def test_upload_file(self):
        self.client.force_login(self.instructor)
        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        
        response = self.client.post(
            self.list_create_url,
            {'file': file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attachment.objects.count(), 1)
        self.assertEqual(Attachment.objects.first().original_filename, 'test.txt')

    def test_upload_invalid_extension(self):
        self.client.force_login(self.instructor)
        file = SimpleUploadedFile("test.exe", b"content", content_type="application/x-msdownload")
        
        response = self.client.post(
            self.list_create_url,
            {'file': file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Niedozwolone rozszerzenie', response.json()['detail'])

    def test_upload_limit(self):
        self.client.force_login(self.instructor)
        # Create 10 attachments
        for i in range(10):
            Attachment.objects.create(
                lesson=self.lesson,
                original_filename=f'file_{i}.txt',
                file='path/to/file'
            )
            
        file = SimpleUploadedFile("new.txt", b"content", content_type="text/plain")
        response = self.client.post(
            self.list_create_url,
            {'file': file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('limit', response.json()['detail'])

    def test_delete_attachment(self):
        self.client.force_login(self.instructor)
        att = Attachment.objects.create(
            lesson=self.lesson,
            original_filename='test.txt',
            file='path/to/file'
        )
        
        url = reverse('api_attachment_detail', kwargs={
            'course_id': self.course.id,
            'lesson_id': self.lesson.id,
            'pk': att.id
        })
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Attachment.objects.count(), 0)

    def test_student_cannot_modify(self):
        self.client.force_login(self.student)
        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        
        response = self.client.post(
            self.list_create_url,
            {'file': file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

