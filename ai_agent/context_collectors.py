from django.utils import timezone
from dashboard.models import Resource, Project, KPI, KPIRating, KPIRatingSubmission, UserAction
from .models import DashboardContext

def collect_dashboard_overview_context(session, request):
    """
    Collects context data from the dashboard overview.
    """
    # Create a new context object
    context = DashboardContext(session=session)

    # Get all projects
    projects = Project.objects.all()

    # Get counts for analytics
    context.total_products = projects.count()
    context.total_resources = Resource.objects.count()
    context.active_products = projects.filter(status='in_progress').count()
    context.completed_products = projects.filter(status='completed').count()

    # Save the context
    context.save()

    return context


def collect_view_state_context(context, request):
    """
    Collects context about the current view and filters.
    """
    # Get the current view from the request path
    path = request.path
    if path.startswith('/dashboard/'):
        path = path[10:]  # Remove '/dashboard/' prefix
    context.current_view = path or 'dashboard'

    # Get applied filters from request GET parameters
    filters = {}
    for key, value in request.GET.items():
        if key not in ['page', 'page_size']:  # Exclude pagination parameters
            filters[key] = value
    context.applied_filters = filters

    # Save the updated context
    context.save()

    return context


def collect_visualization_context(context, request):
    """
    Collects context about visible charts and visualizations.
    """
    # This would typically come from session data or a specific request parameter
    # For now, we'll use a simple approach based on the current view
    visible_charts = []

    if context.current_view == 'dashboard':
        visible_charts = [
            'products_by_status',
            'resources_by_product_count',
            'automation_backlog',
            'smoke_coverage'
        ]
    elif 'kpi' in context.current_view:
        visible_charts = ['kpi_ratings_over_time']

    context.visible_charts = visible_charts

    # Save the updated context
    context.save()

    return context


def collect_user_history_context(context, request):
    """
    Collects context about the user's recent actions.
    """
    if request.user.is_authenticated:
        # Get the 10 most recent actions for this user
        recent_actions = UserAction.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:10]

        # Convert to a list of dictionaries
        actions_list = []
        for action in recent_actions:
            actions_list.append({
                'action_type': action.action_type,
                'details': action.details,
                'timestamp': action.timestamp.isoformat()
            })

        context.recent_actions = actions_list

    # Save the updated context
    context.save()

    return context


def collect_kpi_context(context, request):
    """
    Collects context about KPIs and ratings.
    """
    # Get KPI data if we're in a KPI-related view
    kpi_data = {}

    if 'kpi' in context.current_view:
        # If we're looking at a specific resource's KPIs
        resource_id = None
        for key, value in context.applied_filters.items():
            if key == 'resource_id':
                resource_id = value
                break

        if resource_id:
            # Get KPIs for this resource
            kpis = KPI.objects.filter(resource_id=resource_id)

            # Get the current month and year
            today = timezone.now().date()
            current_month = today.month
            current_year = today.year

            # Collect KPI data
            kpi_list = []
            for kpi in kpis:
                # Get the most recent rating
                latest_rating = KPIRating.objects.filter(
                    kpi=kpi
                ).order_by('-year', '-month').first()

                kpi_info = {
                    'id': kpi.id,
                    'name': kpi.name,
                    'description': kpi.description
                }

                if latest_rating:
                    kpi_info['latest_rating'] = {
                        'rating': latest_rating.rating,
                        'month': latest_rating.month,
                        'year': latest_rating.year,
                        'remarks': latest_rating.remarks
                    }

                kpi_list.append(kpi_info)

            # Get the most recent submission
            latest_submission = KPIRatingSubmission.objects.filter(
                resource_id=resource_id
            ).order_by('-year', '-month').first()

            kpi_data = {
                'resource_id': resource_id,
                'kpis': kpi_list
            }

            if latest_submission:
                kpi_data['latest_submission'] = {
                    'month': latest_submission.month,
                    'year': latest_submission.year,
                    'overall_remarks': latest_submission.overall_remarks
                }

    context.kpi_data = kpi_data

    # Save the updated context
    context.save()

    return context


# This function has been replaced by the implementation below
# def collect_full_dashboard_context(session, request):
#     """
#     Collects all context data from the dashboard.
#     """
#     # Start with the dashboard overview
#     context = collect_dashboard_overview_context(session, request)
# 
#     # Add view state context
#     collect_view_state_context(context, request)
# 
#     # Add visualization context
#     collect_visualization_context(context, request)
# 
#     # Add user history context
#     collect_user_history_context(context, request)
# 
#     # Add KPI context
#     collect_kpi_context(context, request)
from django.utils import timezone
from dashboard.models import Project, Resource, ProductBackupResource, WeeklyProductMeeting, ProductProblem, WeeklyProductUpdate, ProductDocumentation
from .models import DashboardContext


def collect_product_data():
    """
    Collects detailed data about products and their related resources from the database.

    Returns:
        dict: A dictionary containing detailed product data
    """
    try:
        # Get all projects (products)
        products = []
        for project in Project.objects.all():
            product_data = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'in_production': project.in_production,
                'in_development': project.in_development,
                'team_lead': project.team_lead.name if project.team_lead else None,

                # Automation related fields
                'smoke_automation_status': project.smoke_automation_status,
                'regression_automation_status': project.regression_automation_status,
                'pipeline_schedule': project.pipeline_schedule,
                'execution_time_of_smoke': project.execution_time_of_smoke,
                'total_number_of_available_test_cases': project.total_number_of_available_test_cases,
                'status_of_last_automation_run': project.status_of_last_automation_run,
                'date_of_last_automation_run': project.date_of_last_automation_run.isoformat() if project.date_of_last_automation_run else None,
                'automation_framework_tech_stack': project.automation_framework_tech_stack,
                'regression_coverage': project.regression_coverage,
                'smoke_coverage': project.smoke_coverage,
                'bugs_found_through_automation': project.bugs_found_through_automation,
                'total_automatable_test_cases': project.total_automatable_test_cases,
                'total_automatable_smoke_test_cases': project.total_automatable_smoke_test_cases,
                'total_automated_test_cases': project.total_automated_test_cases,
                'total_automated_smoke_test_cases': project.total_automated_smoke_test_cases,
                'sprint_cycle': project.sprint_cycle,
                'total_number_of_functional_test_cases': project.total_number_of_functional_test_cases,
                'total_number_of_business_test_cases': project.total_number_of_business_test_cases,
                'oat_release_cycle': project.oat_release_cycle,

                # Related resources
                'resources': [],
                'backup_resources': [],
                'documentation': [],
                'weekly_updates': [],
            }

            # Add assigned resources
            for pr in project.projectresource_set.all():
                resource_data = {
                    'id': pr.resource.id,
                    'name': pr.resource.name,
                    'role': pr.resource.role,
                    'skill': pr.resource.skill,
                    'assigned_date': pr.assigned_date.isoformat(),
                    'start_date': pr.start_date.isoformat(),
                    'end_date': pr.end_date.isoformat() if pr.end_date else None,
                    'eta': pr.eta.isoformat() if pr.eta else None,
                    'hours_allocated': float(pr.hours_allocated),
                    'utilization_percentage': float(pr.utilization_percentage),
                    'notes': pr.notes,
                }
                product_data['resources'].append(resource_data)

            # Add backup resources
            for br in ProductBackupResource.objects.filter(project=project):
                backup_resource_data = {
                    'id': br.resource.id,
                    'name': br.resource.name,
                    'assigned_date': br.assigned_date.isoformat(),
                    'notes': br.notes,
                }
                product_data['backup_resources'].append(backup_resource_data)

            # Add documentation
            for doc in ProductDocumentation.objects.filter(project=project):
                doc_data = {
                    'id': doc.id,
                    'title': doc.title,
                    'link': doc.link,
                    'created_at': doc.created_at.isoformat(),
                    'updated_at': doc.updated_at.isoformat(),
                }
                product_data['documentation'].append(doc_data)

            # Add weekly product updates
            for update in WeeklyProductUpdate.objects.filter(project=project).order_by('-meeting__meeting_date')[:5]:  # Get the 5 most recent updates
                update_data = update.to_dict()  # Using the to_dict method from the model
                product_data['weekly_updates'].append(update_data)

            products.append(product_data)

        # Get all product meetings
        meetings = []
        for meeting in WeeklyProductMeeting.objects.all().order_by('-meeting_date')[:10]:  # Get the 10 most recent meetings
            meeting_data = {
                'id': meeting.id,
                'meeting_date': meeting.meeting_date.isoformat(),
                'title': meeting.title,
                'notes': meeting.notes,
                'is_completed': meeting.is_completed,
                'product_count': meeting.product_count,
                'created_at': meeting.created_at.isoformat(),
                'updated_at': meeting.updated_at.isoformat(),
            }
            meetings.append(meeting_data)

        return {
            'products': products,
            'product_meetings': meetings,
        }
    except Exception as e:
        print(f"Error collecting product data: {str(e)}")
        return {
            'products': [],
            'product_meetings': [],
            'error': str(e)
        }


def collect_full_dashboard_context(session, request):
    """
    Collect all relevant dashboard context for the given session and request.

    Args:
        session: The ChatSession object
        request: The HTTP request object

    Returns:
        DashboardContext: The collected dashboard context
    """
    try:
        # Get counts of products and resources
        total_products = Project.objects.count()
        total_resources = Resource.objects.count()
        active_products = Project.objects.filter(status='in_progress').count()
        completed_products = Project.objects.filter(status='completed').count()

        # Database access successful
        database_available = True
    except Exception as e:
        print(f"Error accessing database in collect_full_dashboard_context: {str(e)}")
        # Set default values if database access fails
        total_products = 0
        total_resources = 0
        active_products = 0
        completed_products = 0
        database_available = False

    # Determine the current view based on the request path
    path = request.path
    current_view = "Dashboard"

    if '/dashboard/resources/' in path:
        current_view = "Resources"
    elif '/dashboard/projects/' in path:
        current_view = "Projects"
    elif '/dashboard/weekly-meetings/' in path:
        current_view = "Automation Updates"
    elif '/dashboard/quarters/' in path:
        current_view = "Quarter Planning"
    elif '/dashboard/rocks/' in path:
        current_view = "Rocks"
    elif '/dashboard/kpis/' in path:
        current_view = "KPI Management"

    try:
        # Collect detailed product data
        product_data = collect_product_data()

        # Get or create a context object for this session
        defaults = {
            'timestamp': timezone.now(),
            'current_view': current_view,
            'total_products': total_products,
            'total_resources': total_resources,
            'active_products': active_products,
            'completed_products': completed_products,
            'applied_filters': {
                'database_available': database_available,
                'product_data': product_data
            }
        }

        context, created = DashboardContext.objects.get_or_create(
            session=session,
            defaults=defaults
        )

        # If not created, update the existing context
        if not created:
            context.timestamp = timezone.now()
            context.current_view = current_view
            context.total_products = total_products
            context.total_resources = total_resources
            context.active_products = active_products
            context.completed_products = completed_products

            # Add a flag to indicate if the database is available
            context.applied_filters = context.applied_filters or {}
            context.applied_filters['database_available'] = database_available

            # Add detailed product data to the context
            context.applied_filters['product_data'] = product_data

            context.save()
    except Exception as e:
        print(f"Error creating or updating context in collect_full_dashboard_context: {str(e)}")
        # Create a simple context object without saving to the database
        context = DashboardContext(
            session=session,
            timestamp=timezone.now(),
            current_view=current_view,
            total_products=total_products,
            total_resources=total_resources,
            active_products=active_products,
            completed_products=completed_products
        )

        # Add a flag to indicate that the database is not available
        # Try to collect product data even in the exception case
        try:
            product_data = collect_product_data()
            context.applied_filters = {
                'database_available': False,
                'product_data': product_data
            }
        except Exception as product_error:
            print(f"Error collecting product data in exception handler: {str(product_error)}")
            context.applied_filters = {'database_available': False}

    return context
