"""
MCP integration module for the AI agent.
This module provides functions for initializing the MCP server and defining tools
for generating responses using the Model Context Protocol.
"""

import os
import sys
import logging
import importlib.metadata
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the python-sdk to the Python path
sdk_path = Path(__file__).parent.parent / "python-sdk" / "python-sdk-main"
if sdk_path.exists():
    sys.path.append(str(sdk_path))
    sys.path.append(str(sdk_path / "src"))
    logger.info(f"Added Python SDK path: {sdk_path}")
else:
    logger.warning(f"Python SDK path not found: {sdk_path}")

# Mock the version function to handle missing metadata
original_version = importlib.metadata.version

def mock_version(name):
    if name == "mcp":
        return "0.1.0"  # Return a dummy version
    return original_version(name)

# Apply the monkey patch
importlib.metadata.version = mock_version

# Flag to track if MCP is available
MCP_AVAILABLE = False

# Initialize MCP server variable
mcp_server = None

try:
    # Try to import required dependencies
    import jsonschema
    import httpx_sse
    import pydantic_settings
    import starlette
    import sse_starlette

    # Now try to import FastMCP
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
    logger.info("Successfully imported FastMCP and all required dependencies")
except ImportError as e:
    logger.warning(f"Failed to import FastMCP or its dependencies: {str(e)}")
    logger.warning("To install required dependencies, run: python install_mcp_dependencies.py")
    # Create a dummy FastMCP class for fallback
    class FastMCP:
        def __init__(self, name):
            self.name = name
            logger.warning(f"Using dummy MCP implementation for {name}")

        def tool(self):
            def decorator(func):
                return func
            return decorator

# Try to import dashboard models with error handling
try:
    from dashboard.models import Project, Resource, KPI, KPIRating, Quarter, Rock, UserAction
    logger.info("Successfully imported dashboard models")

    # Verify database connection by trying to access the models
    try:
        # Try to get the count of projects to verify database connection
        project_count = Project.objects.count()
        resource_count = Resource.objects.count()
        logger.info(f"Database connection verified. Found {project_count} projects and {resource_count} resources.")
    except Exception as db_error:
        logger.error(f"Failed to access database: {str(db_error)}")
        logger.error("Database connection failed. MCP will not be able to access database models.")
        MCP_AVAILABLE = False
except ImportError as e:
    logger.error(f"Failed to import dashboard models: {str(e)}")
    MCP_AVAILABLE = False

def initialize_mcp():
    """
    Initialize the MCP server with tools for generating responses.
    If MCP is not available, returns a dummy MCP server.

    Returns:
        FastMCP: An initialized MCP server with tools
    """
    global mcp_server, MCP_AVAILABLE

    # If MCP is not available, return early
    if not MCP_AVAILABLE:
        logger.warning("MCP is not available, returning dummy MCP server")
        dummy_server = FastMCP("Dashboard AI Assistant (Dummy)")

        # Add a special tool to inform users about the database connection issue
        @dummy_server.tool()
        def get_database_status():
            """Get the status of the database connection"""
            return "The database connection is currently unavailable. The AI assistant is operating in limited mode and cannot access project or resource information. Please contact your administrator to resolve this issue."

        return dummy_server

    # If the server is already initialized, return it
    if mcp_server is not None:
        logger.info("Using existing MCP server")
        return mcp_server

    # Create the MCP server
    logger.info("Initializing new MCP server")
    mcp_server = FastMCP("Dashboard AI Assistant")

    # Register tools

    @mcp_server.tool()
    def get_regression_percentage(project_name: str) -> str:
        """
        Get the regression percentage for a specific project.

        Args:
            project_name: The name of the project

        Returns:
            str: A response with the regression percentage information
        """
        try:
            # Check if Project model is available
            if 'Project' not in globals():
                logger.error("Project model is not available")
                return f"I'm sorry, but I can't access project information at the moment. The database models are not available."

            # Try to find the project by name (case-insensitive)
            project = Project.objects.filter(name__icontains=project_name).first()

            if not project:
                return f"I couldn't find a project named '{project_name}'. Please check the project name and try again."

            # Check if regression coverage is available
            if project.regression_coverage is not None:
                return f"The regression coverage for {project.name} is {project.regression_coverage}%."

            # If regression_coverage is not available, calculate it from other fields
            if project.total_automatable_test_cases and project.total_automatable_test_cases > 0 and project.total_automated_test_cases is not None:
                regression_percentage = (project.total_automated_test_cases / project.total_automatable_test_cases) * 100
                return f"The regression percentage for {project.name} is {regression_percentage:.2f}% ({project.total_automated_test_cases} out of {project.total_automatable_test_cases} test cases automated)."

            # If we can't calculate it, check the status
            if project.regression_automation_status:
                return f"The regression automation status for {project.name} is '{project.get_regression_automation_status_display()}'. No specific percentage is available."

            return f"I couldn't find regression percentage information for {project.name}."

        except Exception as e:
            logger.error(f"Error in get_regression_percentage: {str(e)}")
            return f"I encountered an error while retrieving regression percentage for '{project_name}': {str(e)}"

    @mcp_server.tool()
    def get_smoke_coverage(project_name: str = None) -> str:
        """
        Get the smoke coverage for a specific project or overall.

        Args:
            project_name: The name of the project (optional)

        Returns:
            str: A response with the smoke coverage information
        """
        try:
            # Check if Project model is available
            if 'Project' not in globals():
                logger.error("Project model is not available")
                return f"I'm sorry, but I can't access project information at the moment. The database models are not available."

            if project_name:
                # Try to find the project by name (case-insensitive)
                project = Project.objects.filter(name__icontains=project_name).first()

                if not project:
                    return f"I couldn't find a project named '{project_name}'. Please check the project name and try again."

                # Check if smoke coverage is available
                if project.smoke_coverage is not None:
                    return f"The smoke test coverage for {project.name} is {project.smoke_coverage}%."

                # If smoke_coverage is not available, calculate it from other fields
                if project.total_automatable_smoke_test_cases and project.total_automatable_smoke_test_cases > 0 and project.total_automated_smoke_test_cases is not None:
                    smoke_percentage = (project.total_automated_smoke_test_cases / project.total_automatable_smoke_test_cases) * 100
                    return f"The smoke test coverage for {project.name} is {smoke_percentage:.2f}% ({project.total_automated_smoke_test_cases} out of {project.total_automatable_smoke_test_cases} smoke test cases automated)."

                # If we can't calculate it, check the status
                if project.smoke_automation_status:
                    return f"The smoke automation status for {project.name} is '{project.get_smoke_automation_status_display()}'. No specific coverage percentage is available."

                return f"I couldn't find smoke coverage information for {project.name}."
            else:
                # Get projects with smoke coverage data
                projects_with_smoke_data = Project.objects.filter(
                    total_automatable_smoke_test_cases__gt=0,
                    total_automated_smoke_test_cases__isnull=False
                )

                if not projects_with_smoke_data:
                    return "I couldn't find smoke coverage information for any projects."

                # Calculate overall smoke coverage
                total_automatable = sum(p.total_automatable_smoke_test_cases for p in projects_with_smoke_data)
                total_automated = sum(p.total_automated_smoke_test_cases for p in projects_with_smoke_data)

                if total_automatable > 0:
                    overall_percentage = (total_automated / total_automatable) * 100
                    return f"The overall smoke test coverage across all projects is {overall_percentage:.2f}% ({total_automated} out of {total_automatable} smoke test cases automated)."

                return "I couldn't calculate the overall smoke coverage because the total number of automatable smoke test cases is zero or not available."

        except Exception as e:
            logger.error(f"Error in get_smoke_coverage: {str(e)}")
            return f"I encountered an error while retrieving smoke coverage: {str(e)}"

    @mcp_server.tool()
    def get_project_status(project_name: str) -> str:
        """
        Get the status of a specific project.

        Args:
            project_name: The name of the project

        Returns:
            str: A response with the project status information
        """
        try:
            # Check if Project model is available
            if 'Project' not in globals():
                logger.error("Project model is not available")
                return f"I'm sorry, but I can't access project information at the moment. The database models are not available."

            # Try to find the project by name (case-insensitive)
            project = Project.objects.filter(name__icontains=project_name).first()

            if not project:
                return f"I couldn't find a project named '{project_name}'. Please check the project name and try again."

            response = f"Project: {project.name}\n"
            response += f"Status: {project.get_status_display()}\n"

            if project.start_date:
                response += f"Start Date: {project.start_date}\n"

            if project.end_date:
                response += f"End Date: {project.end_date}\n"
                if project.is_overdue:
                    response += "This project is overdue.\n"

            if project.smoke_automation_status:
                response += f"Smoke Automation Status: {project.get_smoke_automation_status_display()}\n"

            if project.regression_automation_status:
                response += f"Regression Automation Status: {project.get_regression_automation_status_display()}\n"

            return response

        except Exception as e:
            logger.error(f"Error in get_project_status: {str(e)}")
            return f"I encountered an error while retrieving status for '{project_name}': {str(e)}"

    @mcp_server.tool()
    def get_project_resources(project_name: str) -> str:
        """
        Get the resources assigned to a specific project.

        Args:
            project_name: The name of the project

        Returns:
            str: A response with the project resources information
        """
        try:
            # Check if Project model is available
            if 'Project' not in globals() or 'Resource' not in globals():
                logger.error("Project or Resource model is not available")
                return f"I'm sorry, but I can't access project or resource information at the moment. The database models are not available."

            # Try to find the project by name (case-insensitive)
            project = Project.objects.filter(name__icontains=project_name).first()

            if not project:
                return f"I couldn't find a project named '{project_name}'. Please check the project name and try again."

            # Get resources assigned to this project
            resources = project.resources.all()

            if not resources:
                return f"There are no resources assigned to {project.name}."

            response = f"Resources assigned to {project.name}:\n"

            for i, resource in enumerate(resources, 1):
                response += f"{i}. {resource.name}"
                if resource.role:
                    response += f" - {resource.role}"
                if resource.skill:
                    response += f" ({resource.get_skill_display()})"
                response += "\n"

            return response

        except Exception as e:
            logger.error(f"Error in get_project_resources: {str(e)}")
            return f"I encountered an error while retrieving resources for '{project_name}': {str(e)}"

    @mcp_server.tool()
    def get_kpi_info(kpi_name: str = None, resource_name: str = None) -> str:
        """
        Get information about KPIs, optionally filtered by KPI name or resource name.

        Args:
            kpi_name: The name of the KPI (optional)
            resource_name: The name of the resource (optional)

        Returns:
            str: A response with KPI information
        """
        try:
            # Check if KPI and Resource models are available
            if 'KPI' not in globals() or 'Resource' not in globals() or 'KPIRating' not in globals():
                logger.error("KPI, Resource, or KPIRating model is not available")
                return f"I'm sorry, but I can't access KPI information at the moment. The database models are not available."

            # Build the query based on provided filters
            query = KPI.objects.all()

            if kpi_name:
                query = query.filter(name__icontains=kpi_name)

            if resource_name:
                # Find resources matching the name
                resources = Resource.objects.filter(name__icontains=resource_name)
                if not resources:
                    return f"I couldn't find a resource named '{resource_name}'. Please check the resource name and try again."

                # Filter KPIs by these resources
                query = query.filter(resource__in=resources)

            # Execute the query
            kpis = query.order_by('name')

            if not kpis:
                filters = []
                if kpi_name:
                    filters.append(f"KPI name containing '{kpi_name}'")
                if resource_name:
                    filters.append(f"resource named '{resource_name}'")

                filter_text = " and ".join(filters)
                return f"I couldn't find any KPIs matching {filter_text}." if filters else "No KPIs found in the system."

            # Build the response
            if len(kpis) == 1:
                kpi = kpis[0]
                response = f"KPI: {kpi.name}\n"
                response += f"Description: {kpi.description}\n"
                response += f"Resource: {kpi.resource.name}\n"

                # Get the latest rating
                latest_rating = KPIRating.objects.filter(kpi=kpi).order_by('-year', '-month').first()

                if latest_rating:
                    response += f"Latest Rating: {latest_rating.rating}/5 (Month: {latest_rating.month}, Year: {latest_rating.year})\n"
                    if latest_rating.remarks:
                        response += f"Remarks: {latest_rating.remarks}\n"
                else:
                    response += "No ratings available for this KPI yet.\n"

                return response
            else:
                response = f"Found {len(kpis)} KPIs:\n"

                for i, kpi in enumerate(kpis, 1):
                    response += f"{i}. {kpi.name} - Resource: {kpi.resource.name}\n"

                response += "\nFor detailed information about a specific KPI, please specify the KPI name."
                return response

        except Exception as e:
            logger.error(f"Error in get_kpi_info: {str(e)}")
            return f"I encountered an error while retrieving KPI information: {str(e)}"

    @mcp_server.tool()
    def get_kpi_ratings(kpi_name: str, months: int = 3) -> str:
        """
        Get the ratings history for a specific KPI.

        Args:
            kpi_name: The name of the KPI
            months: Number of months of history to retrieve (default: 3)

        Returns:
            str: A response with the KPI ratings history
        """
        try:
            # Check if KPI and KPIRating models are available
            if 'KPI' not in globals() or 'KPIRating' not in globals():
                logger.error("KPI or KPIRating model is not available")
                return f"I'm sorry, but I can't access KPI ratings information at the moment. The database models are not available."

            # Find the KPI by name
            kpi = KPI.objects.filter(name__icontains=kpi_name).first()

            if not kpi:
                return f"I couldn't find a KPI named '{kpi_name}'. Please check the KPI name and try again."

            # Get ratings for this KPI, ordered by date (most recent first)
            ratings = KPIRating.objects.filter(kpi=kpi).order_by('-year', '-month')[:months]

            if not ratings:
                return f"No ratings found for KPI '{kpi.name}' in the last {months} months."

            response = f"Rating history for KPI '{kpi.name}' (Resource: {kpi.resource.name}):\n\n"

            for rating in ratings:
                response += f"Month: {rating.month}/{rating.year} - Rating: {rating.rating}/5\n"
                if rating.remarks:
                    response += f"Remarks: {rating.remarks}\n"
                response += "\n"

            return response

        except Exception as e:
            logger.error(f"Error in get_kpi_ratings: {str(e)}")
            return f"I encountered an error while retrieving KPI ratings: {str(e)}"

    @mcp_server.tool()
    def get_quarter_info(year: int = None, quarter: int = None) -> str:
        """
        Get information about quarters, optionally filtered by year and quarter number.

        Args:
            year: The year (optional)
            quarter: The quarter number (1-4) (optional)

        Returns:
            str: A response with quarter information
        """
        try:
            # Check if Quarter model is available
            if 'Quarter' not in globals():
                logger.error("Quarter model is not available")
                return f"I'm sorry, but I can't access quarter information at the moment. The database models are not available."

            # Build the query based on provided filters
            query = Quarter.objects.all()

            if year:
                query = query.filter(year=year)

            if quarter:
                query = query.filter(quarter=quarter)

            # Execute the query, ordered by most recent first
            quarters = query.order_by('-year', '-quarter')

            if not quarters:
                filters = []
                if year:
                    filters.append(f"year {year}")
                if quarter:
                    filters.append(f"quarter {quarter}")

                filter_text = " and ".join(filters)
                return f"I couldn't find any quarters matching {filter_text}." if filters else "No quarters found in the system."

            # If we have a specific quarter, show detailed information
            if len(quarters) == 1:
                q = quarters[0]
                response = f"Quarter: Q{q.quarter} {q.year}\n"
                response += f"Theme: {q.theme}\n"
                response += f"Status: {q.get_status_display()}\n"

                if q.start_date:
                    response += f"Start Date: {q.start_date}\n"
                if q.end_date:
                    response += f"End Date: {q.end_date}\n"

                # Get statistics
                stats = q.get_statistics()
                if stats:
                    response += "\nStatistics:\n"
                    response += f"Total Targets: {stats.get('total_targets', 'N/A')}\n"
                    response += f"Completed Targets: {stats.get('completed_targets', 'N/A')}\n"
                    response += f"Completion Rate: {stats.get('completion_rate', 'N/A')}%\n"

                return response
            else:
                # Show a list of quarters
                response = f"Found {len(quarters)} quarters:\n\n"

                for q in quarters:
                    response += f"Q{q.quarter} {q.year} - {q.theme} - Status: {q.get_status_display()}\n"

                response += "\nFor detailed information about a specific quarter, please specify both year and quarter number."
                return response

        except Exception as e:
            logger.error(f"Error in get_quarter_info: {str(e)}")
            return f"I encountered an error while retrieving quarter information: {str(e)}"

    @mcp_server.tool()
    def get_rocks(status: str = None, quarter_year: int = None, quarter_number: int = None) -> str:
        """
        Get information about rocks (key initiatives), optionally filtered by status and quarter.

        Args:
            status: The status of rocks to filter by (optional, e.g., 'not_started', 'in_progress', 'completed')
            quarter_year: The year of the quarter to filter by (optional)
            quarter_number: The quarter number (1-4) to filter by (optional)

        Returns:
            str: A response with rocks information
        """
        try:
            # Check if Rock and Quarter models are available
            if 'Rock' not in globals() or 'Quarter' not in globals():
                logger.error("Rock or Quarter model is not available")
                return f"I'm sorry, but I can't access rocks information at the moment. The database models are not available."

            # Build the query based on provided filters
            query = Rock.objects.all()

            if status:
                query = query.filter(status=status)

            if quarter_year and quarter_number:
                # Find the quarter
                quarter = Quarter.objects.filter(year=quarter_year, quarter=quarter_number).first()
                if quarter:
                    query = query.filter(quarter=quarter)
                else:
                    return f"I couldn't find quarter Q{quarter_number} {quarter_year}. Please check the quarter information and try again."

            # Execute the query, ordered by priority
            rocks = query.order_by('priority')

            if not rocks:
                filters = []
                if status:
                    query_status = dict(Rock.STATUS_CHOICES).get(status, status)
                    filters.append(f"status '{query_status}'")
                if quarter_year and quarter_number:
                    filters.append(f"quarter Q{quarter_number} {quarter_year}")

                filter_text = " and ".join(filters)
                return f"I couldn't find any rocks matching {filter_text}." if filters else "No rocks found in the system."

            # Build the response
            response = f"Found {len(rocks)} rocks:\n\n"

            for i, rock in enumerate(rocks, 1):
                response += f"{i}. {rock.name} - Priority: {rock.priority}\n"
                response += f"   Status: {rock.get_status_display()}\n"
                response += f"   Quarter: Q{rock.quarter.quarter} {rock.quarter.year}\n"

                if rock.start_date:
                    response += f"   Start Date: {rock.start_date}\n"
                if rock.completion_date:
                    response += f"   Completion Date: {rock.completion_date}\n"
                elif rock.target_completion_date:
                    response += f"   Target Completion Date: {rock.target_completion_date}\n"
                    if rock.is_overdue():
                        response += f"   This rock is overdue.\n"

                response += "\n"

            return response

        except Exception as e:
            logger.error(f"Error in get_rocks: {str(e)}")
            return f"I encountered an error while retrieving rocks information: {str(e)}"

    @mcp_server.tool()
    def get_user_activity(username: str = None, action_type: str = None, limit: int = 10) -> str:
        """
        Get information about user activities, optionally filtered by username and action type.

        Args:
            username: The username to filter by (optional)
            action_type: The type of action to filter by (optional)
            limit: Maximum number of activities to return (default: 10)

        Returns:
            str: A response with user activity information
        """
        try:
            # Check if UserAction model is available
            if 'UserAction' not in globals():
                logger.error("UserAction model is not available")
                return f"I'm sorry, but I can't access user activity information at the moment. The database models are not available."

            # Build the query based on provided filters
            query = UserAction.objects.all()

            if username:
                query = query.filter(user__username__icontains=username)

            if action_type:
                query = query.filter(action_type__icontains=action_type)

            # Execute the query, ordered by most recent first
            actions = query.order_by('-timestamp')[:limit]

            if not actions:
                filters = []
                if username:
                    filters.append(f"username containing '{username}'")
                if action_type:
                    filters.append(f"action type containing '{action_type}'")

                filter_text = " and ".join(filters)
                return f"I couldn't find any user activities matching {filter_text}." if filters else "No user activities found in the system."

            # Build the response
            response = f"Recent user activities (showing {len(actions)} of {query.count()}):\n\n"

            for i, action in enumerate(actions, 1):
                response += f"{i}. User: {action.user.username}\n"
                response += f"   Action: {action.action_type}\n"
                response += f"   Time: {action.timestamp}\n"
                if action.details:
                    response += f"   Details: {action.details}\n"
                response += "\n"

            return response

        except Exception as e:
            logger.error(f"Error in get_user_activity: {str(e)}")
            return f"I encountered an error while retrieving user activities: {str(e)}"

    @mcp_server.tool()
    def get_dashboard_visualization_data(chart_name: str = None) -> str:
        """
        Get data for dashboard visualizations, optionally filtered by chart name.

        Args:
            chart_name: The name of the chart to get data for (optional)
                        Valid options: 'products_by_status', 'resources_by_product_count', 
                        'automation_backlog', 'smoke_coverage', 'kpi_ratings_over_time'

        Returns:
            str: A response with visualization data
        """
        try:
            # Check if required models are available
            required_models = ['Project', 'Resource', 'KPI', 'KPIRating']
            missing_models = [model for model in required_models if model not in globals()]
            if missing_models:
                logger.error(f"Missing required models: {', '.join(missing_models)}")
                return f"I'm sorry, but I can't access visualization data at the moment. The following database models are not available: {', '.join(missing_models)}"

            # Define available charts
            available_charts = [
                'products_by_status', 
                'resources_by_product_count', 
                'automation_backlog', 
                'smoke_coverage', 
                'kpi_ratings_over_time'
            ]

            # If no chart specified, list available charts
            if not chart_name:
                response = "Available dashboard visualizations:\n\n"
                for i, chart in enumerate(available_charts, 1):
                    response += f"{i}. {chart}\n"
                response += "\nFor data about a specific chart, please specify the chart name."
                return response

            # Check if the requested chart exists
            if chart_name not in available_charts:
                return f"Chart '{chart_name}' not found. Available charts are: {', '.join(available_charts)}"

            # Get data for the requested chart
            if chart_name == 'products_by_status':
                # Count projects by status
                statuses = dict(Project.STATUS_CHOICES)
                counts = {}

                for status_code, status_name in statuses.items():
                    counts[status_name] = Project.objects.filter(status=status_code).count()

                response = "Products by Status:\n\n"
                for status, count in counts.items():
                    response += f"{status}: {count}\n"

                return response

            elif chart_name == 'resources_by_product_count':
                # Get resources with their project counts
                resources = Resource.objects.all()

                if not resources:
                    return "No resources found in the system."

                response = "Resources by Product Count:\n\n"

                for resource in resources:
                    project_count = resource.project_set.count()
                    response += f"{resource.name}: {project_count} products\n"

                return response

            elif chart_name == 'automation_backlog':
                # Calculate automation backlog
                total_automatable = 0
                total_automated = 0

                for project in Project.objects.all():
                    if project.total_automatable_test_cases:
                        total_automatable += project.total_automatable_test_cases
                    if project.total_automated_test_cases:
                        total_automated += project.total_automated_test_cases

                backlog = total_automatable - total_automated

                response = "Automation Backlog:\n\n"
                response += f"Total Automatable Test Cases: {total_automatable}\n"
                response += f"Total Automated Test Cases: {total_automated}\n"
                response += f"Automation Backlog: {backlog} test cases\n"

                if total_automatable > 0:
                    automation_percentage = (total_automated / total_automatable) * 100
                    response += f"Automation Coverage: {automation_percentage:.2f}%\n"

                return response

            elif chart_name == 'smoke_coverage':
                # Calculate smoke test coverage
                projects_with_smoke_data = Project.objects.filter(
                    total_automatable_smoke_test_cases__gt=0,
                    total_automated_smoke_test_cases__isnull=False
                )

                if not projects_with_smoke_data:
                    return "No projects with smoke test data found."

                response = "Smoke Test Coverage by Project:\n\n"

                for project in projects_with_smoke_data:
                    coverage = (project.total_automated_smoke_test_cases / project.total_automatable_smoke_test_cases) * 100
                    response += f"{project.name}: {coverage:.2f}% ({project.total_automated_smoke_test_cases}/{project.total_automatable_smoke_test_cases})\n"

                # Calculate overall coverage
                total_automatable = sum(p.total_automatable_smoke_test_cases for p in projects_with_smoke_data)
                total_automated = sum(p.total_automated_smoke_test_cases for p in projects_with_smoke_data)

                if total_automatable > 0:
                    overall_coverage = (total_automated / total_automatable) * 100
                    response += f"\nOverall Smoke Test Coverage: {overall_coverage:.2f}% ({total_automated}/{total_automatable})\n"

                return response

            elif chart_name == 'kpi_ratings_over_time':
                # Get KPI ratings over time
                ratings = KPIRating.objects.all().order_by('-year', '-month')[:50]  # Limit to 50 most recent

                if not ratings:
                    return "No KPI ratings found in the system."

                # Group by KPI
                kpi_ratings = {}

                for rating in ratings:
                    kpi_name = rating.kpi.name
                    if kpi_name not in kpi_ratings:
                        kpi_ratings[kpi_name] = []

                    kpi_ratings[kpi_name].append({
                        'month': rating.month,
                        'year': rating.year,
                        'rating': rating.rating
                    })

                response = "KPI Ratings Over Time:\n\n"

                for kpi_name, ratings_list in kpi_ratings.items():
                    response += f"{kpi_name}:\n"

                    # Show up to 5 most recent ratings
                    for i, rating in enumerate(ratings_list[:5]):
                        response += f"  {rating['month']}/{rating['year']}: {rating['rating']}/5\n"

                    if len(ratings_list) > 5:
                        response += f"  ... and {len(ratings_list) - 5} more\n"

                    response += "\n"

                return response

            return f"Data for chart '{chart_name}' is not available."

        except Exception as e:
            logger.error(f"Error in get_dashboard_visualization_data: {str(e)}")
            return f"I encountered an error while retrieving visualization data: {str(e)}"

    return mcp_server
