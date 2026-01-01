"""
Simple test script for the rule-based AI response generation.
This script doesn't rely on Django's ORM and can be run directly.
"""

import re
from types import SimpleNamespace

# Mock the necessary functions and classes
def get_regression_percentage_response(project_name):
    print(f"Debug: get_regression_percentage_response called with project_name = '{project_name}'")
    return f"The regression percentage for {project_name} is 75%."

def get_smoke_coverage_response(project_name):
    print(f"Debug: get_smoke_coverage_response called with project_name = '{project_name}'")
    return f"The smoke test coverage for {project_name} is 80%."

def get_overall_smoke_coverage_response():
    print(f"Debug: get_overall_smoke_coverage_response called")
    return "The overall smoke test coverage across all projects is 65%."

def get_project_status_response(project_name):
    print(f"Debug: get_project_status_response called with project_name = '{project_name}'")
    return f"Project: {project_name}\nStatus: In Progress\nStart Date: 2023-01-01\nEnd Date: 2023-12-31"

def get_resources_for_project_response(project_name):
    print(f"Debug: get_resources_for_project_response called with project_name = '{project_name}'")
    return f"Resources assigned to {project_name}:\n1. John Doe - Developer\n2. Jane Smith - QA Engineer"

def extract_project_name(text):
    """
    Extract the project name from the text, handling cases where the project name
    might contain the word 'project'.
    """
    # If the text is just 'project', return it with the original capitalization
    if text.lower() == 'project':
        return 'Project'

    # If the text is 'project X', return 'Project X' with proper capitalization
    match = re.match(r'^project\s+([a-z0-9].*)$', text)
    if match:
        letter = match.group(1)
        return f"Project {letter.upper()}"

    # Otherwise, return the original text with first letter capitalized
    return text.capitalize()

def generate_ai_response_rule_based(message, context):
    """
    Generate a meaningful AI response based on the user's message and available context
    using a rule-based approach with regex pattern matching.
    """
    # Convert message to lowercase for easier matching
    message_lower = message.lower()
    print(f"Debug: Lowercase message: '{message_lower}'")

    # Check if asking about regression percentage
    if 'regression percentage' in message_lower or 'regression coverage' in message_lower:
        # Check if asking about a specific project
        # Match "regression percentage of X" or "regression coverage of X"
        # The regex pattern captures everything after "of" or "for" until the end of the string or a space
        regression_match = re.search(r'(?:regression percentage|regression coverage)(?:\s+of\s+|\s+for\s+)(project\s+[a-z0-9].*?)(?:\s+|$|\.|\?)', message_lower)
        if regression_match:
            project_name = regression_match.group(1).strip()
            print(f"Debug: Extracted project name from regression question: '{project_name}'")
            # Extract the project name, handling cases where it might contain the word 'project'
            project_name = extract_project_name(project_name)
            print(f"Debug: After extraction: '{project_name}'")
            return get_regression_percentage_response(project_name)
        else:
            # If no project specified, provide a general explanation
            return "Regression percentage refers to the proportion of automated regression test cases compared to the total number of automatable test cases for a project. It's a measure of how well the regression testing is automated. To get the regression percentage for a specific project, please specify the project name."

    # Check if asking about smoke coverage
    if 'smoke coverage' in message_lower or 'smoke test' in message_lower:
        # Check if asking about a specific project
        # Match "smoke coverage of X" or "smoke test coverage of X"
        smoke_match = re.search(r'(?:smoke(?:\s+test)?\s+coverage)(?:\s+of\s+|\s+for\s+)(project\s+[a-z0-9].*?)(?:\s+|$|\.|\?)', message_lower)
        if smoke_match:
            project_name = smoke_match.group(1).strip()
            # Extract the project name, handling cases where it might contain the word 'project'
            project_name = extract_project_name(project_name)
            return get_smoke_coverage_response(project_name)
        else:
            return get_overall_smoke_coverage_response()

    # Check if asking about project status
    # Match "status of X" or "state of X" or "progress of X"
    status_match = re.search(r'(?:status|state|progress)(?:\s+of\s+|\s+for\s+)(project\s+[a-z0-9].*?)(?:\s+|$|\.|\?)', message_lower)
    if status_match:
        project_name = status_match.group(1).strip()
        # Extract the project name, handling cases where it might contain the word 'project'
        project_name = extract_project_name(project_name)
        return get_project_status_response(project_name)

    # Check if asking about resources
    # Match "resources assigned to X" or "people working on X" or similar patterns
    resources_match = re.search(r'(?:resources|people|team)(?:\s+(?:assigned|allocated|working)(?:\s+(?:to|on|for))?)?(?:\s+(project\s+[a-z0-9].*?))?(?:\s+|$|\.|\?)', message_lower)
    if resources_match and resources_match.group(1):
        project_name = resources_match.group(1).strip()
        # Extract the project name, handling cases where it might contain the word 'project'
        project_name = extract_project_name(project_name)
        return get_resources_for_project_response(project_name)

    # Check for simple greetings
    if message_lower in ['hi', 'hello', 'hey', 'greetings']:
        return f"Hello! I'm your AI assistant for the dashboard. I can help you with information about projects, resources, regression percentage, smoke coverage, and more. What would you like to know?"

    # If no specific question pattern is matched, provide a general response
    return f"I understand you're asking about: {message}. " \
           f"I can see you're currently viewing {context.current_view} " \
           f"with {context.total_products} total products and {context.total_resources} resources. " \
           f"You can ask me about regression percentage, smoke coverage, project status, or resources assigned to a project."

def test_rule_based_responses():
    """Test the rule-based AI response generation for various questions."""
    # Create a mock context
    context = SimpleNamespace(
        total_products=35,
        total_resources=41,
        active_products=20,
        completed_products=15,
        current_view='Dashboard'
    )

    # Test questions
    questions = [
        "what is regression percentage?",
        "hi",
        "what is regression percentage of Project A?",
        "what is smoke coverage?",
        "what is smoke coverage of Project B?",
        "what is the status of Project C?",
        "who are the resources assigned to Project D?",
        "some random question"
    ]

    print("Testing rule-based AI responses...\n")

    for question in questions:
        print(f"Question: {question}")
        response = generate_ai_response_rule_based(question, context)
        print(f"Response: {response}\n")

    print("Test completed.")

if __name__ == "__main__":
    test_rule_based_responses()
