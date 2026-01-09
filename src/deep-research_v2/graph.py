from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from app_agents.nodes import planner_node, search_node, writer_node
from dotenv import load_dotenv

load_dotenv()

def create_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("planner", planner_node)
    graph.add_node("search", search_node)
    graph.add_node("writer", writer_node)
    
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "search")
    graph.add_edge("search", "writer")
    graph.add_edge("writer", END)
    
    return graph.compile()
