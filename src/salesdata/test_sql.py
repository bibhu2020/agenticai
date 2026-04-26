import asyncio
import os
import logging
from pathlib import Path
from agent import get_agent
from dotenv import load_dotenv

# Set logging to see SQL generation
logging.basicConfig(level=logging.INFO)

async def test_sql_query():
    print("--- Testing PostgreSQL (SQL) Hybrid Query ---")
    agent = get_agent()
    
    # Complex query: Semantic Mapping -> SQL Join -> Math
    query = "Which Enterprise customer in the North region spent the most on ergonomic work gear in 2024? and how much?"
    
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
    
    asyncio.run(test_sql_query())
