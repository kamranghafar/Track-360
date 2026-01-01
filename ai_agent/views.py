from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.utils import timezone
import json
import re

from .models import ChatSession, ChatMessage, DashboardContext
from .context_collectors import collect_full_dashboard_context
from dashboard.models import Project, Resource, KPI, KPIRating

# Import LLM integration
try:
    from .llm_integration import generate_llm_response, is_llm_available
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    is_llm_available = lambda: False
    generate_llm_response = lambda *args, **kwargs: "I'm currently operating in basic mode. LLM functionality is not available."

# Import MCP integration
try:
    from .mcp_integration import initialize_mcp, MCP_AVAILABLE
    # Initialize MCP when the module is loaded
    mcp_server = initialize_mcp()
    print(f"MCP initialization status: {'Available' if MCP_AVAILABLE else 'Not Available'}")
except Exception as e:
    print(f"Error importing or initializing MCP integration: {str(e)}")
    MCP_AVAILABLE = False
    initialize_mcp = lambda: None
    mcp_server = None


def generate_ai_response_rule_based(message, context, request):
    """
    Generate a meaningful AI response based on the user's message and available context
    using a rule-based approach with regex pattern matching.

    Args:
        message (str): The user's message
        context (DashboardContext): The dashboard context
        request: The HTTP request

    Returns:
        str: The AI response
    """
    # Convert message to lowercase for easier matching
    message_lower = message.lower()

    # Check if asking to list all products
    if 'list all products' in message_lower or 'show all products' in message_lower or 'what products' in message_lower:
        try:
            # Get all products from the database
            from dashboard.models import Project
            products = Project.objects.all().order_by('name')

            if not products.exists():
                return "There are no products in the database."

            response = "Here are all the products:\n"
            for i, product in enumerate(products, 1):
                status_display = product.get_status_display() if hasattr(product, 'get_status_display') else product.status
                response += f"{i}. {product.name} - Status: {status_display}\n"

            return response
        except Exception as e:
            print(f"Error listing products: {str(e)}")
            return f"I encountered an error while trying to list all products: {str(e)}"

    # Check if asking about regression percentage
    if 'regression percentage' in message_lower or 'regression coverage' in message_lower:
        # Check if asking about a specific project
        regression_match = re.search(r'(?:regression percentage|regression coverage)(?:\s+of\s+|\s+for\s+)(.+?)(?:\s+|$)', message_lower)
        if regression_match:
            project_name = regression_match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            return get_regression_percentage_response(project_name)
        else:
            # If no project specified, provide a general explanation
            return "Regression percentage refers to the proportion of automated regression test cases compared to the total number of automatable test cases for a project. It's a measure of how well the regression testing is automated. To get the regression percentage for a specific project, please specify the project name."

    # Check if asking about smoke coverage
    if 'smoke coverage' in message_lower or 'smoke test' in message_lower:
        # Check if asking about a specific project
        smoke_match = re.search(r'(?:smoke(?:\s+test)?\s+coverage)(?:\s+of\s+|\s+for\s+)(.+?)(?:\s+|$)', message_lower)
        if smoke_match:
            project_name = smoke_match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            return get_smoke_coverage_response(project_name)
        else:
            return get_overall_smoke_coverage_response()

    # Check if asking about project status
    status_match = re.search(r'(?:status|state|progress)(?:\s+of\s+|\s+for\s+)(.+?)(?:\s+|$)', message_lower)
    if status_match:
        project_name = status_match.group(1).strip()
        # Remove "project" or "the project" if included in the extracted name
        project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
        return get_project_status_response(project_name)

    # Check if asking about resources
    resources_match = re.search(r'(?:resources|people|team)(?:\s+(?:assigned|allocated|working)(?:\s+(?:to|on|for))?)?(?:\s+(.+?))?(?:\s+|$)', message_lower)
    if resources_match and resources_match.group(1):
        project_name = resources_match.group(1).strip()
        # Remove "project" or "the project" if included in the extracted name
        project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
        return get_resources_for_project_response(project_name)

    # Check for simple greetings
    if message_lower in ['hi', 'hello', 'hey', 'greetings']:
        return f"Hello! I'm your AI assistant for the dashboard. I can help you with information about projects, resources, regression percentage, smoke coverage, and more. What would you like to know?"

    # If no specific question pattern is matched, provide a general response
    return f"I understand you're asking about: {message}. " \
           f"I can see you're currently viewing {context.current_view} " \
           f"with {context.total_products} total products and {context.total_resources} resources. " \
           f"You can ask me about regression percentage, smoke coverage, project status, or resources assigned to a project."


def generate_ai_response_mcp(message, context, request):
    """
    Generate a meaningful AI response based on the user's message and available context
    using the Model Context Protocol (MCP).

    Args:
        message (str): The user's message
        context (DashboardContext): The dashboard context
        request: The HTTP request

    Returns:
        str: The AI response
    """
    # Use the already initialized MCP server
    global mcp_server
    if mcp_server is None:
        print("MCP server not initialized, initializing now")
        mcp_server = initialize_mcp()

    # Determine which tool to use based on the message
    message_lower = message.lower()
    print(f"Processing MCP response for message: {message_lower}")

    # Check for simple greetings
    if message_lower in ['hi', 'hello', 'hey', 'greetings']:
        return f"Hello! I'm your AI assistant for the dashboard. I can help you with information about projects, resources, regression percentage, smoke coverage, and more. What would you like to know?"

    # Check if asking for dashboard summary
    if 'dashboard summary' in message_lower or 'overview' in message_lower or 'summarize' in message_lower:
        print("Detected dashboard summary request")
        try:
            return mcp_server.get_dashboard_summary()
        except Exception as e:
            print(f"Error getting dashboard summary: {str(e)}")
            # Fall back to a generic summary
            return f"Dashboard Overview: There are {context.total_products} total products and {context.total_resources} resources. {context.active_products} products are active and {context.completed_products} are completed."

    # Check if asking about regression percentage
    if 'regression percentage' in message_lower or 'regression coverage' in message_lower:
        print("Detected regression percentage request")
        # Extract project name using regex
        match = re.search(r'(?:regression percentage|regression coverage)(?:\s+of\s+|\s+for\s+)(.+?)(?:\s+|$)', message_lower)
        if match:
            project_name = match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            print(f"Getting regression percentage for project: {project_name}")
            return mcp_server.get_regression_percentage(project_name)
        else:
            # If no project specified, provide a general explanation
            print("No project specified for regression percentage")
            return "Regression percentage refers to the proportion of automated regression test cases compared to the total number of automatable test cases for a project. It's a measure of how well the regression testing is automated. To get the regression percentage for a specific project, please specify the project name."

    # Check if asking about smoke coverage
    if 'smoke coverage' in message_lower or 'smoke test' in message_lower:
        print("Detected smoke coverage request")
        # Extract project name using regex
        match = re.search(r'(?:smoke(?:\s+test)?\s+coverage)(?:\s+of\s+|\s+for\s+)(.+?)(?:\s+|$)', message_lower)
        if match:
            project_name = match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            print(f"Getting smoke coverage for project: {project_name}")
            return mcp_server.get_smoke_coverage(project_name)
        else:
            # If no project name is specified, get overall smoke coverage
            print("Getting overall smoke coverage")
            return mcp_server.get_smoke_coverage()

    # Check if asking about project status
    if 'status' in message_lower or 'state' in message_lower or 'progress' in message_lower:
        print("Detected project status request")
        # Extract project name using regex
        match = re.search(r'(?:status|state|progress)(?:\s+of\s+|\s+for\s+)(.+?)(?:\s+|$)', message_lower)
        if match:
            project_name = match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            print(f"Getting status for project: {project_name}")
            return mcp_server.get_project_status(project_name)

    # Check if asking about resources assigned to a project
    if 'resources' in message_lower or 'people' in message_lower or 'team' in message_lower:
        print("Detected resources request")
        # Extract project name using regex
        match = re.search(r'(?:resources|people|team)(?:\s+(?:assigned|allocated|working)(?:\s+(?:to|on|for))?)?(?:\s+(.+?))?(?:\s+|$)', message_lower)
        if match and match.group(1):
            project_name = match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            print(f"Getting resources for project: {project_name}")
            return mcp_server.get_project_resources(project_name)

    # Check if asking about projects assigned to a resource
    if 'projects assigned to' in message_lower or 'projects for' in message_lower:
        print("Detected projects by resource request")
        # Extract resource name using regex
        match = re.search(r'projects (?:assigned to|for)\s+(.+?)(?:\s+|$)', message_lower)
        if match:
            resource_name = match.group(1).strip()
            print(f"Getting projects for resource: {resource_name}")
            try:
                return mcp_server.get_project_by_resource(resource_name)
            except Exception as e:
                print(f"Error getting projects by resource: {str(e)}")
                return f"I'm sorry, I couldn't find information about projects assigned to {resource_name}."

    # Check if asking about project trends
    if 'trends' in message_lower or 'trending' in message_lower or 'history' in message_lower:
        print("Detected project trends request")
        # Extract project name using regex
        match = re.search(r'(?:trends|trending|history)(?:\s+for\s+|\s+of\s+)(.+?)(?:\s+|$)', message_lower)
        if match:
            project_name = match.group(1).strip()
            # Remove "project" or "the project" if included
            project_name = re.sub(r'^(?:the\s+)?project\s+', '', project_name)
            print(f"Getting trends for project: {project_name}")
            try:
                return mcp_server.get_project_trends(project_name)
            except Exception as e:
                print(f"Error getting project trends: {str(e)}")
                return f"I'm sorry, I couldn't find trend information for {project_name}."

    # If we couldn't determine a specific tool to use, fall back to the rule-based approach
    print("No specific MCP tool matched, falling back to rule-based approach")
    return generate_ai_response_rule_based(message, context, request)


def generate_ai_response(message, context, request):
    """
    Generate a meaningful AI response based on the user's message and available context.
    This function tries to use MCP first, then falls back to LLM, and finally to a rule-based approach if needed.

    Args:
        message (str): The user's message
        context (DashboardContext): The dashboard context
        request: The HTTP request

    Returns:
        str: The AI response
    """
    print(f"Generating AI response for message: '{message}'")

    # Check if the database is available
    database_available = True
    if hasattr(context, 'applied_filters') and isinstance(context.applied_filters, dict):
        database_available = context.applied_filters.get('database_available', True)

    # Convert message to lowercase for easier matching
    message_lower = message.lower()

    # Special handling for "list all products" query - use rule-based approach directly
    if 'list all products' in message_lower or 'show all products' in message_lower or 'what products' in message_lower:
        print("Detected 'list all products' query, using rule-based approach directly")
        return generate_ai_response_rule_based(message, context, request)

    # If database is not available and this is a database-related question, inform the user
    if not database_available and any(term in message_lower for term in ['project', 'resource', 'regression', 'smoke', 'kpi', 'status']):
        print("Database is not available, providing database error message")
        return "I'm sorry, but I can't access the database at the moment. The database connection is currently unavailable. Please contact your administrator to resolve this issue."

    # Special handling for regression percentage questions
    if 'regression percentage' in message_lower and not 'of' in message_lower and not 'for' in message_lower:
        print("Detected standalone regression percentage question")
        return "Regression percentage refers to the proportion of automated regression test cases compared to the total number of automatable test cases for a project. It's a measure of how well the regression testing is automated. To get the regression percentage for a specific project, please specify the project name."

    # Check if MCP is available
    if MCP_AVAILABLE:
        # Try to use MCP for response generation
        try:
            print("Attempting to generate response using MCP")
            mcp_response = generate_ai_response_mcp(message, context, request)
            print(f"MCP response: '{mcp_response[:50]}...'")

            # Check if the response is the generic fallback
            if "I understand you're asking about:" in mcp_response and "You can ask me about regression percentage" in mcp_response:
                print("MCP returned generic response, trying LLM")
                # If MCP returned a generic response, try LLM
                if is_llm_available():
                    try:
                        llm_response = generate_llm_response(message, context, request)
                        print(f"LLM response: '{llm_response[:50]}...'")
                        return llm_response
                    except Exception as e:
                        print(f"Error using LLM after MCP fallback: {str(e)}")
                        return mcp_response
                else:
                    return mcp_response
            else:
                return mcp_response
        except Exception as e:
            # Log the error
            print(f"Error using MCP for response generation: {str(e)}")
            print("Falling back to LLM or rule-based approach")
    else:
        print("MCP is not available, skipping MCP response generation")
        print("Reason: MCP_AVAILABLE flag is set to False")
        print("Falling back to LLM or rule-based approach")

        # Only show database error if database is actually unavailable
        if not database_available and any(term in message_lower for term in ['project', 'resource', 'regression', 'smoke', 'kpi', 'status']):
            print("Database is not available, providing database error message")
            return "I'm sorry, but I can't access the database at the moment. The database connection is currently unavailable. Please contact your administrator to resolve this issue."

    # Try to use the LLM for response generation
    try:
        # Check if LLM is available
        if is_llm_available():
            print("Attempting to generate response using LLM")
            llm_response = generate_llm_response(message, context, request)
            print(f"LLM response: '{llm_response[:50]}...'")
            return llm_response
        else:
            print("LLM is not available, falling back to rule-based approach")
            rule_based_response = generate_ai_response_rule_based(message, context, request)
            print(f"Rule-based response: '{rule_based_response[:50]}...'")
            return rule_based_response
    except Exception as e:
        # Log the error
        print(f"Error using LLM for response generation: {str(e)}")
        print("Falling back to rule-based approach")
        rule_based_response = generate_ai_response_rule_based(message, context, request)
        print(f"Rule-based response: '{rule_based_response[:50]}...'")
        return rule_based_response


def get_regression_percentage_response(project_name):
    """Get response for regression percentage of a specific project"""
    try:
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
        return f"I encountered an error while retrieving regression percentage for '{project_name}': {str(e)}"


def get_smoke_coverage_response(project_name):
    """Get response for smoke coverage of a specific project"""
    try:
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

    except Exception as e:
        return f"I encountered an error while retrieving smoke coverage for '{project_name}': {str(e)}"


def get_overall_smoke_coverage_response():
    """Get response for overall smoke coverage across all projects"""
    try:
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
        return f"I encountered an error while retrieving overall smoke coverage: {str(e)}"


def get_project_status_response(project_name):
    """Get response for status of a specific project"""
    try:
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
        return f"I encountered an error while retrieving status for '{project_name}': {str(e)}"


def get_resources_for_project_response(project_name):
    """Get response for resources assigned to a specific project"""
    try:
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
        return f"I encountered an error while retrieving resources for '{project_name}': {str(e)}"


@login_required
def chat_view(request):
    """
    Main view for the AI agent chat interface.
    """
    # Get or create an active chat session for the user
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        active=True,
        defaults={'created_at': timezone.now()}
    )

    # If a new session was created, collect the initial context
    if created:
        collect_full_dashboard_context(session, request)

    # Get the messages for this session
    messages = ChatMessage.objects.filter(session=session)

    context = {
        'session': session,
        'messages': messages,
        'host': request.get_host(),  # Add host information to avoid hardcoded localhost
    }

    return render(request, 'ai_agent/chat.html', context)


@login_required
def chat_embed_view(request):
    """
    Embedded view for the AI agent chat interface (used in the chat bubble).
    """
    # Get or create an active chat session for the user
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        active=True,
        defaults={'created_at': timezone.now()}
    )

    # If a new session was created, collect the initial context
    if created:
        collect_full_dashboard_context(session, request)

    # Get the messages for this session
    messages = ChatMessage.objects.filter(session=session)

    context = {
        'session': session,
        'messages': messages,
        'host': request.get_host(),  # Add host information to avoid hardcoded localhost
    }

    response = render(request, 'ai_agent/chat_embed.html', context)

    # Explicitly remove X-Frame-Options to allow embedding in iframes
    if 'X-Frame-Options' in response:
        del response['X-Frame-Options']

    # Add Content-Security-Policy header to allow embedding
    response['Content-Security-Policy'] = "frame-ancestors 'self' *"

    return response


@login_required
@require_POST
def send_message(request):
    """
    API endpoint for sending a message to the AI agent.
    """
    # Get the active session
    session = get_object_or_404(ChatSession, user=request.user, active=True)

    # Get the message content from the request
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not message_content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # Create a new user message
    user_message = ChatMessage.objects.create(
        session=session,
        message_type='user',
        content=message_content
    )

    # Update the context with the latest dashboard state
    context = collect_full_dashboard_context(session, request)

    # Parse the user's question and generate a meaningful response
    ai_response = generate_ai_response(message_content, context, request)

    # Create a new AI message
    ai_message = ChatMessage.objects.create(
        session=session,
        message_type='ai',
        content=ai_response
    )

    # Return both messages
    return JsonResponse({
        'user_message': {
            'id': user_message.id,
            'content': user_message.content,
            'timestamp': user_message.timestamp.isoformat()
        },
        'ai_message': {
            'id': ai_message.id,
            'content': ai_message.content,
            'timestamp': ai_message.timestamp.isoformat()
        }
    })


@login_required
@require_POST
def end_chat(request):
    """
    API endpoint for ending the current chat session.
    """
    # Get the active session
    session = get_object_or_404(ChatSession, user=request.user, active=True)

    # Mark the session as inactive
    session.active = False
    session.save()

    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def new_chat(request):
    """
    API endpoint for starting a new chat session.
    """
    # Mark any existing active sessions as inactive
    ChatSession.objects.filter(user=request.user, active=True).update(active=False)

    # Create a new session
    session = ChatSession.objects.create(
        user=request.user,
        active=True
    )

    # Collect the initial context
    collect_full_dashboard_context(session, request)

    return JsonResponse({'status': 'success', 'session_id': session.id})


class ChatHistoryView(LoginRequiredMixin, ListView):
    """
    View for displaying chat history.
    """
    model = ChatSession
    template_name = 'ai_agent/chat_history.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')
