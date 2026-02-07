
"""
Integration Tests for Secure RAG MCP
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

# Create mock chromadb *before* importing server
with patch.dict(sys.modules, {
    "chromadb": MagicMock(),
    "chromadb.config": MagicMock(),
    "chromadb.utils": MagicMock(),
    "chromadb.utils.embedding_functions": MagicMock(),
}):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp-rag-secure/server.py"))
    spec = importlib.util.spec_from_file_location("mcp_rag_secure_server", file_path)
    server = importlib.util.module_from_spec(spec)
    sys.modules["mcp_rag_secure_server"] = server
    spec.loader.exec_module(server)

# Mock collection logic on the loaded server module
mock_collection = MagicMock()
server.collection = mock_collection

def test_ingest_document():
    res = server.ingest_document("tenant-1", "This is sensitive data")
    
    # Verify add call includes tenant_id metadata
    args, kwargs = mock_collection.add.call_args
    assert "documents" in kwargs
    assert "metadatas" in kwargs
    assert kwargs["metadatas"][0]["tenant_id"] == "tenant-1"
    assert "Document ingested" in res

def test_query_knowledge_base():
    # Setup mock return
    mock_collection.query.return_value = {
        "documents": [["This is sensitive data"]],
        "metadatas": [[{"tenant_id": "tenant-1", "source": "doc1"}]],
        "distances": [[0.1]]
    }
    
    res = server.query_knowledge_base("tenant-1", "sensitive")
    
    # Verify query includes tenant_id filter
    args, kwargs = mock_collection.query.call_args
    assert kwargs["where"] == {"tenant_id": "tenant-1"}
    
    assert len(res) == 1
    assert res[0]["content"] == "This is sensitive data"

def test_delete_tenant_data():
    res = server.delete_tenant_data("tenant-1")
    
    # Verify delete includes tenant_id filter
    args, kwargs = mock_collection.delete.call_args
    assert kwargs["where"] == {"tenant_id": "tenant-1"}
    assert "deleted" in res
