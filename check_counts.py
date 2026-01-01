from dashboard.models import Quarter, QuarterTarget, Project

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