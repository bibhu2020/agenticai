import sys
import os
import asyncio

# Add the current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from patterns.react_agent import ReActAgent
from layers.action import ActionLayer
from agents import function_tool

async def main():
    print("=== Multi-Agent Architecture Demo: Handoffs (Swarm Pattern) ===\n")
    
    # 1. Initialize Tools Factory (Hands)
    actions = ActionLayer()
    
    # 2. Create Specialized Agents
    # We create them first so we can reference them in handoff tools
    
    # Finance Agent
    finance_agent = ReActAgent(
        name="FinanceAgent", 
        tools=actions.get_finance_tools(),
        instructions="You are a finance specialist. Use the 'mock_get_stock_price' tool to find stock prices for users. Do NOT apologize for using mock tools."
    )
    
    # Web Agent
    web_agent = ReActAgent(
        name="WebAgent", 
        tools=actions.get_web_tools(),
        instructions="You are a web researcher. You have been activated to answer a query. You MUST IMMEDIATELY use the `mock_search_web` tool with the user's query. Do NOT ask clarifying questions. Do NOT answer from memory. USE THE TOOL."
    )
    
    # 4. Create Router Agent
    # The Router is enabled with NATIVE SDK HANDOFFS.
    # We pass the target agents to the 'handoffs' parameter.
    router_agent = ReActAgent(
        name="Router", 
        handoffs=[finance_agent.agent, web_agent.agent],
        instructions="You are a Router. Redirect the user to the correct specialist.\n- For STOCK PRICES/FINANCE: Call `transfer_to_financeagent`.\n- For WEATHER/NEWS: Call `transfer_to_webagent`.\nTransfer immediately."
    )
    
    print("Scenario 1: User asks for Stock Price")
    print(">>> User: What is the price of NVDA?")
    # The Router will verify if it can handoff
    await router_agent.run("What is the price of NVDA?")
    
    print("\nScenario 2: User asks for Weather")
    print(">>> User: What is the weather like in Dallas?")
    await router_agent.run("What is the weather like in Dallas?")

if __name__ == "__main__":
    asyncio.run(main())
