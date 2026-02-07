
"""
Integration Tests for SEO & ADA MCP
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib.util

# Clean up any existing mocks
for m in ["mcp", "mcp.server", "mcp.server.fastmcp"]:
    if m in sys.modules:
        del sys.modules[m]

# Create a pass-through MockFastMCP
class MockFastMCP:
    def __init__(self, name):
        self.name = name
    
    def tool(self):
        def decorator(func):
            return func
        return decorator
    
    def run(self):
        pass

# Mock the module structure
mock_mcp = MagicMock()
mock_server = MagicMock()
mock_fastmcp = MagicMock()
mock_fastmcp.FastMCP = MockFastMCP

sys.modules["mcp"] = mock_mcp
sys.modules["mcp.server"] = mock_server
sys.modules["mcp.server.fastmcp"] = mock_fastmcp

# Create mock requests *before* importing server
with patch.dict(sys.modules, {
    "requests": MagicMock(), 
    "mcp_telemetry": MagicMock()
}):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp-seo/server.py"))
    spec = importlib.util.spec_from_file_location("mcp_seo_server", file_path)
    server = importlib.util.module_from_spec(spec)
    sys.modules["mcp_seo_server"] = server
    spec.loader.exec_module(server)

def test_analyze_seo():
    mock_requests = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"""
    <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="A test page description.">
        </head>
        <body>
            <h1>Main Heading</h1>
            <img src="logo.png" alt="Company Logo">
            <a href="/about">About</a>
        </body>
    </html>
    """
    mock_requests.get.return_value = mock_resp
    
    with patch.object(server.requests, "get", return_value=mock_resp):
        res = server.analyze_seo("http://test.com")
        assert res["title"] == "Test Page"
        assert res["meta_description"] == "A test page description."
        assert res["h1_count"] == 1
        assert res["images_missing_alt"] == 0
        assert res["internal_links"] == 1

def test_analyze_ada():
    mock_requests = MagicMock()
    mock_resp = MagicMock()
    mock_resp.content = b"""
    <html>
        <body>
            <img src="bad.png">
            <input type="text" id="name">
        </body>
    </html>
    """
    mock_requests.get.return_value = mock_resp
    
    with patch.object(server.requests, "get", return_value=mock_resp):
        res = server.analyze_ada("http://test.com")
        # Check if issues exist in the list
        issues = res["issues"]
        assert any("Missing 'lang' attribute" in i for i in issues)
        assert any("images missing alt text" in i for i in issues)
        assert any("missing label" in i for i in issues)
