from rag.db import get_db

async def search_candidate_knowledge_base(query: str, candidate_name: str) -> str:
    """Searches RAG for candidate details."""
    print(f"[DEBUG] Tool 'search_candidate_knowledge_base' called with query='{query}', candidate='{candidate_name}'")
    db = get_db()
    results = db.query(query, candidate_name=candidate_name, n_results=3)
    
    if not results['documents'][0]:
        print(f"[DEBUG] Tool found NO results for {candidate_name}")
        return "No relevant info found."
    
    print(f"[DEBUG] Tool found {len(results['documents'][0])} segments for {candidate_name}")
    return f"Context for {candidate_name}:\n" + "\n".join(results['documents'][0])
