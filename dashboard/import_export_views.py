import csv
import io
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Resource, Project, ProjectResource

# Resource Import/Export Views
class ResourceExportView(View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'csv')

        # Get all resources
        resources = Resource.objects.all().values(
            'name', 'email', 'role', 'skill', 'availability'
        )

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="resources.csv"'

            writer = csv.DictWriter(response, fieldnames=['name', 'email', 'role', 'skill', 'availability'])
            writer.writeheader()

            for resource in resources:
                writer.writerow(resource)

            return response

        elif format_type == 'excel':
            # Convert to DataFrame
            df = pd.DataFrame(list(resources))

            # Create a response with Excel content type
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="resources.xlsx"'

            # Write DataFrame to Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resources')

            return response

        return JsonResponse({'error': 'Invalid format type'}, status=400)

class ResourceSampleFileView(View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'csv')

        # Sample data
        sample_data = [
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'role': 'Developer',
                'skill': 'both',
                'availability': True
            },
            {
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'role': 'Tester',
                'skill': 'automation',
                'availability': True
            }
        ]

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="sample_resources.csv"'

            writer = csv.DictWriter(response, fieldnames=['name', 'email', 'role', 'skill', 'availability'])
            writer.writeheader()

            for resource in sample_data:
                writer.writerow(resource)

            return response

        elif format_type == 'excel':
            # Convert to DataFrame
            df = pd.DataFrame(sample_data)

            # Create a response with Excel content type
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="sample_resources.xlsx"'

            # Write DataFrame to Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resources')

            return response

        return JsonResponse({'error': 'Invalid format type'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ResourceImportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/import_resources.html')

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'Please select a file to import')
            return redirect('resource-import')

        # Check file extension
        if file.name.endswith('.csv'):
            # Process CSV file
            try:
                decoded_file = file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)

                for row in reader:
                    # Convert availability string to boolean
                    if isinstance(row['availability'], str):
                        row['availability'] = row['availability'].lower() in ['true', 'yes', '1']

                    # Create or update resource
                    Resource.objects.update_or_create(
                        name=row['name'],
                        defaults={
                            'email': row['email'],
                            'role': row['role'],
                            'skill': row['skill'],
                            'availability': row['availability']
                        }
                    )

                messages.success(request, 'Resources imported successfully')
                return redirect('resource-list')

            except Exception as e:
                messages.error(request, f'Error importing resources: {str(e)}')
                return redirect('resource-import')

        elif file.name.endswith(('.xls', '.xlsx')):
            # Process Excel file
            try:
                df = pd.read_excel(file)

                for _, row in df.iterrows():
                    # Convert availability to boolean
                    if isinstance(row['availability'], str):
                        availability = row['availability'].lower() in ['true', 'yes', '1']
                    else:
                        availability = bool(row['availability'])

                    # Create or update resource
                    Resource.objects.update_or_create(
                        name=row['name'],
                        defaults={
                            'email': row['email'],
                            'role': row['role'],
                            'skill': row['skill'],
                            'availability': availability
                        }
                    )

                messages.success(request, 'Resources imported successfully')
                return redirect('resource-list')

            except Exception as e:
                messages.error(request, f'Error importing resources: {str(e)}')
                return redirect('resource-import')

        else:
            messages.error(request, 'Unsupported file format. Please upload a CSV or Excel file.')
            return redirect('resource-import')

# Product Import/Export Views
class ProductExportView(View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'csv')

        # Get all products with automation fields
        products = Project.objects.all().values(
            'name', 'description', 'start_date', 'end_date', 'status',
            'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule',
            'execution_time_of_smoke', 'total_number_of_available_test_cases',
            'status_of_last_automation_run', 'date_of_last_automation_run',
            'automation_framework_tech_stack', 'team_lead_id', 'regression_coverage', 'smoke_coverage',
            'bugs_found_through_automation', 'total_automatable_test_cases',
            'total_automatable_smoke_test_cases', 'total_automated_test_cases',
            'total_automated_smoke_test_cases', 'sprint_cycle',
            'total_number_of_functional_test_cases', 'total_number_of_business_test_cases',
            'oat_release_cycle', 'in_production', 'in_development'
        )

        # Define fieldnames for CSV/Excel
        fieldnames = [
            'name', 'description', 'start_date', 'end_date', 'status',
            'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule',
            'execution_time_of_smoke', 'total_number_of_available_test_cases',
            'status_of_last_automation_run', 'date_of_last_automation_run',
            'automation_framework_tech_stack', 'team_lead_id', 'regression_coverage', 'smoke_coverage',
            'bugs_found_through_automation', 'total_automatable_test_cases',
            'total_automatable_smoke_test_cases', 'total_automated_test_cases',
            'total_automated_smoke_test_cases', 'sprint_cycle',
            'total_number_of_functional_test_cases', 'total_number_of_business_test_cases',
            'oat_release_cycle', 'in_production', 'in_development'
        ]

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="products.csv"'

            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()

            for product in products:
                writer.writerow(product)

            return response

        elif format_type == 'excel':
            # Convert to DataFrame
            df = pd.DataFrame(list(products))

            # Create a response with Excel content type
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

            # Write DataFrame to Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Products')

            return response

        return JsonResponse({'error': 'Invalid format type'}, status=400)

class ProductSampleFileView(View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'csv')

        # Sample data with automation fields
        sample_data = [
            {
                'name': 'Sample Product 1',
                'description': 'This is a sample product description',
                'start_date': '2023-01-01',
                'end_date': '2023-12-31',
                'status': 'in_progress',
                'smoke_automation_status': 'completed',
                'regression_automation_status': 'in_progress',
                'pipeline_schedule': 'weekly',
                'execution_time_of_smoke': '1h 30m',
                'total_number_of_available_test_cases': 150,
                'status_of_last_automation_run': 'Passed with 2 failures',
                'date_of_last_automation_run': '2023-12-15',
                'automation_framework_tech_stack': 'Selenium, Python, pytest',
                'team_lead_id': None,
                'regression_coverage': 75,
                'smoke_coverage': 83,
                'bugs_found_through_automation': 12,
                'total_automatable_test_cases': 120,
                'total_automatable_smoke_test_cases': 30,
                'total_automated_test_cases': 90,
                'total_automated_smoke_test_cases': 25,
                'sprint_cycle': 'Bi-weekly',
                'total_number_of_functional_test_cases': 100,
                'total_number_of_business_test_cases': 50,
                'oat_release_cycle': 'Monthly',
                'in_production': True,
                'in_development': False
            },
            {
                'name': 'Sample Product 2',
                'description': 'Another sample product description',
                'start_date': '2023-02-15',
                'end_date': '2023-11-30',
                'status': 'not_started',
                'smoke_automation_status': 'hold',
                'regression_automation_status': 'na',
                'pipeline_schedule': 'on_demand',
                'execution_time_of_smoke': '45m',
                'total_number_of_available_test_cases': 80,
                'status_of_last_automation_run': 'Not run yet',
                'date_of_last_automation_run': None,
                'automation_framework_tech_stack': 'Cypress, JavaScript',
                'team_lead_id': None,
                'regression_coverage': 0,
                'smoke_coverage': 0,
                'bugs_found_through_automation': 0,
                'total_automatable_test_cases': 60,
                'total_automatable_smoke_test_cases': 15,
                'total_automated_test_cases': 0,
                'total_automated_smoke_test_cases': 0,
                'sprint_cycle': 'Weekly',
                'total_number_of_functional_test_cases': 60,
                'total_number_of_business_test_cases': 20,
                'oat_release_cycle': 'Quarterly',
                'in_production': False,
                'in_development': True
            }
        ]

        # Define fieldnames for CSV/Excel
        fieldnames = [
            'name', 'description', 'start_date', 'end_date', 'status',
            'smoke_automation_status', 'regression_automation_status', 'pipeline_schedule',
            'execution_time_of_smoke', 'total_number_of_available_test_cases',
            'status_of_last_automation_run', 'date_of_last_automation_run',
            'automation_framework_tech_stack', 'team_lead_id', 'regression_coverage', 'smoke_coverage',
            'bugs_found_through_automation', 'total_automatable_test_cases',
            'total_automatable_smoke_test_cases', 'total_automated_test_cases',
            'total_automated_smoke_test_cases', 'sprint_cycle',
            'total_number_of_functional_test_cases', 'total_number_of_business_test_cases',
            'oat_release_cycle', 'in_production', 'in_development'
        ]

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="sample_products.csv"'

            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()

            for product in sample_data:
                writer.writerow(product)

            return response

        elif format_type == 'excel':
            # Convert to DataFrame
            df = pd.DataFrame(sample_data)

            # Create a response with Excel content type
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="sample_products.xlsx"'

            # Write DataFrame to Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Products')

            return response

        return JsonResponse({'error': 'Invalid format type'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ResourceAlignmentExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'excel')  # Default to Excel format

        # Get all project resources with related project and resource data
        project_resources = ProjectResource.objects.select_related('project', 'resource').all()

        # Filter by status if provided
        status = request.GET.get('status')
        if status:
            project_resources = project_resources.filter(project__status=status)

        # Filter by team lead if provided
        team_lead = request.GET.get('team_lead')
        if team_lead:
            project_resources = project_resources.filter(project__team_lead_id=team_lead)

        # Prepare data for export
        export_data = []
        for pr in project_resources:
            export_data.append({
                'product_name': pr.project.name,
                'product_status': pr.project.get_status_display(),
                'resource_name': pr.resource.name,
                'resource_role': pr.resource.role,
                'resource_skill': pr.resource.get_skill_display(),
                'hours_allocated': pr.hours_allocated,
                'utilization_percentage': pr.utilization_percentage,
                'eta': pr.eta,
                'notes': pr.notes
            })

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="resource_alignment.csv"'

            fieldnames = ['product_name', 'product_status', 'resource_name', 'resource_role', 
                         'resource_skill', 'hours_allocated', 'utilization_percentage', 'eta', 'notes']

            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()

            for item in export_data:
                writer.writerow(item)

            return response

        elif format_type == 'excel':
            # Convert to DataFrame
            df = pd.DataFrame(export_data)

            # Create a response with Excel content type
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="resource_alignment.xlsx"'

            # Write DataFrame to Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resource Alignment')

            return response

        return JsonResponse({'error': 'Invalid format type'}, status=400)


class ProductImportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/import_products.html')

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'Please select a file to import')
            return redirect('product-import')

        # Check file extension
        if file.name.endswith('.csv'):
            # Process CSV file
            try:
                decoded_file = file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)

                for row in reader:
                    # Handle boolean fields
                    in_production = False
                    if 'in_production' in row and row['in_production']:
                        if isinstance(row['in_production'], str):
                            in_production = row['in_production'].lower() in ['true', 'yes', '1']
                        else:
                            in_production = bool(row['in_production'])

                    in_development = False
                    if 'in_development' in row and row['in_development']:
                        if isinstance(row['in_development'], str):
                            in_development = row['in_development'].lower() in ['true', 'yes', '1']
                        else:
                            in_development = bool(row['in_development'])

                    # Create or update product with automation fields
                    defaults = {
                        'description': row.get('description', ''),
                        'start_date': row.get('start_date', None),
                        'end_date': row.get('end_date', None) if row.get('end_date') else None,
                        'status': row.get('status', 'not_started'),
                        'smoke_automation_status': row.get('smoke_automation_status', 'na'),
                        'regression_automation_status': row.get('regression_automation_status', 'na'),
                        'pipeline_schedule': row.get('pipeline_schedule', 'na'),
                        'execution_time_of_smoke': row.get('execution_time_of_smoke', ''),
                        'total_number_of_available_test_cases': row.get('total_number_of_available_test_cases', None),
                        'status_of_last_automation_run': row.get('status_of_last_automation_run', ''),
                        'date_of_last_automation_run': row.get('date_of_last_automation_run', None),
                        'automation_framework_tech_stack': row.get('automation_framework_tech_stack', ''),
                        'regression_coverage': row.get('regression_coverage', None),
                        'bugs_found_through_automation': row.get('bugs_found_through_automation', None),
                        'total_automatable_test_cases': row.get('total_automatable_test_cases', None),
                        'total_automatable_smoke_test_cases': row.get('total_automatable_smoke_test_cases', None),
                        'total_automated_test_cases': row.get('total_automated_test_cases', None),
                        'total_automated_smoke_test_cases': row.get('total_automated_smoke_test_cases', None),
                        'sprint_cycle': row.get('sprint_cycle', ''),
                        'total_number_of_functional_test_cases': row.get('total_number_of_functional_test_cases', None),
                        'total_number_of_business_test_cases': row.get('total_number_of_business_test_cases', None),
                        'oat_release_cycle': row.get('oat_release_cycle', ''),
                        'in_production': in_production,
                        'in_development': in_development
                    }

                    # Handle team_lead_id if present
                    if 'team_lead_id' in row and row['team_lead_id']:
                        defaults['team_lead_id'] = row['team_lead_id']

                    # Create or update product
                    Project.objects.update_or_create(
                        name=row['name'],
                        defaults=defaults
                    )

                messages.success(request, 'Products imported successfully')
                return redirect('product-list')

            except Exception as e:
                messages.error(request, f'Error importing products: {str(e)}')
                return redirect('product-import')

        elif file.name.endswith(('.xls', '.xlsx')):
            # Process Excel file
            try:
                df = pd.read_excel(file)

                for _, row in df.iterrows():
                    # Handle boolean fields
                    in_production = False
                    if 'in_production' in row and not pd.isna(row['in_production']):
                        if isinstance(row['in_production'], str):
                            in_production = row['in_production'].lower() in ['true', 'yes', '1']
                        else:
                            in_production = bool(row['in_production'])

                    in_development = False
                    if 'in_development' in row and not pd.isna(row['in_development']):
                        if isinstance(row['in_development'], str):
                            in_development = row['in_development'].lower() in ['true', 'yes', '1']
                        else:
                            in_development = bool(row['in_development'])

                    # Create or update product with automation fields
                    defaults = {
                        'description': row.get('description', ''),
                        'start_date': row.get('start_date', None),
                        'end_date': row.get('end_date', None) if not pd.isna(row.get('end_date', None)) else None,
                        'status': row.get('status', 'not_started'),
                        'smoke_automation_status': row.get('smoke_automation_status', 'na'),
                        'regression_automation_status': row.get('regression_automation_status', 'na'),
                        'pipeline_schedule': row.get('pipeline_schedule', 'na'),
                        'execution_time_of_smoke': row.get('execution_time_of_smoke', ''),
                        'total_number_of_available_test_cases': row.get('total_number_of_available_test_cases', None) if not pd.isna(row.get('total_number_of_available_test_cases', None)) else None,
                        'status_of_last_automation_run': row.get('status_of_last_automation_run', ''),
                        'date_of_last_automation_run': row.get('date_of_last_automation_run', None) if not pd.isna(row.get('date_of_last_automation_run', None)) else None,
                        'automation_framework_tech_stack': row.get('automation_framework_tech_stack', ''),
                        'regression_coverage': row.get('regression_coverage', None) if not pd.isna(row.get('regression_coverage', None)) else None,
                        'bugs_found_through_automation': row.get('bugs_found_through_automation', None) if not pd.isna(row.get('bugs_found_through_automation', None)) else None,
                        'total_automatable_test_cases': row.get('total_automatable_test_cases', None) if not pd.isna(row.get('total_automatable_test_cases', None)) else None,
                        'total_automatable_smoke_test_cases': row.get('total_automatable_smoke_test_cases', None) if not pd.isna(row.get('total_automatable_smoke_test_cases', None)) else None,
                        'total_automated_test_cases': row.get('total_automated_test_cases', None) if not pd.isna(row.get('total_automated_test_cases', None)) else None,
                        'total_automated_smoke_test_cases': row.get('total_automated_smoke_test_cases', None) if not pd.isna(row.get('total_automated_smoke_test_cases', None)) else None,
                        'sprint_cycle': row.get('sprint_cycle', ''),
                        'total_number_of_functional_test_cases': row.get('total_number_of_functional_test_cases', None) if not pd.isna(row.get('total_number_of_functional_test_cases', None)) else None,
                        'total_number_of_business_test_cases': row.get('total_number_of_business_test_cases', None) if not pd.isna(row.get('total_number_of_business_test_cases', None)) else None,
                        'oat_release_cycle': row.get('oat_release_cycle', ''),
                        'in_production': in_production,
                        'in_development': in_development
                    }

                    # Handle team_lead_id if present
                    if 'team_lead_id' in row and not pd.isna(row['team_lead_id']):
                        defaults['team_lead_id'] = row['team_lead_id']

                    # Create or update product
                    Project.objects.update_or_create(
                        name=row['name'],
                        defaults=defaults
                    )

                messages.success(request, 'Products imported successfully')
                return redirect('product-list')

            except Exception as e:
                messages.error(request, f'Error importing products: {str(e)}')
                return redirect('product-import')

        else:
            messages.error(request, 'Unsupported file format. Please upload a CSV or Excel file.')
            return redirect('product-import')
