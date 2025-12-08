"""RAG Search Tool - Search the local healthcare knowledge base"""
import os
from pathlib import Path
from agents import function_tool
from dotenv import load_dotenv

# Import RAG retriever
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.rag import Retriever

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# Initialize RAG Retriever
# ---------------------------------------------------------
# Get the healthcare-rag-chatbot directory path
healthcare_dir = str(Path(__file__).parent.parent.parent)
retriever = Retriever(db_path=healthcare_dir)

# ---------------------------------------------------------
# RAG Search Tool
# ---------------------------------------------------------
@function_tool
def rag_search(query: str) -> str:
    """
    Search the local healthcare knowledge base for relevant information.
    
    Args:
        query: The medical question or topic to search for
        
    Returns:
        Relevant information from the healthcare knowledge base
    """
    print(f"[DEBUG] RAG_SEARCH called with query: '{query}'")
    
    try:
        results = retriever.retrieve(query)
        if not results:
            print("[DEBUG] RAG_SEARCH: No results found in knowledge base")
            return "No relevant information found in the knowledge base."
        
        print(f"[DEBUG] RAG_SEARCH: Found {len(results)} results")
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results[:3], 1):  # Top 3 results
            formatted_results.append(f"Result {i}:\n{doc.page_content}\n")
        
        return "\n".join(formatted_results)
    except Exception as e:
        print(f"[DEBUG] RAG_SEARCH: Error occurred - {str(e)}")
        return f"Error retrieving from knowledge base: {str(e)}"


__all__ = ["rag_search", "retriever"]
