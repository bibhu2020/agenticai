
"""
Integration Tests for GitHub MCP
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

# Create mock github *before* importing server
with patch.dict(sys.modules, {"github": MagicMock(), "github.GithubException": MagicMock()}):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp-github/server.py"))
    spec = importlib.util.spec_from_file_location("mcp_github_server", file_path)
    server = importlib.util.module_from_spec(spec)
    sys.modules["mcp_github_server"] = server
    spec.loader.exec_module(server)


def test_list_issues():
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.number = 1
    mock_issue.title = "Bug Fix"
    mock_issue.state = "open"
    mock_issue.user.login = "user1"
    
    mock_repo.get_issues.return_value = [mock_issue]
    mock_gh.get_repo.return_value = mock_repo
    
    with patch.object(server, "get_client", return_value=mock_gh):
        res = server.list_issues("owner", "repo")
        assert len(res) == 1
        assert res[0]["title"] == "Bug Fix"

def test_create_issue():
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.number = 2
    mock_issue.title = "New Feature"
    mock_issue.html_url = "http://github.com/..."
    
    mock_repo.create_issue.return_value = mock_issue
    mock_gh.get_repo.return_value = mock_repo
    
    with patch.object(server, "get_client", return_value=mock_gh):
        res = server.create_issue("owner", "repo", "New Feature", "Body")
        assert res["number"] == 2
        assert res["title"] == "New Feature"

def test_create_pull_request():
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_pr.number = 3
    mock_pr.title = "PR Title"
    mock_pr.state = "open"
    
    mock_repo.create_pull.return_value = mock_pr
    mock_gh.get_repo.return_value = mock_repo
    
    with patch.object(server, "get_client", return_value=mock_gh):
        res = server.create_pull_request("owner", "repo", "PR Title", "Body", "feature", "main")
        assert res["number"] == 3
        assert res["state"] == "open"
