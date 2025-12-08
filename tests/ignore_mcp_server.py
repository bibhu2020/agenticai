"""
Simplified test for MCP server tool discovery without requiring MCP SDK.
This tests the tool discovery mechanism independently.
"""
import pytest
import sys
import os
import importlib
import inspect
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def discover_tools_simple():
    """
    Simplified tool discovery that doesn't require MCP SDK.
    """
    tools_registry = {}
    tools_dir = Path(__file__).parent.parent / "common" / "mcp" / "tools"
    
    tool_modules = [
        "google_tools",
        "news_tools",
        "search_tools",
        "time_tools",
        "weather_tools",
        "yf_tools"
    ]
    
    # Temporarily add common to path
    common_path = str(Path(__file__).parent.parent / "common")
    if common_path not in sys.path:
        sys.path.insert(0, common_path)
    
    for module_name in tool_modules:
        try:
            # Import the module
            module = importlib.import_module(f"mcp.tools.{module_name}")
            
            # Find all functions in the module
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                # Skip private functions
                if name.startswith('_'):
                    continue
                    
                # Register the tool
                tool_name = f"{module_name}.{name}"
                tools_registry[tool_name] = obj
                
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")
    
    return tools_registry


@pytest.fixture(scope="module")
def tools_registry():
    """Fixture to discover tools once for all tests."""
    return discover_tools_simple()


def test_tool_discovery_works(tools_registry):
    """Test that tool discovery finds tools"""
    assert len(tools_registry) > 0, "No tools were discovered"
    print(f"\n✓ Discovered {len(tools_registry)} tools")


def test_all_modules_have_tools(tools_registry):
    """Test that all expected modules have tools"""
    expected_modules = {
        "google_tools",
        "news_tools",
        "search_tools",
        "time_tools",
        "weather_tools",
        "yf_tools"
    }
    
    # Count tools by module
    tools_by_module = {}
    for tool_name in tools_registry.keys():
        module_name = tool_name.split('.')[0]
        if module_name not in tools_by_module:
            tools_by_module[module_name] = []
        tools_by_module[module_name].append(tool_name)
    
    print(f"\n✓ Tools by module:")
    for module in sorted(expected_modules):
        tools = tools_by_module.get(module, [])
        print(f"  {module}: {len(tools)} tools")
        if tools:
            for tool in tools:
                print(f"    - {tool}")
        assert module in tools_by_module, f"Module {module} has no tools"
        assert len(tools) > 0, f"Module {module} has no tools"


def test_time_tools_exists(tools_registry):
    """Test that time_tools.current_datetime exists"""
    tool_name = "time_tools.current_datetime"
    assert tool_name in tools_registry, f"Tool {tool_name} not found"
    
    # Test calling it
    tool_func = tools_registry[tool_name]
    result = tool_func(format="natural")
    assert result is not None
    assert len(result) > 0
    print(f"\n✓ {tool_name} result: {result}")


def test_google_tools_exists(tools_registry):
    """Test that google_tools are discovered"""
    google_tools = [name for name in tools_registry.keys() if name.startswith("google_tools.")]
    assert len(google_tools) >= 2, f"Expected at least 2 google tools, found {len(google_tools)}"
    print(f"\n✓ Google tools: {google_tools}")


def test_news_tools_exists(tools_registry):
    """Test that news_tools are discovered"""
    news_tools = [name for name in tools_registry.keys() if name.startswith("news_tools.")]
    assert len(news_tools) >= 3, f"Expected at least 3 news tools, found {len(news_tools)}"
    print(f"\n✓ News tools: {news_tools}")


def test_search_tools_exists(tools_registry):
    """Test that search_tools are discovered"""
    search_tools = [name for name in tools_registry.keys() if name.startswith("search_tools.")]
    assert len(search_tools) >= 2, f"Expected at least 2 search tools, found {len(search_tools)}"
    print(f"\n✓ Search tools: {search_tools}")


def test_weather_tools_exists(tools_registry):
    """Test that weather_tools are discovered"""
    weather_tools = [name for name in tools_registry.keys() if name.startswith("weather_tools.")]
    assert len(weather_tools) >= 3, f"Expected at least 3 weather tools, found {len(weather_tools)}"
    print(f"\n✓ Weather tools: {weather_tools}")


def test_yf_tools_exists(tools_registry):
    """Test that yf_tools are discovered"""
    yf_tools = [name for name in tools_registry.keys() if name.startswith("yf_tools.")]
    assert len(yf_tools) >= 3, f"Expected at least 3 yf tools, found {len(yf_tools)}"
    print(f"\n✓ YF tools: {yf_tools}")


def test_total_tool_count(tools_registry):
    """Test that we have a reasonable total number of tools"""
    expected_min = 14  # Minimum expected tools across all modules
    total = len(tools_registry)
    assert total >= expected_min, f"Expected at least {expected_min} tools, found {total}"
    print(f"\n✓ Total tools: {total} (expected >= {expected_min})")
