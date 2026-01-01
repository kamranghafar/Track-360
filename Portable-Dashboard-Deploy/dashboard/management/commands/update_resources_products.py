from django.core.management.base import BaseCommand
from dashboard.models import Resource, Project
from django.db import transaction

class Command(BaseCommand):
    help = 'Update resources and products according to the provided lists'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply the changes to the database',
        )

    def handle(self, *args, **options):
        # First, check current resources and products
        self.stdout.write(self.style.SUCCESS('Current Resources:'))
        resources = Resource.objects.all()
        for resource in resources:
            self.stdout.write(f"- {resource.name}")

        self.stdout.write(self.style.SUCCESS('\nCurrent Products (Projects):'))
        products = Project.objects.all()
        for product in products:
            self.stdout.write(f"- {product.name}")

        # New resources list from the issue description
        new_resources = [
            "Zakir Muhammad Yousuf", "Usama Ali Sheikh", "Samiullah", "Zain Ali Khan", 
            "Muhammad Hasan", "Shaheer", "Yaseen", "Shamaim Shaikh", "Shafaq", "Sarang", 
            "Talha Shahab", "Mahham Batool", "Muzammil Qamar", "Farhan Ahmed Sheikh", 
            "Unzela Saleem", "Ajmal Syed", "Ifrah Ali", "Fawad Qamar", "Umer Mansoor", 
            "Rakesh Kumar", "Humza", "Saqib", "Aisha", "Muhammad Bilal", "Saira Qadir"
        ]

        # New products list from the issue description
        new_products = [
            "vTrader Engine", "RiskAPIs", "vTrader Client", "Risk Web", "Alpine (BOSS)", 
            "vHorizon", "vFlux", "WebOMS", "OMSAPIs", "FCM"
        ]

        self.stdout.write(self.style.SUCCESS('\nNew Resources to be added/updated:'))
        for resource in new_resources:
            self.stdout.write(f"- {resource}")

        self.stdout.write(self.style.SUCCESS('\nNew Products to be added/updated:'))
        for product in new_products:
            self.stdout.write(f"- {product}")

        # Apply changes if --apply flag is provided
        if options['apply']:
            self.update_resources(resources, new_resources)
            self.update_products(products, new_products)
            self.stdout.write(self.style.SUCCESS('Resources and Products updated successfully!'))
        else:
            self.stdout.write(self.style.WARNING('\nRun with --apply to update the database'))

    @transaction.atomic
    def update_resources(self, current_resources, new_resources):
        """Update resources to match the new list"""
        self.stdout.write(self.style.SUCCESS('\nUpdating Resources...'))

        # Delete all existing resources
        Resource.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All existing resources deleted'))

        # Create new resources
        for name in new_resources:
            Resource.objects.create(name=name)
            self.stdout.write(f"Created resource: {name}")

    @transaction.atomic
    def update_products(self, current_products, new_products):
        """Update products to match the new list"""
        self.stdout.write(self.style.SUCCESS('\nUpdating Products...'))

        # Delete all existing products
        Project.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All existing products deleted'))

        # Create new products
        for name in new_products:
            Project.objects.create(name=name)
            self.stdout.write(f"Created product: {name}")
