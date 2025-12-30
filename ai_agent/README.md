# AI Agent with Model Context Protocol (MCP)

This module implements an AI assistant for the dashboard application, using the Model Context Protocol (MCP) to provide context-aware responses to user queries.

## Overview

The AI Agent uses a tiered approach to generate responses:

1. **MCP (Model Context Protocol)**: The primary method, using tools defined in the MCP server to generate responses based on specific query types.
2. **LLM (Large Language Model)**: Fallback method if MCP is not available or can't handle the query.
3. **Rule-based**: Final fallback method using regex pattern matching to generate responses.

## Components

### Models

- `ChatSession`: Stores chat sessions between users and the AI agent.
- `ChatMessage`: Stores individual messages in a chat session.
- `DashboardContext`: Stores context information from the dashboard for use with the AI agent.

### Views

- `chat_view`: Main view for the AI agent chat interface.
- `chat_embed_view`: Embedded view for the AI agent chat interface (used in the chat bubble).
- `send_message`: API endpoint for sending a message to the AI agent.
- `end_chat`: API endpoint for ending the current chat session.
- `new_chat`: API endpoint for starting a new chat session.
- `ChatHistoryView`: View for displaying chat history.

### MCP Integration

The `mcp_integration.py` module implements the Model Context Protocol integration:

- `initialize_mcp()`: Initializes the MCP server with tools for generating responses.
- Tools:
  - `get_regression_percentage`: Gets the regression percentage for a specific project.
  - `get_smoke_coverage`: Gets the smoke coverage for a specific project or overall.
  - `get_project_status`: Gets the status of a specific project.
  - `get_project_resources`: Gets the resources assigned to a specific project.

### Context Collection

The `context_collectors.py` module implements functions for collecting context from the dashboard:

- `collect_dashboard_overview_context`: Collects context data from the dashboard overview.
- `collect_view_state_context`: Collects context about the current view and filters.
- `collect_visualization_context`: Collects context about visible charts and visualizations.
- `collect_user_history_context`: Collects context about the user's recent actions.
- `collect_kpi_context`: Collects context about KPIs and ratings.
- `collect_full_dashboard_context`: Collects all context data from the dashboard.

### LLM Integration

The `llm_integration.py` module implements the Large Language Model integration:

- `generate_llm_response`: Generates a response using an LLM based on the user's message and dashboard context.
- `is_llm_available`: Checks if the LLM is available.

## Fallback Mechanisms

The AI Agent includes several fallback mechanisms to ensure it continues to function even if certain components are unavailable:

1. If MCP is not available (e.g., if the python-sdk is not installed), it falls back to using the LLM.
2. If the LLM is not available (e.g., if the required libraries are not installed), it falls back to using the rule-based approach.
3. If all else fails, it provides a generic response based on the available context.

## Usage

To use the AI Agent, include the chat bubble in your template:

```html
<!-- AI Assistant Chat Bubble -->
<div id="ai-chat-bubble-container">
    <div id="ai-chat-window" class="hidden">
        <div class="ai-chat-header">
            <h5>AI Assistant</h5>
            <button id="ai-chat-close" class="btn btn-sm btn-link text-white">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <iframe id="ai-chat-iframe" src="{% url 'ai_agent:chat_embed' %}" frameborder="0"></iframe>
    </div>
    <button id="ai-chat-bubble" class="btn btn-primary rounded-circle">
        <i class="fas fa-robot"></i>
    </button>
</div>
```

## Requirements

- Python 3.8+
- Django 5.0+
- MCP SDK (optional, for MCP integration)
- Transformers, PyTorch, etc. (optional, for LLM integration)