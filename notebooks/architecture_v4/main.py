import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from patterns.swarm import AutoGenSystem

load_dotenv()

async def main():
    print("Optimization: Initializing Architecture V4 (AutoGen AgentChat 0.7+)...")
    
    # Initialize System
    system = AutoGenSystem(model_name="gpt-4o", provider="openai")
    
    # --- Scenario 1: Financial Query ---
    print("\n--- Scenario 1: Stock Price (Router -> FinanceAgent) ---")
    user_input = "What is the stock price of AAPL?"
    print(f"User: {user_input}")
    
    # Run
    await system.run_query(user_input)

    # --- Scenario 2: Web Query ---
    print("\n--- Scenario 2: Weather (Router -> WebAgent) ---")
    user_input = "What is the weather in Dallas?"
    print(f"User: {user_input}")
    
    await system.run_query(user_input)

if __name__ == "__main__":
    asyncio.run(main())
