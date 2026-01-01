from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Resource, MonthlyFeedback
import calendar
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Reset monthly feedback status for the new month'

    def handle(self, *args, **options):
        # Get current month and year
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # Calculate previous month and year
        if current_month == 1:
            previous_month = 12
            previous_year = current_year - 1
        else:
            previous_month = current_month - 1
            previous_year = current_year
            
        # Get all resources
        resources = Resource.objects.all()
        
        # Count of resources that need feedback
        resources_count = resources.count()
        feedback_created_count = 0
        
        self.stdout.write(self.style.SUCCESS(f'Starting monthly feedback reset for {calendar.month_name[current_month]} {current_year}'))
        self.stdout.write(f'Found {resources_count} resources that need feedback')
        
        # For each resource, check if feedback exists for the current month
        for resource in resources:
            # Check if feedback already exists for the current month
            feedback_exists = MonthlyFeedback.objects.filter(
                resource=resource,
                month=current_month,
                year=current_year
            ).exists()
            
            # If feedback doesn't exist, create a new one with status 'due'
            if not feedback_exists:
                MonthlyFeedback.objects.create(
                    resource=resource,
                    month=current_month,
                    year=current_year,
                    feedback='',
                    status='due',
                    # Use the resource's lead or manager as the submitter if available
                    submitted_by=resource.lead.user if resource.lead and resource.lead.user else (
                        resource.manager.user if resource.manager and resource.manager.user else None
                    )
                )
                feedback_created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Created {feedback_created_count} new feedback entries for {calendar.month_name[current_month]} {current_year}'))
        
        # Optional: Archive or mark as read-only all feedback from the previous month
        previous_month_feedback = MonthlyFeedback.objects.filter(
            month=previous_month,
            year=previous_year,
            status='due'
        )
        
        # Count of feedback entries that were not submitted last month
        not_submitted_count = previous_month_feedback.count()
        
        if not_submitted_count > 0:
            self.stdout.write(f'Found {not_submitted_count} feedback entries from {calendar.month_name[previous_month]} {previous_year} that were not submitted')
            
            # You could automatically mark these as "Not Submitted" or keep them as "due"
            # For now, we'll just log them
            for feedback in previous_month_feedback:
                self.stdout.write(f'  - Feedback for {feedback.resource.name} was not submitted')
        
        self.stdout.write(self.style.SUCCESS('Monthly feedback reset completed successfully'))