from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Project, Resource, SprintCycle, OATReleaseCycle
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Adds automation details for all products'

    def handle(self, *args, **options):
        self.stdout.write('Adding automation details for all products...')
        
        # Get all products
        products = Project.objects.all()
        
        if not products.exists():
            self.stdout.write(self.style.ERROR('No products found in the database.'))
            return
        
        # Get all resources for team leads
        resources = Resource.objects.all()
        
        # Get all sprint cycles
        sprint_cycles = SprintCycle.objects.all()
        if not sprint_cycles.exists():
            self.stdout.write(self.style.WARNING('No sprint cycles found. Creating default ones...'))
            default_cycles = ['Bi-weekly', 'Monthly', 'Quarterly', 'Weekly', 'Custom']
            for cycle in default_cycles:
                SprintCycle.objects.create(
                    name=cycle,
                    description=f'Sprint cycle that runs {cycle.lower()}',
                    active=True
                )
            sprint_cycles = SprintCycle.objects.all()
        
        # Get all OAT release cycles
        oat_cycles = OATReleaseCycle.objects.all()
        if not oat_cycles.exists():
            self.stdout.write(self.style.WARNING('No OAT release cycles found. Creating default ones...'))
            default_cycles = ['Monthly', 'Quarterly', 'Bi-annual', 'Annual', 'On-demand']
            for cycle in default_cycles:
                OATReleaseCycle.objects.create(
                    name=cycle,
                    description=f'OAT release cycle that runs {cycle.lower()}',
                    active=True
                )
            oat_cycles = OATReleaseCycle.objects.all()
        
        # Automation framework tech stacks
        tech_stacks = [
            'Selenium + Python',
            'Cypress + JavaScript',
            'Playwright + TypeScript',
            'Appium + Java',
            'RestAssured + Java',
            'Postman + Newman',
            'Robot Framework',
            'Cucumber + Java',
            'TestNG + Java',
            'PyTest + Python',
            'JUnit + Java',
            'Selenium + C#',
            'Protractor + JavaScript',
            'WebdriverIO + JavaScript'
        ]
        
        # Last automation run statuses
        run_statuses = [
            'Passed',
            'Failed',
            'Partial Pass',
            'Blocked',
            'Not Run',
            'In Progress',
            'Aborted',
            'Unstable'
        ]
        
        products_updated = 0
        
        for product in products:
            # Generate random test case counts
            total_available = random.randint(100, 500)
            total_automatable = random.randint(int(total_available * 0.5), total_available)
            total_automated = random.randint(int(total_automatable * 0.3), total_automatable)
            
            total_automatable_smoke = random.randint(20, min(100, int(total_automatable * 0.3)))
            total_automated_smoke = random.randint(int(total_automatable_smoke * 0.5), total_automatable_smoke)
            
            total_functional = random.randint(int(total_available * 0.6), total_available)
            total_business = total_available - total_functional
            
            # Generate random automation statuses
            smoke_status = random.choice(['hold', 'completed', 'in_progress', 'na'])
            regression_status = random.choice(['hold', 'completed', 'in_progress', 'na'])
            
            # Generate random pipeline schedule
            pipeline_schedule = random.choice(['on_demand', 'weekly', 'nightly', 'na'])
            
            # Generate random execution time
            hours = random.randint(0, 3)
            minutes = random.randint(1, 59)
            execution_time = f"{hours}h {minutes}m"
            
            # Generate random last run date (within the last 30 days)
            last_run_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
            
            # Generate random regression coverage
            regression_coverage = random.randint(0, 100)
            
            # Generate random bugs found
            bugs_found = random.randint(0, 50)
            
            # Select random team lead
            team_lead = random.choice(resources) if resources.exists() else None
            
            # Select random sprint cycle
            sprint_cycle = random.choice(sprint_cycles).name if sprint_cycles.exists() else ''
            
            # Select random OAT release cycle
            oat_release_cycle = random.choice(oat_cycles).name if oat_cycles.exists() else ''
            
            # Generate random readiness for production
            readiness = random.choice([True, False])
            
            # Select random tech stack
            tech_stack = random.choice(tech_stacks)
            
            # Select random last run status
            last_run_status = random.choice(run_statuses)
            
            # Update the product with the generated data
            product.smoke_automation_status = smoke_status
            product.regression_automation_status = regression_status
            product.pipeline_schedule = pipeline_schedule
            product.execution_time_of_smoke = execution_time
            product.total_number_of_available_test_cases = total_available
            product.status_of_last_automation_run = last_run_status
            product.date_of_last_automation_run = last_run_date
            product.automation_framework_tech_stack = tech_stack
            product.team_lead = team_lead
            product.regression_coverage = regression_coverage
            product.bugs_found_through_automation = bugs_found
            product.total_automatable_test_cases = total_automatable
            product.total_automatable_smoke_test_cases = total_automatable_smoke
            product.total_automated_test_cases = total_automated
            product.total_automated_smoke_test_cases = total_automated_smoke
            product.sprint_cycle = sprint_cycle
            product.total_number_of_functional_test_cases = total_functional
            product.total_number_of_business_test_cases = total_business
            product.oat_release_cycle = oat_release_cycle
            product.readiness_for_production = readiness
            
            product.save()
            products_updated += 1
            
            self.stdout.write(f'Updated automation details for product: {product.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated automation details for {products_updated} products'))