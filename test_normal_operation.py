"""
Test script to verify that the AI assistant works correctly when both the database and MCP are available.
This script simulates the normal operation of the AI assistant and checks if it provides appropriate responses.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Import the necessary modules
from ai_agent.views import generate_ai_response
from ai_agent.models import ChatSession, DashboardContext

def test_normal_operation():
    """Test that the AI assistant works correctly when both the database and MCP are available."""
    # Create a test user
    user, created = User.objects.get_or_create(username='testuser')
    
    # Create a test session
    session, created = ChatSession.objects.get_or_create(
        user=user,
        defaults={'active': True}
    )
    
    # Create a test context with database_available=True
    context = DashboardContext(
        session=session,
        total_products=35,
        total_resources=41,
        active_products=20,
        completed_products=15,
        current_view='Dashboard'
    )
    context.applied_filters = {'database_available': True}
    
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
        "what is the status of Project B?",
        "how many resources do we have?"
    ]
    
    print("Testing AI responses with both database and MCP available...\n")
    
    # Mock MCP_AVAILABLE to be True
    with patch('ai_agent.views.MCP_AVAILABLE', True):
        for question in questions:
            print(f"Question: {question}")
            response = generate_ai_response(question, context, request)
            print(f"Response: {response}\n")
    
    print("Test completed.")

if __name__ == "__main__":
    test_normal_operation()