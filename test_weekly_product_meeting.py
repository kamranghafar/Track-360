import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_weekly_product_meeting_detail():
    client = Client()
    # Try to access the weekly product meeting detail page with ID 5
    response = client.get(reverse('weekly-product-meeting-detail', kwargs={'pk': 5}))
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Success! The page loaded without errors.")
    else:
        print(f"Error: {response.content}")

if __name__ == "__main__":
    test_weekly_product_meeting_detail()