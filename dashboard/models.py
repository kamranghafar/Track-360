from django.db import models
from django.utils import timezone
from django.urls import reverse
import json
from datetime import timedelta, date
from django.contrib.auth.models import User

# Create your models here.
# Admin-configurable models for dropdown lists
class SprintCycle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class OATReleaseCycle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Resource(models.Model):
    SKILL_CHOICES = [
        ('automation', 'Automation'),
        ('manual', 'Manual'),
        ('both', 'Both')
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=100, blank=True)
    lead = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members_as_lead')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members_as_manager')
    skill = models.CharField(max_length=20, choices=SKILL_CHOICES, default='manual')
    availability = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resource')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    AUTOMATION_STATUS_CHOICES = [
        ('hold', 'Hold'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('na', 'N/A'),
    ]

    PIPELINE_SCHEDULE_CHOICES = [
        ('on_demand', 'On-Demand'),
        ('weekly', 'Weekly'),
        ('nightly', 'Nightly'),
        ('na', 'N/A'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    resources = models.ManyToManyField(Resource, through='ProjectResource')

    # Automation related fields
    smoke_automation_status = models.CharField(max_length=20, choices=AUTOMATION_STATUS_CHOICES, default='na', blank=True)
    regression_automation_status = models.CharField(max_length=20, choices=AUTOMATION_STATUS_CHOICES, default='na', blank=True)
    pipeline_schedule = models.CharField(max_length=20, choices=PIPELINE_SCHEDULE_CHOICES, default='na', blank=True)
    execution_time_of_smoke = models.CharField(max_length=50, blank=True, help_text="Hours and Minutes")
    total_number_of_available_test_cases = models.IntegerField(null=True, blank=True)
    status_of_last_automation_run = models.TextField(blank=True)
    date_of_last_automation_run = models.DateField(null=True, blank=True)
    automation_framework_tech_stack = models.TextField(blank=True)
    team_lead = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, blank=True, related_name='products_as_lead', db_column='team_lead_id')
    regression_coverage = models.IntegerField(null=True, blank=True, help_text="Percentage or count")
    smoke_coverage = models.IntegerField(null=True, blank=True, help_text="Percentage of smoke test cases automated")
    bugs_found_through_automation = models.IntegerField(null=True, blank=True)
    total_automatable_test_cases = models.IntegerField(null=True, blank=True)
    total_automatable_smoke_test_cases = models.IntegerField(null=True, blank=True)
    total_automated_test_cases = models.IntegerField(null=True, blank=True)
    total_automated_smoke_test_cases = models.IntegerField(null=True, blank=True)
    sprint_cycle = models.CharField(max_length=50, blank=True)
    total_number_of_functional_test_cases = models.IntegerField(null=True, blank=True)
    total_number_of_business_test_cases = models.IntegerField(null=True, blank=True)
    oat_release_cycle = models.CharField(max_length=50, blank=True)
    in_production = models.BooleanField(default=False)
    in_development = models.BooleanField(default=False)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None

    @property
    def is_overdue(self):
        if self.end_date and self.status != 'completed':
            return self.end_date < timezone.now().date()
        return False

class ProjectResource(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    assigned_date = models.DateField(default=timezone.now)
    start_date = models.DateField(default=timezone.now, help_text="Start date of resource's involvement in the project")
    end_date = models.DateField(null=True, blank=True, help_text="End date of resource's involvement in the project")
    eta = models.DateField(null=True, blank=True, help_text="Estimated Time of Arrival/Completion")
    hours_allocated = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    utilization_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Maximum 100%")
    notes = models.TextField(blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.utilization_percentage > 100:
            raise ValidationError({'utilization_percentage': 'Utilization percentage cannot exceed 100%'})
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before start date'})

    class Meta:
        unique_together = ('project', 'resource')

    def __str__(self):
        return f"{self.resource.name} assigned to {self.project.name}"


class ProductBackupResource(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='backup_resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='backup_for_projects')
    assigned_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Check if the resource is already a backup for this project
        if ProductBackupResource.objects.filter(project=self.project, resource=self.resource).exclude(pk=self.pk).exists():
            raise ValidationError({'resource': 'This resource is already a backup for this project'})

    class Meta:
        unique_together = ('project', 'resource')
        verbose_name = "Product Backup Resource"
        verbose_name_plural = "Product Backup Resources"

    def __str__(self):
        return f"{self.resource.name} backup for {self.project.name}"

class WeeklyMeeting(models.Model):
    meeting_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200, default="Automation Updates")
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.meeting_date.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse('weekly-meeting-detail', kwargs={'pk': self.pk})

    @property
    def project_count(self):
        return self.weeklyprojectupdate_set.count()

class WeeklyProjectUpdate(models.Model):
    meeting = models.ForeignKey(WeeklyMeeting, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Fields that can be updated during the meeting
    smoke_automation_status = models.CharField(max_length=20, choices=Project.AUTOMATION_STATUS_CHOICES, default='na')
    regression_automation_status = models.CharField(max_length=20, choices=Project.AUTOMATION_STATUS_CHOICES, default='na')
    pipeline_schedule = models.CharField(max_length=20, choices=Project.PIPELINE_SCHEDULE_CHOICES, default='na')
    execution_time_hours = models.IntegerField(default=0)
    execution_time_minutes = models.IntegerField(default=0)
    total_available_test_cases = models.IntegerField(default=0)
    bugs_found_through_automation = models.IntegerField(default=0)
    regression_coverage = models.IntegerField(default=0)
    total_automatable_test_cases = models.IntegerField(default=0)
    total_automated_test_cases = models.IntegerField(default=0)
    total_automated_smoke_test_cases = models.IntegerField(default=0)
    sprint_cycle = models.ForeignKey(SprintCycle, on_delete=models.SET_NULL, null=True, blank=True)
    last_automation_run_status = models.TextField(blank=True)
    last_automation_run_date = models.DateField(null=True, blank=True)
    automation_framework_tech_stack = models.TextField(blank=True)
    functional_test_cases_count = models.IntegerField(default=0)
    business_test_cases_count = models.IntegerField(default=0)
    oat_release_cycle = models.ForeignKey(OATReleaseCycle, on_delete=models.SET_NULL, null=True, blank=True)
    readiness_for_production = models.BooleanField(default=False)
    team_lead = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('meeting', 'project')

    def __str__(self):
        return f"{self.project.name} update for {self.meeting}"

    def get_execution_time_display(self):
        return f"{self.execution_time_hours}h {self.execution_time_minutes}m"

    def to_dict(self):
        """Convert instance to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'project_id': self.project.id,
            'project_name': self.project.name,
            'smoke_automation_status': self.smoke_automation_status,
            'regression_automation_status': self.regression_automation_status,
            'pipeline_schedule': self.pipeline_schedule,
            'execution_time': self.get_execution_time_display(),
            'total_available_test_cases': self.total_available_test_cases,
            'bugs_found_through_automation': self.bugs_found_through_automation,
            'regression_coverage': self.regression_coverage,
            'total_automatable_test_cases': self.total_automatable_test_cases,
            'total_automated_test_cases': self.total_automated_test_cases,
            'total_automated_smoke_test_cases': self.total_automated_smoke_test_cases,
            'sprint_cycle': self.sprint_cycle.name if self.sprint_cycle else '',
            'last_automation_run_status': self.last_automation_run_status,
            'last_automation_run_date': self.last_automation_run_date.isoformat() if self.last_automation_run_date else None,
            'automation_framework_tech_stack': self.automation_framework_tech_stack,
            'functional_test_cases_count': self.functional_test_cases_count,
            'business_test_cases_count': self.business_test_cases_count,
            'oat_release_cycle': self.oat_release_cycle.name if self.oat_release_cycle else '',
            'readiness_for_production': self.readiness_for_production,
            'team_lead': self.team_lead.name if self.team_lead else '',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class WeeklyProductMeeting(models.Model):
    meeting_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200, default="Manual Updates")
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.meeting_date.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse('weekly-product-meeting-detail', kwargs={'pk': self.pk})

    @property
    def product_count(self):
        return self.weeklyproductupdate_set.count()

class ProductProblem(models.Model):
    TIMELINE_CHOICES = [
        ('immediate', 'Immediate (1-2 days)'),
        ('short', 'Short-term (1 week)'),
        ('medium', 'Medium-term (2-4 weeks)'),
        ('long', 'Long-term (1+ months)'),
    ]

    product_update = models.ForeignKey('WeeklyProductUpdate', on_delete=models.CASCADE, related_name='product_problems')
    problem_description = models.TextField(help_text="Problem identified during the meeting")
    expected_solutions = models.TextField(blank=True, help_text="Expected solutions for the identified problem")
    solution_timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, default='medium')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Problem for {self.product_update.project.name}"

    def get_solution_timeline_display(self):
        return dict(self.TIMELINE_CHOICES).get(self.solution_timeline, self.solution_timeline)

class WeeklyProductUpdate(models.Model):
    meeting = models.ForeignKey(WeeklyProductMeeting, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Fields that can be updated during the meeting
    latest_project_updates = models.TextField(blank=True, help_text="Latest updates about the product")
    product_notes = models.TextField(blank=True, help_text="Product notes and additional information")

    # Legacy fields - kept for backward compatibility but will be deprecated
    problems = models.TextField(blank=True, help_text="[Legacy] Problems identified during the meeting")
    expected_solution = models.TextField(blank=True, help_text="[Legacy] Expected solution for the identified problems")
    solution_timeline = models.CharField(max_length=20, choices=ProductProblem.TIMELINE_CHOICES, default='medium', help_text="[Legacy] Timeline for the solution")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('meeting', 'project')

    def __str__(self):
        return f"{self.project.name} update for {self.meeting}"

    def to_dict(self):
        """Convert instance to dictionary for JSON serialization"""
        problems_data = [
            {
                'id': problem.id,
                'description': problem.problem_description,
                'expected_solutions': problem.expected_solutions,
                'solution_timeline': problem.get_solution_timeline_display(),
            }
            for problem in self.product_problems.all()
        ]

        return {
            'id': self.id,
            'project_id': self.project.id,
            'project_name': self.project.name,
            'latest_project_updates': self.latest_project_updates,
            'product_notes': self.product_notes,
            'problems': problems_data,
            # Include legacy fields for backward compatibility
            'legacy_problems': self.problems,
            'legacy_expected_solution': self.expected_solution,
            'legacy_solution_timeline': self.get_solution_timeline_display(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def get_solution_timeline_display(self):
        return dict(ProductProblem.TIMELINE_CHOICES).get(self.solution_timeline, self.solution_timeline)


class Quarter(models.Model):
    QUARTER_CHOICES = [
        (1, 'Q1'),
        (2, 'Q2'),
        (3, 'Q3'),
        (4, 'Q4'),
    ]

    year = models.IntegerField()
    quarter_number = models.IntegerField(choices=QUARTER_CHOICES)
    name = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('year', 'quarter_number')
        ordering = ['-year', 'quarter_number']

    def __str__(self):
        return f"Q{self.quarter_number} {self.year}" if not self.name else f"{self.name} (Q{self.quarter_number} {self.year})"

    def save(self, *args, **kwargs):
        # Auto-calculate start and end dates if not provided
        if not self.start_date or not self.end_date:
            # Calculate start date (first day of the first month of the quarter)
            first_month = (self.quarter_number - 1) * 3 + 1
            self.start_date = date(self.year, first_month, 1)

            # Calculate end date (last day of the last month of the quarter)
            last_month = first_month + 2
            if last_month == 12:
                self.end_date = date(self.year, 12, 31)
            else:
                # Get the first day of the next month, then subtract one day
                next_month_year = self.year
                next_month = last_month + 1
                if next_month > 12:
                    next_month = 1
                    next_month_year += 1
                self.end_date = date(next_month_year, next_month, 1) - timedelta(days=1)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('quarter-detail', kwargs={'pk': self.pk})

    def get_completion_url(self):
        return reverse('quarter-complete', kwargs={'pk': self.pk})

    def get_timeline_data(self):
        """Return data for the quarter timeline display"""
        return {
            'id': self.id,
            'name': str(self),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'completed': self.completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
        }

    def get_statistics(self):
        """Return statistics for the quarter completion summary"""
        targets = self.targets.all()
        total_targets = targets.count()
        completed_targets = targets.exclude(achieved_value__isnull=True).count()

        # Calculate average achievement percentage
        achievement_percentages = [
            target.achievement_percentage 
            for target in targets 
            if target.achievement_percentage is not None
        ]
        avg_achievement = sum(achievement_percentages) / len(achievement_percentages) if achievement_percentages else 0

        return {
            'total_targets': total_targets,
            'completed_targets': completed_targets,
            'completion_percentage': (completed_targets / total_targets * 100) if total_targets > 0 else 0,
            'avg_achievement_percentage': avg_achievement,
        }


class QuarterTarget(models.Model):
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE, related_name='targets')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='quarterly_targets')
    target_description = models.TextField()
    target_value = models.IntegerField(null=True, blank=True, help_text="Numeric target value if applicable")
    achieved_value = models.IntegerField(null=True, blank=True, help_text="Actual achieved value")
    achievement_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Percentage of target achieved")
    achievement_notes = models.TextField(blank=True)
    resources = models.ManyToManyField(Resource, through='QuarterTargetResource')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        pass

    def __str__(self):
        return f"{self.project.name} - {self.quarter}"

    def get_absolute_url(self):
        return reverse('quarter-target-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Calculate achievement percentage if target_value and achieved_value are set
        if self.target_value is not None and self.achieved_value is not None and self.target_value > 0:
            self.achievement_percentage = (self.achieved_value / self.target_value) * 100
        super().save(*args, **kwargs)


class QuarterTargetResource(models.Model):
    quarter_target = models.ForeignKey(QuarterTarget, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    allocation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Maximum 100%")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('quarter_target', 'resource')

    def __str__(self):
        return f"{self.resource.name} assigned to {self.quarter_target}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.allocation_percentage > 100:
            raise ValidationError({'allocation_percentage': 'Allocation percentage cannot exceed 100%'})


class ResourceLeave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('holiday', 'Holiday'),
        ('other', 'Other'),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='vacation')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before start date'})

    def __str__(self):
        return f"{self.resource.name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"


class Rock(models.Model):
    """
    A Rock represents an important task or goal that needs to be accomplished.
    Rocks can be assigned to resources and optionally associated with projects or quarter targets.
    """
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    # Relationships
    assignee = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='assigned_rocks')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='rocks')
    quarter_target = models.ForeignKey(QuarterTarget, on_delete=models.SET_NULL, null=True, blank=True, related_name='rocks')

    # Dates and tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(null=True, blank=True, help_text="Date when work on the rock started")
    due_date = models.DateField(null=True, blank=True, help_text="Date when the rock is due")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Date and time when the rock was completed")

    class Meta:
        ordering = ['-priority', 'due_date', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('rock-detail', kwargs={'pk': self.pk})

    def start_rock(self):
        """Mark the rock as in progress and set the start date."""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.start_date = timezone.now().date()
            self.save()

    def complete_rock(self):
        """Mark the rock as completed and set the completion date."""
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()

    @property
    def is_overdue(self):
        """Check if the rock is overdue."""
        if self.due_date and self.status != 'completed':
            return self.due_date < timezone.now().date()
        return False


class ProductDocumentation(models.Model):
    """
    A ProductDocumentation represents a document related to a product.
    It contains a title, a link to the document, and a reference to the product.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documentation')
    title = models.CharField(max_length=200)
    link = models.URLField(help_text="URL to the document")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Most recently added items at the top

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.project.pk})


class DepartmentDocument(models.Model):
    """
    A DepartmentDocument represents a document related to a department.
    It contains a title and a link to a Confluence page.
    """
    title = models.CharField(max_length=200)
    confluence_link = models.URLField(help_text="URL to the Confluence page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Most recently added items at the top

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('department-document-list')


class ProductionBug(models.Model):
    """
    A ProductionBug represents an issue found in a product in the production environment.
    It tracks details about the issue, its status, severity, and resolution.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('tested', 'Tested'),
        ('done', 'Done'),
    ]

    SEVERITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    TEST_CASE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    title = models.CharField(max_length=200, help_text="Production Issue Title")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='production_bugs')
    gops_board_link = models.URLField(help_text="GOPS Board Link", blank=True)
    product_board_link = models.URLField(help_text="Product Board Link", blank=True)
    reported_date = models.DateField(default=timezone.now, help_text="Date when the issue was reported")
    resolved_date = models.DateField(null=True, blank=True, help_text="Date when the issue was resolved")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    details = models.TextField(blank=True, help_text="Comments/Details about the issue")
    test_case_added = models.CharField(max_length=5, choices=TEST_CASE_CHOICES, default='no')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reported_date', 'status', '-severity']

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    def get_absolute_url(self):
        return reverse('production-bug-detail', kwargs={'pk': self.pk})


class RoadmapItem(models.Model):
    """
    A RoadmapItem represents a strategic goal, milestone, or deliverable in the roadmap.
    It can be associated with a project or quarterly target and assigned to an owner.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.IntegerField(default=0, help_text="Percentage of completion (0-100)")

    # Relationships
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='owned_roadmap_items')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_items')
    quarter_target = models.ForeignKey(QuarterTarget, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_items')
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE, related_name='roadmap_items')

    # Dates and tracking
    start_date = models.DateField(help_text="Start date of the roadmap item")
    end_date = models.DateField(help_text="End date of the roadmap item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Date and time when the item was completed")

    class Meta:
        ordering = ['start_date', 'end_date', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('roadmap-item-detail', kwargs={'pk': self.pk})

    def start_item(self):
        """Mark the item as in progress."""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.save()

    def complete_item(self):
        """Mark the item as completed and set the completion date."""
        if self.status != 'completed':
            self.status = 'completed'
            self.progress = 100
            self.completed_at = timezone.now()
            self.save()

    def update_progress(self, progress):
        """Update the progress percentage."""
        self.progress = min(max(progress, 0), 100)  # Ensure progress is between 0 and 100
        if self.progress == 100 and self.status != 'completed':
            self.complete_item()
        elif self.progress > 0 and self.status == 'not_started':
            self.start_item()
        else:
            self.save()

    @property
    def is_overdue(self):
        """Check if the roadmap item is overdue."""
        if self.end_date and self.status != 'completed':
            return self.end_date < timezone.now().date()
        return False

    @property
    def duration_days(self):
        """Calculate the duration of the roadmap item in days."""
        return (self.end_date - self.start_date).days

    def get_timeline_data(self):
        """Return data for the roadmap timeline display"""
        return {
            'id': self.id,
            'title': self.title,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'priority': self.priority,
            'progress': self.progress,
            'owner': self.owner.name,
            'project': self.project.name if self.project else None,
            'quarter_target': str(self.quarter_target) if self.quarter_target else None,
            'is_overdue': self.is_overdue,
        }


class RecordsPassword(models.Model):
    """
    Stores the password for accessing the Records section.
    Only one instance of this model should exist.
    """
    password = models.CharField(max_length=100, help_text="Password for accessing the Records section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Records Section Password"

    class Meta:
        verbose_name = "Records Password"
        verbose_name_plural = "Records Password"


class UserAction(models.Model):
    """
    Stores information about user actions for auditing purposes.
    """
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, blank=True, null=True, help_text="The model class name related to the action")
    record_id = models.IntegerField(blank=True, null=True, help_text="The primary key of the related record")
    details = models.TextField(blank=True, null=True, help_text="Additional details about the action")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "User Action"
        verbose_name_plural = "User Actions"

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class DeletedRecord(models.Model):
    """
    Stores information about deleted records for potential restoration.
    Acts as a trash/recycle bin for the application.
    """
    model_name = models.CharField(max_length=100, help_text="The model class name of the deleted record")
    record_id = models.IntegerField(help_text="The primary key of the deleted record")
    data = models.TextField(help_text="JSON serialized data of the deleted record")
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-deleted_at']
        verbose_name = "Deleted Record"
        verbose_name_plural = "Deleted Records"

    def __str__(self):
        return f"{self.model_name} #{self.record_id} (deleted on {self.deleted_at.strftime('%Y-%m-%d %H:%M')})"

    def get_data_dict(self):
        """Returns the deserialized data as a dictionary"""
        return json.loads(self.data)

    def restore(self):
        """
        Restores the deleted record by recreating it from the stored data.
        Returns the newly created record.
        """
        from django.apps import apps

        # Get the model class
        model_class = apps.get_model('dashboard', self.model_name)

        # Create a new instance with the stored data
        data_dict = self.get_data_dict()

        # Remove the id from the data to let Django create a new one
        # or use the original id if we want to preserve it
        record_id = data_dict.pop('id', None)

        # Create the new record
        new_record = model_class(**data_dict)

        # If we want to preserve the original ID
        if record_id:
            new_record.id = record_id

        new_record.save()

        # Delete this DeletedRecord entry as it's been restored
        self.delete()

        return new_record


class KPI(models.Model):
    """
    Stores Key Performance Indicators (KPIs) for resources.
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='kpis')
    name = models.CharField(max_length=200, help_text="Name of the KPI")
    description = models.TextField(blank=True, help_text="Detailed description of the KPI")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"
        ordering = ['resource', 'name']
        unique_together = ['resource', 'name']

    def __str__(self):
        return f"{self.resource.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('kpi-detail', kwargs={'pk': self.pk})


class KPIRating(models.Model):
    """
    Stores monthly ratings for KPIs.
    """
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Below Expectations'),
        (3, '3 - Meets Expectations'),
        (4, '4 - Exceeds Expectations'),
        (5, '5 - Outstanding')
    ]

    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='ratings')
    month = models.IntegerField(help_text="Month (1-12)")
    year = models.IntegerField(help_text="Year (e.g., 2023)")
    rating = models.IntegerField(choices=RATING_CHOICES, help_text="Rating from 1 to 5")
    remarks = models.TextField(blank=True, help_text="Optional remarks for this KPI rating")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KPI Rating"
        verbose_name_plural = "KPI Ratings"
        ordering = ['-year', '-month', 'kpi']
        unique_together = ['kpi', 'month', 'year']

    def __str__(self):
        return f"{self.kpi} - {self.month}/{self.year}: {self.rating}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.month is None:
            raise ValidationError({'month': 'Month is required'})
        if self.month < 1 or self.month > 12:
            raise ValidationError({'month': 'Month must be between 1 and 12'})
        if self.year is None:
            raise ValidationError({'year': 'Year is required'})
        if self.rating is None:
            raise ValidationError({'rating': 'Rating is required'})
        if self.rating < 1 or self.rating > 5:
            raise ValidationError({'rating': 'Rating must be between 1 and 5'})


class KPIRatingSubmission(models.Model):
    """
    Stores overall remarks for a set of KPI ratings submitted together.
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='kpi_submissions')
    month = models.IntegerField(help_text="Month (1-12)")
    year = models.IntegerField(help_text="Year (e.g., 2023)")
    overall_remarks = models.TextField(help_text="Mandatory overall remarks for this submission")
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KPI Rating Submission"
        verbose_name_plural = "KPI Rating Submissions"
        ordering = ['-year', '-month', 'resource']
        unique_together = ['resource', 'month', 'year']

    def __str__(self):
        return f"{self.resource.name} - {self.month}/{self.year} Submission"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.month is None:
            raise ValidationError({'month': 'Month is required'})
        if self.month < 1 or self.month > 12:
            raise ValidationError({'month': 'Month must be between 1 and 12'})
        if self.year is None:
            raise ValidationError({'year': 'Year is required'})
        if not self.overall_remarks:
            raise ValidationError({'overall_remarks': 'Overall remarks are required'})


class OneOnOneFeedback(models.Model):
    """
    Stores 1:1 feedback for resources.
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='one_on_one_feedbacks')
    notes = models.TextField(help_text="Feedback notes for the resource")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "1:1 Feedback"
        verbose_name_plural = "1:1 Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.resource.name} - {self.created_at.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse('one-on-one-feedback-detail', kwargs={'pk': self.pk})


class MonthlyFeedback(models.Model):
    """
    Stores monthly feedback for resources.
    One feedback per resource per month.
    """
    STATUS_CHOICES = [
        ('due', 'Feedback Due'),
        ('submitted', 'Submitted'),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='monthly_feedbacks')
    month = models.IntegerField(help_text="Month (1-12)")
    year = models.IntegerField(help_text="Year (e.g., 2023)")
    feedback = models.TextField(help_text="Monthly feedback for the resource")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='due')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_monthly_feedbacks')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Monthly Feedback"
        verbose_name_plural = "Monthly Feedbacks"
        ordering = ['-year', '-month', 'resource']
        unique_together = ['resource', 'month', 'year']

    def __str__(self):
        return f"Monthly Feedback for {self.resource.name} - {self.month}/{self.year}"

    def get_absolute_url(self):
        return reverse('monthly-feedback-detail', kwargs={'pk': self.pk})

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.month is None:
            raise ValidationError({'month': 'Month is required'})
        if self.month < 1 or self.month > 12:
            raise ValidationError({'month': 'Month must be between 1 and 12'})
        if self.year is None:
            raise ValidationError({'year': 'Year is required'})
        if not self.feedback and self.status == 'submitted':
            raise ValidationError({'feedback': 'Feedback is required when status is submitted'})

    def save(self, *args, **kwargs):
        # If feedback is being submitted, update status
        if self.feedback and self.status == 'due':
            self.status = 'submitted'
        super().save(*args, **kwargs)


class SOP(models.Model):
    """
    Stores Standard Operating Procedures (SOPs) with their links and status.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('under_review', 'Under Review'),
        ('review_done', 'Review Done'),
        ('rollout_in_progress', 'Rollout in Progress'),
        ('rollout_done', 'Rollout Done'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=200, help_text="Name of the SOP")
    link = models.URLField(help_text="URL link to the SOP document")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SOP"
        verbose_name_plural = "SOPs"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('sop-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Check if this is an update to an existing SOP
        if self.pk:
            # Get the original SOP instance from the database
            original = SOP.objects.get(pk=self.pk)
            # If status has changed, create a status history entry
            if original.status != self.status:
                # Save first to ensure the SOP exists
                super().save(*args, **kwargs)
                # Create status history entry (user will be set in the view)
                SOPStatusHistory.objects.create(
                    sop=self,
                    old_status=original.status,
                    new_status=self.status
                )
                return  # Return early as we've already saved
        # If it's a new SOP or status hasn't changed
        super().save(*args, **kwargs)


class SOPStatusHistory(models.Model):
    """
    Tracks the history of status changes for SOPs.
    """
    sop = models.ForeignKey(SOP, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=30, choices=SOP.STATUS_CHOICES)
    new_status = models.CharField(max_length=30, choices=SOP.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SOP Status History"
        verbose_name_plural = "SOP Status Histories"
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.sop.name}: {self.old_status} → {self.new_status} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"


class AutomationRunner(models.Model):
    """
    An AutomationRunner represents a link to an automation runner board.
    Users can provide a name and link for the Automation Runner.
    """
    name = models.CharField(max_length=200, help_text="Name of the Automation Runner")
    link = models.URLField(help_text="URL link to the runner board")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Automation Runner"
        verbose_name_plural = "Automation Runners"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('automation-runner-detail', kwargs={'pk': self.pk})


class AutomationSprint(models.Model):
    """
    An AutomationSprint represents a sprint for automation work.
    It tracks details about the sprint, resources, and progress.
    """
    SPRINT_LENGTH_CHOICES = [
        ('1_week', '1 week'),
        ('2_weeks', '2 weeks'),
        ('3_weeks', '3 weeks'),
    ]

    SPRINT_TYPE_CHOICES = [
        ('6th_sprint', '6th Sprint'),
        ('20_allocation', '20% Allocation'),
    ]

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
        ('on_hold', 'On Hold'),
        ('to_do', 'To Do'),
    ]

    DEV_TRAINING_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('to_do', 'To Do'),
    ]

    # Sprint Creation Fields
    product = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='automation_sprints')
    engineering_manager_name = models.CharField(max_length=200)
    sprint_length = models.CharField(max_length=10, choices=SPRINT_LENGTH_CHOICES)
    total_dev_resources = models.IntegerField()
    sprint_type = models.CharField(max_length=20, choices=SPRINT_TYPE_CHOICES)
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    rationale = models.TextField(blank=True)
    risks = models.TextField(blank=True)
    qa_point_of_contact = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, related_name='qa_sprints')
    dev_training_status = models.CharField(max_length=20, choices=DEV_TRAINING_STATUS_CHOICES, default='to_do')
    notes = models.TextField(blank=True)

    # Post-Creation Sprint Details
    total_sprint_days = models.IntegerField(default=0)
    total_planned_working_hours = models.IntegerField(default=0)
    blocked_hours = models.IntegerField(default=0)
    total_planned_test_cases = models.IntegerField(default=0)
    total_test_cases_automated = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Automation Sprint"
        verbose_name_plural = "Automation Sprints"
        ordering = ['-start_date', 'product__name']

    def __str__(self):
        return f"{self.product.name} Sprint - {self.start_date}"

    def get_absolute_url(self):
        return reverse('automation-sprint-detail', kwargs={'pk': self.pk})
