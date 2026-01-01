from django.core.management.base import BaseCommand
from dashboard.models import Project

class Command(BaseCommand):
    help = 'Checks automation details for all products'

    def handle(self, *args, **options):
        self.stdout.write('Checking automation details for all products...')
        
        # Get all products
        products = Project.objects.all()
        
        if not products.exists():
            self.stdout.write(self.style.ERROR('No products found in the database.'))
            return
        
        self.stdout.write(f'Found {products.count()} products in the database.')
        
        # Check automation details for each product
        for product in products:
            self.stdout.write(f'\nProduct: {product.name}')
            self.stdout.write('-' * 50)
            self.stdout.write(f'Smoke Automation Status: {product.smoke_automation_status}')
            self.stdout.write(f'Regression Automation Status: {product.regression_automation_status}')
            self.stdout.write(f'Pipeline Schedule: {product.pipeline_schedule}')
            self.stdout.write(f'Execution Time of Smoke: {product.execution_time_of_smoke}')
            self.stdout.write(f'Total Available Test Cases: {product.total_number_of_available_test_cases}')
            self.stdout.write(f'Status of Last Automation Run: {product.status_of_last_automation_run}')
            self.stdout.write(f'Date of Last Automation Run: {product.date_of_last_automation_run}')
            self.stdout.write(f'Automation Framework Tech Stack: {product.automation_framework_tech_stack}')
            self.stdout.write(f'Team Lead: {product.team_lead.name if product.team_lead else "None"}')
            self.stdout.write(f'Regression Coverage: {product.regression_coverage}%')
            self.stdout.write(f'Bugs Found Through Automation: {product.bugs_found_through_automation}')
            self.stdout.write(f'Total Automatable Test Cases: {product.total_automatable_test_cases}')
            self.stdout.write(f'Total Automatable Smoke Test Cases: {product.total_automatable_smoke_test_cases}')
            self.stdout.write(f'Total Automated Test Cases: {product.total_automated_test_cases}')
            self.stdout.write(f'Total Automated Smoke Test Cases: {product.total_automated_smoke_test_cases}')
            self.stdout.write(f'Sprint Cycle: {product.sprint_cycle}')
            self.stdout.write(f'Total Functional Test Cases: {product.total_number_of_functional_test_cases}')
            self.stdout.write(f'Total Business Test Cases: {product.total_number_of_business_test_cases}')
            self.stdout.write(f'OAT Release Cycle: {product.oat_release_cycle}')
            self.stdout.write(f'Readiness for Production: {product.readiness_for_production}')
        
        self.stdout.write(self.style.SUCCESS('\nAutomation details check completed.'))