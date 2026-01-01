from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from .models import Resource, Project, ProjectResource, WeeklyMeeting, WeeklyProjectUpdate, SprintCycle, OATReleaseCycle, Quarter, QuarterTarget, QuarterTargetResource, WeeklyProductMeeting, WeeklyProductUpdate, ResourceLeave, Rock, RoadmapItem, ProductDocumentation, ProductionBug, DepartmentDocument, DeletedRecord, RecordsPassword, UserAction, KPI, KPIRating, KPIRatingSubmission, OneOnOneFeedback, MonthlyFeedback, SOP, SOPStatusHistory, ProductBackupResource, AutomationRunner, AutomationSprint
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django import forms
import json
from decimal import Decimal
from json import JSONEncoder
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.core.exceptions import PermissionDenied


class ResourceForm(forms.ModelForm):
    is_team_lead = forms.BooleanField(required=False, label="Team Lead", 
                                     help_text="Check if this resource is a team lead")
    is_manager = forms.BooleanField(required=False, label="Manager", 
                                   help_text="Check if this resource is a manager")

    class Meta:
        model = Resource
        fields = ['name', 'email', 'role', 'lead', 'manager', 'skill', 'availability', 'user']

    def __init__(self, *args, **kwargs):
        # Get the request from kwargs if available
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Initialize checkboxes based on existing data
        if self.instance.pk:
            # Check if this resource is a lead for any team members
            self.fields['is_team_lead'].initial = Resource.objects.filter(lead=self.instance).exists()
            # Check if this resource is a manager for any team members
            self.fields['is_manager'].initial = Resource.objects.filter(manager=self.instance).exists()

            # Also check if this resource has been marked as a team lead or manager
            # This ensures the checkboxes remain checked when editing
            if self.initial.get('is_team_lead'):
                self.fields['is_team_lead'].initial = True
            if self.initial.get('is_manager'):
                self.fields['is_manager'].initial = True

            # Check if we have stored checkbox state in the session
            if self.request and self.request.session.get(f'resource_{self.instance.pk}_is_team_lead'):
                self.fields['is_team_lead'].initial = True
            if self.request and self.request.session.get(f'resource_{self.instance.pk}_is_manager'):
                self.fields['is_manager'].initial = True

        # Filter lead and manager fields to show resources that are already leads or managers
        # or have been marked as leads or managers via checkboxes

        # Get all resources that are leads for someone
        leads = Resource.objects.filter(team_members_as_lead__isnull=False).distinct()
        # Get all resources that are managers for someone
        managers = Resource.objects.filter(team_members_as_manager__isnull=False).distinct()

        # Get resources that have been marked as team leads or managers via checkboxes
        team_lead_resources = []
        manager_resources = []

        if self.request and self.request.session:
            # Find resources marked as team leads or managers in the session
            for key, value in self.request.session.items():
                if key.startswith('resource_') and key.endswith('_is_team_lead') and value:
                    resource_id = key.split('_')[1]
                    try:
                        resource = Resource.objects.get(pk=resource_id)
                        team_lead_resources.append(resource)
                    except Resource.DoesNotExist:
                        pass
                elif key.startswith('resource_') and key.endswith('_is_manager') and value:
                    resource_id = key.split('_')[1]
                    try:
                        resource = Resource.objects.get(pk=resource_id)
                        manager_resources.append(resource)
                    except Resource.DoesNotExist:
                        pass

        # Combine the querysets
        if team_lead_resources:
            leads = leads | Resource.objects.filter(pk__in=[r.pk for r in team_lead_resources]).distinct()
        if manager_resources:
            managers = managers | Resource.objects.filter(pk__in=[r.pk for r in manager_resources]).distinct()

        # Set the queryset for lead field to include leads
        self.fields['lead'].queryset = leads
        # Set the queryset for manager field to include managers
        self.fields['manager'].queryset = managers

        # If the current instance has a lead or manager that's not in the filtered queryset,
        # add them to the queryset to maintain the current selection
        if self.instance.pk and self.instance.lead and self.instance.lead not in leads:
            self.fields['lead'].queryset = leads | Resource.objects.filter(pk=self.instance.lead.pk).distinct()

        if self.instance.pk and self.instance.manager and self.instance.manager not in managers:
            self.fields['manager'].queryset = managers | Resource.objects.filter(pk=self.instance.manager.pk).distinct()

    def clean(self):
        cleaned_data = super().clean()
        is_team_lead = cleaned_data.get('is_team_lead')
        is_manager = cleaned_data.get('is_manager')

        # Ensure both checkboxes are not checked
        if is_team_lead and is_manager:
            raise forms.ValidationError("A resource cannot be both a Team Lead and a Manager. Please select only one.")

        return cleaned_data

# Custom JSON encoder that can handle Decimal objects
class DecimalEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class RecyclableDeleteView(DeleteView):
    """
    A base DeleteView that moves records to the DeletedRecord model instead of permanently deleting them.
    This allows for potential restoration of deleted records.
    """

    def delete(self, request, *args, **kwargs):
        """
        Override the delete method to store the record in the DeletedRecord model
        before "deleting" it from the main database.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Convert the object to a dictionary
        # This is a simple approach - for complex models with relationships,
        # you might need a more sophisticated serialization
        model_fields = [field.name for field in self.object._meta.fields]
        data_dict = {field: getattr(self.object, field) for field in model_fields}

        # Handle non-serializable types
        for key, value in data_dict.items():
            if isinstance(value, datetime):
                data_dict[key] = value.isoformat()
            elif hasattr(value, 'pk'):  # Foreign key
                data_dict[key] = value.pk

        # Create a DeletedRecord entry
        DeletedRecord.objects.create(
            model_name=self.object.__class__.__name__,
            record_id=self.object.pk,
            data=json.dumps(data_dict),
            deleted_by=request.user if request.user.is_authenticated else None
        )

        # Now delete the object as usual
        self.object.delete()

        return HttpResponseRedirect(success_url)


class PaginationMixin:
    """
    A mixin to add pagination functionality to ListView classes.
    Allows users to choose between 20, 50, or 100 entries per page.
    Default is 50 entries per page.
    """
    paginate_by = 50  # Default page size

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, from the request's GET parameters.
        Valid values are 20, 50, and 100. Default is 50.
        """
        page_size = self.request.GET.get('page_size', self.paginate_by)
        try:
            page_size = int(page_size)
            if page_size in [20, 50, 100]:
                return page_size
        except (TypeError, ValueError):
            pass
        return self.paginate_by

    def get_context_data(self, **kwargs):
        """
        Add pagination-related context variables.
        """
        context = super().get_context_data(**kwargs)
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        context['available_page_sizes'] = [20, 50, 100]
        return context

# Dashboard view
@login_required
def dashboard(request):
    # Get all projects
    projects = Project.objects.all()

    # Get counts for analytics
    total_products = projects.count()
    total_resources = Resource.objects.count()
    active_products = projects.filter(status='in_progress').count()
    completed_products = projects.filter(status='completed').count()

    # Get projects by status for chart
    products_by_status = projects.values('status').annotate(count=Count('id'))

    # Get resources by project count
    resources_by_product_count = Resource.objects.annotate(product_count=Count('project')).order_by('-product_count')[:5]

    # Get projects with most resources (from filtered set)
    products_with_most_resources = projects.annotate(resource_count=Count('resources')).order_by('-resource_count')[:5]

    # Get recent projects (from filtered set)
    recent_products = projects.order_by('-created_at')[:5]

    # Get overdue projects (from filtered set)
    overdue_products = [p for p in projects.filter(status__in=['not_started', 'in_progress', 'on_hold']) if p.is_overdue]

    # Calculate automation backlog for all projects (from filtered set)
    projects_with_automation_data = projects.filter(
        total_automatable_test_cases__isnull=False,
        total_automated_test_cases__isnull=False
    )

    automation_backlog = []
    for project in projects_with_automation_data:
        backlog = project.total_automatable_test_cases - project.total_automated_test_cases
        if backlog > 0:
            automation_backlog.append({
                'name': project.name,
                'backlog': backlog
            })

    # Calculate smoke coverage percentage (from filtered set)
    projects_with_smoke_data = projects.filter(
        total_automatable_smoke_test_cases__gt=0,
        total_automated_smoke_test_cases__isnull=False
    )

    smoke_coverage_data = []
    for project in projects_with_smoke_data:
        coverage = (project.total_automated_smoke_test_cases / project.total_automatable_smoke_test_cases) * 100
        smoke_coverage_data.append({
            'name': project.name,
            'coverage': round(coverage, 2)
        })

    # Calculate regression coverage percentage (from filtered set)
    projects_with_regression_data = projects.filter(
        total_automatable_test_cases__gt=0,
        total_automated_test_cases__isnull=False
    )

    regression_coverage_data = []
    for project in projects_with_regression_data:
        coverage = (project.total_automated_test_cases / project.total_automatable_test_cases) * 100
        regression_coverage_data.append({
            'name': project.name,
            'coverage': round(coverage, 2)
        })

    # Get resource count based on project assignments
    resources_with_assignments = Resource.objects.annotate(
        assignment_count=Count('projectresource')
    ).order_by('-assignment_count')

    # Get monthly feedback statistics for the current month
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Get resources accessible to the current user
    try:
        user_resource = Resource.objects.get(user=request.user)

        # If user is a lead, show only resources that report to them
        if Resource.objects.filter(lead=user_resource).exists():
            accessible_resources = Resource.objects.filter(lead=user_resource)
        # If user is a manager, show all resources
        elif Resource.objects.filter(manager=user_resource).exists():
            accessible_resources = Resource.objects.all()
        # Otherwise, user can only see themselves
        else:
            accessible_resources = Resource.objects.filter(id=user_resource.id)

    except Resource.DoesNotExist:
        # If user doesn't have a resource, don't show any resources
        accessible_resources = Resource.objects.none()

    # Count feedbacks for accessible resources
    total_feedbacks = accessible_resources.count()

    # Count submitted feedbacks
    submitted_feedbacks = MonthlyFeedback.objects.filter(
        resource__in=accessible_resources,
        month=current_month,
        year=current_year,
        status='submitted'
    ).count()

    # Count due feedbacks
    due_feedbacks = total_feedbacks - submitted_feedbacks

    # Calculate completion percentage
    if total_feedbacks > 0:
        feedback_completion_percentage = (submitted_feedbacks / total_feedbacks) * 100
    else:
        feedback_completion_percentage = 0

    # Get month name for display
    import calendar
    month_name = calendar.month_name[current_month]

    # Get automation runners
    automation_runners = AutomationRunner.objects.all()

    context = {
        'total_products': total_products,
        'total_resources': total_resources,
        'active_products': active_products,
        'completed_products': completed_products,
        'products_by_status': products_by_status,
        'resources_by_product_count': resources_by_product_count,
        'products_with_most_resources': products_with_most_resources,
        'recent_products': recent_products,
        'overdue_products': overdue_products,
        'automation_backlog': automation_backlog,
        'smoke_coverage_data': smoke_coverage_data,
        'regression_coverage_data': regression_coverage_data,
        'resources_with_assignments': resources_with_assignments,
        # Monthly feedback statistics
        'total_feedbacks': total_feedbacks,
        'submitted_feedbacks': submitted_feedbacks,
        'due_feedbacks': due_feedbacks,
        'feedback_completion_percentage': round(feedback_completion_percentage, 2),
        'current_month': month_name,
        'current_year': current_year,
        'automation_runners': automation_runners,
    }

    return render(request, 'dashboard/dashboard.html', context)

# Resource views
class ResourceListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = Resource
    template_name = 'dashboard/resource_list.html'
    context_object_name = 'resources'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by resource name
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # Filter by skill
        skill = self.request.GET.get('skill')
        if skill:
            queryset = queryset.filter(skill=skill)

        # Filter by lead
        lead = self.request.GET.get('lead')
        if lead:
            queryset = queryset.filter(lead=lead)

        # Filter by manager
        manager = self.request.GET.get('manager')
        if manager:
            queryset = queryset.filter(manager=manager)

        # Filter by availability
        availability = self.request.GET.get('availability')
        if availability:
            availability_bool = availability == 'True'
            queryset = queryset.filter(availability=availability_bool)

        # Filter by role (partial match)
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role__icontains=role)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter options to context
        context['skill_choices'] = Resource.SKILL_CHOICES

        # Filter leads to only show resources that are actually leads for someone
        context['leads'] = Resource.objects.filter(team_members_as_lead__isnull=False).distinct()

        # Filter managers to only show resources that are actually managers for someone
        context['managers'] = Resource.objects.filter(team_members_as_manager__isnull=False).distinct()

        context['boolean_choices'] = [('True', 'Yes'), ('False', 'No')]

        # Add current filter values to context
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'skill': self.request.GET.get('skill', ''),
            'lead': self.request.GET.get('lead', ''),
            'manager': self.request.GET.get('manager', ''),
            'availability': self.request.GET.get('availability', ''),
            'role': self.request.GET.get('role', '')
        }

        return context

class ResourceDetailView(LoginRequiredMixin, DetailView):
    model = Resource
    template_name = 'dashboard/resource_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all projects this resource is assigned to
        context['products'] = Project.objects.filter(resources=self.object)
        # Get all project-resource assignments for this resource
        context['project_resources'] = ProjectResource.objects.filter(resource=self.object).select_related('project')
        return context

class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = Resource
    template_name = 'dashboard/resource_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resource-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Handle the team lead and manager checkboxes
        # Store the checkbox state in the session so it can be retrieved when editing
        self.request.session[f'resource_{self.object.pk}_is_team_lead'] = form.cleaned_data.get('is_team_lead', False)
        self.request.session[f'resource_{self.object.pk}_is_manager'] = form.cleaned_data.get('is_manager', False)
        return response

class ResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = Resource
    template_name = 'dashboard/resource_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resource-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Handle the team lead and manager checkboxes
        # Store the checkbox state in the session so it can be retrieved when editing
        self.request.session[f'resource_{self.object.pk}_is_team_lead'] = form.cleaned_data.get('is_team_lead', False)
        self.request.session[f'resource_{self.object.pk}_is_manager'] = form.cleaned_data.get('is_manager', False)
        return response

class ResourceDeleteView(LoginRequiredMixin, RecyclableDeleteView):
    model = Resource
    template_name = 'dashboard/resource_confirm_delete.html'
    success_url = reverse_lazy('resource-list')

# Product views
class ProductListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = Project
    template_name = 'dashboard/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by product name
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by team lead
        team_lead = self.request.GET.get('team_lead')
        if team_lead:
            queryset = queryset.filter(team_lead=team_lead)

        # Filter by smoke automation status
        smoke_automation_status = self.request.GET.get('smoke_automation_status')
        if smoke_automation_status:
            queryset = queryset.filter(smoke_automation_status=smoke_automation_status)

        # Filter by regression automation status
        regression_automation_status = self.request.GET.get('regression_automation_status')
        if regression_automation_status:
            queryset = queryset.filter(regression_automation_status=regression_automation_status)

        # Filter by pipeline schedule
        pipeline_schedule = self.request.GET.get('pipeline_schedule')
        if pipeline_schedule:
            queryset = queryset.filter(pipeline_schedule=pipeline_schedule)

        # Filter by production status
        in_production = self.request.GET.get('in_production')
        if in_production:
            in_production_bool = in_production == 'True'
            queryset = queryset.filter(in_production=in_production_bool)

        # Filter by development status
        in_development = self.request.GET.get('in_development')
        if in_development:
            in_development_bool = in_development == 'True'
            queryset = queryset.filter(in_development=in_development_bool)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter options to context
        context['status_choices'] = Project.STATUS_CHOICES
        context['automation_status_choices'] = Project.AUTOMATION_STATUS_CHOICES
        context['pipeline_schedule_choices'] = Project.PIPELINE_SCHEDULE_CHOICES
        # Filter team_leads to only show resources that are actually team leads for products
        context['team_leads'] = Resource.objects.filter(products_as_lead__isnull=False).distinct()
        context['boolean_choices'] = [('True', 'Yes'), ('False', 'No')]

        # Add current filter values to context
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'team_lead': self.request.GET.get('team_lead', ''),
            'smoke_automation_status': self.request.GET.get('smoke_automation_status', ''),
            'regression_automation_status': self.request.GET.get('regression_automation_status', ''),
            'pipeline_schedule': self.request.GET.get('pipeline_schedule', ''),
            'in_production': self.request.GET.get('in_production', ''),
            'in_development': self.request.GET.get('in_development', '')
        }

        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'dashboard/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_resources'] = ProjectResource.objects.filter(project=self.object)

        # Get backup resources for this product
        context['backup_resources'] = ProductBackupResource.objects.filter(project=self.object)

        # Get historical project updates from weekly meetings
        historical_updates = WeeklyProjectUpdate.objects.filter(
            project=self.object
        ).order_by('-meeting__meeting_date')

        # Get documentation for this product
        context['documentation'] = ProductDocumentation.objects.filter(project=self.object)

        # Get manual product updates
        manual_updates = WeeklyProductUpdate.objects.filter(
            project=self.object
        ).order_by('-meeting__meeting_date')
        context['manual_updates'] = manual_updates

        # Prepare data for smoke coverage chart
        smoke_coverage_data = []
        if self.object.smoke_coverage is not None:
            smoke_coverage_data = [
                {'name': 'Smoke Coverage', 'coverage': self.object.smoke_coverage},
                {'name': 'Remaining', 'coverage': 100 - self.object.smoke_coverage}
            ]
        context['smoke_coverage_data'] = smoke_coverage_data

        # Prepare data for regression coverage chart
        regression_coverage_data = []
        if self.object.regression_coverage is not None:
            regression_coverage_data = [
                {'name': 'Regression Coverage', 'coverage': self.object.regression_coverage},
                {'name': 'Remaining', 'coverage': 100 - self.object.regression_coverage}
            ]
        context['regression_coverage_data'] = regression_coverage_data

        context['historical_updates'] = historical_updates
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'dashboard/product_form.html'
    fields = [
        'name', 'description', 'status',
        # Automation related fields
        'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule',
        'execution_time_of_smoke', 'total_number_of_available_test_cases',
        'status_of_last_automation_run', 'date_of_last_automation_run',
        'automation_framework_tech_stack', 'team_lead',
        'bugs_found_through_automation', 'total_automatable_test_cases',
        'total_automatable_smoke_test_cases', 'total_automated_test_cases',
        'total_automated_smoke_test_cases', 'sprint_cycle',
        'total_number_of_functional_test_cases', 'total_number_of_business_test_cases',
        'oat_release_cycle', 'in_production', 'in_development'
    ]
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Calculate regression coverage
        if self.object.total_automatable_test_cases and self.object.total_automatable_test_cases > 0:
            self.object.regression_coverage = int((self.object.total_automated_test_cases or 0) / self.object.total_automatable_test_cases * 100)
        else:
            self.object.regression_coverage = 0

        # Calculate smoke coverage
        if self.object.total_automatable_smoke_test_cases and self.object.total_automatable_smoke_test_cases > 0:
            self.object.smoke_coverage = int((self.object.total_automated_smoke_test_cases or 0) / self.object.total_automatable_smoke_test_cases * 100)
        else:
            self.object.smoke_coverage = 0

        self.object.save()
        return response

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'dashboard/product_form.html'
    fields = [
        'name', 'description', 'status',
        # Automation related fields
        'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule',
        'execution_time_of_smoke', 'total_number_of_available_test_cases',
        'status_of_last_automation_run', 'date_of_last_automation_run',
        'automation_framework_tech_stack', 'team_lead',
        'bugs_found_through_automation', 'total_automatable_test_cases',
        'total_automatable_smoke_test_cases', 'total_automated_test_cases',
        'total_automated_smoke_test_cases', 'sprint_cycle',
        'total_number_of_functional_test_cases', 'total_number_of_business_test_cases',
        'oat_release_cycle', 'in_production', 'in_development'
    ]
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Calculate regression coverage
        if self.object.total_automatable_test_cases and self.object.total_automatable_test_cases > 0:
            self.object.regression_coverage = int((self.object.total_automated_test_cases or 0) / self.object.total_automatable_test_cases * 100)
        else:
            self.object.regression_coverage = 0

        # Calculate smoke coverage
        if self.object.total_automatable_smoke_test_cases and self.object.total_automatable_smoke_test_cases > 0:
            self.object.smoke_coverage = int((self.object.total_automated_smoke_test_cases or 0) / self.object.total_automatable_smoke_test_cases * 100)
        else:
            self.object.smoke_coverage = 0

        self.object.save()
        return response

class ProductDeleteView(LoginRequiredMixin, RecyclableDeleteView):
    model = Project
    template_name = 'dashboard/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object
        return context

# Product Resource Assignment views
def assign_resource(request, product_id):
    project = get_object_or_404(Project, id=product_id)

    if request.method == 'POST':
        resource_id = request.POST.get('resource')
        hours = request.POST.get('hours_allocated')
        utilization = request.POST.get('utilization_percentage', 0)
        eta = request.POST.get('eta', None)
        notes = request.POST.get('notes', '')

        if resource_id:
            resource = get_object_or_404(Resource, id=resource_id)

            # Check if assignment already exists
            project_resource, created = ProjectResource.objects.get_or_create(
                project=project,
                resource=resource,
                defaults={
                    'hours_allocated': hours,
                    'utilization_percentage': utilization,
                    'eta': eta if eta else None,
                    'notes': notes,
                    'assigned_date': timezone.now()
                }
            )

            if not created:
                project_resource.hours_allocated = hours
                project_resource.utilization_percentage = utilization
                project_resource.eta = eta if eta else None
                project_resource.notes = notes
                project_resource.save()
                messages.success(request, f'Updated assignment for {resource.name}')
            else:
                messages.success(request, f'Assigned {resource.name} to {project.name}')

            return redirect('product-detail', pk=project.id)

    # Get resources not already assigned to this project
    assigned_resources = project.resources.all()
    available_resources = Resource.objects.exclude(id__in=[r.id for r in assigned_resources])

    context = {
        'product': project,
        'available_resources': available_resources
    }

    return render(request, 'dashboard/assign_resource.html', context)

def remove_resource(request, product_id, resource_id):
    project_resource = get_object_or_404(ProjectResource, project_id=product_id, resource_id=resource_id)
    resource_name = project_resource.resource.name
    project_name = project_resource.project.name

    project_resource.delete()
    messages.success(request, f'Removed {resource_name} from {project_name}')

    return redirect('product-detail', pk=product_id)

def update_resource_notes(request, product_id, resource_id):
    """Update notes and ETA for a resource assignment."""
    project_resource = get_object_or_404(ProjectResource, project_id=product_id, resource_id=resource_id)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        eta = request.POST.get('eta', None)

        project_resource.notes = notes
        project_resource.eta = eta if eta else None
        project_resource.save()

        messages.success(request, f'Updated information for {project_resource.resource.name} on {project_resource.project.name}')

    # Redirect back to the resource alignment page
    return redirect('resource-alignment')

def assign_backup_resource(request, product_id):
    """Assign a backup resource to a product."""
    project = get_object_or_404(Project, id=product_id)

    if request.method == 'POST':
        resource_id = request.POST.get('resource')
        notes = request.POST.get('notes', '')

        if resource_id:
            resource = get_object_or_404(Resource, id=resource_id)

            # Check if resource is already a backup for this project
            backup_resource, created = ProductBackupResource.objects.get_or_create(
                project=project,
                resource=resource,
                defaults={
                    'notes': notes,
                    'assigned_date': timezone.now()
                }
            )

            if not created:
                backup_resource.notes = notes
                backup_resource.save()
                messages.success(request, f'Updated backup assignment for {resource.name}')
            else:
                messages.success(request, f'Assigned {resource.name} as backup for {project.name}')

            return redirect('product-detail', pk=project.id)

    # Get all resources
    all_resources = Resource.objects.all()

    # Get resources already assigned as backups to this project
    backup_resources = project.backup_resources.all()
    backup_resource_ids = [br.resource.id for br in backup_resources]

    # Filter out resources already assigned as backups
    available_resources = all_resources.exclude(id__in=backup_resource_ids)

    context = {
        'product': project,
        'available_resources': available_resources
    }

    return render(request, 'dashboard/assign_backup_resource.html', context)

def remove_backup_resource(request, product_id, resource_id):
    """Remove a backup resource from a product."""
    backup_resource = get_object_or_404(ProductBackupResource, project_id=product_id, resource_id=resource_id)
    resource_name = backup_resource.resource.name
    project_name = backup_resource.project.name

    backup_resource.delete()
    messages.success(request, f'Removed {resource_name} as backup from {project_name}')

    return redirect('product-detail', pk=product_id)

def update_backup_resource_notes(request, product_id, resource_id):
    """Update notes for a backup resource assignment."""
    backup_resource = get_object_or_404(ProductBackupResource, project_id=product_id, resource_id=resource_id)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')

        backup_resource.notes = notes
        backup_resource.save()

        messages.success(request, f'Updated information for backup resource {backup_resource.resource.name} on {backup_resource.project.name}')

    return redirect('product-detail', pk=product_id)

# Weekly Automation Updates views
class WeeklyMeetingListView(PaginationMixin, ListView):
    model = WeeklyMeeting
    template_name = 'dashboard/weekly_meeting_list.html'
    context_object_name = 'meetings'
    ordering = ['-meeting_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_meetings = [m for m in context['meetings'] if not m.is_completed]
        completed_meetings = [m for m in context['meetings'] if m.is_completed]
        context['has_active_meetings'] = len(active_meetings) > 0
        context['has_completed_meetings'] = len(completed_meetings) > 0
        # Add counts for tab badges
        context['active_count'] = len(active_meetings)
        context['completed_count'] = len(completed_meetings)
        return context

class WeeklyMeetingDetailView(DetailView):
    model = WeeklyMeeting
    template_name = 'dashboard/weekly_meeting_detail.html'
    context_object_name = 'meeting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_updates'] = WeeklyProjectUpdate.objects.filter(meeting=self.object)

        # Check if there's an active meeting session in the session
        context['meeting_active'] = self.request.session.get(f'meeting_active_{self.object.id}', False)

        # Add data for select elements
        context['resources'] = Resource.objects.all()
        context['sprint_cycles'] = SprintCycle.objects.all()
        context['oat_release_cycles'] = OATReleaseCycle.objects.all()

        return context

class WeeklyMeetingCreateView(CreateView):
    model = WeeklyMeeting
    template_name = 'dashboard/weekly_meeting_form.html'
    fields = ['meeting_date', 'title', 'notes', 'is_completed']
    success_url = reverse_lazy('weekly-meeting-list')

class WeeklyMeetingUpdateView(UpdateView):
    model = WeeklyMeeting
    template_name = 'dashboard/weekly_meeting_form.html'
    fields = ['meeting_date', 'title', 'notes', 'is_completed']
    success_url = reverse_lazy('weekly-meeting-list')

class WeeklyMeetingDeleteView(RecyclableDeleteView):
    model = WeeklyMeeting
    template_name = 'dashboard/weekly_meeting_confirm_delete.html'
    context_object_name = 'meeting'
    success_url = reverse_lazy('weekly-meeting-list')

class WeeklyProjectUpdateDetailView(DetailView):
    model = WeeklyProjectUpdate
    template_name = 'dashboard/weekly_project_update_detail.html'
    context_object_name = 'project_update'

class WeeklyProjectUpdateEditView(UpdateView):
    model = WeeklyProjectUpdate
    template_name = 'dashboard/weekly_project_update_form.html'
    context_object_name = 'project_update'
    fields = [
        'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule',
        'execution_time_hours', 'execution_time_minutes', 'total_available_test_cases',
        'bugs_found_through_automation', 'regression_coverage', 'total_automatable_test_cases',
        'total_automated_test_cases', 'total_automated_smoke_test_cases', 'sprint_cycle',
        'last_automation_run_status', 'last_automation_run_date', 'automation_framework_tech_stack',
        'functional_test_cases_count', 'business_test_cases_count', 'oat_release_cycle',
        'readiness_for_production', 'team_lead'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resources'] = Resource.objects.all()
        context['sprint_cycles'] = SprintCycle.objects.all()
        context['oat_release_cycles'] = OATReleaseCycle.objects.all()
        context['meeting_active'] = self.request.session.get(f'meeting_active_{self.object.meeting.id}', False)
        return context

    def get_success_url(self):
        return reverse_lazy('weekly-meeting-detail', kwargs={'pk': self.object.meeting.id})

# Start and End Weekly Meeting views
def start_weekly_meeting(request, pk):
    meeting = get_object_or_404(WeeklyMeeting, pk=pk)

    if request.method == 'POST':
        # Set the meeting as active in the session
        request.session[f'meeting_active_{meeting.id}'] = True

        # Get all projects
        projects = Project.objects.all()

        # Store original project values in the session for comparison when the meeting ends
        original_values = {}

        # Create WeeklyProjectUpdate objects for each project if they don't exist
        for project in projects:
            # Store original values for this project
            original_values[project.id] = {
                'smoke_automation_status': project.smoke_automation_status or 'na',
                'regression_automation_status': project.regression_automation_status or 'na',
                'pipeline_schedule': project.pipeline_schedule or 'na',
                'execution_time_of_smoke': project.execution_time_of_smoke or "0h 0m",
                'total_number_of_available_test_cases': project.total_number_of_available_test_cases or 0,
                'bugs_found_through_automation': project.bugs_found_through_automation or 0,
                'regression_coverage': project.regression_coverage or 0,
                'total_automatable_test_cases': project.total_automatable_test_cases or 0,
                'total_automated_test_cases': project.total_automated_test_cases or 0,
                'total_automated_smoke_test_cases': project.total_automated_smoke_test_cases or 0,
                'status_of_last_automation_run': project.status_of_last_automation_run or '',
                'date_of_last_automation_run': project.date_of_last_automation_run.strftime('%Y-%m-%d') if project.date_of_last_automation_run else None,
                'automation_framework_tech_stack': project.automation_framework_tech_stack or '',
                'total_number_of_functional_test_cases': project.total_number_of_functional_test_cases or 0,
                'total_number_of_business_test_cases': project.total_number_of_business_test_cases or 0,
                'readiness_for_production': getattr(project, 'readiness_for_production', False),
                'team_lead_id': project.team_lead.id if project.team_lead else None,
                'team_lead_name': project.team_lead.name if project.team_lead else 'Not assigned',
                'sprint_cycle': project.sprint_cycle or '',
                'oat_release_cycle': project.oat_release_cycle or '',
            }

            # Parse execution time from project
            execution_hours = 0
            execution_minutes = 0
            if project.execution_time_of_smoke:
                time_str = project.execution_time_of_smoke.strip()
                # Try to parse "Xh Ym" format
                import re
                match = re.match(r'(\d+)h\s*(\d+)m', time_str)
                if match:
                    execution_hours = int(match.group(1))
                    execution_minutes = int(match.group(2))

            # Look up SprintCycle and OATReleaseCycle objects based on string values
            sprint_cycle = None
            oat_release_cycle = None

            if project.sprint_cycle:
                try:
                    sprint_cycle = SprintCycle.objects.get(name=project.sprint_cycle.strip())
                except SprintCycle.DoesNotExist:
                    pass

            if project.oat_release_cycle:
                try:
                    oat_release_cycle = OATReleaseCycle.objects.get(name=project.oat_release_cycle.strip())
                except OATReleaseCycle.DoesNotExist:
                    pass

            WeeklyProjectUpdate.objects.get_or_create(
                meeting=meeting,
                project=project,
                defaults={
                    'smoke_automation_status': project.smoke_automation_status or 'na',
                    'regression_automation_status': project.regression_automation_status or 'na',
                    'pipeline_schedule': project.pipeline_schedule or 'na',
                    'execution_time_hours': execution_hours,
                    'execution_time_minutes': execution_minutes,
                    'total_available_test_cases': project.total_number_of_available_test_cases or 0,
                    'bugs_found_through_automation': project.bugs_found_through_automation or 0,
                    'regression_coverage': project.regression_coverage or 0,
                    'total_automatable_test_cases': project.total_automatable_test_cases or 0,
                    'total_automated_test_cases': project.total_automated_test_cases or 0,
                    'total_automated_smoke_test_cases': project.total_automated_smoke_test_cases or 0,
                    'last_automation_run_status': project.status_of_last_automation_run or '',
                    'last_automation_run_date': project.date_of_last_automation_run,
                    'automation_framework_tech_stack': project.automation_framework_tech_stack or '',
                    'functional_test_cases_count': project.total_number_of_functional_test_cases or 0,
                    'business_test_cases_count': project.total_number_of_business_test_cases or 0,
                    'readiness_for_production': getattr(project, 'readiness_for_production', False),
                    'team_lead': project.team_lead,
                    'sprint_cycle': sprint_cycle,
                    'oat_release_cycle': oat_release_cycle,
                }
            )

        # Store original values in the session
        request.session[f'original_values_{meeting.id}'] = original_values

        messages.success(request, f'Weekly meeting "{meeting.title}" has been started.')

    return redirect('weekly-meeting-detail', pk=meeting.id)

def end_weekly_meeting(request, pk):
    meeting = get_object_or_404(WeeklyMeeting, pk=pk)

    if request.method == 'POST':
        # Get the original values from the session
        original_values = request.session.get(f'original_values_{meeting.id}', {})

        # Remove the meeting active flag and original values from the session
        if f'meeting_active_{meeting.id}' in request.session:
            del request.session[f'meeting_active_{meeting.id}']
        if f'original_values_{meeting.id}' in request.session:
            del request.session[f'original_values_{meeting.id}']

        # Mark the meeting as completed
        meeting.is_completed = True
        meeting.save()

        # Get all project updates for this meeting
        project_updates = WeeklyProjectUpdate.objects.filter(meeting=meeting)

        # Generate meeting notes summarizing changes
        summary_notes = []

        for update in project_updates:
            project = update.project
            changes = []

            # Skip if we don't have original values for this project
            if str(project.id) not in original_values:
                continue

            # Get original values for this project
            orig = original_values[str(project.id)]

            # Check for changes in each field by comparing with original values (not current project values)
            # Only add to changes if the values are actually different

            # For status fields, compare the actual values, not the display values
            orig_smoke_status = str(orig['smoke_automation_status'])
            update_smoke_status = str(update.smoke_automation_status)
            if orig_smoke_status != update_smoke_status:
                # Get display values for the status choices
                old_status = dict(Project.AUTOMATION_STATUS_CHOICES).get(orig['smoke_automation_status'], orig['smoke_automation_status'])
                new_status = dict(Project.AUTOMATION_STATUS_CHOICES).get(update.smoke_automation_status, update.smoke_automation_status)
                changes.append(f"Smoke Automation Status changed from '{old_status}' to '{new_status}'")

            orig_regression_status = str(orig['regression_automation_status'])
            update_regression_status = str(update.regression_automation_status)
            if orig_regression_status != update_regression_status:
                old_status = dict(Project.AUTOMATION_STATUS_CHOICES).get(orig['regression_automation_status'], orig['regression_automation_status'])
                new_status = dict(Project.AUTOMATION_STATUS_CHOICES).get(update.regression_automation_status, update.regression_automation_status)
                changes.append(f"Regression Automation Status changed from '{old_status}' to '{new_status}'")

            orig_pipeline = str(orig['pipeline_schedule'])
            update_pipeline = str(update.pipeline_schedule)
            if orig_pipeline != update_pipeline:
                old_schedule = dict(Project.PIPELINE_SCHEDULE_CHOICES).get(orig['pipeline_schedule'], orig['pipeline_schedule'])
                new_schedule = dict(Project.PIPELINE_SCHEDULE_CHOICES).get(update.pipeline_schedule, update.pipeline_schedule)
                changes.append(f"Pipeline Schedule changed from '{old_schedule}' to '{new_schedule}'")

            # For numeric fields, convert to integers before comparing
            orig_available_tests = int(orig['total_number_of_available_test_cases'])
            update_available_tests = int(update.total_available_test_cases)
            if orig_available_tests != update_available_tests:
                changes.append(f"Total Available Test Cases changed from {orig_available_tests} to {update_available_tests}")

            orig_regression_coverage = int(orig['regression_coverage'])
            update_regression_coverage = int(update.regression_coverage)
            if orig_regression_coverage != update_regression_coverage:
                changes.append(f"Regression Coverage changed from {orig_regression_coverage}% to {update_regression_coverage}%")

            orig_bugs = int(orig['bugs_found_through_automation'])
            update_bugs = int(update.bugs_found_through_automation)
            if orig_bugs != update_bugs:
                changes.append(f"Bugs Found Through Automation changed from {orig_bugs} to {update_bugs}")

            # Check for changes in execution time
            update_execution_time = update.get_execution_time_display()
            orig_execution_time = str(orig['execution_time_of_smoke'] or '')

            # Normalize empty values to "0h 0m" for comparison
            if not orig_execution_time or orig_execution_time.strip() == '':
                orig_execution_time = "0h 0m"

            # Normalize "0h 0m" values for comparison
            is_orig_zero = orig_execution_time.strip() == "0h 0m"
            is_update_zero = update_execution_time.strip() == "0h 0m"

            # Only add to changes if there's a real difference and not just empty values
            # Also check if execution time fields were modified during the meeting
            if update_execution_time != orig_execution_time and not (is_orig_zero and is_update_zero) and \
               ('execution_time_hours' in request.session.get(f'modified_fields_{meeting.id}_{project.id}', []) or \
                'execution_time_minutes' in request.session.get(f'modified_fields_{meeting.id}_{project.id}', [])):
                changes.append(f"Execution Time changed from {orig_execution_time} to {update_execution_time}")

            # Check for changes in test case counts
            orig_automatable = int(orig['total_automatable_test_cases'])
            update_automatable = int(update.total_automatable_test_cases)
            if orig_automatable != update_automatable:
                changes.append(f"Total Automatable Test Cases changed from {orig_automatable} to {update_automatable}")

            orig_automated = int(orig['total_automated_test_cases'])
            update_automated = int(update.total_automated_test_cases)
            if orig_automated != update_automated:
                changes.append(f"Total Automated Test Cases changed from {orig_automated} to {update_automated}")

            orig_smoke = int(orig['total_automated_smoke_test_cases'])
            update_smoke = int(update.total_automated_smoke_test_cases)
            if orig_smoke != update_smoke:
                changes.append(f"Total Automated Smoke Test Cases changed from {orig_smoke} to {update_smoke}")

            orig_functional = int(orig['total_number_of_functional_test_cases'])
            update_functional = int(update.functional_test_cases_count)
            if orig_functional != update_functional:
                changes.append(f"Functional Test Cases changed from {orig_functional} to {update_functional}")

            orig_business = int(orig['total_number_of_business_test_cases'])
            update_business = int(update.business_test_cases_count)
            if orig_business != update_business:
                changes.append(f"Business Test Cases changed from {orig_business} to {update_business}")

            # Check for changes in text fields
            orig_run_status = str(orig['status_of_last_automation_run'] or '').strip()
            update_run_status = str(update.last_automation_run_status or '').strip()
            # Only add to changes if there's a real difference (ignoring whitespace)
            if orig_run_status != update_run_status:
                old_status = orig_run_status or 'Not specified'
                new_status = update_run_status or 'Not specified'
                changes.append(f"Last Automation Run Status changed from '{old_status}' to '{new_status}'")

            orig_tech_stack = str(orig['automation_framework_tech_stack'] or '').strip()
            update_tech_stack = str(update.automation_framework_tech_stack or '').strip()
            # Only add to changes if there's a real difference (ignoring whitespace)
            if orig_tech_stack != update_tech_stack:
                old_stack = orig_tech_stack or 'Not specified'
                new_stack = update_tech_stack or 'Not specified'
                changes.append(f"Automation Framework/Tech Stack changed from '{old_stack}' to '{new_stack}'")

            # Check for changes in date fields
            update_date = update.last_automation_run_date.strftime('%Y-%m-%d') if update.last_automation_run_date else None
            orig_date = orig['date_of_last_automation_run']

            # Normalize None and empty string values for comparison
            if update_date is None and (orig_date is None or orig_date == ''):
                # Both are effectively empty, so no change
                pass
            elif update_date != orig_date:
                old_date = orig_date or 'Not specified'
                new_date = update_date or 'Not specified'
                changes.append(f"Last Automation Run Date changed from {old_date} to {new_date}")

            # Check for changes in boolean fields
            orig_readiness = bool(orig['readiness_for_production'])
            update_readiness = bool(update.readiness_for_production)
            if orig_readiness != update_readiness:
                old_status = 'Ready' if orig_readiness else 'Not Ready'
                new_status = 'Ready' if update_readiness else 'Not Ready'
                changes.append(f"Readiness for Production changed from {old_status} to {new_status}")

            # Check for changes in foreign key fields
            update_team_lead_id = update.team_lead.id if update.team_lead else None
            orig_team_lead_id = orig['team_lead_id']

            # Only consider it a change if at least one value is not None
            # and they are different
            if (update_team_lead_id is not None or orig_team_lead_id is not None) and update_team_lead_id != orig_team_lead_id:
                old_lead = orig['team_lead_name']
                new_lead = update.team_lead.name if update.team_lead else 'Not assigned'
                changes.append(f"Team Lead changed from {old_lead} to {new_lead}")

            # For sprint_cycle, compare with the original string value
            update_sprint_cycle_name = update.sprint_cycle.name if update.sprint_cycle else ''
            orig_sprint_cycle = str(orig['sprint_cycle'] or '')

            # Normalize empty values for comparison
            update_sprint_cycle_name = update_sprint_cycle_name.strip()
            orig_sprint_cycle = orig_sprint_cycle.strip()

            # Only consider it a change if the user actually made changes during the meeting
            # If both values are empty or both values are the same, don't report a change
            # Check if 'sprint_cycle' is in the modified fields to ensure it was actually changed by the user
            if update_sprint_cycle_name != orig_sprint_cycle and 'sprint_cycle' in request.session.get(f'modified_fields_{meeting.id}_{project.id}', []):
                old_cycle = orig_sprint_cycle or 'Not specified'
                new_cycle = update_sprint_cycle_name or 'Not specified'
                changes.append(f"Sprint Cycle changed from {old_cycle} to {new_cycle}")

            # For oat_release_cycle, compare with the original string value
            update_oat_cycle_name = update.oat_release_cycle.name if update.oat_release_cycle else ''
            orig_oat_cycle = str(orig['oat_release_cycle'] or '')

            # Normalize empty values for comparison
            update_oat_cycle_name = update_oat_cycle_name.strip()
            orig_oat_cycle = orig_oat_cycle.strip()

            # Only consider it a change if the user actually made changes during the meeting
            # If both values are empty or both values are the same, don't report a change
            # Check if 'oat_release_cycle' is in the modified fields to ensure it was actually changed by the user
            if update_oat_cycle_name != orig_oat_cycle and 'oat_release_cycle' in request.session.get(f'modified_fields_{meeting.id}_{project.id}', []):
                old_cycle = orig_oat_cycle or 'Not specified'
                new_cycle = update_oat_cycle_name or 'Not specified'
                changes.append(f"OAT Release Cycle changed from {old_cycle} to {new_cycle}")

            if changes:
                summary_notes.append(f"Project: {project.name}\n" + "\n".join([f"- {change}" for change in changes]))

        # Update meeting notes with the summary
        if summary_notes:
            meeting_summary = "Meeting Summary:\n\n" + "\n\n".join(summary_notes)
            if meeting.notes:
                meeting.notes += f"\n\n{meeting_summary}"
            else:
                meeting.notes = meeting_summary
            meeting.save()

        # Update project fields with values from project updates
        for update in project_updates:
            project = update.project

            # Get the modified fields for this project update from the session
            modified_fields = request.session.get(f'modified_fields_{meeting.id}_{project.id}', [])

            # Only update fields that were explicitly modified during the meeting
            if 'smoke_automation_status' in modified_fields:
                project.smoke_automation_status = update.smoke_automation_status

            if 'regression_automation_status' in modified_fields:
                project.regression_automation_status = update.regression_automation_status

            if 'pipeline_schedule' in modified_fields:
                project.pipeline_schedule = update.pipeline_schedule

            # Update additional fields that were modified during the meeting
            if 'execution_time_hours' in modified_fields or 'execution_time_minutes' in modified_fields:
                # Format execution time as "Xh Ym"
                project.execution_time_of_smoke = f"{update.execution_time_hours}h {update.execution_time_minutes}m"

            if 'total_available_test_cases' in modified_fields:
                project.total_number_of_available_test_cases = update.total_available_test_cases

            if 'bugs_found_through_automation' in modified_fields:
                project.bugs_found_through_automation = update.bugs_found_through_automation

            if 'regression_coverage' in modified_fields:
                project.regression_coverage = update.regression_coverage

            if 'total_automatable_test_cases' in modified_fields:
                project.total_automatable_test_cases = update.total_automatable_test_cases

            if 'total_automated_test_cases' in modified_fields:
                project.total_automated_test_cases = update.total_automated_test_cases

            if 'total_automated_smoke_test_cases' in modified_fields:
                project.total_automated_smoke_test_cases = update.total_automated_smoke_test_cases

            if 'functional_test_cases_count' in modified_fields:
                project.total_number_of_functional_test_cases = update.functional_test_cases_count

            if 'business_test_cases_count' in modified_fields:
                project.total_number_of_business_test_cases = update.business_test_cases_count

            if 'last_automation_run_status' in modified_fields:
                project.status_of_last_automation_run = update.last_automation_run_status

            if 'last_automation_run_date' in modified_fields:
                project.date_of_last_automation_run = update.last_automation_run_date

            if 'automation_framework_tech_stack' in modified_fields:
                project.automation_framework_tech_stack = update.automation_framework_tech_stack

            if 'readiness_for_production' in modified_fields:
                project.readiness_for_production = update.readiness_for_production

            if 'team_lead' in modified_fields:
                project.team_lead = update.team_lead

            if 'sprint_cycle' in modified_fields:
                project.sprint_cycle = update.sprint_cycle.name if update.sprint_cycle else ""

            if 'oat_release_cycle' in modified_fields:
                project.oat_release_cycle = update.oat_release_cycle.name if update.oat_release_cycle else ""

            # Save the project with the updated fields
            project.save()

            # Remove the modified fields from the session
            if f'modified_fields_{meeting.id}_{project.id}' in request.session:
                del request.session[f'modified_fields_{meeting.id}_{project.id}']

        messages.success(request, f'Weekly meeting "{meeting.title}" has been completed and summary notes have been generated.')

    return redirect('weekly-meeting-detail', pk=meeting.id)

def update_project_in_meeting(request, meeting_id, project_id):
    meeting = get_object_or_404(WeeklyMeeting, pk=meeting_id)
    project = get_object_or_404(Project, pk=project_id)

    # Check if the meeting is active
    if not request.session.get(f'meeting_active_{meeting.id}', False):
        messages.error(request, "This meeting is not currently active.")
        return redirect('weekly-meeting-detail', pk=meeting.id)

    # Get the project update or create it if it doesn't exist
    project_update, created = WeeklyProjectUpdate.objects.get_or_create(
        meeting=meeting,
        project=project
    )

    if request.method == 'POST':

        # Store original values to track changes
        original_values = {}
        if not created:
            # If the project update already exists, store its current values
            original_values = {
                'smoke_automation_status': project_update.smoke_automation_status,
                'regression_automation_status': project_update.regression_automation_status,
                'pipeline_schedule': project_update.pipeline_schedule,
                'execution_time_hours': project_update.execution_time_hours,
                'execution_time_minutes': project_update.execution_time_minutes,
                'total_available_test_cases': project_update.total_available_test_cases,
                'bugs_found_through_automation': project_update.bugs_found_through_automation,
                'regression_coverage': project_update.regression_coverage,
                'total_automatable_test_cases': project_update.total_automatable_test_cases,
                'total_automated_test_cases': project_update.total_automated_test_cases,
                'total_automated_smoke_test_cases': project_update.total_automated_smoke_test_cases,
                'functional_test_cases_count': project_update.functional_test_cases_count,
                'business_test_cases_count': project_update.business_test_cases_count,
                'last_automation_run_status': project_update.last_automation_run_status,
                'automation_framework_tech_stack': project_update.automation_framework_tech_stack,
                'last_automation_run_date': project_update.last_automation_run_date,
                'readiness_for_production': project_update.readiness_for_production,
                'team_lead_id': project_update.team_lead.id if project_update.team_lead else None,
                'sprint_cycle_id': project_update.sprint_cycle.id if project_update.sprint_cycle else None,
                'oat_release_cycle_id': project_update.oat_release_cycle.id if project_update.oat_release_cycle else None,
            }

        # Track which fields have been modified
        modified_fields = []

        # Update status fields only if they've changed
        new_smoke_status = request.POST.get('smoke_automation_status', project_update.smoke_automation_status)
        if new_smoke_status != project_update.smoke_automation_status:
            project_update.smoke_automation_status = new_smoke_status
            modified_fields.append('smoke_automation_status')

        new_regression_status = request.POST.get('regression_automation_status', project_update.regression_automation_status)
        if new_regression_status != project_update.regression_automation_status:
            project_update.regression_automation_status = new_regression_status
            modified_fields.append('regression_automation_status')

        new_pipeline_schedule = request.POST.get('pipeline_schedule', project_update.pipeline_schedule)
        if new_pipeline_schedule != project_update.pipeline_schedule:
            project_update.pipeline_schedule = new_pipeline_schedule
            modified_fields.append('pipeline_schedule')

        # Handle numeric fields with validation
        try:
            # Update execution time hours if changed
            new_execution_time_hours = int(request.POST.get('execution_time_hours', 0))
            if new_execution_time_hours != project_update.execution_time_hours:
                project_update.execution_time_hours = new_execution_time_hours
                modified_fields.append('execution_time_hours')

            # Update execution time minutes if changed
            new_execution_time_minutes = int(request.POST.get('execution_time_minutes', 0))
            if new_execution_time_minutes != project_update.execution_time_minutes:
                project_update.execution_time_minutes = new_execution_time_minutes
                modified_fields.append('execution_time_minutes')

            # Update total available test cases if changed
            new_total_available_test_cases = int(request.POST.get('total_available_test_cases', 0))
            if new_total_available_test_cases != project_update.total_available_test_cases:
                project_update.total_available_test_cases = new_total_available_test_cases
                modified_fields.append('total_available_test_cases')

            # Update bugs found through automation if changed
            new_bugs_found = int(request.POST.get('bugs_found_through_automation', 0))
            if new_bugs_found != project_update.bugs_found_through_automation:
                project_update.bugs_found_through_automation = new_bugs_found
                modified_fields.append('bugs_found_through_automation')

            # Update regression coverage if changed
            new_regression_coverage = int(request.POST.get('regression_coverage', 0))
            if new_regression_coverage != project_update.regression_coverage:
                project_update.regression_coverage = new_regression_coverage
                modified_fields.append('regression_coverage')

            # Update total automatable test cases if changed
            new_total_automatable = int(request.POST.get('total_automatable_test_cases', 0))
            if new_total_automatable != project_update.total_automatable_test_cases:
                project_update.total_automatable_test_cases = new_total_automatable
                modified_fields.append('total_automatable_test_cases')

            # Update total automated test cases if changed
            new_total_automated = int(request.POST.get('total_automated_test_cases', 0))
            if new_total_automated != project_update.total_automated_test_cases:
                project_update.total_automated_test_cases = new_total_automated
                modified_fields.append('total_automated_test_cases')

            # Update total automated smoke test cases if changed
            new_total_automated_smoke = int(request.POST.get('total_automated_smoke_test_cases', 0))
            if new_total_automated_smoke != project_update.total_automated_smoke_test_cases:
                project_update.total_automated_smoke_test_cases = new_total_automated_smoke
                modified_fields.append('total_automated_smoke_test_cases')

            # Update functional test cases count if changed
            new_functional_test_cases = int(request.POST.get('functional_test_cases_count', 0))
            if new_functional_test_cases != project_update.functional_test_cases_count:
                project_update.functional_test_cases_count = new_functional_test_cases
                modified_fields.append('functional_test_cases_count')

            # Update business test cases count if changed
            new_business_test_cases = int(request.POST.get('business_test_cases_count', 0))
            if new_business_test_cases != project_update.business_test_cases_count:
                project_update.business_test_cases_count = new_business_test_cases
                modified_fields.append('business_test_cases_count')
        except ValueError:
            messages.error(request, "Invalid numeric value provided.")
            return redirect('weekly-meeting-detail', pk=meeting.id)

        # Handle text fields
        new_last_automation_run_status = request.POST.get('last_automation_run_status', '')
        if new_last_automation_run_status != project_update.last_automation_run_status:
            project_update.last_automation_run_status = new_last_automation_run_status
            modified_fields.append('last_automation_run_status')

        new_automation_framework_tech_stack = request.POST.get('automation_framework_tech_stack', '')
        if new_automation_framework_tech_stack != project_update.automation_framework_tech_stack:
            project_update.automation_framework_tech_stack = new_automation_framework_tech_stack
            modified_fields.append('automation_framework_tech_stack')

        # Handle date fields
        last_run_date = request.POST.get('last_automation_run_date')
        if last_run_date:
            try:
                new_last_run_date = timezone.datetime.strptime(last_run_date, '%Y-%m-%d').date()
                if new_last_run_date != project_update.last_automation_run_date:
                    project_update.last_automation_run_date = new_last_run_date
                    modified_fields.append('last_automation_run_date')
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('weekly-meeting-detail', pk=meeting.id)
        elif project_update.last_automation_run_date is not None:
            # If the date field was cleared
            project_update.last_automation_run_date = None
            modified_fields.append('last_automation_run_date')

        # Handle boolean fields
        new_readiness = 'readiness_for_production' in request.POST
        if new_readiness != project_update.readiness_for_production:
            project_update.readiness_for_production = new_readiness
            modified_fields.append('readiness_for_production')

        # Handle foreign key fields
        team_lead_id = request.POST.get('team_lead')
        current_team_lead_id = project_update.team_lead.id if project_update.team_lead else None
        if team_lead_id != current_team_lead_id and team_lead_id:
            try:
                project_update.team_lead = Resource.objects.get(pk=team_lead_id)
                modified_fields.append('team_lead')
            except Resource.DoesNotExist:
                pass
        elif not team_lead_id and project_update.team_lead is not None:
            project_update.team_lead = None
            modified_fields.append('team_lead')

        sprint_cycle_id = request.POST.get('sprint_cycle')
        current_sprint_cycle_id = project_update.sprint_cycle.id if project_update.sprint_cycle else None
        if sprint_cycle_id != current_sprint_cycle_id and sprint_cycle_id:
            try:
                project_update.sprint_cycle = SprintCycle.objects.get(pk=sprint_cycle_id)
                modified_fields.append('sprint_cycle')
            except SprintCycle.DoesNotExist:
                pass
        elif not sprint_cycle_id and project_update.sprint_cycle is not None:
            project_update.sprint_cycle = None
            modified_fields.append('sprint_cycle')

        oat_release_cycle_id = request.POST.get('oat_release_cycle')
        current_oat_release_cycle_id = project_update.oat_release_cycle.id if project_update.oat_release_cycle else None
        if oat_release_cycle_id != current_oat_release_cycle_id and oat_release_cycle_id:
            try:
                project_update.oat_release_cycle = OATReleaseCycle.objects.get(pk=oat_release_cycle_id)
                modified_fields.append('oat_release_cycle')
            except OATReleaseCycle.DoesNotExist:
                pass
        elif not oat_release_cycle_id and project_update.oat_release_cycle is not None:
            project_update.oat_release_cycle = None
            modified_fields.append('oat_release_cycle')

        # Only save if fields were actually modified
        if modified_fields or created:
            project_update.save()

            # Store the modified fields in the session for use when ending the meeting
            request.session[f'modified_fields_{meeting.id}_{project.id}'] = modified_fields

            if modified_fields:
                messages.success(request, f'Project "{project.name}" has been updated. Modified fields: {", ".join(modified_fields)}')
            else:
                messages.success(request, f'Project "{project.name}" has been updated.')

    return redirect('weekly-meeting-detail', pk=meeting.id)


# Weekly Product Meeting views
class WeeklyProductMeetingListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = WeeklyProductMeeting
    template_name = 'dashboard/weekly_product_meeting_list.html'
    context_object_name = 'meetings'
    ordering = ['-meeting_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_meetings = [m for m in context['meetings'] if not m.is_completed]
        completed_meetings = [m for m in context['meetings'] if m.is_completed]
        context['has_active_meetings'] = len(active_meetings) > 0
        context['has_completed_meetings'] = len(completed_meetings) > 0
        return context

class WeeklyProductMeetingDetailView(DetailView):
    model = WeeklyProductMeeting
    context_object_name = 'meeting'

    def get_template_names(self):
        # Check if the request has a 'view' parameter set to 'table'
        if self.request.GET.get('view') == 'table':
            return ['dashboard/weekly_product_meeting_detail_table.html']
        return ['dashboard/weekly_product_meeting_detail.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_updates = WeeklyProductUpdate.objects.filter(meeting=self.object)
        context['product_updates'] = product_updates

        # Check if there's an active meeting session in the session
        context['meeting_active'] = self.request.session.get(f'product_meeting_active_{self.object.id}', False)

        return context

class WeeklyProductMeetingCreateView(CreateView):
    model = WeeklyProductMeeting
    template_name = 'dashboard/weekly_product_meeting_form.html'
    fields = ['meeting_date', 'title', 'notes', 'is_completed']
    success_url = reverse_lazy('weekly-product-meeting-list')

class WeeklyProductMeetingUpdateView(UpdateView):
    model = WeeklyProductMeeting
    template_name = 'dashboard/weekly_product_meeting_form.html'
    fields = ['meeting_date', 'title', 'notes', 'is_completed']
    success_url = reverse_lazy('weekly-product-meeting-list')

class WeeklyProductMeetingDeleteView(RecyclableDeleteView):
    model = WeeklyProductMeeting
    template_name = 'dashboard/weekly_product_meeting_confirm_delete.html'
    context_object_name = 'meeting'
    success_url = reverse_lazy('weekly-product-meeting-list')

class WeeklyProductUpdateDetailView(DetailView):
    model = WeeklyProductUpdate
    template_name = 'dashboard/weekly_product_update_detail.html'
    context_object_name = 'product_update'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # No need to add notes attribute for backward compatibility anymore
        # as the model now has a notes field
        return context

class WeeklyProductUpdateEditView(UpdateView):
    model = WeeklyProductUpdate
    template_name = 'dashboard/weekly_product_update_form.html'
    context_object_name = 'product_update'
    fields = ['product_notes', 'problems', 'expected_solution', 'solution_timeline']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meeting_active'] = self.request.session.get(f'product_meeting_active_{self.object.meeting.id}', False)
        return context

    def get_success_url(self):
        return reverse_lazy('weekly-product-meeting-detail', kwargs={'pk': self.object.meeting.id})


class LatestProductUpdatesView(ListView):
    """View for displaying the latest product updates across all meetings."""
    model = WeeklyProductUpdate
    template_name = 'dashboard/latest_product_updates.html'
    context_object_name = 'product_updates'

    def get_queryset(self):
        # Get the latest update for each project
        latest_updates = []
        projects = Project.objects.all()

        for project in projects:
            # Find the latest update for this project
            latest_update = WeeklyProductUpdate.objects.filter(
                project=project
            ).order_by('-meeting__meeting_date').first()

            if latest_update:
                # We no longer need to add notes attribute for backward compatibility
                # as the model now has a notes field
                # Add solution_timeline_display for UI
                latest_update.solution_timeline_display = latest_update.get_solution_timeline_display()
                latest_updates.append(latest_update)

        return latest_updates

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add current date to context for determining new updates
        context['now'] = timezone.now()
        return context

# Start and End Weekly Product Meeting views
def start_weekly_product_meeting(request, pk):
    meeting = get_object_or_404(WeeklyProductMeeting, pk=pk)

    if request.method == 'POST':
        # Check if this is the product selection form or the start meeting form
        if 'select_products' in request.POST:
            # Get all projects for selection
            projects = Project.objects.all()
            return render(request, 'dashboard/select_products_for_meeting.html', {
                'meeting': meeting,
                'projects': projects
            })
        elif 'start_meeting' in request.POST:
            # Set the meeting as active in the session
            request.session[f'product_meeting_active_{meeting.id}'] = True

            # Get selected projects
            selected_project_ids = request.POST.getlist('selected_projects')
            projects = Project.objects.filter(id__in=selected_project_ids)

            if not projects:
                messages.error(request, "Please select at least one product to start the meeting.")
                return redirect('weekly-product-meeting-detail', pk=meeting.id)

            # Store original project values in the session for comparison when the meeting ends
            original_values = {}

            # Create WeeklyProductUpdate objects for each selected project if they don't exist
            for project in projects:
                # Find the most recent product update for this project from previous meetings
                previous_update = WeeklyProductUpdate.objects.filter(
                    project=project
                ).exclude(
                    meeting=meeting
                ).order_by('-meeting__meeting_date').first()

                # Set default values based on previous meeting data if available
                default_latest_updates = previous_update.latest_project_updates if previous_update else ''
                default_product_notes = previous_update.product_notes if previous_update and hasattr(previous_update, 'product_notes') else ''
                default_problems = previous_update.problems if previous_update else ''
                default_expected_solution = previous_update.expected_solution if previous_update else ''
                default_solution_timeline = previous_update.solution_timeline if previous_update else 'medium'

                # Store original values for this project
                original_values[project.id] = {
                    'latest_project_updates': default_latest_updates,
                    'product_notes': default_product_notes,
                    'problems': default_problems,
                    'expected_solution': default_expected_solution,
                    'solution_timeline': default_solution_timeline,
                }

                # Get or create the product update
                product_update, created = WeeklyProductUpdate.objects.get_or_create(
                    meeting=meeting,
                    project=project,
                    defaults={
                        'latest_project_updates': default_latest_updates,
                        'product_notes': default_product_notes,
                        'problems': default_problems,
                        'expected_solution': default_expected_solution,
                        'solution_timeline': default_solution_timeline,
                    }
                )

                # If the product update already exists,
                # update it with data from previous meetings
                if not created and previous_update:
                    # Update with the latest data from previous meetings
                    product_update.latest_project_updates = default_latest_updates
                    product_update.product_notes = default_product_notes
                    product_update.problems = default_problems
                    product_update.expected_solution = default_expected_solution
                    product_update.solution_timeline = default_solution_timeline
                    product_update.save()

            # Store original values in the session
            request.session[f'product_original_values_{meeting.id}'] = original_values

            messages.success(request, f'Weekly product meeting "{meeting.title}" has been started with {len(projects)} selected products.')
        else:
            # Regular POST without specific action, just start the meeting selection process
            # Get all projects for selection
            projects = Project.objects.all()
            return render(request, 'dashboard/select_products_for_meeting.html', {
                'meeting': meeting,
                'projects': projects
            })

    return redirect('weekly-product-meeting-detail', pk=meeting.id)

def end_weekly_product_meeting(request, pk):
    meeting = get_object_or_404(WeeklyProductMeeting, pk=pk)

    if request.method == 'POST':
        # Get the original values from the session
        original_values = request.session.get(f'product_original_values_{meeting.id}', {})

        # Remove the meeting active flag and original values from the session
        if f'product_meeting_active_{meeting.id}' in request.session:
            del request.session[f'product_meeting_active_{meeting.id}']
        if f'product_original_values_{meeting.id}' in request.session:
            del request.session[f'product_original_values_{meeting.id}']

        # Mark the meeting as completed
        meeting.is_completed = True
        meeting.save()

        # Get all product updates for this meeting
        product_updates = WeeklyProductUpdate.objects.filter(meeting=meeting)

        # Generate meeting notes summarizing changes
        summary_notes = []

        for update in product_updates:
            project = update.project
            project_id = str(project.id)

            # Skip if there are no updates, product notes, problems, or expected solutions
            if not update.latest_project_updates and not update.product_notes and not update.problems and not update.expected_solution:
                continue

            # Check if there were actual changes to this product's data
            has_changes = False
            if project_id in original_values:
                orig = original_values[project_id]
                if (update.latest_project_updates != orig.get('latest_project_updates', '') or
                    update.product_notes != orig.get('product_notes', '') or
                    update.problems != orig.get('problems', '') or
                    update.expected_solution != orig.get('expected_solution', '') or
                    update.solution_timeline != orig.get('solution_timeline', 'medium')):
                    has_changes = True
            else:
                # If we don't have original values, assume there were changes
                has_changes = True

            # Skip this product if no changes were made
            if not has_changes:
                continue

            # Add this product's updates to the summary
            product_summary = [f"Product: {project.name}"]

            if update.latest_project_updates:
                product_summary.append(f"Latest Project Updates: {update.latest_project_updates}")

            if update.product_notes:
                product_summary.append(f"Product Notes: {update.product_notes}")

            if update.problems:
                product_summary.append(f"Problems: {update.problems}")

            if update.expected_solution:
                product_summary.append(f"Expected Solution: {update.expected_solution}")

            product_summary.append(f"Solution Timeline: {update.get_solution_timeline_display()}")

            if len(product_summary) > 1:  # Only add if there's more than just the product name
                summary_notes.append("\n".join(product_summary))

        # Update meeting notes with the summary
        if summary_notes:
            meeting_summary = "Meeting Summary:\n\n" + "\n\n".join(summary_notes)
            if meeting.notes:
                meeting.notes += f"\n\n{meeting_summary}"
            else:
                meeting.notes = meeting_summary
            meeting.save()

        # Update project fields with values from product updates
        for update in product_updates:
            project = update.project

            # Get the modified fields for this product update from the session
            modified_fields = request.session.get(f'product_modified_fields_{meeting.id}_{project.id}', [])

            # We no longer append manual updates to the project description
            # Instead, they are displayed in a separate "Manual Updates" section on the product detail page

            # The following fields are now stored only in the WeeklyProductUpdate model:
            # - latest_project_updates
            # - problems
            # - expected_solution
            # - solution_timeline

            # No need to modify the project.description field

            # Save the project with the updated fields
            project.save()

            # Remove the modified fields from the session
            if f'product_modified_fields_{meeting.id}_{project.id}' in request.session:
                del request.session[f'product_modified_fields_{meeting.id}_{project.id}']

        messages.success(request, f'Weekly product meeting "{meeting.title}" has been completed and summary notes have been generated.')

    return redirect('weekly-product-meeting-detail', pk=meeting.id)

def update_product_in_meeting(request, meeting_id, project_id):
    meeting = get_object_or_404(WeeklyProductMeeting, pk=meeting_id)
    project = get_object_or_404(Project, pk=project_id)

    # Check if the meeting is active
    if not request.session.get(f'product_meeting_active_{meeting.id}', False):
        messages.error(request, "This meeting is not currently active.")
        return redirect('weekly-product-meeting-detail', pk=meeting.id)

    # Get the product update or create it if it doesn't exist
    product_update, created = WeeklyProductUpdate.objects.get_or_create(
        meeting=meeting,
        project=project
    )

    # Find the most recent product update for this project from previous meetings
    previous_update = WeeklyProductUpdate.objects.filter(
        project=project,
        meeting__id__lt=meeting.id  # Only from previous meetings
    ).order_by('-meeting__meeting_date').first()

    # If this is a newly created product update and there's a previous update,
    # use the previous data to populate it
    if created and previous_update:
        product_update.latest_project_updates = previous_update.latest_project_updates or previous_update.problems  # Use legacy field if needed
        product_update.product_notes = previous_update.product_notes if hasattr(previous_update, 'product_notes') else ''
        product_update.problems = previous_update.problems
        product_update.expected_solution = previous_update.expected_solution
        product_update.solution_timeline = previous_update.solution_timeline
        product_update.save()

        # Copy any existing problems from the previous update
        # Only copy if this is a newly created product update to avoid duplicates
        if created:
            for problem in previous_update.product_problems.all():
                ProductProblem.objects.create(
                    product_update=product_update,
                    problem_description=problem.problem_description,
                    expected_solutions=problem.expected_solutions,
                    solution_timeline=problem.solution_timeline
                )

    if request.method == 'POST':
        # Track which fields have been modified
        modified_fields = []

        # Update latest project updates field
        new_latest_updates = request.POST.get('latest_project_updates', '')
        if new_latest_updates != product_update.latest_project_updates:
            product_update.latest_project_updates = new_latest_updates
            modified_fields.append('latest_project_updates')

        # Handle product_notes field
        if 'product_notes' in request.POST:
            new_product_notes = request.POST.get('product_notes', '')
            if new_product_notes != product_update.product_notes:
                product_update.product_notes = new_product_notes
                modified_fields.append('product_notes')

        # For backward compatibility, also update legacy fields
        if 'problems' in request.POST:
            new_problems = request.POST.get('problems', '')
            if new_problems != product_update.problems:
                product_update.problems = new_problems
                modified_fields.append('problems')

        if 'expected_solution' in request.POST:
            new_expected_solution = request.POST.get('expected_solution', '')
            if new_expected_solution != product_update.expected_solution:
                product_update.expected_solution = new_expected_solution
                modified_fields.append('expected_solution')

        if 'solution_timeline' in request.POST:
            new_solution_timeline = request.POST.get('solution_timeline', 'medium')
            if new_solution_timeline != product_update.solution_timeline:
                product_update.solution_timeline = new_solution_timeline
                modified_fields.append('solution_timeline')

        # Save the product update first to ensure it exists for problem relationships
        if modified_fields or created:
            product_update.save()

        # Handle multiple problems
        # First, check if we're adding a new problem
        if 'add_problem' in request.POST:
            problem_description = request.POST.get('new_problem_description', '')
            expected_solutions = request.POST.get('new_expected_solutions', '')
            solution_timeline = request.POST.get('new_solution_timeline', 'medium')

            if problem_description:
                ProductProblem.objects.create(
                    product_update=product_update,
                    problem_description=problem_description,
                    expected_solutions=expected_solutions,
                    solution_timeline=solution_timeline
                )
                modified_fields.append('added_problem')

        # Then, handle updates to existing problems
        for key, value in request.POST.items():
            # Check for problem updates in format problem_<id>_<field>
            if key.startswith('problem_') and '_' in key:
                parts = key.split('_')
                if len(parts) >= 3:
                    problem_id = parts[1]
                    field_name = '_'.join(parts[2:])  # Join back in case field name contains underscores

                    try:
                        problem = ProductProblem.objects.get(id=problem_id, product_update=product_update)

                        if field_name == 'description' and value != problem.problem_description:
                            problem.problem_description = value
                            problem.save()
                            modified_fields.append(f'problem_{problem_id}_description')

                        elif field_name == 'expected_solutions' and value != problem.expected_solutions:
                            problem.expected_solutions = value
                            problem.save()
                            modified_fields.append(f'problem_{problem_id}_expected_solutions')

                        elif field_name == 'solution_timeline' and value != problem.solution_timeline:
                            problem.solution_timeline = value
                            problem.save()
                            modified_fields.append(f'problem_{problem_id}_solution_timeline')

                        elif field_name == 'delete' and value == 'true':
                            problem.delete()
                            modified_fields.append(f'deleted_problem_{problem_id}')

                    except ProductProblem.DoesNotExist:
                        pass  # Ignore if problem doesn't exist

        if modified_fields:
            # Store the modified fields in the session for use in end_weekly_product_meeting
            request.session[f'product_modified_fields_{meeting.id}_{project.id}'] = modified_fields
            messages.success(request, f'Product "{project.name}" has been updated. Modified fields: {", ".join(modified_fields)}')
        else:
            messages.success(request, f'Product "{project.name}" has been updated.')

    return redirect('weekly-product-meeting-detail', pk=meeting.id)


# Quarter views
class QuarterListView(PaginationMixin, ListView):
    model = Quarter
    template_name = 'dashboard/quarter_list.html'
    context_object_name = 'quarters'
    ordering = ['-year', 'quarter_number']

class QuarterDetailView(DetailView):
    model = Quarter
    template_name = 'dashboard/quarter_detail.html'
    context_object_name = 'quarter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['targets'] = QuarterTarget.objects.filter(quarter=self.object)
        return context

class QuarterCreateView(CreateView):
    model = Quarter
    template_name = 'dashboard/quarter_form.html'
    fields = ['year', 'quarter_number', 'name']
    success_url = reverse_lazy('quarter-list')

class QuarterUpdateView(UpdateView):
    model = Quarter
    template_name = 'dashboard/quarter_form.html'
    fields = ['year', 'quarter_number', 'name']
    success_url = reverse_lazy('quarter-list')

class QuarterDeleteView(RecyclableDeleteView):
    model = Quarter
    template_name = 'dashboard/quarter_confirm_delete.html'
    success_url = reverse_lazy('quarter-list')

# Quarter Target views
class QuarterTargetListView(PaginationMixin, ListView):
    model = QuarterTarget
    template_name = 'dashboard/quarter_target_list.html'
    context_object_name = 'targets'

    def get_queryset(self):
        queryset = super().get_queryset()
        quarter_id = self.kwargs.get('quarter_id')
        if quarter_id:
            queryset = queryset.filter(quarter_id=quarter_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarter_id = self.kwargs.get('quarter_id')
        if quarter_id:
            context['quarter'] = get_object_or_404(Quarter, pk=quarter_id)
        return context

class QuarterTargetDetailView(DetailView):
    model = QuarterTarget
    template_name = 'dashboard/quarter_target_detail.html'
    context_object_name = 'target'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resources'] = QuarterTargetResource.objects.filter(quarter_target=self.object)
        return context

class QuarterTargetCreateView(CreateView):
    model = QuarterTarget
    template_name = 'dashboard/quarter_target_form.html'
    fields = ['project', 'target_description', 'target_value']

    def form_valid(self, form):
        form.instance.quarter_id = self.kwargs.get('quarter_id')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quarter'] = get_object_or_404(Quarter, pk=self.kwargs.get('quarter_id'))
        return context

    def get_success_url(self):
        return reverse_lazy('quarter-detail', kwargs={'pk': self.kwargs.get('quarter_id')})

class QuarterTargetUpdateView(UpdateView):
    model = QuarterTarget
    template_name = 'dashboard/quarter_target_form.html'
    fields = ['project', 'target_description', 'target_value']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quarter'] = self.object.quarter
        return context

    def get_success_url(self):
        return reverse_lazy('quarter-detail', kwargs={'pk': self.object.quarter.id})

class QuarterTargetDeleteView(RecyclableDeleteView):
    model = QuarterTarget
    template_name = 'dashboard/quarter_target_confirm_delete.html'
    context_object_name = 'target'

    def get_success_url(self):
        return reverse_lazy('quarter-detail', kwargs={'pk': self.object.quarter.id})

# Quarter Target Resource views
def assign_resource_to_target(request, target_id):
    target = get_object_or_404(QuarterTarget, id=target_id)

    if request.method == 'POST':
        resource_id = request.POST.get('resource')
        allocation = request.POST.get('allocation_percentage', 0)
        notes = request.POST.get('notes', '')

        if resource_id:
            resource = get_object_or_404(Resource, id=resource_id)

            # Check if assignment already exists
            target_resource, created = QuarterTargetResource.objects.get_or_create(
                quarter_target=target,
                resource=resource,
                defaults={
                    'allocation_percentage': allocation,
                    'notes': notes
                }
            )

            if not created:
                target_resource.allocation_percentage = allocation
                target_resource.notes = notes
                target_resource.save()
                messages.success(request, f'Updated resource allocation for {resource.name}')
            else:
                messages.success(request, f'Assigned {resource.name} to target')

            return redirect('quarter-target-detail', pk=target.id)

    # Get resources not already assigned to this target
    assigned_resources = target.resources.all()
    available_resources = Resource.objects.exclude(id__in=[r.id for r in assigned_resources])

    context = {
        'target': target,
        'available_resources': available_resources
    }

    return render(request, 'dashboard/assign_resource_to_target.html', context)

def remove_resource_from_target(request, target_id, resource_id):
    target_resource = get_object_or_404(QuarterTargetResource, quarter_target_id=target_id, resource_id=resource_id)
    resource_name = target_resource.resource.name

    target_resource.delete()
    messages.success(request, f'Removed {resource_name} from target')

    return redirect('quarter-target-detail', pk=target_id)

# Quarter Timeline and Completion views
class QuarterTimelineView(TemplateView):
    template_name = 'dashboard/quarter_timeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarters = Quarter.objects.all().order_by('-year', 'quarter_number')
        context['quarters'] = quarters
        context['timeline_data'] = json.dumps([q.get_timeline_data() for q in quarters], cls=DecimalEncoder)
        return context

class QuarterTargetDashboardView(TemplateView):
    template_name = 'dashboard/quarter_target_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all quarters
        quarters = Quarter.objects.all().order_by('-year', 'quarter_number')
        context['quarters'] = quarters

        # Count completed quarters
        completed_quarters = Quarter.objects.filter(completed=True).count()
        context['completed_quarters'] = completed_quarters

        # Get statistics for each quarter
        quarter_stats = []
        for quarter in quarters:
            stats = quarter.get_statistics()
            quarter_stats.append({
                'id': quarter.id,
                'name': str(quarter),
                'year': quarter.year,
                'quarter_number': quarter.quarter_number,
                'total_targets': stats['total_targets'],
                'completed_targets': stats['completed_targets'],
                'completion_percentage': stats['completion_percentage'],
                'avg_achievement_percentage': stats['avg_achievement_percentage'],
                'completed': quarter.completed
            })
        context['quarter_stats'] = quarter_stats

        # Get all quarter targets
        targets = QuarterTarget.objects.all().select_related('quarter', 'project')
        context['targets'] = targets

        # Get projects with quarter targets
        projects_with_targets = Project.objects.filter(quarterly_targets__isnull=False).distinct()
        context['projects_with_targets'] = projects_with_targets

        # Get target achievement data by project
        project_achievement_data = []
        for project in projects_with_targets:
            project_targets = targets.filter(project=project)
            achievement_percentages = [
                target.achievement_percentage 
                for target in project_targets 
                if target.achievement_percentage is not None
            ]
            avg_achievement = sum(achievement_percentages) / len(achievement_percentages) if achievement_percentages else 0
            project_achievement_data.append({
                'project_name': project.name,
                'avg_achievement': avg_achievement,
                'target_count': project_targets.count()
            })
        context['project_achievement_data'] = project_achievement_data


        return context

class QuarterCompletionForm(forms.ModelForm):
    completion_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        model = Quarter
        fields = ['completion_date', 'completion_notes', 'completed']
        widgets = {
            'completion_notes': forms.Textarea(attrs={'rows': 4}),
        }

class QuarterTargetAchievementForm(forms.ModelForm):
    class Meta:
        model = QuarterTarget
        fields = ['achieved_value', 'achievement_notes']
        widgets = {
            'achievement_notes': forms.Textarea(attrs={'rows': 3}),
        }

def complete_quarter(request, pk):
    quarter = get_object_or_404(Quarter, pk=pk)
    targets = quarter.targets.all()

    # Create a formset for the targets
    TargetFormSet = forms.modelformset_factory(
        QuarterTarget,
        form=QuarterTargetAchievementForm,
        extra=0
    )

    if request.method == 'POST':
        quarter_form = QuarterCompletionForm(request.POST, instance=quarter)
        target_formset = TargetFormSet(request.POST, queryset=targets)

        if quarter_form.is_valid() and target_formset.is_valid():
            # Save the quarter form
            quarter = quarter_form.save(commit=False)
            quarter.completed = True
            quarter.save()

            # Save the target formset
            target_formset.save()

            messages.success(request, f'Quarter {quarter} has been marked as completed.')
            return redirect('quarter-summary', pk=quarter.pk)
    else:
        quarter_form = QuarterCompletionForm(instance=quarter)
        target_formset = TargetFormSet(queryset=targets)

    context = {
        'quarter': quarter,
        'quarter_form': quarter_form,
        'target_formset': target_formset,
    }

    return render(request, 'dashboard/quarter_complete.html', context)

def quarter_summary(request, pk):
    quarter = get_object_or_404(Quarter, pk=pk)

    if not quarter.completed:
        messages.warning(request, f'Quarter {quarter} has not been completed yet.')
        return redirect('quarter-detail', pk=quarter.pk)

    context = {
        'quarter': quarter,
        'targets': quarter.targets.all(),
        'statistics': quarter.get_statistics(),
    }

    return render(request, 'dashboard/quarter_summary.html', context)


# Resource Planning Views
class ResourcePlanningView(TemplateView):
    template_name = 'dashboard/resource_planning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all resources
        resources = Resource.objects.all()

        # Get all project assignments
        project_resources = ProjectResource.objects.select_related('project', 'resource').all()

        # Get search parameter
        search_query = self.request.GET.get('search', '')

        # Get current date for filtering leaves
        current_date = timezone.now().date()

        # Get leaves based on search parameter
        if search_query:
            # If searching, include all leaves
            leaves = ResourceLeave.objects.select_related('resource').all()
        else:
            # By default, only show current and upcoming leaves
            leaves = ResourceLeave.objects.select_related('resource').filter(
                Q(start_date__gte=current_date) | Q(end_date__gte=current_date)
            )

        # Prepare data for calendar view
        calendar_data = []

        # Add project assignments to calendar data
        for pr in project_resources:
            end_date = pr.end_date if pr.end_date else (pr.start_date + timedelta(days=30))  # Default to 30 days if no end date
            calendar_data.append({
                'id': f'project_{pr.id}',
                'title': f'{pr.resource.name} - {pr.project.name}',
                'start': pr.start_date.isoformat(),
                'end': end_date.isoformat(),
                'color': '#3788d8',  # Blue for project assignments
                'extendedProps': {
                    'type': 'project',
                    'resource_id': pr.resource.id,
                    'project_id': pr.project.id,
                    'utilization': float(pr.utilization_percentage),
                    'hours': float(pr.hours_allocated),
                    'notes': pr.notes
                }
            })

        # Add leaves to calendar data
        current_date = timezone.now().date()
        for leave in leaves:
            # Check if this is a past leave
            is_past_leave = leave.end_date < current_date

            # Add "Past Leave" tag to title if it's a past leave
            title = f'{leave.resource.name} - {leave.get_leave_type_display()}'
            if is_past_leave and self.request.GET.get('search', ''):
                title += ' (Past Leave)'

            calendar_data.append({
                'id': f'leave_{leave.id}',
                'title': title,
                'start': leave.start_date.isoformat(),
                'end': leave.end_date.isoformat(),
                'color': '#e74c3c',  # Red for leaves
                'extendedProps': {
                    'type': 'leave',
                    'resource_id': leave.resource.id,
                    'leave_type': leave.leave_type,
                    'description': leave.description,
                    'is_past_leave': is_past_leave
                }
            })

        context['resources'] = resources
        context['projects'] = Project.objects.all()
        context['project_resources'] = project_resources
        context['leaves'] = leaves
        context['calendar_data'] = json.dumps(calendar_data)
        return context


class ResourceLeaveCreateView(CreateView):
    model = ResourceLeave
    template_name = 'dashboard/resource_leave_form.html'
    fields = ['resource', 'start_date', 'end_date', 'leave_type', 'description']
    success_url = reverse_lazy('resource-planning')

    def form_valid(self, form):
        messages.success(self.request, f"Leave for {form.instance.resource.name} has been created successfully.")
        return super().form_valid(form)


class ResourceLeaveUpdateView(UpdateView):
    model = ResourceLeave
    template_name = 'dashboard/resource_leave_form.html'
    fields = ['resource', 'start_date', 'end_date', 'leave_type', 'description']
    success_url = reverse_lazy('resource-planning')

    def form_valid(self, form):
        messages.success(self.request, f"Leave for {form.instance.resource.name} has been updated successfully.")
        return super().form_valid(form)


class ResourceLeaveDeleteView(RecyclableDeleteView):
    model = ResourceLeave
    template_name = 'dashboard/resource_leave_confirm_delete.html'
    success_url = reverse_lazy('resource-planning')

    def delete(self, request, *args, **kwargs):
        leave = self.get_object()
        messages.success(request, f"Leave for {leave.resource.name} has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


def assign_resource_with_dates(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        resource_id = request.POST.get('resource')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        hours = request.POST.get('hours_allocated')
        utilization = request.POST.get('utilization_percentage', 0)
        notes = request.POST.get('notes', '')

        if resource_id and start_date:
            resource = get_object_or_404(Resource, id=resource_id)

            # Check if assignment already exists
            project_resource, created = ProjectResource.objects.get_or_create(
                project=project,
                resource=resource,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date if end_date else None,
                    'hours_allocated': hours,
                    'utilization_percentage': utilization,
                    'notes': notes,
                    'assigned_date': timezone.now()
                }
            )

            if not created:
                project_resource.start_date = start_date
                project_resource.end_date = end_date if end_date else None
                project_resource.hours_allocated = hours
                project_resource.utilization_percentage = utilization
                project_resource.notes = notes
                project_resource.save()
                messages.success(request, f'Updated assignment for {resource.name}')
            else:
                messages.success(request, f'Assigned {resource.name} to {project.name}')

            return redirect('resource-planning')

    # Get resources not already assigned to this project
    assigned_resources = project.resources.all()
    available_resources = Resource.objects.exclude(id__in=[r.id for r in assigned_resources])

    context = {
        'project': project,
        'available_resources': available_resources
    }

    return render(request, 'dashboard/assign_resource_with_dates.html', context)


def edit_resource_allocation(request, project_id, resource_id):
    project = get_object_or_404(Project, id=project_id)
    resource = get_object_or_404(Resource, id=resource_id)
    project_resource = get_object_or_404(ProjectResource, project=project, resource=resource)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        hours = request.POST.get('hours_allocated')
        utilization = request.POST.get('utilization_percentage', 0)
        notes = request.POST.get('notes', '')

        if start_date:
            project_resource.start_date = start_date
            project_resource.end_date = end_date if end_date else None
            project_resource.hours_allocated = hours
            project_resource.utilization_percentage = utilization
            project_resource.notes = notes
            project_resource.save()
            messages.success(request, f'Updated assignment for {resource.name}')
            return redirect('resource-planning')

    # Include the current resource in the form
    all_resources = Resource.objects.all()

    context = {
        'project': project,
        'resource': resource,
        'project_resource': project_resource,
        'all_resources': all_resources,
        'editing': True
    }

    return render(request, 'dashboard/edit_resource_allocation.html', context)


def remove_resource_from_planning(request, project_id, resource_id):
    project_resource = get_object_or_404(ProjectResource, project_id=project_id, resource_id=resource_id)
    resource_name = project_resource.resource.name
    project_name = project_resource.project.name

    project_resource.delete()
    messages.success(request, f'Removed {resource_name} from {project_name}')

    return redirect('resource-planning')


# Rock Management Views
class RockListView(PaginationMixin, ListView):
    model = Rock
    template_name = 'dashboard/rock_list.html'
    context_object_name = 'rocks'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply filters if provided
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        assignee_filter = self.request.GET.get('assignee')
        project_filter = self.request.GET.get('project')
        quarter_target_filter = self.request.GET.get('quarter_target')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if assignee_filter:
            queryset = queryset.filter(assignee_id=assignee_filter)
        if project_filter:
            queryset = queryset.filter(project_id=project_filter)
        if quarter_target_filter:
            queryset = queryset.filter(quarter_target_id=quarter_target_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter options to context
        context['resources'] = Resource.objects.all()
        context['projects'] = Project.objects.all()
        context['quarter_targets'] = QuarterTarget.objects.all()

        # Add current filter values to context
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_assignee'] = self.request.GET.get('assignee', '')
        context['current_project'] = self.request.GET.get('project', '')
        context['current_quarter_target'] = self.request.GET.get('quarter_target', '')

        # Add filter applied flag
        context['filters_applied'] = any([
            context['current_status'],
            context['current_priority'],
            context['current_assignee'],
            context['current_project'],
            context['current_quarter_target']
        ])

        return context


class RockDetailView(DetailView):
    model = Rock
    template_name = 'dashboard/rock_detail.html'
    context_object_name = 'rock'


class RockCreateView(CreateView):
    model = Rock
    template_name = 'dashboard/rock_form.html'
    fields = ['title', 'description', 'priority', 'assignee', 'project', 'quarter_target', 'due_date']

    def form_valid(self, form):
        messages.success(self.request, f"Rock '{form.instance.title}' has been created successfully.")
        return super().form_valid(form)


class RockUpdateView(UpdateView):
    model = Rock
    template_name = 'dashboard/rock_form.html'
    fields = ['title', 'description', 'priority', 'status', 'assignee', 'project', 'quarter_target', 'due_date']

    def form_valid(self, form):
        messages.success(self.request, f"Rock '{form.instance.title}' has been updated successfully.")
        return super().form_valid(form)


class RockDeleteView(RecyclableDeleteView):
    model = Rock
    template_name = 'dashboard/rock_confirm_delete.html'
    success_url = reverse_lazy('rock-list')

    def delete(self, request, *args, **kwargs):
        rock = self.get_object()
        messages.success(request, f"Rock '{rock.title}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


def start_rock(request, pk):
    """Mark a rock as in progress."""
    rock = get_object_or_404(Rock, pk=pk)

    if rock.status == 'not_started':
        rock.start_rock()
        messages.success(request, f"Rock '{rock.title}' has been started.")
    else:
        messages.warning(request, f"Rock '{rock.title}' is already in progress or completed.")

    return redirect('rock-detail', pk=rock.pk)


def complete_rock(request, pk):
    """Mark a rock as completed."""
    rock = get_object_or_404(Rock, pk=pk)

    if rock.status != 'completed':
        rock.complete_rock()
        messages.success(request, f"Rock '{rock.title}' has been completed.")
    else:
        messages.warning(request, f"Rock '{rock.title}' is already completed.")

    return redirect('rock-detail', pk=rock.pk)


class RockDashboardView(TemplateView):
    template_name = 'dashboard/rock_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all rocks
        rocks = Rock.objects.all()

        # Rocks by status
        rocks_by_status = rocks.values('status').annotate(count=Count('id'))

        # Rocks by priority
        rocks_by_priority = rocks.values('priority').annotate(count=Count('id'))

        # Rocks by assignee
        rocks_by_assignee = rocks.values('assignee__name').annotate(count=Count('id'))

        # Rocks by project
        rocks_by_project = rocks.values('project__name').annotate(count=Count('id'))

        # Overdue rocks
        overdue_rocks = [rock for rock in rocks if rock.is_overdue]

        # Recently completed rocks
        recently_completed = rocks.filter(
            status='completed',
            completed_at__isnull=False
        ).order_by('-completed_at')[:5]

        # Upcoming due rocks
        upcoming_due = rocks.filter(
            status__in=['not_started', 'in_progress'],
            due_date__isnull=False
        ).order_by('due_date')[:5]

        context.update({
            'rocks_count': rocks.count(),
            'completed_count': rocks.filter(status='completed').count(),
            'in_progress_count': rocks.filter(status='in_progress').count(),
            'not_started_count': rocks.filter(status='not_started').count(),
            'rocks_by_status': rocks_by_status,
            'rocks_by_priority': rocks_by_priority,
            'rocks_by_assignee': rocks_by_assignee,
            'rocks_by_project': rocks_by_project,
            'overdue_rocks': overdue_rocks,
            'recently_completed': recently_completed,
            'upcoming_due': upcoming_due,
        })

        return context


def assign_rock(request, resource_id):
    """Assign a rock to a resource."""
    resource = get_object_or_404(Resource, id=resource_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        project_id = request.POST.get('project')
        quarter_target_id = request.POST.get('quarter_target')
        due_date = request.POST.get('due_date')

        if title:
            rock = Rock(
                title=title,
                description=description,
                priority=priority,
                assignee=resource
            )

            if project_id:
                rock.project = get_object_or_404(Project, id=project_id)

            if quarter_target_id:
                rock.quarter_target = get_object_or_404(QuarterTarget, id=quarter_target_id)

            if due_date:
                rock.due_date = due_date

            rock.save()
            messages.success(request, f"Rock '{rock.title}' has been assigned to {resource.name}.")
            return redirect('rock-detail', pk=rock.pk)

    context = {
        'resource': resource,
        'projects': Project.objects.all(),
        'quarter_targets': QuarterTarget.objects.all()
    }

    return render(request, 'dashboard/assign_rock.html', context)


# Strategic Roadmap Views
class RoadmapItemListView(PaginationMixin, ListView):
    model = RoadmapItem
    template_name = 'dashboard/roadmap_item_list.html'
    context_object_name = 'roadmap_items'

    def get_queryset(self):
        queryset = RoadmapItem.objects.all().select_related('owner', 'project', 'quarter_target', 'quarter')

        # Filter by owner
        owner_id = self.request.GET.get('owner')
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)

        # Filter by project
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by quarter
        quarter_id = self.request.GET.get('quarter')
        if quarter_id:
            queryset = queryset.filter(quarter_id=quarter_id)

        # Sort by field
        sort_by = self.request.GET.get('sort_by', 'start_date')
        sort_order = self.request.GET.get('sort_order', 'asc')

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owners'] = Resource.objects.all()
        context['projects'] = Project.objects.all()
        context['quarters'] = Quarter.objects.all().order_by('-year', 'quarter_number')
        context['statuses'] = dict(RoadmapItem.STATUS_CHOICES)
        context['priorities'] = dict(RoadmapItem.PRIORITY_CHOICES)

        # Add filter parameters to context for form persistence
        context['selected_owner'] = self.request.GET.get('owner', '')
        context['selected_project'] = self.request.GET.get('project', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_quarter'] = self.request.GET.get('quarter', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'start_date')
        context['sort_order'] = self.request.GET.get('sort_order', 'asc')

        return context


class RoadmapItemDetailView(DetailView):
    model = RoadmapItem
    template_name = 'dashboard/roadmap_item_detail.html'
    context_object_name = 'roadmap_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RoadmapItemCreateView(CreateView):
    model = RoadmapItem
    template_name = 'dashboard/roadmap_item_form.html'
    fields = ['title', 'description', 'owner', 'project', 'quarter_target', 'quarter', 
              'start_date', 'end_date', 'status', 'priority', 'progress']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['progress'].widget = forms.NumberInput(attrs={'min': '0', 'max': '100'})
        return form

    def get_initial(self):
        initial = super().get_initial()
        quarter_id = self.kwargs.get('quarter_id')
        if quarter_id:
            initial['quarter'] = quarter_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarter_id = self.kwargs.get('quarter_id')
        if quarter_id:
            context['quarter'] = get_object_or_404(Quarter, pk=quarter_id)
        return context

    def get_success_url(self):
        # Roadmap timeline temporarily hidden, redirect to dashboard instead
        return reverse_lazy('dashboard')


class RoadmapItemUpdateView(UpdateView):
    model = RoadmapItem
    template_name = 'dashboard/roadmap_item_form.html'
    fields = ['title', 'description', 'owner', 'project', 'quarter_target', 'quarter', 
              'start_date', 'end_date', 'status', 'priority', 'progress']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['progress'].widget = forms.NumberInput(attrs={'min': '0', 'max': '100'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        # Roadmap item detail temporarily hidden, redirect to dashboard instead
        return reverse_lazy('dashboard')


class RoadmapItemDeleteView(RecyclableDeleteView):
    model = RoadmapItem
    template_name = 'dashboard/roadmap_item_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, f"Roadmap item '{self.object.title}' has been deleted.")
        # Roadmap item list temporarily hidden, redirect to dashboard instead
        return reverse_lazy('dashboard')


class RoadmapTimelineView(TemplateView):
    template_name = 'dashboard/roadmap_timeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the current quarter or use the one specified in the URL
        quarter_id = self.kwargs.get('quarter_id')
        if quarter_id:
            quarter = get_object_or_404(Quarter, pk=quarter_id)
        else:
            # Get the current quarter based on the current date
            current_date = timezone.now().date()
            quarters = Quarter.objects.filter(
                start_date__lte=current_date,
                end_date__gte=current_date
            ).order_by('-year', 'quarter_number')

            if quarters.exists():
                quarter = quarters.first()
            else:
                # If no current quarter, get the most recent one
                quarter = Quarter.objects.all().order_by('-year', '-quarter_number').first()

        # Get all roadmap items for the quarter
        roadmap_items = RoadmapItem.objects.filter(quarter=quarter).select_related('owner', 'project', 'quarter_target')

        # Filter by owner
        owner_id = self.request.GET.get('owner')
        if owner_id:
            roadmap_items = roadmap_items.filter(owner_id=owner_id)

        # Filter by project
        project_id = self.request.GET.get('project')
        if project_id:
            roadmap_items = roadmap_items.filter(project_id=project_id)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            roadmap_items = roadmap_items.filter(status=status)

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            roadmap_items = roadmap_items.filter(priority=priority)

        # Prepare timeline data
        timeline_data = [item.get_timeline_data() for item in roadmap_items]

        context['quarter'] = quarter
        context['quarters'] = Quarter.objects.all().order_by('-year', 'quarter_number')
        context['roadmap_items'] = roadmap_items
        context['timeline_data'] = json.dumps(timeline_data, cls=DecimalEncoder)
        context['owners'] = Resource.objects.all()
        context['projects'] = Project.objects.all()
        context['statuses'] = dict(RoadmapItem.STATUS_CHOICES)
        context['priorities'] = dict(RoadmapItem.PRIORITY_CHOICES)

        # Add filter parameters to context for form persistence
        context['selected_owner'] = self.request.GET.get('owner', '')
        context['selected_project'] = self.request.GET.get('project', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')

        return context


def start_roadmap_item(request, pk):
    """Mark a roadmap item as in progress."""
    roadmap_item = get_object_or_404(RoadmapItem, pk=pk)

    if roadmap_item.status == 'not_started':
        roadmap_item.start_item()
        messages.success(request, f"Roadmap item '{roadmap_item.title}' has been started.")
    else:
        messages.warning(request, f"Roadmap item '{roadmap_item.title}' is already in progress or completed.")

    # Roadmap item detail temporarily hidden, redirect to dashboard instead
    return redirect('dashboard')


def complete_roadmap_item(request, pk):
    """Mark a roadmap item as completed."""
    roadmap_item = get_object_or_404(RoadmapItem, pk=pk)

    if roadmap_item.status != 'completed':
        roadmap_item.complete_item()
        messages.success(request, f"Roadmap item '{roadmap_item.title}' has been completed.")
    else:
        messages.warning(request, f"Roadmap item '{roadmap_item.title}' is already completed.")

    # Roadmap item detail temporarily hidden, redirect to dashboard instead
    return redirect('dashboard')


def update_roadmap_item_progress(request, pk):
    """Update the progress of a roadmap item."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    roadmap_item = get_object_or_404(RoadmapItem, pk=pk)

    try:
        progress = int(request.POST.get('progress', 0))
        roadmap_item.update_progress(progress)

        return JsonResponse({
            'success': True,
            'message': f"Progress for '{roadmap_item.title}' updated to {roadmap_item.progress}%",
            'progress': roadmap_item.progress,
            'status': roadmap_item.status
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def update_roadmap_item_dates(request, pk):
    """Update the start and end dates of a roadmap item via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    roadmap_item = get_object_or_404(RoadmapItem, pk=pk)

    try:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not start_date or not end_date:
            return JsonResponse({'error': 'Start date and end date are required'}, status=400)

        # Update the roadmap item
        roadmap_item.start_date = start_date
        roadmap_item.end_date = end_date
        roadmap_item.save()

        return JsonResponse({
            'success': True,
            'message': f"Roadmap item '{roadmap_item.title}' dates updated successfully",
            'start_date': roadmap_item.start_date.isoformat(),
            'end_date': roadmap_item.end_date.isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Product Documentation views
class ProductDocumentationCreateView(CreateView):
    model = ProductDocumentation
    fields = ['title', 'link']
    template_name = 'dashboard/product_documentation_form.html'

    def form_valid(self, form):
        form.instance.project_id = self.kwargs.get('product_id')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(Project, pk=self.kwargs.get('product_id'))
        return context


class ProductDocumentationUpdateView(UpdateView):
    model = ProductDocumentation
    fields = ['title', 'link']
    template_name = 'dashboard/product_documentation_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object.project
        return context


class ProductDocumentationDeleteView(RecyclableDeleteView):
    model = ProductDocumentation
    template_name = 'dashboard/product_documentation_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('product-detail', kwargs={'pk': self.object.project.pk})


# Production Bugs Management Views
class ProductionBugListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = ProductionBug
    template_name = 'dashboard/production_bug_list.html'
    context_object_name = 'bugs'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('project')

        # Filter by project if specified
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Filter by status if specified
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by severity if specified
        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        # Filter by test case added if specified
        test_case = self.request.GET.get('test_case')
        if test_case:
            queryset = queryset.filter(test_case_added=test_case)

        # Search by title or details if specified
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(details__icontains=search_query) |
                Q(project__name__icontains=search_query)
            )

        # Sort by field if specified
        sort_by = self.request.GET.get('sort_by', '-reported_date')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['status_choices'] = ProductionBug.STATUS_CHOICES
        context['severity_choices'] = ProductionBug.SEVERITY_CHOICES
        context['test_case_choices'] = ProductionBug.TEST_CASE_CHOICES

        # Add current filter values to context
        context['current_filters'] = {
            'project': self.request.GET.get('project', ''),
            'status': self.request.GET.get('status', ''),
            'severity': self.request.GET.get('severity', ''),
            'test_case': self.request.GET.get('test_case', ''),
            'search': self.request.GET.get('search', ''),
            'sort_by': self.request.GET.get('sort_by', '-reported_date'),
        }

        return context


class ProductionBugDetailView(DetailView):
    model = ProductionBug
    template_name = 'dashboard/production_bug_detail.html'
    context_object_name = 'bug'


class ProductionBugCreateView(CreateView):
    model = ProductionBug
    template_name = 'dashboard/production_bug_form.html'
    fields = ['title', 'project', 'gops_board_link', 'product_board_link', 
              'reported_date', 'resolved_date', 'status', 'severity', 
              'details', 'test_case_added']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['reported_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['resolved_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Production Bug'
        return context


class ProductionBugUpdateView(UpdateView):
    model = ProductionBug
    template_name = 'dashboard/production_bug_form.html'
    fields = ['title', 'project', 'gops_board_link', 'product_board_link', 
              'reported_date', 'resolved_date', 'status', 'severity', 
              'details', 'test_case_added']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['reported_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['resolved_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Production Bug'
        return context


class ProductionBugDeleteView(RecyclableDeleteView):
    model = ProductionBug
    template_name = 'dashboard/production_bug_confirm_delete.html'
    success_url = reverse_lazy('production-bug-list')


# Documentation Management Views
class ProductDocumentationListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = ProductDocumentation
    template_name = 'dashboard/product_documentation_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('project')

        # Filter by project if specified
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Search by title or project name
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(project__name__icontains=search_query)
            )

        # Sort by field if specified
        sort_by = self.request.GET.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()

        # Add current filter values to context
        context['current_filters'] = {
            'project': self.request.GET.get('project', ''),
            'search': self.request.GET.get('search', ''),
            'sort_by': self.request.GET.get('sort_by', '-created_at'),
        }

        return context


class DepartmentDocumentListView(PaginationMixin, ListView):
    model = DepartmentDocument
    template_name = 'dashboard/department_document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by title
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        # Sort by field if specified
        sort_by = self.request.GET.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add current filter values to context
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'sort_by': self.request.GET.get('sort_by', '-created_at'),
        }

        return context


class DepartmentDocumentCreateView(CreateView):
    model = DepartmentDocument
    template_name = 'dashboard/department_document_form.html'
    fields = ['title', 'confluence_link']
    success_url = reverse_lazy('department-document-list')


class DepartmentDocumentUpdateView(UpdateView):
    model = DepartmentDocument
    template_name = 'dashboard/department_document_form.html'
    fields = ['title', 'confluence_link']
    success_url = reverse_lazy('department-document-list')


class DepartmentDocumentDeleteView(RecyclableDeleteView):
    model = DepartmentDocument
    template_name = 'dashboard/department_document_confirm_delete.html'
    success_url = reverse_lazy('department-document-list')


# Records Section Views
class RecordsPasswordForm(forms.Form):
    """Form for verifying the Records section password."""
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            records_password = RecordsPassword.objects.first()
            if not records_password or password != records_password.password:
                raise forms.ValidationError("Incorrect password")
        except RecordsPassword.DoesNotExist:
            raise forms.ValidationError("Records section is not configured")
        return password


class RecordsPasswordSetForm(forms.ModelForm):
    """Form for setting the Records section password."""
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = RecordsPassword
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")

        return cleaned_data


class RecordsPasswordVerificationMixin:
    """
    Mixin that requires password verification for accessing the Records section.
    """
    def dispatch(self, request, *args, **kwargs):
        # Check if the user has already verified the password in this session
        if request.session.get('records_password_verified'):
            return super().dispatch(request, *args, **kwargs)

        # If not, redirect to the password verification page
        return redirect('records-password-verify')


class RecordsPasswordVerifyView(FormView):
    """View for verifying the Records section password."""
    template_name = 'dashboard/records_password_verify.html'
    form_class = RecordsPasswordForm
    success_url = reverse_lazy('records-list')

    def form_valid(self, form):
        # Mark the session as verified
        self.request.session['records_password_verified'] = True
        return super().form_valid(form)


class RecordsPasswordSetView(FormView):
    """View for setting the Records section password."""
    template_name = 'dashboard/records_password_set.html'
    form_class = RecordsPasswordSetForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Get or create the RecordsPassword instance
        try:
            records_password = RecordsPassword.objects.first()
            if records_password:
                records_password.password = form.cleaned_data['password']
                records_password.save()
            else:
                form.save()
        except Exception as e:
            messages.error(self.request, f"Error setting password: {str(e)}")
            return self.form_invalid(form)

        messages.success(self.request, "Records section password has been set successfully.")
        return super().form_valid(form)


class RecordsListView(RecordsPasswordVerificationMixin, PaginationMixin, ListView):
    """View for listing deleted records."""
    model = DeletedRecord
    template_name = 'dashboard/records_list.html'
    context_object_name = 'records'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by model name if specified
        model_name = self.request.GET.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)

        # Search by record ID or model name
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(record_id__icontains=search_query) | 
                Q(model_name__icontains=search_query)
            )

        # Sort by field if specified
        sort_by = self.request.GET.get('sort_by', '-deleted_at')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get unique model names for filtering
        model_names = DeletedRecord.objects.values_list('model_name', flat=True).distinct()
        context['model_names'] = model_names

        # Add current filter values to context
        context['current_filters'] = {
            'model_name': self.request.GET.get('model_name', ''),
            'search': self.request.GET.get('search', ''),
            'sort_by': self.request.GET.get('sort_by', '-deleted_at'),
        }

        return context


def restore_record(request, pk):
    """View for restoring a deleted record."""
    # Check if the user has verified the password
    if not request.session.get('records_password_verified'):
        return redirect('records-password-verify')

    record = get_object_or_404(DeletedRecord, pk=pk)

    try:
        # Restore the record
        restored_record = record.restore()
        messages.success(request, f"{record.model_name} #{record.record_id} has been restored successfully.")
    except Exception as e:
        messages.error(request, f"Error restoring record: {str(e)}")

    return redirect('records-list')


class SettingsView(LoginRequiredMixin, TemplateView):
    """View for user settings page."""
    template_name = 'dashboard/settings.html'


# KPI Management Views
class KPIManagementView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    Main view for KPI Management - displays a list of resources
    """
    model = Resource
    template_name = 'dashboard/kpi_management.html'
    context_object_name = 'resources'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Add annotation for KPI count
        queryset = queryset.annotate(kpi_count=Count('kpis'))

        # Filter by search query if provided
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(role__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')

        # Get current month and year for quick links
        today = timezone.now().date()
        context['current_month'] = today.month
        context['current_year'] = today.year

        # Get previous month and year for quick links
        prev_month = today.month - 1
        prev_year = today.year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        context['prev_month'] = prev_month
        context['prev_year'] = prev_year

        return context


class ResourceKPIListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    Displays a list of KPIs for a specific resource
    """
    model = KPI
    template_name = 'dashboard/resource_kpi_list.html'
    context_object_name = 'kpis'

    def get_queryset(self):
        self.resource = get_object_or_404(Resource, pk=self.kwargs['resource_id'])
        return KPI.objects.filter(resource=self.resource)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource'] = self.resource

        # Get current month and year for rating link
        today = timezone.now().date()
        context['current_month'] = today.month
        context['current_year'] = today.year

        # Check if there are any KPI submissions for this resource
        context['has_submissions'] = KPIRatingSubmission.objects.filter(resource=self.resource).exists()

        return context


class KPICreateView(LoginRequiredMixin, CreateView):
    """
    Create a new KPI for a resource
    """
    model = KPI
    template_name = 'dashboard/kpi_form.html'
    fields = ['name', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.resource = get_object_or_404(Resource, pk=self.kwargs['resource_id'])
        context['resource'] = self.resource
        context['title'] = f"Add KPI for {self.resource.name}"
        return context

    def form_valid(self, form):
        form.instance.resource = get_object_or_404(Resource, pk=self.kwargs['resource_id'])
        messages.success(self.request, f"KPI '{form.instance.name}' has been created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('resource-kpi-list', kwargs={'resource_id': self.kwargs['resource_id']})


class KPIDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a KPI including its ratings history
    """
    model = KPI
    template_name = 'dashboard/kpi_detail.html'
    context_object_name = 'kpi'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all ratings for this KPI
        context['ratings'] = self.object.ratings.all().order_by('-year', '-month')

        # Calculate average rating
        if context['ratings'].exists():
            context['avg_rating'] = context['ratings'].aggregate(Avg('rating'))['rating__avg']
        else:
            context['avg_rating'] = None

        # Get current month and year for rating link
        today = timezone.now().date()
        context['current_month'] = today.month
        context['current_year'] = today.year

        return context


class KPIUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update a KPI
    """
    model = KPI
    template_name = 'dashboard/kpi_form.html'
    fields = ['name', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource'] = self.object.resource
        context['title'] = f"Edit KPI: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"KPI '{form.instance.name}' has been updated successfully.")
        return super().form_valid(form)


class KPIDeleteView(LoginRequiredMixin, RecyclableDeleteView):
    """
    Delete a KPI
    """
    model = KPI
    template_name = 'dashboard/kpi_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource'] = self.object.resource
        return context

    def get_success_url(self):
        return reverse_lazy('resource-kpi-list', kwargs={'resource_id': self.object.resource.id})

    def delete(self, request, *args, **kwargs):
        kpi = self.get_object()
        messages.success(request, f"KPI '{kpi.name}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


class KPIRatingForm(forms.ModelForm):
    """
    Form for rating KPIs
    """
    class Meta:
        model = KPIRating
        fields = ['rating', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }


class KPIRatingView(LoginRequiredMixin, TemplateView):
    """
    Rate KPIs for a resource for a specific month/year
    """
    template_name = 'dashboard/kpi_rating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get resource, month, and year from URL
        resource_id = self.kwargs['resource_id']
        month = self.kwargs['month']
        year = self.kwargs['year']

        # Get resource
        resource = get_object_or_404(Resource, pk=resource_id)
        context['resource'] = resource
        context['month'] = month
        context['year'] = year
        context['month_name'] = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }[month]

        # Get KPIs for this resource
        kpis = KPI.objects.filter(resource=resource)

        # Check if there's an existing submission for this month/year
        submission = KPIRatingSubmission.objects.filter(
            resource=resource,
            month=month,
            year=year
        ).first()
        context['submission'] = submission

        # Prepare forms for each KPI
        kpi_forms = []
        for kpi in kpis:
            # Check if there's an existing rating for this KPI/month/year
            rating = KPIRating.objects.filter(
                kpi=kpi,
                month=month,
                year=year
            ).first()

            if rating:
                form = KPIRatingForm(instance=rating, prefix=f'kpi_{kpi.id}')
            else:
                form = KPIRatingForm(prefix=f'kpi_{kpi.id}')

            # Set month, year, and kpi on the form instance to avoid validation errors
            if not rating:
                form.instance.kpi = kpi
                form.instance.month = month
                form.instance.year = year

            kpi_forms.append({
                'kpi': kpi,
                'form': form,
                'rating': rating
            })

        context['kpi_forms'] = kpi_forms

        # Form for overall remarks
        if submission:
            context['overall_remarks'] = submission.overall_remarks
        else:
            context['overall_remarks'] = ''

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        resource = context['resource']
        month = context['month']
        year = context['year']

        # Process each KPI form
        kpi_forms = context['kpi_forms']
        all_valid = True

        for kpi_form_data in kpi_forms:
            kpi = kpi_form_data['kpi']
            form = KPIRatingForm(request.POST, instance=kpi_form_data['rating'], prefix=f'kpi_{kpi.id}')
            kpi_form_data['form'] = form

            # Set month and year before validation to avoid form field errors
            rating = form.instance
            rating.kpi = kpi
            rating.month = month
            rating.year = year

            if form.is_valid():
                form.save()
            else:
                all_valid = False

        # Process overall remarks
        overall_remarks = request.POST.get('overall_remarks', '').strip()
        if not overall_remarks:
            messages.error(request, "Overall remarks are required.")
            all_valid = False
            context['overall_remarks'] = ''
        else:
            context['overall_remarks'] = overall_remarks

        if all_valid:
            # Create or update submission
            submission, created = KPIRatingSubmission.objects.update_or_create(
                resource=resource,
                month=month,
                year=year,
                defaults={
                    'overall_remarks': overall_remarks,
                    'submitted_by': request.user
                }
            )

            messages.success(request, f"KPI ratings for {resource.name} for {context['month_name']} {year} have been submitted successfully.")
            return redirect('resource-kpi-list', resource_id=resource.id)

        return self.render_to_response(context)


class KPIRatingSubmissionListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    List of KPI rating submissions for a resource
    """
    model = KPIRatingSubmission
    template_name = 'dashboard/kpi_submission_list.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        self.resource = get_object_or_404(Resource, pk=self.kwargs['resource_id'])
        return KPIRatingSubmission.objects.filter(resource=self.resource)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource'] = self.resource

        # Add month names to submissions
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        for submission in context['submissions']:
            submission.month_name = month_names[submission.month]

        return context


class KPIRatingSubmissionDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a KPI rating submission
    """
    model = KPIRatingSubmission
    template_name = 'dashboard/kpi_submission_detail.html'
    context_object_name = 'submission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get month name
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        context['month_name'] = month_names[self.object.month]

        # Get all KPI ratings for this submission
        resource = self.object.resource
        month = self.object.month
        year = self.object.year

        # Get all KPIs for this resource
        kpis = KPI.objects.filter(resource=resource)

        # Get ratings for each KPI
        kpi_ratings = []
        for kpi in kpis:
            rating = KPIRating.objects.filter(
                kpi=kpi,
                month=month,
                year=year
            ).first()

            if rating:
                kpi_ratings.append({
                    'kpi': kpi,
                    'rating': rating
                })

        context['kpi_ratings'] = kpi_ratings

        # Calculate average rating
        if kpi_ratings:
            total_rating = sum(item['rating'].rating for item in kpi_ratings)
            context['avg_rating'] = total_rating / len(kpi_ratings)
        else:
            context['avg_rating'] = None

        return context


class ResourceAlignmentView(LoginRequiredMixin, PaginationMixin, ListView):
    """View for resource alignment across all products."""
    model = Project
    template_name = 'dashboard/resource_alignment.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by team lead
        team_lead = self.request.GET.get('team_lead')
        if team_lead:
            queryset = queryset.filter(team_lead=team_lead)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter options to context
        context['status_choices'] = Project.STATUS_CHOICES
        context['team_leads'] = Resource.objects.all()

        # Add current filter values to context
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'team_lead': self.request.GET.get('team_lead', '')
        }

        # Get all resources for assignment
        context['resources'] = Resource.objects.all()

        # Get all project resources
        project_resources = ProjectResource.objects.select_related('project', 'resource').all()

        # Organize resources by project
        resources_by_project = {}
        for pr in project_resources:
            if pr.project.id not in resources_by_project:
                resources_by_project[pr.project.id] = []
            resources_by_project[pr.project.id].append(pr)

        context['resources_by_project'] = resources_by_project

        return context


class UserActionListView(LoginRequiredMixin, PaginationMixin, ListView):
    """View for listing user actions."""
    model = UserAction
    template_name = 'dashboard/user_action_list.html'
    context_object_name = 'actions'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by user if specified
        user_id = self.request.GET.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by action type if specified
        action_type = self.request.GET.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        # Filter by model name if specified
        model_name = self.request.GET.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)

        # Filter by date range if specified
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            # Add time component to make it inclusive of the entire day
            queryset = queryset.filter(timestamp__gte=f"{start_date} 00:00:00")
        if end_date:
            # Add time component to make it inclusive of the entire day
            queryset = queryset.filter(timestamp__lte=f"{end_date} 23:59:59")

        # Search by details if specified
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(details__icontains=search_query) | 
                Q(user__username__icontains=search_query) |
                Q(model_name__icontains=search_query)
            )

        # Sort by field if specified
        sort_by = self.request.GET.get('sort_by', '-timestamp')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['current_filters'] = {
            'user_id': self.request.GET.get('user_id', ''),
            'action_type': self.request.GET.get('action_type', ''),
            'model_name': self.request.GET.get('model_name', ''),
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
            'search': self.request.GET.get('search', ''),
            'sort_by': self.request.GET.get('sort_by', '-timestamp'),
        }

        # Convert user_id to string for template comparison
        if context['current_filters']['user_id']:
            context['current_filters']['user_id'] = str(context['current_filters']['user_id'])

        # Add action types for filtering
        context['action_types'] = UserAction.ACTION_TYPES

        # Add unique model names for filtering
        context['model_names'] = UserAction.objects.values_list('model_name', flat=True).distinct()

        # Add users for filtering
        from django.contrib.auth.models import User
        context['users'] = User.objects.all()

        return context


# One-on-One Feedback Views
class OneOnOneFeedbackForm(forms.ModelForm):
    """
    Form for creating and updating 1:1 feedback.
    """
    class Meta:
        model = OneOnOneFeedback
        fields = ['resource', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resource'].widget.attrs.update({'class': 'form-control'})
        self.fields['notes'].widget.attrs.update({'class': 'form-control'})


class OneOnOneFeedbackListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    View for listing all 1:1 feedbacks with pagination.
    """
    model = OneOnOneFeedback
    template_name = 'dashboard/one_on_one_feedback_list.html'
    context_object_name = 'feedbacks'

    def get_queryset(self):
        queryset = OneOnOneFeedback.objects.all()

        # Get filter parameters from request
        resource_name = self.request.GET.get('resource_name', '')

        # Apply filters
        if resource_name:
            queryset = queryset.filter(resource__name__icontains=resource_name)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['resource_name'] = self.request.GET.get('resource_name', '')

        # Add resources for dropdown
        context['resources'] = Resource.objects.all().order_by('name')

        return context


class OneOnOneFeedbackDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of a 1:1 feedback.
    """
    model = OneOnOneFeedback
    template_name = 'dashboard/one_on_one_feedback_detail.html'
    context_object_name = 'feedback'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OneOnOneFeedbackCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new 1:1 feedback.
    """
    model = OneOnOneFeedback
    form_class = OneOnOneFeedbackForm
    template_name = 'dashboard/one_on_one_feedback_form.html'

    def get_initial(self):
        initial = super().get_initial()
        resource_id = self.request.GET.get('resource_id')
        if resource_id:
            initial['resource'] = resource_id
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "1:1 Feedback created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create 1:1 Feedback'
        return context


class OneOnOneFeedbackUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing 1:1 feedback.
    """
    model = OneOnOneFeedback
    form_class = OneOnOneFeedbackForm
    template_name = 'dashboard/one_on_one_feedback_form.html'

    def form_valid(self, form):
        messages.success(self.request, "1:1 Feedback updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update 1:1 Feedback'
        return context


class OneOnOneFeedbackDeleteView(LoginRequiredMixin, RecyclableDeleteView):
    """
    View for deleting a 1:1 feedback.
    """
    model = OneOnOneFeedback
    template_name = 'dashboard/one_on_one_feedback_confirm_delete.html'
    success_url = reverse_lazy('one-on-one-feedback-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "1:1 Feedback deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Monthly Feedback Views
class MonthlyFeedbackForm(forms.ModelForm):
    """
    Form for creating and updating monthly feedback.
    """
    class Meta:
        model = MonthlyFeedback
        fields = ['resource', 'month', 'year', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'month': forms.Select(choices=[(i, i) for i in range(1, 13)]),
            'year': forms.Select(choices=[(i, i) for i in range(timezone.now().year - 2, timezone.now().year + 3)]),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['resource'].widget.attrs.update({'class': 'form-control'})
        self.fields['month'].widget.attrs.update({'class': 'form-control'})
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
        self.fields['feedback'].widget.attrs.update({'class': 'form-control'})

        # Filter resources based on user role
        if self.user:
            try:
                user_resource = Resource.objects.get(user=self.user)
                # If user is a lead, show only resources that report to them
                if Resource.objects.filter(lead=user_resource).exists():
                    self.fields['resource'].queryset = Resource.objects.filter(lead=user_resource)
                # If user is a manager, show all resources
                elif Resource.objects.filter(manager=user_resource).exists():
                    self.fields['resource'].queryset = Resource.objects.all()
                # Otherwise, user can only see themselves
                else:
                    self.fields['resource'].queryset = Resource.objects.filter(id=user_resource.id)
            except Resource.DoesNotExist:
                # If user doesn't have a resource, don't show any resources
                self.fields['resource'].queryset = Resource.objects.none()


class MonthlyFeedbackListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    View for listing resources for monthly feedback with pagination.
    """
    model = Resource
    template_name = 'dashboard/monthly_feedback_list.html'
    context_object_name = 'resources'

    def get_queryset(self):
        try:
            user_resource = Resource.objects.get(user=self.request.user)

            # If user is a lead, show only resources that report to them
            if Resource.objects.filter(lead=user_resource).exists():
                queryset = Resource.objects.filter(lead=user_resource)
            # If user is a manager, show all resources
            elif Resource.objects.filter(manager=user_resource).exists():
                queryset = Resource.objects.all()
            # Otherwise, user can only see themselves
            else:
                queryset = Resource.objects.filter(id=user_resource.id)

            # Get filter parameters from request
            resource_name = self.request.GET.get('resource_name', '')

            # Apply filters
            if resource_name:
                queryset = queryset.filter(name__icontains=resource_name)

            return queryset.order_by('name')
        except Resource.DoesNotExist:
            return Resource.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['resource_name'] = self.request.GET.get('resource_name', '')

        # Get current month and year
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Add feedback status for each resource
        resources_with_status = []
        for resource in context['resources']:
            try:
                feedback = MonthlyFeedback.objects.get(
                    resource=resource,
                    month=current_month,
                    year=current_year
                )
                status = feedback.status
                feedback_id = feedback.id
            except MonthlyFeedback.DoesNotExist:
                status = 'due'
                feedback_id = None

            resources_with_status.append({
                'resource': resource,
                'status': status,
                'feedback_id': feedback_id
            })

        context['resources_with_status'] = resources_with_status
        context['current_month'] = current_month
        context['current_year'] = current_year

        # Add month name for display
        import calendar
        context['month_name'] = calendar.month_name[current_month]

        return context


class MonthlyFeedbackDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of a monthly feedback.
    """
    model = MonthlyFeedback
    template_name = 'dashboard/monthly_feedback_detail.html'
    context_object_name = 'feedback'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if user has permission to view this feedback
        try:
            user_resource = Resource.objects.get(user=self.request.user)
            feedback_resource = self.object.resource

            # User can view feedback if:
            # 1. They are the resource the feedback is about
            # 2. They are the lead of the resource
            # 3. They are the manager of the resource
            # 4. They submitted the feedback
            if (user_resource == feedback_resource or 
                user_resource == feedback_resource.lead or 
                user_resource == feedback_resource.manager or 
                self.request.user == self.object.submitted_by):
                context['can_view'] = True
            else:
                context['can_view'] = False

        except Resource.DoesNotExist:
            # If user doesn't have a resource, they can only view if they submitted the feedback
            context['can_view'] = self.request.user == self.object.submitted_by

        return context


class MonthlyFeedbackCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new monthly feedback.
    """
    model = MonthlyFeedback
    form_class = MonthlyFeedbackForm
    template_name = 'dashboard/monthly_feedback_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        resource_id = self.request.GET.get('resource_id')
        if resource_id:
            initial['resource'] = resource_id

        # Set default month and year to current month and year
        initial['month'] = timezone.now().month
        initial['year'] = timezone.now().year

        return initial

    def form_valid(self, form):
        form.instance.submitted_by = self.request.user
        form.instance.status = 'submitted'
        messages.success(self.request, "Monthly Feedback submitted successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Submit Monthly Feedback'
        return context


class MonthlyFeedbackUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing monthly feedback.
    """
    model = MonthlyFeedback
    form_class = MonthlyFeedbackForm
    template_name = 'dashboard/monthly_feedback_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Check if the feedback was already submitted
        if self.object.status == 'submitted':
            messages.error(self.request, "This feedback has already been submitted and cannot be edited.")
            return HttpResponseRedirect(self.get_success_url())

        form.instance.status = 'submitted'
        messages.success(self.request, "Monthly Feedback updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Monthly Feedback'
        return context


class MonthlyFeedbackHistoryView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    View for listing all submitted feedback for resources under the user's reporting.
    """
    model = MonthlyFeedback
    template_name = 'dashboard/monthly_feedback_history.html'
    context_object_name = 'feedbacks'
    paginate_by = 20

    def get_queryset(self):
        try:
            user_resource = Resource.objects.get(user=self.request.user)

            # Get resources under user's reporting
            if Resource.objects.filter(lead=user_resource).exists():
                # If user is a lead, show feedback for resources that report to them
                resources_under_reporting = Resource.objects.filter(lead=user_resource)
            elif Resource.objects.filter(manager=user_resource).exists():
                # If user is a manager, show feedback for all resources
                resources_under_reporting = Resource.objects.all()
            else:
                # Otherwise, user can only see their own feedback
                resources_under_reporting = Resource.objects.filter(id=user_resource.id)

            # Get filter parameters from request
            month = self.request.GET.get('month', '')
            year = self.request.GET.get('year', '')
            resource_name = self.request.GET.get('resource_name', '')
            status = self.request.GET.get('status', '')

            # Start with all feedback for resources under reporting
            queryset = MonthlyFeedback.objects.filter(resource__in=resources_under_reporting)

            # Apply filters
            if month and month.isdigit():
                queryset = queryset.filter(month=int(month))

            if year and year.isdigit():
                queryset = queryset.filter(year=int(year))

            if resource_name:
                queryset = queryset.filter(resource__name__icontains=resource_name)

            if status:
                queryset = queryset.filter(status=status)

            return queryset.order_by('-year', '-month', 'resource__name')
        except Resource.DoesNotExist:
            return MonthlyFeedback.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['month'] = self.request.GET.get('month', '')
        context['year'] = self.request.GET.get('year', '')
        context['resource_name'] = self.request.GET.get('resource_name', '')
        context['status'] = self.request.GET.get('status', '')

        # Add month choices for filter
        import calendar
        context['month_choices'] = [(str(i), calendar.month_name[i]) for i in range(1, 13)]

        # Add year choices for filter (last 5 years)
        current_year = timezone.now().year
        context['year_choices'] = [(str(year), str(year)) for year in range(current_year - 4, current_year + 1)]

        # Add status choices for filter
        context['status_choices'] = [('due', 'Feedback Due'), ('submitted', 'Submitted')]

        return context


class LinkUserResourceForm(forms.Form):
    """
    Form for linking a user account to a resource.
    """
    resource = forms.ModelChoiceField(
        queryset=Resource.objects.filter(user__isnull=True),
        required=True,
        label="Select Resource",
        help_text="Select the resource that represents you"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If user already has a linked resource, show a message
        if self.user and hasattr(self.user, 'resource'):
            self.fields['resource'].help_text = "You already have a linked resource. Selecting a new one will update the link."
            self.fields['resource'].initial = self.user.resource


@login_required
def link_user_to_resource(request):
    """
    View for linking a user account to a resource.
    """
    # Check if user already has a linked resource
    existing_resource = None
    try:
        if hasattr(request.user, 'resource'):
            existing_resource = request.user.resource
    except Resource.DoesNotExist:
        pass

    if request.method == 'POST':
        form = LinkUserResourceForm(request.POST, user=request.user)
        if form.is_valid():
            resource = form.cleaned_data['resource']

            # If this resource is already linked to another user, show an error
            if resource.user and resource.user != request.user:
                messages.error(request, f"This resource is already linked to user {resource.user.username}")
                return redirect('link-user-resource')

            # If user already has a linked resource, unlink it
            if existing_resource and existing_resource != resource:
                existing_resource.user = None
                existing_resource.save()
                messages.info(request, f"Unlinked from previous resource: {existing_resource.name}")

            # Link the selected resource to the user
            resource.user = request.user
            resource.save()
            messages.success(request, f"Successfully linked your account to resource: {resource.name}")
            return redirect('dashboard')
    else:
        form = LinkUserResourceForm(user=request.user)

    return render(request, 'dashboard/link_user_resource.html', {
        'form': form,
        'existing_resource': existing_resource,
    })


# SOP Management Views
class SOPForm(forms.ModelForm):
    """
    Form for creating and updating SOPs.
    """
    class Meta:
        model = SOP
        fields = ['name', 'link', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class SOPListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    View for listing all SOPs with tabs for All SOPs and Add SOP.
    """
    model = SOP
    template_name = 'dashboard/sop_list.html'
    context_object_name = 'sops'
    paginate_by = 10

    def get_queryset(self):
        queryset = SOP.objects.all()

        # Get filter parameters from request
        name = self.request.GET.get('name', '')
        status = self.request.GET.get('status', '')

        # Apply filters
        if name:
            queryset = queryset.filter(name__icontains=name)
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['name'] = self.request.GET.get('name', '')
        context['status'] = self.request.GET.get('status', '')

        # Add status choices for filtering
        context['status_choices'] = SOP.STATUS_CHOICES

        # Add form for creating new SOP
        context['form'] = SOPForm()

        # Set active tab
        context['active_tab'] = self.request.GET.get('tab', 'all')

        return context


class SOPCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new SOP.
    """
    model = SOP
    form_class = SOPForm
    template_name = 'dashboard/sop_form.html'
    success_url = reverse_lazy('sop-list')

    def form_valid(self, form):
        messages.success(self.request, "SOP created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create SOP'
        return context


class SOPUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing SOP.
    """
    model = SOP
    form_class = SOPForm
    template_name = 'dashboard/sop_form.html'

    def form_valid(self, form):
        # Set the user who changed the status
        if 'status' in form.changed_data:
            # The status will be updated in the save method of the SOP model
            # We need to set the user for the status history entry
            # This will be done in the view that handles the form submission
            pass

        messages.success(self.request, "SOP updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update SOP'
        return context


class SOPDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of a SOP, including its status history.
    """
    model = SOP
    template_name = 'dashboard/sop_detail.html'
    context_object_name = 'sop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add status history to context
        context['status_history'] = self.object.status_history.all()

        return context


class SOPStatusUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating the status of a SOP.
    """
    model = SOP
    fields = ['status']
    template_name = 'dashboard/sop_status_form.html'

    def form_valid(self, form):
        # Set the user who changed the status
        # This will be used in the SOPStatusHistory entry
        status_history = self.object.status_history.last()
        if status_history and status_history.changed_by is None:
            status_history.changed_by = self.request.user
            status_history.save()

        messages.success(self.request, f"SOP status updated to {self.object.get_status_display()}.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update SOP Status'
        return context


class AutomationRunnerForm(forms.ModelForm):
    """
    Form for creating and updating Automation Runners.
    """
    class Meta:
        model = AutomationRunner
        fields = ['name', 'link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }


class AutomationRunnerListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    View for displaying a list of Automation Runners.
    """
    model = AutomationRunner
    template_name = 'dashboard/automation_runner_list.html'
    context_object_name = 'automation_runners'
    paginate_by = 10

    def get_queryset(self):
        queryset = AutomationRunner.objects.all()

        # Get filter parameters from request
        name = self.request.GET.get('name', '')

        # Apply filters
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['name'] = self.request.GET.get('name', '')

        # Add form for creating new Automation Runner
        context['form'] = AutomationRunnerForm()

        return context


class AutomationRunnerDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of an Automation Runner.
    """
    model = AutomationRunner
    template_name = 'dashboard/automation_runner_detail.html'
    context_object_name = 'automation_runner'


class AutomationRunnerCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new Automation Runner.
    """
    model = AutomationRunner
    form_class = AutomationRunnerForm
    template_name = 'dashboard/automation_runner_form.html'
    success_url = reverse_lazy('automation-runner-list')

    def form_valid(self, form):
        messages.success(self.request, "Automation Runner created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Automation Runner'
        return context


class AutomationRunnerUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing Automation Runner.
    """
    model = AutomationRunner
    form_class = AutomationRunnerForm
    template_name = 'dashboard/automation_runner_form.html'
    success_url = reverse_lazy('automation-runner-list')

    def form_valid(self, form):
        messages.success(self.request, "Automation Runner updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Automation Runner'
        return context


class AutomationRunnerDeleteView(LoginRequiredMixin, RecyclableDeleteView):
    """
    View for deleting an Automation Runner.
    """
    model = AutomationRunner
    template_name = 'dashboard/automation_runner_confirm_delete.html'
    success_url = reverse_lazy('automation-runner-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Automation Runner deleted successfully.")
        return super().delete(request, *args, **kwargs)


class AutomationSprintCreateForm(forms.ModelForm):
    """
    Form for creating new Automation Sprints without metrics fields.
    """
    class Meta:
        model = AutomationSprint
        fields = [
            'product', 'engineering_manager_name', 'sprint_length', 'total_dev_resources', 
            'sprint_type', 'start_date', 'status', 'rationale', 'risks', 
            'qa_point_of_contact', 'dev_training_status', 'notes'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'engineering_manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sprint_length': forms.Select(attrs={'class': 'form-control'}),
            'total_dev_resources': forms.NumberInput(attrs={'class': 'form-control'}),
            'sprint_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rationale': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'risks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'qa_point_of_contact': forms.Select(attrs={'class': 'form-control'}),
            'dev_training_status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AutomationSprintForm(forms.ModelForm):
    """
    Form for updating Automation Sprints including metrics fields.
    """
    class Meta:
        model = AutomationSprint
        fields = [
            'product', 'engineering_manager_name', 'sprint_length', 'total_dev_resources', 
            'sprint_type', 'start_date', 'status', 'rationale', 'risks', 
            'qa_point_of_contact', 'dev_training_status', 'notes',
            'total_sprint_days', 'total_planned_working_hours', 'blocked_hours',
            'total_planned_test_cases', 'total_test_cases_automated'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'engineering_manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sprint_length': forms.Select(attrs={'class': 'form-control'}),
            'total_dev_resources': forms.NumberInput(attrs={'class': 'form-control'}),
            'sprint_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rationale': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'risks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'qa_point_of_contact': forms.Select(attrs={'class': 'form-control'}),
            'dev_training_status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_sprint_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_planned_working_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'blocked_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_planned_test_cases': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_test_cases_automated': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AutomationSprintListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    View for displaying a list of Automation Sprints.
    """
    model = AutomationSprint
    template_name = 'dashboard/automation_sprint_list.html'
    context_object_name = 'automation_sprints'
    paginate_by = 10

    def get_queryset(self):
        queryset = AutomationSprint.objects.all()

        # Get filter parameters from request
        product = self.request.GET.get('product', '')
        status = self.request.GET.get('status', '')
        sprint_type = self.request.GET.get('sprint_type', '')

        # Apply filters
        if product:
            queryset = queryset.filter(product__name__icontains=product)
        if status:
            queryset = queryset.filter(status=status)
        if sprint_type:
            queryset = queryset.filter(sprint_type=sprint_type)

        return queryset.order_by('-start_date', 'product__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to context
        context['product'] = self.request.GET.get('product', '')
        context['status'] = self.request.GET.get('status', '')
        context['sprint_type'] = self.request.GET.get('sprint_type', '')

        # Add form for creating new Automation Sprint
        context['form'] = AutomationSprintCreateForm()

        # Add choices for dropdowns
        context['status_choices'] = AutomationSprint.STATUS_CHOICES
        context['sprint_type_choices'] = AutomationSprint.SPRINT_TYPE_CHOICES

        return context


class AutomationSprintDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of an Automation Sprint.
    """
    model = AutomationSprint
    template_name = 'dashboard/automation_sprint_detail.html'
    context_object_name = 'automation_sprint'


class AutomationSprintCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new Automation Sprint.
    """
    model = AutomationSprint
    form_class = AutomationSprintCreateForm
    template_name = 'dashboard/automation_sprint_form.html'
    success_url = reverse_lazy('automation-sprint-list')

    def form_valid(self, form):
        messages.success(self.request, "Automation Sprint created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Automation Sprint'
        return context


class AutomationSprintUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing Automation Sprint.
    """
    model = AutomationSprint
    form_class = AutomationSprintForm
    template_name = 'dashboard/automation_sprint_form.html'
    success_url = reverse_lazy('automation-sprint-list')

    def form_valid(self, form):
        messages.success(self.request, "Automation Sprint updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Automation Sprint'
        return context


class AutomationSprintDeleteView(LoginRequiredMixin, RecyclableDeleteView):
    """
    View for deleting an Automation Sprint.
    """
    model = AutomationSprint
    template_name = 'dashboard/automation_sprint_confirm_delete.html'
    success_url = reverse_lazy('automation-sprint-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Automation Sprint deleted successfully.")
        return super().delete(request, *args, **kwargs)


class SprintMetricsForm(forms.ModelForm):
    """
    Form for updating Sprint Metrics.
    All fields are optional.
    """
    total_sprint_days = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    total_planned_working_hours = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    blocked_hours = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    total_planned_test_cases = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    total_test_cases_automated = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = AutomationSprint
        fields = [
            'total_sprint_days', 
            'total_planned_working_hours', 
            'blocked_hours',
            'total_planned_test_cases',
            'total_test_cases_automated'
        ]


class SprintMetricsUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating Sprint Metrics.
    """
    model = AutomationSprint
    form_class = SprintMetricsForm
    template_name = 'dashboard/automation_sprint_metrics_form.html'

    def get_success_url(self):
        return reverse_lazy('automation-sprint-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Ensure total_planned_test_cases is properly saved
        if 'total_planned_test_cases' in form.cleaned_data and form.cleaned_data['total_planned_test_cases'] is not None:
            form.instance.total_planned_test_cases = form.cleaned_data['total_planned_test_cases']

        messages.success(self.request, "Sprint Metrics updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Sprint Metrics'
        context['sprint'] = self.object
        return context
