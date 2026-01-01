import os
import django

# Set up Django settings before importing any Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Now it's safe to import Django models
from django.test import Client
from django.urls import reverse
from dashboard.models import WeeklyProductMeeting, WeeklyProductUpdate

client = Client()
meeting_id = 48  # The meeting ID from the error message

# First, check if the meeting exists
try:
    meeting = WeeklyProductMeeting.objects.get(id=meeting_id)
    print(f"Found meeting: {meeting}")
    
    # Check if the meeting is already completed
    if meeting.is_completed:
        print(f"Meeting is already completed. Setting it back to active for testing...")
        meeting.is_completed = False
        meeting.save()
    
    # Check if there are product updates for this meeting
    updates = WeeklyProductUpdate.objects.filter(meeting=meeting)
    print(f"Found {updates.count()} product updates for this meeting")
    
    if updates.count() == 0:
        print("No product updates found for this meeting. Cannot test ending the meeting.")
        exit(1)
    
    # Try to end the meeting
    print("\nAttempting to end the meeting...")
    response = client.post(reverse('end-weekly-product-meeting', args=[meeting_id]))
    
    if response.status_code == 302:  # Successful redirect
        print("Meeting ended successfully!")
        
        # Verify the meeting is now marked as completed
        meeting.refresh_from_db()
        if meeting.is_completed:
            print("Meeting is now marked as completed.")
        else:
            print("WARNING: Meeting is not marked as completed after ending.")
    else:
        print("Error ending meeting:", response.content.decode()[:500] + "..." if len(response.content) > 500 else response.content.decode())
    
except WeeklyProductMeeting.DoesNotExist:
    print(f"Meeting with ID {meeting_id} does not exist.")