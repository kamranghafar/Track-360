from django.core.management.base import BaseCommand
from dashboard.models import Resource, Project, ProjectResource
import random
from datetime import timedelta
import decimal

class Command(BaseCommand):
    help = 'Assigns resources to products (projects) to complete the dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Assigning resources to products...')
        
        # Get all resources and products
        resources = Resource.objects.all()
        products = Project.objects.all()
        
        if not resources.exists():
            self.stdout.write(self.style.ERROR('No resources found in the database.'))
            return
            
        if not products.exists():
            self.stdout.write(self.style.ERROR('No products found in the database.'))
            return
        
        # Delete existing project resources to avoid conflicts
        ProjectResource.objects.all().delete()
        self.stdout.write('Cleared existing project resources')
        
        # Counter for created assignments
        assignments_created = 0
        
        # Assign resources to products
        for product in products:
            # Assign 3-8 random resources to each product
            num_resources = random.randint(3, 8)
            selected_resources = random.sample(list(resources), min(num_resources, resources.count()))
            
            for resource in selected_resources:
                hours = decimal.Decimal(random.randint(10, 40))
                utilization = decimal.Decimal(random.randint(25, 100))
                
                ProjectResource.objects.create(
                    project=product,
                    resource=resource,
                    assigned_date=product.start_date + timedelta(days=random.randint(1, 30)),
                    hours_allocated=hours,
                    utilization_percentage=utilization,
                    notes=f"Assigned to {product.name} for {hours} hours per week at {utilization}% utilization"
                )
                assignments_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {assignments_created} resource assignments'))