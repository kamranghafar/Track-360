import sys
import os
from pathlib import Path
import importlib.metadata

# Add the python-sdk to the Python path
sdk_path = Path(__file__).parent / "python-sdk" / "python-sdk-main"
if sdk_path.exists():
    sys.path.append(str(sdk_path))
    sys.path.append(str(sdk_path / "src"))
    print(f"Added Python SDK path: {sdk_path}")
else:
    print(f"Python SDK path not found: {sdk_path}")

# Mock the version function to handle missing metadata
import importlib.metadata
original_version = importlib.metadata.version

def mock_version(name):
    if name == "mcp":
        return "0.1.0"  # Return a dummy version
    return original_version(name)

# Apply the monkey patch
importlib.metadata.version = mock_version

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    print("Successfully imported FastMCP")

    # Try to initialize MCP
    mcp_server = FastMCP("Test MCP Server")
    print("Successfully initialized MCP server")
    print(f"MCP server name: {mcp_server.name}")
    print("MCP is working correctly!")

except ImportError as e:
    print(f"Failed to import FastMCP: {str(e)}")
except Exception as e:
    print(f"Error initializing MCP: {str(e)}")
