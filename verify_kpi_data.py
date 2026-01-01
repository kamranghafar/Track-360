import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from dashboard.models import Resource, KPI, KPIRating, KPIRatingSubmission
from django.db.models import Count

def verify_kpi_data():
    # Count total KPIs
    kpi_count = KPI.objects.count()
    print(f"Total KPIs in database: {kpi_count}")
    
    # Count total KPI ratings
    rating_count = KPIRating.objects.count()
    print(f"Total KPI ratings in database: {rating_count}")
    
    # Count total KPI submissions
    submission_count = KPIRatingSubmission.objects.count()
    print(f"Total KPI submissions in database: {submission_count}")
    
    # Check resources with KPIs
    resources_with_kpis = Resource.objects.annotate(kpi_count=Count('kpis')).filter(kpi_count__gt=0)
    print(f"Resources with KPIs: {resources_with_kpis.count()} out of {Resource.objects.count()}")
    
    # Sample KPI data
    print("\nSample KPI data:")
    sample_kpis = KPI.objects.all()[:5]
    for kpi in sample_kpis:
        print(f"- {kpi.resource.name}: {kpi.name}")
        
        # Get ratings for this KPI
        ratings = KPIRating.objects.filter(kpi=kpi).order_by('-year', '-month')[:2]
        if ratings:
            print("  Recent ratings:")
            for rating in ratings:
                print(f"  - {rating.month}/{rating.year}: {rating.rating} - {rating.remarks[:50]}...")
        
    # Sample submission data
    print("\nSample KPI submission data:")
    sample_submissions = KPIRatingSubmission.objects.all().order_by('-year', '-month')[:3]
    for submission in sample_submissions:
        print(f"- {submission.resource.name}: {submission.month}/{submission.year}")
        print(f"  Remarks: {submission.overall_remarks[:100]}...")

if __name__ == "__main__":
    verify_kpi_data()