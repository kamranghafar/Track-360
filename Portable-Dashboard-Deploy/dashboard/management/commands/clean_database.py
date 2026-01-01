from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import (
    Resource, Project, ProjectResource, SprintCycle, OATReleaseCycle, 
    WeeklyMeeting, WeeklyProjectUpdate, WeeklyProductMeeting, ProductProblem, 
    WeeklyProductUpdate, Quarter, QuarterTarget, QuarterTargetResource, 
    ResourceLeave, Rock, ProductDocumentation, DepartmentDocument, 
    ProductionBug, RoadmapItem
)

class Command(BaseCommand):
    help = 'Deletes all data from the database while preserving the database structure'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning database - removing all data...')
        
        # Delete all existing data in reverse order of dependencies
        self.stdout.write('Deleting RoadmapItem data...')
        RoadmapItem.objects.all().delete()
        
        self.stdout.write('Deleting ProductionBug data...')
        ProductionBug.objects.all().delete()
        
        self.stdout.write('Deleting DepartmentDocument data...')
        DepartmentDocument.objects.all().delete()
        
        self.stdout.write('Deleting ProductDocumentation data...')
        ProductDocumentation.objects.all().delete()
        
        self.stdout.write('Deleting Rock data...')
        Rock.objects.all().delete()
        
        self.stdout.write('Deleting ResourceLeave data...')
        ResourceLeave.objects.all().delete()
        
        self.stdout.write('Deleting QuarterTargetResource data...')
        QuarterTargetResource.objects.all().delete()
        
        self.stdout.write('Deleting QuarterTarget data...')
        QuarterTarget.objects.all().delete()
        
        self.stdout.write('Deleting Quarter data...')
        Quarter.objects.all().delete()
        
        self.stdout.write('Deleting ProductProblem data...')
        ProductProblem.objects.all().delete()
        
        self.stdout.write('Deleting WeeklyProductUpdate data...')
        WeeklyProductUpdate.objects.all().delete()
        
        self.stdout.write('Deleting WeeklyProductMeeting data...')
        WeeklyProductMeeting.objects.all().delete()
        
        self.stdout.write('Deleting WeeklyProjectUpdate data...')
        WeeklyProjectUpdate.objects.all().delete()
        
        self.stdout.write('Deleting WeeklyMeeting data...')
        WeeklyMeeting.objects.all().delete()
        
        self.stdout.write('Deleting ProjectResource data...')
        ProjectResource.objects.all().delete()
        
        self.stdout.write('Deleting Project data...')
        Project.objects.all().delete()
        
        self.stdout.write('Deleting Resource data...')
        Resource.objects.all().delete()
        
        self.stdout.write('Deleting SprintCycle data...')
        SprintCycle.objects.all().delete()
        
        self.stdout.write('Deleting OATReleaseCycle data...')
        OATReleaseCycle.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('All data has been successfully removed from the database'))
        self.stdout.write(self.style.SUCCESS('Database structure has been preserved'))