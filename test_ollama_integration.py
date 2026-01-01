import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from ai_agent.llm_integration import generate_ollama_response, OLLAMA_AVAILABLE
from ai_agent.models import DashboardContext, ChatSession
from django.contrib.auth.models import User

def test_ollama_integration():
    """
    Test the Ollama integration by generating a response to a test message.
    """
    print("Testing Ollama integration...")
    
    # Check if Ollama is available
    if not OLLAMA_AVAILABLE:
        print("Ollama is not available. Please make sure Ollama is installed and running.")
        return False
    
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
        
        # Test message
        test_message = "Tell me about the products in the dashboard"
        
        # Generate a response
        print(f"Generating response for message: '{test_message}'")
        response = generate_ollama_response(test_message, context)
        
        if response:
            print("Ollama integration test successful!")
            print(f"Response: {response}")
            return True
        else:
            print("Ollama integration test failed. No response was generated.")
            return False
            
    except Exception as e:
        print(f"Error during Ollama integration test: {str(e)}")
        return False

if __name__ == "__main__":
    test_ollama_integration()