import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from dashboard.models import Resource, KPI, KPIRating, KPIRatingSubmission
import random
from datetime import datetime, timedelta

def create_kpi_test_data():
    print('Creating KPI test data...')
    
    # Check if we have resources
    resources = Resource.objects.all()
    if not resources.exists():
        print('No resources found. Please create resources first.')
        return
    
    # Get or create a user for KPI submissions
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@example.com'
        }
    )
    if created:
        user.set_password('admin')
        user.save()
        print('Created admin user')
    
    # Sample KPI names and descriptions
    kpi_templates = [
        {
            'name': 'Code Quality',
            'description': 'Maintains high standards of code quality, follows best practices, and ensures code is well-documented.'
        },
        {
            'name': 'Test Coverage',
            'description': 'Ensures adequate test coverage for all code changes and new features.'
        },
        {
            'name': 'Bug Resolution',
            'description': 'Efficiently identifies and resolves bugs with minimal regression.'
        },
        {
            'name': 'Feature Delivery',
            'description': 'Delivers features on time and with high quality.'
        },
        {
            'name': 'Technical Documentation',
            'description': 'Creates and maintains comprehensive technical documentation.'
        },
        {
            'name': 'Team Collaboration',
            'description': 'Works effectively with team members and contributes to a positive team environment.'
        },
        {
            'name': 'Knowledge Sharing',
            'description': 'Actively shares knowledge with team members and helps others grow.'
        },
        {
            'name': 'Innovation',
            'description': 'Proposes and implements innovative solutions to technical challenges.'
        }
    ]
    
    # Create KPIs for each resource
    kpis_created = 0
    ratings_created = 0
    submissions_created = 0
    
    for resource in resources:
        # Randomly select 3-5 KPIs for each resource
        num_kpis = random.randint(3, min(5, len(kpi_templates)))
        selected_kpis = random.sample(kpi_templates, num_kpis)
        
        for kpi_template in selected_kpis:
            # Create KPI
            kpi, created = KPI.objects.get_or_create(
                resource=resource,
                name=kpi_template['name'],
                defaults={
                    'description': kpi_template['description']
                }
            )
            if created:
                kpis_created += 1
            
            # Create ratings for the past 6 months
            today = timezone.now().date()
            for i in range(6):
                month = today.month - i
                year = today.year
                while month <= 0:
                    month += 12
                    year -= 1
                
                # Create rating
                rating, created = KPIRating.objects.get_or_create(
                    kpi=kpi,
                    month=month,
                    year=year,
                    defaults={
                        'rating': random.randint(2, 5),  # Random rating between 2-5
                        'remarks': f'Monthly evaluation for {kpi.name}. Performance was {["below expectations", "meeting expectations", "exceeding expectations"][random.randint(0, 2)]}.'
                    }
                )
                if created:
                    ratings_created += 1
        
        # Create KPI submissions for the past 3 months
        for i in range(3):
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            
            # Create submission
            submission, created = KPIRatingSubmission.objects.get_or_create(
                resource=resource,
                month=month,
                year=year,
                defaults={
                    'overall_remarks': f'Overall performance for {month}/{year} was {["satisfactory", "good", "excellent"][random.randint(0, 2)]}. Continue to focus on {["technical skills", "collaboration", "innovation", "documentation"][random.randint(0, 3)]}.', 
                    'submitted_by': user
                }
            )
            if created:
                submissions_created += 1
    
    print(f'Successfully created {kpis_created} KPIs, {ratings_created} ratings, and {submissions_created} submissions')

if __name__ == "__main__":
    create_kpi_test_data()