from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class RegistrationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_view_access(self):
        """Test that the registration page is accessible."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_view_redirect_authenticated(self):
        """Test that authenticated users are redirected."""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com', 
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_login(user)
        response = self.client.get(self.url)
        # Expect redirect to 'begin', which itself is a redirect (302)
        self.assertRedirects(response, reverse('begin'), target_status_code=302)

class RegistrationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api_register')

    def test_register_success(self):
        """Test successful registration via API."""
        data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        self.assertEqual(response.data['email'], 'newuser@example.com')
        
        # Verify default fields if any (e.g., is_active)
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(user.is_active)

    def test_register_duplicate_email(self):
        """Test registration with existing email fails."""
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com', 
            password='password123'
        )
        
        data = {
            'email': 'existing@example.com',
            'password': 'newpassword123',
            'first_name': 'Another',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'User with this email already exists.')

    def test_register_short_password(self):
        """Test registration with short password fails."""
        data = {
            'email': 'shortpass@example.com',
            'password': 'short',
            'first_name': 'Short',
            'last_name': 'Pass'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'Password must be at least 8 characters long.')

    def test_register_missing_fields(self):
        """Test registration with missing fields fails."""
        data = {
            'email': '',
            'password': '',
            # Missing names
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

