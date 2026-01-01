from django.core.management.base import BaseCommand
from dashboard.models import (
    Resource, Project, ProjectResource, SprintCycle, OATReleaseCycle, 
    WeeklyMeeting, WeeklyProjectUpdate, WeeklyProductMeeting, ProductProblem, 
    WeeklyProductUpdate, Quarter, QuarterTarget, QuarterTargetResource, 
    ResourceLeave, Rock, ProductDocumentation, DepartmentDocument, 
    ProductionBug, RoadmapItem
)

class Command(BaseCommand):
    help = 'Verifies that all tables in the database are empty'

    def handle(self, *args, **options):
        self.stdout.write('Verifying that all tables are empty...')
        
        # Define a dictionary of models to check
        models_to_check = {
            'Resource': Resource,
            'Project': Project,
            'ProjectResource': ProjectResource,
            'SprintCycle': SprintCycle,
            'OATReleaseCycle': OATReleaseCycle,
            'WeeklyMeeting': WeeklyMeeting,
            'WeeklyProjectUpdate': WeeklyProjectUpdate,
            'WeeklyProductMeeting': WeeklyProductMeeting,
            'ProductProblem': ProductProblem,
            'WeeklyProductUpdate': WeeklyProductUpdate,
            'Quarter': Quarter,
            'QuarterTarget': QuarterTarget,
            'QuarterTargetResource': QuarterTargetResource,
            'ResourceLeave': ResourceLeave,
            'Rock': Rock,
            'ProductDocumentation': ProductDocumentation,
            'DepartmentDocument': DepartmentDocument,
            'ProductionBug': ProductionBug,
            'RoadmapItem': RoadmapItem
        }
        
        # Check each model and count rows
        total_rows = 0
        for model_name, model in models_to_check.items():
            count = model.objects.count()
            total_rows += count
            
            if count == 0:
                self.stdout.write(self.style.SUCCESS(f'{model_name}: {count} rows (empty)'))
            else:
                self.stdout.write(self.style.ERROR(f'{model_name}: {count} rows (not empty)'))
        
        # Print total rows
        if total_rows == 0:
            self.stdout.write(self.style.SUCCESS(f'\nTotal rows across all tables: {total_rows}'))
            self.stdout.write(self.style.SUCCESS('All tables are empty. Database has been successfully cleaned.'))
        else:
            self.stdout.write(self.style.ERROR(f'\nTotal rows across all tables: {total_rows}'))
            self.stdout.write(self.style.ERROR('Some tables still contain data. Database cleaning was not complete.'))