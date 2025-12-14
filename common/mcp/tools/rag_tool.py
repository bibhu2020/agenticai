"""RAG Search Tool - Search the local healthcare knowledge base"""
import os
from pathlib import Path
from agents import function_tool, RunContextWrapper

from common.rag.rag import Retriever
from dataclasses import dataclass

@dataclass
class UserContext:
    uid: str
    db_path: str = ""
    file_path: str = ""
    similarity_threshold: float = 0.4  # FAISS L2 distance threshold for RAG relevance


# ---------------------------------------------------------
# RAG Search Tool
# ---------------------------------------------------------
@function_tool
def rag_search(wrapper: RunContextWrapper[UserContext], query: str) -> str:
    """
    Search the local healthcare knowledge base for relevant information.
    
    Args:
        query: The medical question or topic to search for
        
    Returns:
        Relevant information from the healthcare knowledge base
    """
    print(f"[DEBUG] RAG_SEARCH called with query: '{query}'")
    
    # Get similarity threshold from user context
    similarity_threshold = wrapper.context.similarity_threshold
    print(f"[DEBUG] RAG_SEARCH: Using similarity threshold: {similarity_threshold}")
    
    try:
        # Initialize retriever with user context
        retriever = Retriever(
            db_path=wrapper.context.db_path,
            file_path=wrapper.context.file_path
        )

        # Get results with similarity scores
        results_with_scores = retriever.retrieve_with_scores(query, k=5)  # Increased from 4 to 5
        
        if not results_with_scores:
            print("[DEBUG] RAG_SEARCH: No results found in knowledge base")
            return "No relevant information found in the knowledge base."
        
        print(f"[DEBUG] RAG_SEARCH: Found {len(results_with_scores)} results")
        
        # Check if the best match meets the threshold
        # FAISS returns (document, distance) where lower distance = better match
        best_score = results_with_scores[0][1]
        print(f"[DEBUG] RAG_SEARCH: Best similarity score (distance): {best_score:.4f} (threshold: {similarity_threshold})")
        
        if best_score > similarity_threshold:
            print(f"[DEBUG] RAG_SEARCH: Best match score {best_score:.4f} is above threshold {similarity_threshold}")
            print("[DEBUG] RAG_SEARCH: Results not relevant enough, triggering web search fallback")
            return "No relevant information found in the knowledge base."
        
        print(f"[DEBUG] RAG_SEARCH: Results are relevant (score: {best_score:.4f} <= {similarity_threshold})")
        
        # Log all scores for debugging
        all_scores = [f"{score:.4f}" for _, score in results_with_scores]
        print(f"[DEBUG] RAG_SEARCH: All scores: {', '.join(all_scores)}")
        
        # Format results - only include documents that meet the similarity threshold
        formatted_results = []
        for i, (doc, score) in enumerate(results_with_scores[:5], 1):  # Top 5 results
            if score <= similarity_threshold:
                content = doc.page_content.strip()
                formatted_results.append(f"Result {i} (score: {score:.4f}):\n{content}\n")
        
        if not formatted_results:
            print("[DEBUG] RAG_SEARCH: No results met the similarity threshold")
            print("[DEBUG] RAG_SEARCH: Triggering web search fallback")
            return "No relevant information found in the knowledge base."
        
        result_text = "\n".join(formatted_results)
        print(f"[DEBUG] RAG_SEARCH: Returning {len(formatted_results)} results, total length: {len(result_text)} characters")
        print(f"[DEBUG] RAG_SEARCH: First 300 chars: {result_text[:300]}...")
        
        return result_text
        
    except Exception as e:
        print(f"[DEBUG] RAG_SEARCH: Error occurred - {str(e)}")
        return f"Error retrieving from knowledge base: {str(e)}"



__all__ = ["rag_search", "retriever"]
