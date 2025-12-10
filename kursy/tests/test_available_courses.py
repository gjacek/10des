from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from kursy.models import Course, CourseEdition, Enrollment

User = get_user_model()

class StudentAvailableCoursesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(username='student', email='student@example.com', password='password')
        self.instructor = User.objects.create_user(username='instructor', email='instructor@example.com', password='password', is_instructor=True)
        
        self.edition = CourseEdition.objects.create(name='2025/2026')
        
        # Course 1: Visible, no enrollment
        self.course1 = Course.objects.create(
            name='Course 1', 
            description='Desc 1', 
            instructor=self.instructor, 
            edition=self.edition,
            is_visible=True
        )
        
        # Course 2: Visible, pending enrollment
        self.course2 = Course.objects.create(
            name='Course 2', 
            description='Desc 2', 
            instructor=self.instructor, 
            edition=self.edition,
            is_visible=True
        )
        Enrollment.objects.create(student=self.student, course=self.course2, status='pending')
        
        # Course 3: Not visible
        self.course3 = Course.objects.create(
            name='Course 3', 
            description='Desc 3', 
            instructor=self.instructor, 
            edition=self.edition,
            is_visible=False
        )

    def test_view_context(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('student_available_courses'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/student/available_courses.html')
        
        courses_data = response.context['courses_with_status']
        # Should contain course1 and course2, but not course3
        self.assertEqual(len(courses_data), 2)
        
        # Check course 1 status
        c1_data = next(c for c in courses_data if c['course'].id == self.course1.id)
        self.assertEqual(c1_data['user_status'], 'none')
        
        # Check course 2 status
        c2_data = next(c for c in courses_data if c['course'].id == self.course2.id)
        self.assertEqual(c2_data['user_status'], 'pending')

class EnrollmentApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(username='student', email='student@example.com', password='password')
        self.instructor = User.objects.create_user(username='instructor', email='instructor@example.com', password='password', is_instructor=True)
        self.edition = CourseEdition.objects.create(name='2025/2026')
        
        self.course = Course.objects.create(
            name='Course API', 
            description='Desc', 
            instructor=self.instructor, 
            edition=self.edition,
            is_visible=True
        )

    def test_enroll_success(self):
        self.client.login(username='student', password='password')
        url = reverse('api_enroll_course', args=[self.course.id])
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], 'pending')
        
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course, status='pending').exists())

    def test_enroll_already_exists(self):
        self.client.login(username='student', password='password')
        Enrollment.objects.create(student=self.student, course=self.course, status='pending')
        
        url = reverse('api_enroll_course', args=[self.course.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'pending')

    def test_enroll_instructor_forbidden(self):
        self.client.login(username='instructor', password='password')
        url = reverse('api_enroll_course', args=[self.course.id])
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

