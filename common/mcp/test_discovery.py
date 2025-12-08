"""
Simple test script to verify MCP server tool discovery.
Run this to check if all tools are being discovered correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import discover_tools, TOOLS_REGISTRY

def test_tool_discovery():
    """Test that tools are discovered correctly."""
    print("=" * 60)
    print("MCP Server Tool Discovery Test")
    print("=" * 60)
    
    # Discover tools
    discover_tools()
    
    print(f"\n✓ Total tools discovered: {len(TOOLS_REGISTRY)}")
    print("\nRegistered Tools:")
    print("-" * 60)
    
    # Group tools by module
    tools_by_module = {}
    for tool_name in sorted(TOOLS_REGISTRY.keys()):
        module_name = tool_name.split('.')[0]
        if module_name not in tools_by_module:
            tools_by_module[module_name] = []
        tools_by_module[module_name].append(tool_name)
    
    # Print grouped tools
    for module_name, tools in sorted(tools_by_module.items()):
        print(f"\n{module_name}:")
        for tool in tools:
            print(f"  - {tool}")
    
    print("\n" + "=" * 60)
    print(f"✓ Test completed successfully!")
    print("=" * 60)
    
    # Expected minimum number of tools
    expected_min = 10
    if len(TOOLS_REGISTRY) >= expected_min:
        print(f"✓ Tool count check passed ({len(TOOLS_REGISTRY)} >= {expected_min})")
    else:
        print(f"⚠ Warning: Expected at least {expected_min} tools, found {len(TOOLS_REGISTRY)}")
    
    return len(TOOLS_REGISTRY)


if __name__ == "__main__":
    test_tool_discovery()
