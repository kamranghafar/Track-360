from django.core.management.base import BaseCommand
from dashboard.models import Quarter, QuarterTarget, Project

class Command(BaseCommand):
    help = 'Check counts of quarters, targets, and projects with targets'

    def handle(self, *args, **options):
        # Count total quarters
        total_quarters = Quarter.objects.count()
        self.stdout.write(f"Total Quarters: {total_quarters}")

        # Count completed quarters
        completed_quarters = Quarter.objects.filter(completed=True).count()
        self.stdout.write(f"Completed Quarters: {completed_quarters}")

        # Count total targets
        total_targets = QuarterTarget.objects.count()
        self.stdout.write(f"Total Targets: {total_targets}")

        # Count projects with targets
        projects_with_targets = Project.objects.filter(quarterly_targets__isnull=False).distinct().count()
        self.stdout.write(f"Projects with Targets: {projects_with_targets}")