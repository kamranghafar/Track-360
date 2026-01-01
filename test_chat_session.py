import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from ai_agent.models import ChatSession
from django.utils import timezone

# Test creating a ChatSession
def test_create_chat_session():
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )

    # Create a ChatSession
    session = ChatSession.objects.create(
        user=user,
        active=True
    )

    # Print session details
    print(f"Created ChatSession with ID: {session.id}")
    print(f"User: {session.user.username}")
    print(f"Created at: {session.created_at}")
    print(f"Updated at: {session.updated_at}")
    print(f"Active: {session.active}")

    # Verify that updated_at is set
    if session.updated_at:
        print("SUCCESS: updated_at field is set correctly")
    else:
        print("ERROR: updated_at field is not set")

    return session

if __name__ == "__main__":
    test_create_chat_session()
