from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Resource, Project, Quarter, QuarterTarget, QuarterTargetResource
import random
from datetime import timedelta, date
import decimal

class Command(BaseCommand):
    help = 'Adds dummy data for Quarter Targets for current and previous years'

    def handle(self, *args, **options):
        self.stdout.write('Adding Quarter Targets dummy data...')

        # Get current year
        current_year = timezone.now().year
        
        # Define years to create quarters for (current year and previous year)
        years_to_create = [current_year - 1, current_year]
        
        # Quarter names
        quarter_names = [
            "Q1 Planning and Strategy",
            "Q2 Development and Implementation",
            "Q3 Testing and Refinement",
            "Q4 Deployment and Review"
        ]
        
        # Target descriptions for variety
        target_descriptions = [
            "Increase test automation coverage to {coverage}%",
            "Reduce manual testing effort by {reduction}%",
            "Implement {count} new automated test suites",
            "Integrate {count} new testing tools",
            "Complete automation for {count} critical features",
            "Achieve {coverage}% code coverage in unit tests",
            "Reduce test execution time by {reduction}%",
            "Implement CI/CD pipeline for {count} projects",
            "Optimize {count} test scenarios for better performance",
            "Develop {count} reusable test components"
        ]
        
        # Statistics for created data
        quarters_created = 0
        quarter_targets_created = 0
        quarter_target_resources_created = 0
        
        # Create quarters for each year
        for year in years_to_create:
            self.stdout.write(f'Creating quarters for year {year}...')
            
            # Create all 4 quarters for the year
            for quarter_number in range(1, 5):
                quarter, created = Quarter.objects.get_or_create(
                    year=year,
                    quarter_number=quarter_number,
                    defaults={
                        'name': quarter_names[quarter_number-1],
                        # The start_date and end_date will be auto-calculated in the save method
                    }
                )
                
                # Mark previous year quarters as completed
                if year < current_year:
                    if not quarter.completed:
                        quarter.completed = True
                        quarter.completion_date = date(year, ((quarter_number - 1) * 3 + 3), 28)  # Last day of the quarter's last month
                        quarter.completion_notes = f"Completed quarter with {random.randint(75, 95)}% of targets achieved"
                        quarter.save()
                
                # Mark current year's past quarters as completed
                current_quarter = (timezone.now().month - 1) // 3 + 1
                if year == current_year and quarter_number < current_quarter:
                    if not quarter.completed:
                        quarter.completed = True
                        last_month = min(((quarter_number - 1) * 3 + 3), 12)
                        quarter.completion_date = date(year, last_month, 28)  # Last day of the quarter's last month
                        quarter.completion_notes = f"Completed quarter with {random.randint(75, 95)}% of targets achieved"
                        quarter.save()
                
                if created:
                    quarters_created += 1
                
                # Get all projects
                projects = list(Project.objects.all())
                if not projects:
                    self.stdout.write(self.style.WARNING('No projects found. Please run add_dummy_data.py first.'))
                    return
                
                # For previous year, create targets for all projects
                # For current year, create targets for 60-80% of projects
                if year < current_year:
                    num_projects = len(projects)
                    selected_projects = projects
                else:
                    num_projects = int(len(projects) * random.uniform(0.6, 0.8))
                    selected_projects = random.sample(projects, num_projects)
                
                for project in selected_projects:
                    # Create a quarter target for this project
                    description_template = random.choice(target_descriptions)
                    
                    # Fill in the template with random values
                    if '{coverage}' in description_template:
                        description = description_template.format(coverage=random.randint(60, 95))
                    elif '{reduction}' in description_template:
                        description = description_template.format(reduction=random.randint(20, 50))
                    elif '{count}' in description_template:
                        description = description_template.format(count=random.randint(2, 10))
                    else:
                        description = description_template
                    
                    target_value = random.randint(50, 100)
                    
                    # For previous year and completed current year quarters, set achieved values
                    achieved_value = None
                    achievement_notes = ""
                    
                    if year < current_year or (year == current_year and quarter_number < current_quarter):
                        # For completed quarters, set achieved values
                        achievement_percentage = random.uniform(0.7, 1.2)  # 70% to 120% achievement
                        achieved_value = int(target_value * achievement_percentage)
                        
                        if achievement_percentage >= 1:
                            achievement_notes = f"Successfully achieved target with {int((achievement_percentage - 1) * 100)}% over target"
                        else:
                            achievement_notes = f"Partially achieved target with {int(achievement_percentage * 100)}% completion"
                    
                    quarter_target, target_created = QuarterTarget.objects.get_or_create(
                        quarter=quarter,
                        project=project,
                        defaults={
                            'target_description': description,
                            'target_value': target_value,
                            'achieved_value': achieved_value,
                            'achievement_notes': achievement_notes
                        }
                    )
                    
                    # Update existing targets if not created
                    if not target_created and (achieved_value is not None) and quarter_target.achieved_value is None:
                        quarter_target.achieved_value = achieved_value
                        quarter_target.achievement_notes = achievement_notes
                        quarter_target.save()
                    
                    if target_created:
                        quarter_targets_created += 1
                        
                        # Assign 2-4 resources to this quarter target
                        num_resources = random.randint(2, 4)
                        resources = list(Resource.objects.all())
                        
                        if not resources:
                            self.stdout.write(self.style.WARNING('No resources found. Please run add_dummy_data.py first.'))
                            continue
                            
                        selected_resources = random.sample(resources, min(num_resources, len(resources)))
                        
                        for resource in selected_resources:
                            allocation = decimal.Decimal(random.randint(25, 100))
                            
                            QuarterTargetResource.objects.create(
                                quarter_target=quarter_target,
                                resource=resource,
                                allocation_percentage=allocation,
                                notes=f"Allocated at {allocation}% for {quarter.name} target"
                            )
                            quarter_target_resources_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {quarters_created} quarters with {quarter_targets_created} targets and {quarter_target_resources_created} resource assignments'))
        
        # Count total quarters and targets
        total_quarters = Quarter.objects.count()
        total_targets = QuarterTarget.objects.count()
        total_resources = QuarterTargetResource.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'Total quarters in database: {total_quarters}'))
        self.stdout.write(self.style.SUCCESS(f'Total quarter targets in database: {total_targets}'))
        self.stdout.write(self.style.SUCCESS(f'Total quarter target resources in database: {total_resources}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully added Quarter Targets dummy data'))