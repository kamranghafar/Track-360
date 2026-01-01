from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Resource, Project, QuarterTarget, Rock
import random
from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Adds dummy data for Rock Management'

    def handle(self, *args, **options):
        self.stdout.write('Adding dummy data for Rock Management...')

        # Check if we have resources and projects
        if not Resource.objects.exists():
            self.stdout.write(self.style.ERROR('No resources found. Please run add_dummy_data.py first.'))
            return

        if not Project.objects.exists():
            self.stdout.write(self.style.ERROR('No projects found. Please run add_dummy_data.py first.'))
            return

        # Sample rock titles and descriptions
        rock_data = [
            {
                'title': 'Implement Automated UI Testing',
                'description': 'Set up and implement automated UI testing framework for the main application.'
            },
            {
                'title': 'Create API Test Suite',
                'description': 'Develop comprehensive test suite for the REST API endpoints.'
            },
            {
                'title': 'Performance Testing Framework',
                'description': 'Establish a performance testing framework to measure application response times.'
            },
            {
                'title': 'Security Testing Implementation',
                'description': 'Implement security testing procedures and tools for vulnerability assessment.'
            },
            {
                'title': 'Mobile App Test Automation',
                'description': 'Create automated tests for the mobile application on both iOS and Android platforms.'
            },
            {
                'title': 'Database Testing Strategy',
                'description': 'Develop and document a comprehensive database testing strategy.'
            },
            {
                'title': 'CI/CD Pipeline Integration',
                'description': 'Integrate automated tests into the CI/CD pipeline for continuous testing.'
            },
            {
                'title': 'Test Documentation Overhaul',
                'description': 'Update and standardize all test documentation for better knowledge sharing.'
            },
            {
                'title': 'Cross-Browser Testing Setup',
                'description': 'Establish cross-browser testing capabilities for web applications.'
            },
            {
                'title': 'Accessibility Testing Implementation',
                'description': 'Implement accessibility testing to ensure compliance with WCAG standards.'
            },
            {
                'title': 'Load Testing for Peak Traffic',
                'description': 'Create load testing scenarios to simulate peak traffic conditions.'
            },
            {
                'title': 'Test Data Management Solution',
                'description': 'Implement a solution for managing test data across environments.'
            },
            {
                'title': 'Regression Test Automation',
                'description': 'Automate critical regression test cases to reduce manual testing effort.'
            },
            {
                'title': 'Test Environment Setup Automation',
                'description': 'Create scripts to automate the setup and teardown of test environments.'
            },
            {
                'title': 'End-to-End Test Scenarios',
                'description': 'Develop end-to-end test scenarios covering critical user journeys.'
            }
        ]

        # Create rocks
        rocks_created = 0
        
        # Get all resources, projects, and quarter targets
        resources = list(Resource.objects.all())
        projects = list(Project.objects.all())
        quarter_targets = list(QuarterTarget.objects.all())
        
        # Create rocks with random attributes
        for rock_info in rock_data:
            # Randomly decide if this rock should be created
            if random.random() < 0.8:  # 80% chance to create each rock
                # Randomly select status
                status = random.choice(['not_started', 'in_progress', 'completed'])
                
                # Randomly select priority
                priority = random.choice(['high', 'medium', 'low'])
                
                # Randomly select assignee
                assignee = random.choice(resources)
                
                # Randomly select project (or None)
                project = random.choice(projects) if random.random() < 0.8 else None
                
                # Randomly select quarter target (or None)
                quarter_target = random.choice(quarter_targets) if quarter_targets and random.random() < 0.6 else None
                
                # Set dates based on status
                created_at = timezone.now() - timedelta(days=random.randint(1, 90))
                due_date = timezone.now() + timedelta(days=random.randint(1, 60))
                
                start_date = None
                completed_at = None
                
                if status == 'in_progress':
                    start_date = created_at + timedelta(days=random.randint(1, 10))
                elif status == 'completed':
                    start_date = created_at + timedelta(days=random.randint(1, 10))
                    completed_at = start_date + timedelta(days=random.randint(5, 30))
                    # Ensure completed_at is not in the future
                    if completed_at > timezone.now():
                        completed_at = timezone.now() - timedelta(days=random.randint(1, 5))
                
                # Create the rock
                rock, created = Rock.objects.get_or_create(
                    title=rock_info['title'],
                    defaults={
                        'description': rock_info['description'],
                        'priority': priority,
                        'status': status,
                        'assignee': assignee,
                        'project': project,
                        'quarter_target': quarter_target,
                        'created_at': created_at,
                        'start_date': start_date,
                        'due_date': due_date,
                        'completed_at': completed_at
                    }
                )
                
                if created:
                    rocks_created += 1
        
        # Create some overdue rocks
        for i in range(5):
            title = f"Overdue Task {i+1}"
            description = f"This is an overdue task that needs immediate attention."
            
            # Set due date in the past
            due_date = timezone.now() - timedelta(days=random.randint(1, 30))
            
            # Randomly select status (not completed)
            status = random.choice(['not_started', 'in_progress'])
            
            # Create the rock
            rock, created = Rock.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'priority': 'high',  # Overdue tasks are high priority
                    'status': status,
                    'assignee': random.choice(resources),
                    'project': random.choice(projects) if random.random() < 0.8 else None,
                    'quarter_target': random.choice(quarter_targets) if quarter_targets and random.random() < 0.6 else None,
                    'created_at': due_date - timedelta(days=random.randint(10, 30)),
                    'start_date': due_date - timedelta(days=random.randint(1, 9)) if status == 'in_progress' else None,
                    'due_date': due_date
                }
            )
            
            if created:
                rocks_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {rocks_created} rocks for Rock Management'))
        self.stdout.write(self.style.SUCCESS('Successfully added Rock Management dummy data'))