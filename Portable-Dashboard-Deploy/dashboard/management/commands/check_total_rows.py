from django.core.management.base import BaseCommand
from dashboard.models import Resource, Project, ProjectResource, WeeklyMeeting, WeeklyProjectUpdate, Quarter, QuarterTarget, QuarterTargetResource, WeeklyProductMeeting, WeeklyProductUpdate

class Command(BaseCommand):
    help = 'Checks total rows of data in the database'

    def handle(self, *args, **options):
        self.stdout.write('Checking total rows of data...')
        
        # Count rows in each model
        resource_count = Resource.objects.count()
        project_count = Project.objects.count()
        project_resource_count = ProjectResource.objects.count()
        weekly_meeting_count = WeeklyMeeting.objects.count()
        weekly_project_update_count = WeeklyProjectUpdate.objects.count()
        weekly_product_meeting_count = WeeklyProductMeeting.objects.count()
        weekly_product_update_count = WeeklyProductUpdate.objects.count()
        quarter_count = Quarter.objects.count()
        quarter_target_count = QuarterTarget.objects.count()
        quarter_target_resource_count = QuarterTargetResource.objects.count()
        
        # Calculate total rows
        total_rows = (
            resource_count +
            project_count +
            project_resource_count +
            weekly_meeting_count +
            weekly_project_update_count +
            weekly_product_meeting_count +
            weekly_product_update_count +
            quarter_count +
            quarter_target_count +
            quarter_target_resource_count
        )
        
        # Print counts
        self.stdout.write(f'Resources: {resource_count}')
        self.stdout.write(f'Projects (Products): {project_count}')
        self.stdout.write(f'Project Resources: {project_resource_count}')
        self.stdout.write(f'Weekly Meetings: {weekly_meeting_count}')
        self.stdout.write(f'Weekly Project Updates: {weekly_project_update_count}')
        self.stdout.write(f'Weekly Product Meetings: {weekly_product_meeting_count}')
        self.stdout.write(f'Weekly Product Updates: {weekly_product_update_count}')
        self.stdout.write(f'Quarters: {quarter_count}')
        self.stdout.write(f'Quarter Targets: {quarter_target_count}')
        self.stdout.write(f'Quarter Target Resources: {quarter_target_resource_count}')
        
        self.stdout.write(f'\nTotal rows: {total_rows}')