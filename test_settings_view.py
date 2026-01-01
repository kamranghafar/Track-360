import os
import django

# Set up Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Now import Django models and utilities
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_settings_view():
    # Create a test client
    client = Client()

    # Create a test user if one doesn't exist
    username = 'testuser'
    password = 'testpassword'

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password)

    # Log in the user
    login_successful = client.login(username=username, password=password)
    print(f"Login successful: {login_successful}")

    # Access the settings page
    response = client.get(reverse('settings'), follow=True)

    # Print information about redirects
    if response.redirect_chain:
        print("Redirects occurred:")
        for redirect_url, status_code in response.redirect_chain:
            print(f"  Redirected to {redirect_url} with status code {status_code}")

    # Check if the final response is successful
    if response.status_code == 200:
        print("Success! The settings page loaded without errors.")
        print(f"Final URL: {response.request['PATH_INFO']}")
    else:
        print(f"Error: The settings page returned status code {response.status_code}")
        print(f"Final URL: {response.request['PATH_INFO'] if 'PATH_INFO' in response.request else 'Unknown'}")

if __name__ == "__main__":
    # Run the test
    test_settings_view()
