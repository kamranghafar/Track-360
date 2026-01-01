import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from dashboard.models import Resource

# Check if there are any resources
resources = Resource.objects.all()
if resources.exists():
    print(f"Found {resources.count()} resources:")
    for resource in resources:
        print(f"- {resource.name} ({resource.role})")
else:
    print("No resources found in the database.")