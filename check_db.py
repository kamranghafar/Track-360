import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Now we can import Django models
from dashboard.models import Quarter, QuarterTarget, Project, Resource, KPI, KPIRating

# Count total quarters
total_quarters = Quarter.objects.count()
print(f"Total Quarters: {total_quarters}")

# Count completed quarters
completed_quarters = Quarter.objects.filter(completed=True).count()
print(f"Completed Quarters: {completed_quarters}")

# Count total targets
total_targets = QuarterTarget.objects.count()
print(f"Total Targets: {total_targets}")

# Count projects with targets
projects_with_targets = Project.objects.filter(quarterly_targets__isnull=False).distinct().count()
print(f"Projects with Targets: {projects_with_targets}")

# Count total projects
total_projects = Project.objects.count()
print(f"Total Projects: {total_projects}")

# Count total resources
total_resources = Resource.objects.count()
print(f"Total Resources: {total_resources}")

# Count total KPIs
total_kpis = KPI.objects.count()
print(f"Total KPIs: {total_kpis}")

# Count total KPI ratings
total_kpi_ratings = KPIRating.objects.count()
print(f"Total KPI Ratings: {total_kpi_ratings}")

print("Database check completed successfully!")