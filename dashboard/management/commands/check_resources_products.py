from django.core.management.base import BaseCommand
from dashboard.models import Resource, Project

class Command(BaseCommand):
    help = 'Checks existing resources and products in the database'

    def handle(self, *args, **options):
        self.stdout.write('Checking existing resources and products...')
        
        # Check resources
        resources = Resource.objects.all()
        self.stdout.write(f'Total resources: {resources.count()}')
        self.stdout.write('Resource names:')
        for resource in resources:
            self.stdout.write(f'- {resource.name}')
        
        # Check products (projects)
        products = Project.objects.all()
        self.stdout.write(f'\nTotal products: {products.count()}')
        self.stdout.write('Product names:')
        for product in products:
            self.stdout.write(f'- {product.name}')