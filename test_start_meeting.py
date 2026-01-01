import os
import django

# Set up Django settings before importing any Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Now it's safe to import Django models
from django.test import Client
from django.urls import reverse
from dashboard.models import Project, WeeklyProductMeeting

client = Client()
meeting_id = 48  # The meeting ID from the error message

# First, check if the meeting exists
try:
    meeting = WeeklyProductMeeting.objects.get(id=meeting_id)
    print(f"Found meeting: {meeting}")
except WeeklyProductMeeting.DoesNotExist:
    print(f"Meeting with ID {meeting_id} does not exist. Creating a test meeting...")
    meeting = WeeklyProductMeeting.objects.create(
        title="Test Manual Meeting",
        meeting_date="2025-07-14 14:06:57"
    )
    meeting_id = meeting.id
    print(f"Created test meeting with ID: {meeting_id}")

# Get some projects to select for the meeting
projects = Project.objects.all()[:3]  # Get up to 3 projects
if not projects:
    print("No projects found. Creating a test project...")
    project = Project.objects.create(name="Test Project")
    projects = [project]

project_ids = [str(project.id) for project in projects]
print(f"Selected projects: {', '.join([project.name for project in projects])}")

# Step 1: Send initial POST to get to the product selection page
print("\nStep 1: Initiating meeting start process...")
response = client.post(reverse('start-weekly-product-meeting', args=[meeting_id]))
print(f"Status code: {response.status_code}")

# Step 2: Send POST with select_products parameter
print("\nStep 2: Selecting products for the meeting...")
response = client.post(
    reverse('start-weekly-product-meeting', args=[meeting_id]),
    {'select_products': 'true'}
)
print(f"Status code: {response.status_code}")

# Step 3: Send POST with start_meeting parameter and selected projects
print("\nStep 3: Starting the meeting with selected products...")
response = client.post(
    reverse('start-weekly-product-meeting', args=[meeting_id]),
    {'start_meeting': 'true', 'selected_projects': project_ids}
)
print(f"Status code: {response.status_code}")

if response.status_code == 302:  # Successful redirect
    print("Meeting started successfully!")
else:
    print("Error starting meeting:", response.content.decode()[:500] + "..." if len(response.content) > 500 else response.content.decode())
