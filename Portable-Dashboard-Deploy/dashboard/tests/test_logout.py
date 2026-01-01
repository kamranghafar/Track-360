from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class LogoutTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        # Create a test client
        self.client = Client()

    def test_logout_functionality_post(self):
        """Test logout functionality using POST request"""
        # First, log in the user
        login_successful = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login_successful, "Login failed")

        # Verify the user is logged in
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200, "User should be able to access dashboard when logged in")

        # Now log out the user using POST request
        response = self.client.post(reverse('logout'))

        # Check the response status code (should be 200 or 302)
        self.assertIn(response.status_code, [200, 302], "Logout response should be 200 or 302")

        # If it's a redirect, check that it redirects to the login page
        if response.status_code == 302:
            self.assertEqual(response.url, reverse('login'), "Should redirect to login page")

        # Verify the user is logged out
        # Django test client has a user property that tells us if the user is authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated, "User should be logged out after logout request")

        # Try to access a protected page
        response = self.client.get(reverse('dashboard'))

        # Check if we're redirected to the login page
        self.assertEqual(response.status_code, 302, "Should be redirected when accessing protected page while logged out")
        expected_redirect = f"{reverse('login')}?next={reverse('dashboard')}"
        self.assertTrue(response.url.startswith(reverse('login')), f"Should redirect to login page, got {response.url}")

    def test_logout_functionality_get(self):
        """Test logout functionality using GET request"""
        # First, log in the user
        login_successful = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login_successful, "Login failed")

        # Verify the user is logged in
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200, "User should be able to access dashboard when logged in")

        # Now log out the user using GET request
        response = self.client.get(reverse('logout'))

        # Check the response status code (should be 200 or 302)
        self.assertIn(response.status_code, [200, 302], "Logout response should be 200 or 302")

        # If it's a redirect, check that it redirects to the login page
        if response.status_code == 302:
            self.assertEqual(response.url, reverse('login'), "Should redirect to login page")

        # Verify the user is logged out
        # Django test client has a user property that tells us if the user is authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated, "User should be logged out after logout request")

        # Try to access a protected page
        response = self.client.get(reverse('dashboard'))

        # Check if we're redirected to the login page
        self.assertEqual(response.status_code, 302, "Should be redirected when accessing protected page while logged out")
        expected_redirect = f"{reverse('login')}?next={reverse('dashboard')}"
        self.assertTrue(response.url.startswith(reverse('login')), f"Should redirect to login page, got {response.url}")
