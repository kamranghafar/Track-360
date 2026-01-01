from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Resource, Project, ProjectResource, SprintCycle, OATReleaseCycle, WeeklyMeeting, WeeklyProjectUpdate, Quarter, QuarterTarget, QuarterTargetResource
import random
from datetime import timedelta, date
import decimal

class Command(BaseCommand):
    help = 'Adds dummy data to the database for testing'

    def handle(self, *args, **options):
        self.stdout.write('Adding dummy data...')

        # Create Sprint Cycles
        sprint_cycles = [
            'Bi-weekly',
            'Monthly',
            'Quarterly',
            'Weekly',
            'Custom'
        ]

        for cycle in sprint_cycles:
            SprintCycle.objects.get_or_create(
                name=cycle,
                defaults={
                    'description': f'Sprint cycle that runs {cycle.lower()}',
                    'active': True
                }
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
            OATReleaseCycle.objects.get_or_create(
                name=cycle,
                defaults={
                    'description': f'OAT release cycle that runs {cycle.lower()}',
                    'active': True
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(oat_cycles)} OAT release cycles'))

        # Create Resources
        resource_names = [
            'John Smith', 'Jane Doe', 'Michael Johnson', 'Emily Williams', 'David Brown',
            'Sarah Miller', 'Robert Wilson', 'Jennifer Moore', 'William Taylor', 'Linda Anderson',
            'James Thomas', 'Patricia Jackson', 'Richard White', 'Barbara Harris', 'Charles Martin',
            'Susan Thompson', 'Joseph Garcia', 'Margaret Martinez', 'Thomas Robinson', 'Jessica Clark',
            'Daniel Rodriguez', 'Nancy Lewis', 'Paul Walker', 'Karen Hall', 'Mark Allen'
        ]

        roles = ['QA Engineer', 'Automation Engineer', 'Test Lead', 'QA Manager', 'SDET']
        skills = ['automation', 'manual', 'both']

        resources_created = 0
        for name in resource_names:
            first_name = name.split()[0].lower()
            last_name = name.split()[1].lower()
            email = f"{first_name}.{last_name}@example.com"

            resource, created = Resource.objects.get_or_create(
                name=name,
                defaults={
                    'email': email,
                    'role': random.choice(roles),
                    'skill': random.choice(skills),
                    'availability': random.choice([True, True, True, False])  # 75% available
                }
            )

            if created:
                resources_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {resources_created} resources'))

        # Create Projects
        project_names = [
            'Customer Portal', 'Mobile App', 'Payment Gateway', 'Inventory System',
            'CRM Integration', 'Data Analytics Platform', 'E-commerce Website',
            'Content Management System', 'API Gateway', 'Authentication Service',
            'Notification System', 'Reporting Dashboard', 'User Management',
            'Search Engine', 'Recommendation System'
        ]

        statuses = ['not_started', 'in_progress', 'completed', 'on_hold']
        automation_statuses = ['hold', 'completed', 'in_progress', 'na']
        pipeline_schedules = ['on_demand', 'weekly', 'nightly', 'na']

        projects_created = 0
        for name in project_names[:10]:  # Create 10 projects
            start_date = timezone.now() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(90, 365))

            # Randomly select a team lead
            team_lead = random.choice(Resource.objects.all()) if Resource.objects.exists() else None

            # Generate random test case counts
            total_automatable = random.randint(50, 200)
            total_automated = random.randint(0, total_automatable)
            total_automatable_smoke = random.randint(10, 50)
            total_automated_smoke = random.randint(0, total_automatable_smoke)

            project, created = Project.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'This is a test project for {name}',
                    'start_date': start_date,
                    'end_date': end_date,
                    'status': random.choice(statuses),
                    'budget': decimal.Decimal(random.randint(10000, 100000)),
                    'smoke_automation_status': random.choice(automation_statuses),
                    'regression_automation_status': random.choice(automation_statuses),
                    'pipeline_schedule': random.choice(pipeline_schedules),
                    'execution_time_of_smoke': f"{random.randint(0, 2)}h {random.randint(1, 59)}m",
                    'total_number_of_available_test_cases': random.randint(100, 300),
                    'status_of_last_automation_run': random.choice(['Passed', 'Failed', 'Partial', 'Not Run']),
                    'date_of_last_automation_run': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'automation_framework_tech_stack': random.choice(['Selenium+Python', 'Cypress', 'Playwright', 'Appium', 'RestAssured+Java']),
                    'team_lead': team_lead,
                    'regression_coverage': random.randint(0, 100),
                    'bugs_found_through_automation': random.randint(0, 50),
                    'total_automatable_test_cases': total_automatable,
                    'total_automatable_smoke_test_cases': total_automatable_smoke,
                    'total_automated_test_cases': total_automated,
                    'total_automated_smoke_test_cases': total_automated_smoke,
                    'sprint_cycle': random.choice(sprint_cycles),
                    'total_number_of_functional_test_cases': random.randint(50, 150),
                    'total_number_of_business_test_cases': random.randint(20, 100),
                    'oat_release_cycle': random.choice(oat_cycles),
                    'readiness_for_production': random.choice([True, False])
                }
            )

            if created:
                projects_created += 1

                # Assign 2-5 random resources to each project
                num_resources = random.randint(2, 5)
                resources = random.sample(list(Resource.objects.all()), min(num_resources, Resource.objects.count()))

                for resource in resources:
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

        self.stdout.write(self.style.SUCCESS(f'Created {projects_created} projects with resource assignments'))

        # Create Weekly Meetings
        meetings_created = 0
        for i in range(5):  # Create 5 weekly meetings
            meeting_date = timezone.now() - timedelta(days=i*7)  # One meeting per week

            meeting, created = WeeklyMeeting.objects.get_or_create(
                meeting_date=meeting_date,
                defaults={
                    'title': f"Weekly Automation Meeting {meeting_date.strftime('%Y-%m-%d')}",
                    'notes': f"Notes for meeting on {meeting_date.strftime('%Y-%m-%d')}",
                    'is_completed': True
                }
            )

            if created:
                meetings_created += 1

                # Add updates for 3-5 random projects
                num_projects = random.randint(3, 5)
                projects = random.sample(list(Project.objects.all()), min(num_projects, Project.objects.count()))

                for project in projects:
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

        self.stdout.write(self.style.SUCCESS(f'Created {meetings_created} weekly meetings with project updates'))

        # Create Quarters for the current year
        current_year = timezone.now().year
        quarters_created = 0
        quarter_targets_created = 0
        quarter_target_resources_created = 0

        # Quarter names (optional)
        quarter_names = [
            "Q1 Planning and Strategy",
            "Q2 Development and Implementation",
            "Q3 Testing and Refinement",
            "Q4 Deployment and Review"
        ]

        # Create all 4 quarters for the current year
        for quarter_number in range(1, 5):
            quarter, created = Quarter.objects.get_or_create(
                year=current_year,
                quarter_number=quarter_number,
                defaults={
                    'name': quarter_names[quarter_number-1],
                    # The start_date and end_date will be auto-calculated in the save method
                }
            )

            if created:
                quarters_created += 1

                # Create quarter targets for 3-5 random projects
                num_projects = random.randint(3, 5)
                projects = random.sample(list(Project.objects.all()), min(num_projects, Project.objects.count()))

                for project in projects:
                    # Create a quarter target for this project
                    target_descriptions = [
                        f"Increase test automation coverage to {random.randint(60, 95)}%",
                        f"Reduce manual testing effort by {random.randint(20, 50)}%",
                        f"Implement {random.randint(2, 10)} new automated test suites",
                        f"Integrate {random.randint(1, 5)} new testing tools",
                        f"Complete automation for {random.randint(3, 8)} critical features"
                    ]

                    quarter_target, target_created = QuarterTarget.objects.get_or_create(
                        quarter=quarter,
                        project=project,
                        defaults={
                            'target_description': random.choice(target_descriptions),
                            'target_value': random.randint(50, 100)
                        }
                    )

                    if target_created:
                        quarter_targets_created += 1

                        # Assign 1-3 resources to this quarter target
                        num_resources = random.randint(1, 3)
                        resources = random.sample(list(Resource.objects.all()), min(num_resources, Resource.objects.count()))

                        for resource in resources:
                            allocation = decimal.Decimal(random.randint(25, 100))

                            QuarterTargetResource.objects.create(
                                quarter_target=quarter_target,
                                resource=resource,
                                allocation_percentage=allocation,
                                notes=f"Allocated at {allocation}% for {quarter.name} target"
                            )
                            quarter_target_resources_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {quarters_created} quarters with {quarter_targets_created} targets and {quarter_target_resources_created} resource assignments'))

        self.stdout.write(self.style.SUCCESS('Successfully added dummy data'))
