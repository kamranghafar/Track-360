import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Import the necessary modules
from ai_agent.views import generate_ai_response
from ai_agent.models import ChatSession, DashboardContext

def test_ai_response():
    """Test the AI response generation for various questions."""
    # Create a test user
    user, created = User.objects.get_or_create(username='testuser')
    
    # Create a test session
    session, created = ChatSession.objects.get_or_create(
        user=user,
        defaults={'active': True}
    )
    
    # Create a test context
    context, created = DashboardContext.objects.get_or_create(
        session=session,
        defaults={
            'total_products': 35,
            'total_resources': 41,
            'active_products': 20,
            'completed_products': 15,
            'current_view': 'Dashboard'
        }
    )
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    
    # Test questions
    questions = [
        "what is regression percentage?",
        "hi",
        "what is regression percentage of Project A?",
        "what is smoke coverage?",
        "what is the status of Project B?"
    ]
    
    print("Testing AI responses...\n")
    
    for question in questions:
        print(f"Question: {question}")
        response = generate_ai_response(question, context, request)
        print(f"Response: {response}\n")
        
    print("Test completed.")

if __name__ == "__main__":
    test_ai_response()