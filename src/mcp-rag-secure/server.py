
"""
Secure Multi-Tenant RAG MCP Server
"""
import sys
import os
import uuid
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from mcp_telemetry import log_usage

# Initialize FastMCP Server
mcp = FastMCP("Secure RAG")

# Initialize ChromaDB (Persistent)
# Store in src/mcp-rag-secure/chroma_db
current_dir = os.path.dirname(os.path.abspath(__file__))
persist_directory = os.path.join(current_dir, "chroma_db")

client = chromadb.PersistentClient(path=persist_directory)

# Use default embedding function (all-MiniLM-L6-v2 usually)
# Explicitly use SentenceTransformer if installed, else default
try:
    from sentence_transformers import SentenceTransformer
    # Custom embedding function wrapper
    class SentenceTransformerEmbeddingFunction(embedding_functions.EmbeddingFunction):
        def __init__(self, model_name="all-MiniLM-L6-v2"):
            self.model = SentenceTransformer(model_name)
        def __call__(self, input: List[str]) -> List[List[float]]:
            return self.model.encode(input).tolist()
            
    emb_fn = SentenceTransformerEmbeddingFunction()
except ImportError:
    emb_fn = embedding_functions.DefaultEmbeddingFunction()

# Create collection
collection = client.get_or_create_collection(
    name="secure_rag",
    embedding_function=emb_fn
)

@mcp.tool()
def ingest_document(tenant_id: str, content: str, metadata: Dict[str, Any] = None) -> str:
    """
    Ingest a document into the RAG system with strict tenant isolation.
    """
    log_usage("mcp-rag-secure", "ingest_document")
    if not metadata:
        metadata = {}
    
    # Enforce tenant_id in metadata
    metadata["tenant_id"] = tenant_id
    
    doc_id = str(uuid.uuid4())
    
    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[doc_id]
    )
    return f"Document ingested with ID: {doc_id}"

@mcp.tool()
def query_knowledge_base(tenant_id: str, query: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Query the knowledge base. Results are strictly filtered by tenant_id.
    """
    log_usage("mcp-rag-secure", "query_knowledge_base")
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where={"tenant_id": tenant_id} # Critical security filter
    )
    
    formatted_results = []
    if results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            formatted_results.append({
                "content": doc,
                "metadata": meta,
                "score": results["distances"][0][i] if results["distances"] else None
            })
            
    return formatted_results

@mcp.tool()
def delete_tenant_data(tenant_id: str) -> str:
    """
    Delete all data associated with a specific tenant.
    """
    collection.delete(
        where={"tenant_id": tenant_id}
    )
    return f"All data for tenant {tenant_id} has been deleted."

if __name__ == "__main__":
    mcp.run()
