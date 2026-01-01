import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from ai_agent.views import generate_ai_response_rule_based
from ai_agent.models import DashboardContext, ChatSession
from django.contrib.auth.models import User
from django.http import HttpRequest

def test_list_products():
    """
    Test the 'list all products' query handling in the rule-based approach.
    """
    print("Testing 'list all products' query...")
    
    # Create a test user and chat session
    try:
        user, created = User.objects.get_or_create(username='test_user')
        session = ChatSession.objects.create(user=user)
        
        # Create a simple context
        context = DashboardContext.objects.create(
            session=session,
            total_products=5,
            total_resources=10,
            active_products=3,
            completed_products=2,
            current_view="Dashboard"
        )
        
        # Create a mock request
        request = HttpRequest()
        request.user = user
        
        # Test message
        test_message = "list all products"
        
        # Generate a response using the rule-based approach
        print(f"Generating response for message: '{test_message}'")
        response = generate_ai_response_rule_based(test_message, context, request)
        
        print(f"Response: {response}")
        
        # Check if the response contains the expected text
        if "Here are all the products:" in response:
            print("Test passed! The rule-based approach correctly handled the 'list all products' query.")
            return True
        else:
            print("Test failed. The response doesn't contain the expected text.")
            return False
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    test_list_products()