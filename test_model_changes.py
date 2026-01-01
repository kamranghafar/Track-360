import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from dashboard.models import WeeklyProductUpdate, WeeklyProductMeeting, Project

def test_model_changes():
    # Get a WeeklyProductUpdate instance
    update = WeeklyProductUpdate.objects.first()
    if update:
        print(f"WeeklyProductUpdate ID: {update.id}")
        print(f"Project: {update.project.name}")
        print(f"Meeting: {update.meeting}")
        print(f"Latest Project Updates: {update.latest_project_updates}")
        print(f"Notes: {update.notes}")
        print(f"Problems: {update.problems}")
        print(f"Expected Solution: {update.expected_solution}")
        print(f"Solution Timeline: {update.get_solution_timeline_display()}")
        
        # Test setting the notes field
        update.notes = "Test notes"
        update.save()
        print(f"Updated Notes: {update.notes}")
        
        # Verify the notes field was saved correctly
        updated_update = WeeklyProductUpdate.objects.get(id=update.id)
        print(f"Verified Notes: {updated_update.notes}")
    else:
        print("No WeeklyProductUpdate instances found.")
        
        # Create a test instance
        meeting = WeeklyProductMeeting.objects.first()
        project = Project.objects.first()
        
        if meeting and project:
            update = WeeklyProductUpdate.objects.create(
                meeting=meeting,
                project=project,
                latest_project_updates="Test latest updates",
                notes="Test notes",
                problems="Test problems",
                expected_solution="Test solution",
                solution_timeline="medium"
            )
            print(f"Created WeeklyProductUpdate ID: {update.id}")
            print(f"Notes: {update.notes}")
        else:
            print("No WeeklyProductMeeting or Project instances found.")

if __name__ == "__main__":
    test_model_changes()