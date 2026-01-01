"""
Test script to verify that the AI assistant handles the case when MCP is not available but the database is.
This script simulates a situation where MCP is not available and checks if the AI assistant
provides appropriate responses.
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

def test_mcp_unavailable():
    """Test that the AI assistant handles the case when MCP is not available but the database is."""
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
    
    print("Testing AI responses with MCP unavailable but database available...\n")
    
    # Mock MCP_AVAILABLE to be False
    with patch('ai_agent.views.MCP_AVAILABLE', False):
        for question in questions:
            print(f"Question: {question}")
            response = generate_ai_response(question, context, request)
            print(f"Response: {response}\n")
    
    print("Test completed.")

if __name__ == "__main__":
    test_mcp_unavailable()