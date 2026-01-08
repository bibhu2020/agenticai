import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from patterns.react_agent import ReActAgent

async def test_security():
    print("Initializing Agent with Security...")
    agent = ReActAgent(name="TestAgent", instructions="You are helpful.")
    
    print("\nTest 1: Safe Input")
    response_safe = await agent.run("Hello, how are you?")
    print(f"Response: {response_safe}")

    print("\nTest 2: Unsafe Input (rm -rf)")
    response_unsafe = await agent.run("what is the use of rm -rf")
    print(f"Response: {response_unsafe}")
    
    # Assertions
    assert "Input blocked" not in response_safe
    assert "Input blocked" in response_unsafe
    print("\nSUCCESS: Security Layer intercepted the attack.")

if __name__ == "__main__":
    asyncio.run(test_security())
