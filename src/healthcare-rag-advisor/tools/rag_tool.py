"""RAG Search Tool — searches the local healthcare knowledge base."""
from langchain_core.tools import tool
from rag import Retriever

_retriever = Retriever()
_SIMILARITY_THRESHOLD = 0.8  # FAISS L2 distance; lower = better match


@tool
def rag_search(query: str) -> str:
    """Search the local healthcare knowledge base for relevant medical information."""
    try:
        results = _retriever.retrieve_with_scores(query, k=5)
        if not results:
            return "No relevant information found in the knowledge base."

        best_score = results[0][1]
        if best_score > _SIMILARITY_THRESHOLD:
            return "No relevant information found in the knowledge base."

        formatted = []
        for i, (doc, score) in enumerate(results, 1):
            if score <= _SIMILARITY_THRESHOLD:
                formatted.append(f"Result {i} (score: {score:.4f}):\n{doc.page_content.strip()}")

        return "\n\n".join(formatted) if formatted else "No relevant information found in the knowledge base."
    except Exception as e:
        return f"Error retrieving from knowledge base: {e}"
