import asyncio
import os
import logging
from pathlib import Path
from agent import get_agent
from dotenv import load_dotenv

# Set logging to see agent thoughts
logging.basicConfig(level=logging.INFO)

async def test_hybrid_query():
    print("--- Testing Hybrid (Semantic + Analytical) Query ---")
    agent = get_agent()
    
    # Fuzzy query that requires semantic mapping
    query = "What is the total sales for our tools designed for virtual meetings in 2024?"
    
    print(f"Query: {query}\n")
    
    # Run the agent
    handler = agent.run(user_msg=query)
    response = await handler
    
    print("\n--- Agent Response ---")
    print(response.response.content)
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(dotenv_path=ROOT_DIR / ".env")
    
    asyncio.run(test_hybrid_query())
