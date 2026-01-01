from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class LoginTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        # Create a test client
        self.client = Client()

    def test_login_page_loads(self):
        """Test that the login page loads without errors"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/login.html')

    def test_login_functionality(self):
        """Test login functionality"""
        # Try to login with correct credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        # Check if login was successful (should redirect to dashboard)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)