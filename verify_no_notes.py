import os
import django

# Set up Django settings before importing any Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from dashboard.models import WeeklyProductUpdate, WeeklyProductMeeting

# Get the meeting we just used in our test
meeting_id = 48
try:
    meeting = WeeklyProductMeeting.objects.get(id=meeting_id)
    print(f"Found meeting: {meeting}")
    
    # Get all product updates for this meeting
    updates = WeeklyProductUpdate.objects.filter(meeting=meeting)
    print(f"Found {updates.count()} product updates for this meeting")
    
    # Check if any of the updates have a notes field
    for update in updates:
        # Try to access the notes field - this should raise an AttributeError
        try:
            notes = update.notes
            print(f"WARNING: Product update for {update.project.name} has a notes field: {notes}")
        except AttributeError:
            print(f"Good: Product update for {update.project.name} does not have a notes field")
        
        # Check the to_dict method to ensure it doesn't include notes
        update_dict = update.to_dict()
        if 'notes' in update_dict:
            print(f"WARNING: to_dict() for {update.project.name} includes a 'notes' key")
        else:
            print(f"Good: to_dict() for {update.project.name} does not include a 'notes' key")
            
except WeeklyProductMeeting.DoesNotExist:
    print(f"Meeting with ID {meeting_id} does not exist.")