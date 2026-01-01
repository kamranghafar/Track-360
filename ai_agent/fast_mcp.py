# Simple implementation of a Fast Model Context Protocol (MCP) framework
from typing import Callable, Dict, List, Any, Optional, Union
import inspect
import functools

class FastMCP:
    """A simple implementation of Model Context Protocol for dashboard context"""

    def __init__(self, name: str):
        """Initialize the MCP server with a name"""
        self.name = name
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}

    def tool(self):
        """Decorator to register a tool function"""
        def decorator(func):
            self.tools[func.__name__] = func
            self.descriptions[func.__name__] = func.__doc__ or ""

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return decorator

    def call_tool(self, tool_name: str, **kwargs):
        """Call a tool by name with the given arguments"""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"

        tool = self.tools[tool_name]
        sig = inspect.signature(tool)

        # Filter kwargs to only include parameters accepted by the tool
        valid_kwargs = {}
        for param_name in sig.parameters:
            if param_name in kwargs:
                valid_kwargs[param_name] = kwargs[param_name]

        try:
            return tool(**valid_kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """Get a list of tool descriptions"""
        return [
            {
                "name": name,
                "description": self.descriptions[name]
            }
            for name in self.tools
        ]

    # Method to directly call the registered tools
    def __getattr__(self, name):
        if name in self.tools:
            return self.tools[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
