from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from core.state import AgentState
from tools.search import google_search
import os

# --- Models ---
class SearchItem(BaseModel):
    query: str = Field(description="The search term to use for the web search.")
    reason: str = Field(description="The reason for searching this term.")

class SearchPlan(BaseModel):
    searches: List[SearchItem] = Field(description="A list of web searches to perform.")

# --- Nodes ---

def planner_node(state: AgentState):
    print("--- PLANNER ---")
    query = state['query']
    depth = state.get('research_depth', 'Standard')
    
    num_searches = 3
    if depth == 'Quick': num_searches = 3
    elif depth == 'Standard': num_searches = 5
    elif depth == 'Deep': num_searches = 10
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = (
        "You are a helpful research assistant. Given a query, come up with a set of web searches "
        "to perform to best answer the query. Generate exactly {n} search terms."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    chain = prompt | llm.with_structured_output(SearchPlan)
    result = chain.invoke({"query": query, "n": num_searches})
    
    # Convert Pydantic models to dicts for State
    plan = {
        "searches": [{"query": s.query, "reason": s.reason} for s in result.searches],
        "note": ""
    }
    
    print(f"Planned {len(plan['searches'])} searches.")
    return {"search_plan": plan}

async def search_node(state: AgentState):
    print("--- SEARCH ---")
    plan = state['search_plan']
    results = []
    import asyncio
    
    # Execute searches in parallel
    print(f"Executing {len(plan['searches'])} searches in parallel...")
    tasks = [google_search.ainvoke(item['query']) for item in plan['searches']]
    results_content = await asyncio.gather(*tasks)
    
    for i, item in enumerate(plan['searches']):
        results.append(f"Query: {item['query']}\nResult: {results_content[i]}")
        
    return {"search_results": results}

def writer_node(state: AgentState):
    print("--- WRITER ---")
    query = state['query']
    results = state['search_results']
    fmt = state.get('report_format', 'Academic')
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = (
        "You are a research assistant. Write a comprehensive report based on the provided search results. "
        "The report format should be {format}. Use only the provided information."
        "Cite sources where possible using links provided in the results."
        "The output should be in Markdown."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Original Query: {query}\n\nSearch Results:\n{results}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"query": query, "results": "\n\n".join(results), "format": fmt})
    
    return {"final_report": response.content}
