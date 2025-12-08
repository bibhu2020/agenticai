#!/usr/bin/env python3
"""
MCP Server with stdio transport that exposes all tools from the tools folder.
"""
import asyncio
import sys
import os
import inspect
import importlib
from pathlib import Path
from typing import Any, Callable

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server
app = Server("tools-server")

# Dictionary to store all discovered tools
TOOLS_REGISTRY: dict[str, Callable] = {}

def discover_tools():
    """
    Dynamically discover all @function_tool decorated functions from the tools folder.
    """
    tools_dir = Path(__file__).parent / "tools"
    tool_modules = [
        "google_tools",
        "news_tools", 
        "search_tools",
        "time_tools",
        "weather_tools",
        "yf_tools"
    ]
    
    print(f"[MCP Server] Discovering tools from: {tools_dir}", file=sys.stderr)
    
    for module_name in tool_modules:
        try:
            # Import the module
            module = importlib.import_module(f"mcp.tools.{module_name}")
            
            # Find all functions in the module
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                # Check if it has the function_tool decorator
                # The @function_tool decorator typically adds metadata to the function
                if hasattr(obj, '__wrapped__') or name.startswith('_'):
                    continue
                    
                # Check if it's a tool by looking for common patterns
                if callable(obj) and not name.startswith('_'):
                    # Register the tool
                    tool_name = f"{module_name}.{name}"
                    TOOLS_REGISTRY[tool_name] = obj
                    print(f"[MCP Server] Registered tool: {tool_name}", file=sys.stderr)
                    
        except Exception as e:
            print(f"[MCP Server] Error loading module {module_name}: {e}", file=sys.stderr)
    
    print(f"[MCP Server] Total tools registered: {len(TOOLS_REGISTRY)}", file=sys.stderr)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.
    """
    tools = []
    
    for tool_name, tool_func in TOOLS_REGISTRY.items():
        # Extract function signature and docstring
        sig = inspect.signature(tool_func)
        doc = inspect.getdoc(tool_func) or "No description available"
        
        # Build input schema from function parameters
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # Default type
            param_desc = ""
            
            # Try to infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                annotation = param.annotation
                if annotation == int:
                    param_type = "integer"
                elif annotation == bool:
                    param_type = "boolean"
                elif annotation == float:
                    param_type = "number"
            
            properties[param_name] = {
                "type": param_type,
                "description": param_desc or f"Parameter: {param_name}"
            }
            
            # Check if parameter is required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Create tool definition
        tool = Tool(
            name=tool_name,
            description=doc.split('\n')[0][:200],  # First line, max 200 chars
            inputSchema={
                "type": "object",
                "properties": properties,
                "required": required
            }
        )
        tools.append(tool)
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Execute a tool with the provided arguments.
    """
    print(f"[MCP Server] Calling tool: {name} with args: {arguments}", file=sys.stderr)
    
    if name not in TOOLS_REGISTRY:
        raise ValueError(f"Tool not found: {name}")
    
    tool_func = TOOLS_REGISTRY[name]
    
    try:
        # Call the tool function
        if inspect.iscoroutinefunction(tool_func):
            result = await tool_func(**arguments)
        else:
            result = tool_func(**arguments)
        
        # Convert result to string if needed
        if not isinstance(result, str):
            result = str(result)
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        print(f"[MCP Server] {error_msg}", file=sys.stderr)
        return [TextContent(type="text", text=error_msg)]


async def main():
    """
    Main entry point for the MCP server.
    """
    # Discover all tools before starting the server
    discover_tools()
    
    print(f"[MCP Server] Starting MCP server with {len(TOOLS_REGISTRY)} tools", file=sys.stderr)
    
    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
