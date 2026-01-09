from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from app_agents.nodes import market_analyst_node, sentiment_analyst_node, strategy_advisor_node, risk_manager_node
from dotenv import load_dotenv

load_dotenv()

def create_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("market_analyst", market_analyst_node)
    graph.add_node("sentiment_analyst", sentiment_analyst_node)
    graph.add_node("strategy_advisor", strategy_advisor_node)
    graph.add_node("risk_manager", risk_manager_node)
    
    # Parallel execution of data gathering
    graph.add_edge(START, "market_analyst")
    graph.add_edge(START, "sentiment_analyst")
    
    # Sync point: Strategy needs both
    graph.add_edge("market_analyst", "strategy_advisor")
    graph.add_edge("sentiment_analyst", "strategy_advisor")
    
    graph.add_edge("strategy_advisor", "risk_manager")
    graph.add_edge("risk_manager", END)
    
    return graph.compile()
