from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Resource, Project, ProjectResource, SprintCycle, OATReleaseCycle, WeeklyMeeting, WeeklyProjectUpdate
import random
from datetime import timedelta
import decimal

class Command(BaseCommand):
    help = 'Deletes all existing data and adds new data with 10 projects and 15 resources'

    def handle(self, *args, **options):
        self.stdout.write('Deleting all existing data...')
        
        # Delete all existing data in reverse order of dependencies
        WeeklyProjectUpdate.objects.all().delete()
        WeeklyMeeting.objects.all().delete()
        ProjectResource.objects.all().delete()
        Project.objects.all().delete()
        Resource.objects.all().delete()
        SprintCycle.objects.all().delete()
        OATReleaseCycle.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('All existing data deleted successfully'))
        
        # Create Sprint Cycles
        sprint_cycles = [
            'Bi-weekly',
            'Monthly',
            'Quarterly',
            'Weekly',
            'Custom'
        ]
        
        for cycle in sprint_cycles:
            SprintCycle.objects.create(
                name=cycle,
                description=f'Sprint cycle that runs {cycle.lower()}',
                active=True
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(sprint_cycles)} sprint cycles'))
        
        # Create OAT Release Cycles
        oat_cycles = [
            'Monthly',
            'Quarterly',
            'Bi-annual',
            'Annual',
            'On-demand'
        ]
        
        for cycle in oat_cycles:
            OATReleaseCycle.objects.create(
                name=cycle,
                description=f'OAT release cycle that runs {cycle.lower()}',
                active=True
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(oat_cycles)} OAT release cycles'))
        
        # Create 15 Resources
        resource_names = [
            'John Smith', 'Jane Doe', 'Michael Johnson', 'Emily Williams', 'David Brown',
            'Sarah Miller', 'Robert Wilson', 'Jennifer Moore', 'William Taylor', 'Linda Anderson',
            'James Thomas', 'Patricia Jackson', 'Richard White', 'Barbara Harris', 'Charles Martin'
        ]
        
        roles = ['QA Engineer', 'Automation Engineer', 'Test Lead', 'QA Manager', 'SDET']
        skills = ['automation', 'manual', 'both']
        
        resources = []
        for name in resource_names:
            first_name = name.split()[0].lower()
            last_name = name.split()[1].lower()
            email = f"{first_name}.{last_name}@example.com"
            
            resource = Resource.objects.create(
                name=name,
                email=email,
                role=random.choice(roles),
                skill=random.choice(skills),
                availability=random.choice([True, True, True, False])  # 75% available
            )
            resources.append(resource)
        
        self.stdout.write(self.style.SUCCESS(f'Created 15 resources'))
        
        # Create 10 Projects
        project_names = [
            'Customer Portal', 'Mobile App', 'Payment Gateway', 'Inventory System',
            'CRM Integration', 'Data Analytics Platform', 'E-commerce Website',
            'Content Management System', 'API Gateway', 'Authentication Service'
        ]
        
        statuses = ['not_started', 'in_progress', 'completed', 'on_hold']
        automation_statuses = ['hold', 'completed', 'in_progress', 'na']
        pipeline_schedules = ['on_demand', 'weekly', 'nightly', 'na']
        
        projects = []
        for name in project_names:
            start_date = timezone.now() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(90, 365))
            
            # Randomly select a team lead
            team_lead = random.choice(resources) if resources else None
            
            # Generate random test case counts
            total_automatable = random.randint(50, 200)
            total_automated = random.randint(0, total_automatable)
            total_automatable_smoke = random.randint(10, 50)
            total_automated_smoke = random.randint(0, total_automatable_smoke)
            
            project = Project.objects.create(
                name=name,
                description=f'This is a project for {name}',
                start_date=start_date,
                end_date=end_date,
                status=random.choice(statuses),
                budget=decimal.Decimal(random.randint(10000, 100000)),
                smoke_automation_status=random.choice(automation_statuses),
                regression_automation_status=random.choice(automation_statuses),
                pipeline_schedule=random.choice(pipeline_schedules),
                execution_time_of_smoke=f"{random.randint(0, 2)}h {random.randint(1, 59)}m",
                total_number_of_available_test_cases=random.randint(100, 300),
                status_of_last_automation_run=random.choice(['Passed', 'Failed', 'Partial', 'Not Run']),
                date_of_last_automation_run=timezone.now() - timedelta(days=random.randint(1, 30)),
                automation_framework_tech_stack=random.choice(['Selenium+Python', 'Cypress', 'Playwright', 'Appium', 'RestAssured+Java']),
                team_lead=team_lead,
                regression_coverage=random.randint(0, 100),
                bugs_found_through_automation=random.randint(0, 50),
                total_automatable_test_cases=total_automatable,
                total_automatable_smoke_test_cases=total_automatable_smoke,
                total_automated_test_cases=total_automated,
                total_automated_smoke_test_cases=total_automated_smoke,
                sprint_cycle=random.choice(sprint_cycles),
                total_number_of_functional_test_cases=random.randint(50, 150),
                total_number_of_business_test_cases=random.randint(20, 100),
                oat_release_cycle=random.choice(oat_cycles),
                readiness_for_production=random.choice([True, False])
            )
            projects.append(project)
            
            # Assign 2-5 random resources to each project
            num_resources = random.randint(2, 5)
            project_resources = random.sample(resources, min(num_resources, len(resources)))
            
            for resource in project_resources:
                hours = decimal.Decimal(random.randint(10, 40))
                utilization = decimal.Decimal(random.randint(25, 100))
                
                ProjectResource.objects.create(
                    project=project,
                    resource=resource,
                    assigned_date=start_date + timedelta(days=random.randint(1, 30)),
                    hours_allocated=hours,
                    utilization_percentage=utilization,
                    notes=f"Assigned to {project.name} for {hours} hours per week at {utilization}% utilization"
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created 10 projects with resource assignments'))
        
        # Create 3 Weekly Meetings
        for i in range(3):
            meeting_date = timezone.now() - timedelta(days=i*7)  # One meeting per week
            
            meeting = WeeklyMeeting.objects.create(
                meeting_date=meeting_date,
                title=f"Weekly Automation Meeting {meeting_date.strftime('%Y-%m-%d')}",
                notes=f"Notes for meeting on {meeting_date.strftime('%Y-%m-%d')}",
                is_completed=True
            )
            
            # Add updates for 3-5 random projects
            num_projects = random.randint(3, 5)
            meeting_projects = random.sample(projects, min(num_projects, len(projects)))
            
            for project in meeting_projects:
                # Get a random sprint cycle and OAT release cycle
                sprint_cycle = SprintCycle.objects.order_by('?').first()
                oat_cycle = OATReleaseCycle.objects.order_by('?').first()
                
                # Get a random team lead
                team_lead = Resource.objects.order_by('?').first()
                
                # Generate random test case counts
                total_automatable = random.randint(50, 200)
                total_automated = random.randint(0, total_automatable)
                total_automated_smoke = random.randint(0, 50)
                
                WeeklyProjectUpdate.objects.create(
                    meeting=meeting,
                    project=project,
                    smoke_automation_status=random.choice(automation_statuses),
                    regression_automation_status=random.choice(automation_statuses),
                    pipeline_schedule=random.choice(pipeline_schedules),
                    execution_time_hours=random.randint(0, 2),
                    execution_time_minutes=random.randint(1, 59),
                    total_available_test_cases=random.randint(100, 300),
                    bugs_found_through_automation=random.randint(0, 50),
                    regression_coverage=random.randint(0, 100),
                    total_automatable_test_cases=total_automatable,
                    total_automated_test_cases=total_automated,
                    total_automated_smoke_test_cases=total_automated_smoke,
                    sprint_cycle=sprint_cycle,
                    last_automation_run_status=random.choice(['Passed', 'Failed', 'Partial', 'Not Run']),
                    last_automation_run_date=meeting_date - timedelta(days=random.randint(1, 7)),
                    automation_framework_tech_stack=random.choice(['Selenium+Python', 'Cypress', 'Playwright', 'Appium', 'RestAssured+Java']),
                    functional_test_cases_count=random.randint(50, 150),
                    business_test_cases_count=random.randint(20, 100),
                    oat_release_cycle=oat_cycle,
                    readiness_for_production=random.choice([True, False]),
                    team_lead=team_lead
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created 3 weekly meetings with project updates'))
        
        self.stdout.write(self.style.SUCCESS('Successfully reset data with 10 projects and 15 resources'))