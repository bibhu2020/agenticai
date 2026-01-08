import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from patterns.agent_graph import MultiAgentSystem
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("Optimization: Initializing Architecture V3 (LangGraph)...")
    
    # Initialize System
    system = MultiAgentSystem(model_name="gpt-4o", provider="openai")
    graph = system.build_graph()
    
    # --- Scenario 1: Financial Query ---
    print("\n--- Scenario 1: Stock Price (Router -> FinanceAgent) ---")
    user_input = "What is the stock price of AAPL?"
    print(f"User: {user_input}")
    
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    # Run Graph
    # use stream for updates or invoke for final
    result = await graph.ainvoke(initial_state)
    
    # Print Last Message
    last_msg = result["messages"][-1]
    print(f"[Final Answer]: {last_msg.content}")

    # --- Scenario 2: Web Query ---
    print("\n--- Scenario 2: Weather (Router -> WebAgent) ---")
    user_input = "What is the weather in Dallas?"
    print(f"User: {user_input}")
    
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    result = await graph.ainvoke(initial_state)
    
    last_msg = result["messages"][-1]
    print(f"[Final Answer]: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
