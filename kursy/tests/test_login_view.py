from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.begin_url = reverse('begin')

    def test_login_view_access_anonymous(self):
        """Test that the login page is accessible for anonymous users."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_redirect_authenticated(self):
        """Test that authenticated users are redirected to 'begin'."""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com', 
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_login(user)
        response = self.client.get(self.url)
        # Expect redirect to 'begin'
        self.assertRedirects(response, self.begin_url, target_status_code=302)

