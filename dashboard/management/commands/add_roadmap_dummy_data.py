from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Resource, Project, Quarter, QuarterTarget, RoadmapItem
import random
from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Adds dummy data for Strategic Roadmap'

    def handle(self, *args, **options):
        self.stdout.write('Adding dummy data for Strategic Roadmap...')

        # Check if we have resources, projects, and quarters
        if not Resource.objects.exists():
            self.stdout.write(self.style.ERROR('No resources found. Please run add_dummy_data.py first.'))
            return

        if not Project.objects.exists():
            self.stdout.write(self.style.ERROR('No projects found. Please run add_dummy_data.py first.'))
            return

        if not Quarter.objects.exists():
            self.stdout.write(self.style.ERROR('No quarters found. Please run add_dummy_data.py first.'))
            return

        # Sample roadmap item titles and descriptions
        roadmap_data = [
            {
                'title': 'Implement Automated Testing Framework',
                'description': 'Design and implement a comprehensive automated testing framework for all products.'
            },
            {
                'title': 'Launch Mobile App v2.0',
                'description': 'Release version 2.0 of the mobile application with new features and improvements.'
            },
            {
                'title': 'API Gateway Redesign',
                'description': 'Redesign the API gateway to improve performance and security.'
            },
            {
                'title': 'Cloud Migration Phase 1',
                'description': 'Complete the first phase of migrating on-premise systems to cloud infrastructure.'
            },
            {
                'title': 'Implement CI/CD Pipeline',
                'description': 'Set up continuous integration and continuous deployment pipeline for all projects.'
            },
            {
                'title': 'Security Compliance Audit',
                'description': 'Conduct a comprehensive security audit to ensure compliance with industry standards.'
            },
            {
                'title': 'Data Analytics Platform Launch',
                'description': 'Launch the new data analytics platform for internal and customer use.'
            },
            {
                'title': 'Customer Portal Redesign',
                'description': 'Redesign the customer portal with improved UX/UI and new features.'
            },
            {
                'title': 'Microservices Architecture Implementation',
                'description': 'Convert monolithic applications to microservices architecture.'
            },
            {
                'title': 'DevOps Transformation',
                'description': 'Complete the DevOps transformation across all development teams.'
            },
            {
                'title': 'AI-Powered Recommendation Engine',
                'description': 'Develop and deploy an AI-powered recommendation engine for the e-commerce platform.'
            },
            {
                'title': 'Blockchain Integration for Payments',
                'description': 'Integrate blockchain technology for secure and transparent payment processing.'
            },
            {
                'title': 'Cross-Platform Mobile Framework',
                'description': 'Implement a cross-platform mobile development framework to reduce development time.'
            },
            {
                'title': 'IoT Platform Development',
                'description': 'Develop a platform for managing and analyzing data from IoT devices.'
            },
            {
                'title': 'Customer Experience Enhancement Program',
                'description': 'Launch a program to enhance customer experience across all touchpoints.'
            }
        ]

        # Create roadmap items
        items_created = 0

        # Get all resources, projects, quarters, and quarter targets
        resources = list(Resource.objects.all())
        projects = list(Project.objects.all())
        quarters = list(Quarter.objects.all())
        quarter_targets = list(QuarterTarget.objects.all())

        # Create roadmap items with random attributes
        for item_info in roadmap_data:
            # Randomly decide if this item should be created
            if random.random() < 0.8:  # 80% chance to create each item
                # Randomly select status
                status = random.choice(['not_started', 'in_progress', 'completed'])

                # Randomly select owner
                owner = random.choice(resources)

                # Randomly select project (or None)
                project = random.choice(projects) if random.random() < 0.8 else None

                # Randomly select quarter
                quarter = random.choice(quarters)

                # Randomly select quarter target (or None)
                quarter_target = None
                if quarter_targets and random.random() < 0.6:
                    # Filter quarter targets by the selected quarter
                    matching_targets = [qt for qt in quarter_targets if qt.quarter == quarter]
                    if matching_targets:
                        quarter_target = random.choice(matching_targets)

                # Set dates based on quarter
                quarter_start = quarter.start_date
                quarter_end = quarter.end_date

                # Ensure dates are within the quarter
                start_date = quarter_start + timedelta(days=random.randint(0, (quarter_end - quarter_start).days // 3))
                end_date = start_date + timedelta(days=random.randint(14, (quarter_end - start_date).days))

                # Ensure end_date is not after quarter_end
                if end_date > quarter_end:
                    end_date = quarter_end

                created_at = timezone.now() - timedelta(days=random.randint(1, 90))
                completed_at = None

                if status == 'completed':
                    completed_at = timezone.now() - timedelta(days=random.randint(1, 30))

                # Create the roadmap item
                roadmap_item, created = RoadmapItem.objects.get_or_create(
                    title=item_info['title'],
                    quarter=quarter,
                    defaults={
                        'description': item_info['description'],
                        'status': status,
                        'owner': owner,
                        'project': project,
                        'quarter_target': quarter_target,
                        'start_date': start_date,
                        'end_date': end_date,
                        'created_at': created_at,
                        'completed_at': completed_at
                    }
                )

                if created:
                    items_created += 1

        # Create some overdue roadmap items
        for i in range(3):
            title = f"Overdue Strategic Initiative {i+1}"
            description = f"This is an overdue strategic initiative that needs immediate attention."

            # Randomly select a quarter
            quarter = random.choice(quarters)

            # Set dates
            start_date = quarter.start_date + timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(14, 30))

            # Ensure end_date is in the past (overdue)
            today = timezone.now().date()
            if end_date >= today:
                end_date = today - timedelta(days=random.randint(1, 10))

            # Randomly select status (not completed)
            status = random.choice(['not_started', 'in_progress'])

            # Create the roadmap item
            roadmap_item, created = RoadmapItem.objects.get_or_create(
                title=title,
                quarter=quarter,
                defaults={
                    'description': description,
                    'status': status,
                    'owner': random.choice(resources),
                    'project': random.choice(projects) if random.random() < 0.8 else None,
                    'quarter_target': None,  # No quarter target for overdue items
                    'start_date': start_date,
                    'end_date': end_date,
                    'created_at': start_date - timedelta(days=random.randint(1, 10))
                }
            )

            if created:
                items_created += 1

        # Create some upcoming roadmap items
        for i in range(3):
            title = f"Upcoming Strategic Initiative {i+1}"
            description = f"This is an upcoming strategic initiative planned for the near future."

            # Randomly select a quarter
            quarter = random.choice(quarters)

            # Set dates in the future
            today = timezone.now().date()
            start_date = today + timedelta(days=random.randint(7, 30))
            end_date = start_date + timedelta(days=random.randint(30, 90))

            # Ensure dates are within the quarter
            if start_date > quarter.end_date:
                start_date = quarter.start_date + timedelta(days=random.randint(0, (quarter.end_date - quarter.start_date).days // 2))
                end_date = start_date + timedelta(days=random.randint(14, (quarter.end_date - start_date).days))

            # Create the roadmap item
            roadmap_item, created = RoadmapItem.objects.get_or_create(
                title=title,
                quarter=quarter,
                defaults={
                    'description': description,
                    'status': 'not_started',
                    'owner': random.choice(resources),
                    'project': random.choice(projects) if random.random() < 0.8 else None,
                    'quarter_target': None,
                    'start_date': start_date,
                    'end_date': end_date,
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 10))
                }
            )

            if created:
                items_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {items_created} items for Strategic Roadmap'))
        self.stdout.write(self.style.SUCCESS('Successfully added Strategic Roadmap dummy data'))