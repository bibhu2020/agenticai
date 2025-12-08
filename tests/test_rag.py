import pytest
import os
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "healthcare-rag-chatbot"))

from src.rag.rag import Retriever


# Shared fixture for the database path
@pytest.fixture(scope="module")
def db_path():
    """Provide the database path for all tests"""
    return "/home/azureuser/ws/agenticaiprojects/src/healthcare-rag-chatbot/"


def test_1_create_rag_db(db_path):
    """Test 1: Create RAG database from PDF files"""
    retriever = Retriever(db_path=db_path)
    
    # Create the knowledge base
    retriever.load_knowledge_base()

    # Assertions - verify database was created
    assert retriever.retriever is not None, "Retriever should be initialized"
    assert retriever.db_path is not None, "DB path should be set"
    assert retriever.directory_path is not None, "Directory path should be set"
    assert retriever.embeddings is not None, "Embeddings should be initialized"
    assert retriever.text_splitter is not None, "Text splitter should be initialized"
    
    # Verify the database file exists
    assert os.path.exists(retriever.db_path), "Database directory should exist"

    print("\n✓ Test 1 PASSED: Knowledge base created successfully")
    print(f"  Database location: {retriever.db_path}")


def test_2_perform_similarity_search(db_path):
    """Test 2: Perform similarity search on existing database"""
    retriever = Retriever(db_path=db_path)
    
    # Load existing knowledge base
    retriever.load_knowledge_base()
    
    # Verify database was loaded
    assert retriever.retriever is not None, "Retriever should be loaded"
    
    # Perform similarity search
    query = "What is diabetes?"
    results = retriever.retrieve(query)
    
    # Verify search results
    assert results is not None, "Search should return results"
    assert isinstance(results, list), "Results should be a list"
    
    print(f"\n✓ Test 2 PASSED: Similarity search completed")
    print(f"  Query: '{query}'")
    print(f"  Results found: {len(results)}")
    
    if len(results) > 0:
        print(f"  Top result preview: {results[0].page_content[:200]}...")
    else:
        print(f"  ⚠ Warning: No results found for query")


# def test_3_delete_rag_db(db_path):
#     """Test 3: Delete the RAG database"""
#     retriever = Retriever(db_path=db_path)
    
#     # Verify database exists before deletion
#     db_exists_before = os.path.exists(retriever.db_path)
#     print(f"\n  Database exists before deletion: {db_exists_before}")
    
#     if db_exists_before:
#         # Delete the database
#         retriever.delete_knowledge_base()
        
#         # Verify deletion
#         db_exists_after = os.path.exists(retriever.db_path)
#         assert not db_exists_after, "Database should be deleted"
        
#         print(f"✓ Test 3 PASSED: Database deleted successfully")
#         print(f"  Database location: {retriever.db_path}")
#     else:
#         print(f"⚠ Test 3 SKIPPED: Database does not exist")


# Run tests with: pytest -s tests/test_rag.py
# Run in order: pytest -s tests/test_rag.py -v
