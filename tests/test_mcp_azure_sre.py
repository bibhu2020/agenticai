
"""
Integration Tests for Azure SRE MCP
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

# Create mock clients *before* importing server by mocking the modules
with patch.dict(sys.modules, {
    "azure.identity": MagicMock(),
    "azure.mgmt.resource": MagicMock(),
    "azure.mgmt.monitor": MagicMock(),
    "azure.mgmt.compute": MagicMock(),
    "azure.monitor.query": MagicMock(),
    "mcp_telemetry": MagicMock(),
}):
    # Import the server module explicitly to avoid name collision
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp-azure-sre/server.py"))
    spec = importlib.util.spec_from_file_location("mcp_azure_sre_server", file_path)
    server = importlib.util.module_from_spec(spec)
    sys.modules["mcp_azure_sre_server"] = server
    spec.loader.exec_module(server)

def test_list_resources():
    mock_client = MagicMock()
    mock_resource = MagicMock()
    mock_resource.name = "vm1"
    mock_resource.type = "Microsoft.Compute/virtualMachines"
    mock_resource.location = "eastus"
    mock_resource.id = "/subscriptions/123/..."
    mock_client.resources.list.return_value = [mock_resource]
    
    # Patch attributes on the specific loaded module
    with patch.object(server, "ResourceManagementClient", return_value=mock_client):
        with patch.object(server, "DefaultAzureCredential"):
            res = server.list_resources("sub-id")
            assert len(res) == 1
            assert res[0]["name"] == "vm1"

def test_restart_vm():
    mock_client = MagicMock()
    mock_poller = MagicMock()
    mock_client.virtual_machines.begin_restart.return_value = mock_poller
    
    with patch.object(server, "ComputeManagementClient", return_value=mock_client):
        with patch.object(server, "DefaultAzureCredential"):
            res = server.restart_vm("sub", "rg", "vm")
            assert "Successfully restarted" in res

def test_analyze_logs():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = "Success"
    
    # Mock table structure
    mock_table = MagicMock()
    mock_table.columns = ["Time", "Message"]
    mock_table.rows = [["2023-01-01", "Error 500"]]
    mock_resp.tables = [mock_table]
    
    mock_client.query_workspace.return_value = mock_resp
    
    with patch.object(server, "LogsQueryClient", return_value=mock_client):
        with patch.object(server, "DefaultAzureCredential"):
            res = server.analyze_logs("ws-id", "Error | count")
            assert len(res) == 1
            assert res[0]["Message"] == "Error 500"
