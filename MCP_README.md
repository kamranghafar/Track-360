# Model Context Protocol (MCP) Integration

This document provides instructions for setting up and using the Model Context Protocol (MCP) integration in the Dashboard AI Assistant.

## Overview

The Model Context Protocol (MCP) is a framework for building AI assistants with access to tools and context. The Dashboard AI Assistant uses MCP to provide tools for accessing dashboard data and generating responses.

## Setup Instructions

### 1. Install Dependencies

The MCP integration requires several dependencies. You can install them by running the following command:

```bash
python install_mcp_dependencies.py
```

This will install the following dependencies:
- jsonschema
- httpx_sse
- pywin32 (Windows only)
- pydantic_settings
- starlette
- sse_starlette

### 2. Verify MCP Installation

You can verify that MCP is properly installed and working by running the test script:

```bash
python test_mcp.py
```

If MCP is working correctly, you should see the following output:
```
Added Python SDK path: <path_to_sdk>
Successfully imported FastMCP
Successfully initialized MCP server
MCP server name: Test MCP Server
MCP is working correctly!
```

## Troubleshooting

If you encounter the error "MCP is not available", it could be due to one of the following reasons:

1. **Missing dependencies**: Make sure you've installed all the required dependencies by running `python install_mcp_dependencies.py`.

2. **Python SDK not found**: Ensure that the Python SDK is in the correct location at `<project_root>/python-sdk/python-sdk-main`.

3. **Import errors**: Check the logs for specific import errors. You may need to install additional dependencies.

## Using MCP in the Dashboard AI Assistant

The MCP integration is automatically initialized when the application starts. The `mcp_integration.py` file defines tools for accessing dashboard data and generating responses.

When a user sends a message to the AI assistant, the `generate_ai_response()` function in `views.py` tries to use MCP to generate a response. If MCP is not available, it falls back to using the LLM or rule-based approach.

## Adding New Tools

To add a new tool to the MCP integration, you can define a new function in the `initialize_mcp()` function in `mcp_integration.py` and decorate it with `@mcp_server.tool()`.

Example:
```python
@mcp_server.tool()
def my_new_tool(param1: str, param2: int = 0) -> str:
    """
    Description of what the tool does.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        str: Description of the return value
    """
    # Tool implementation
    return f"Result: {param1}, {param2}"
```