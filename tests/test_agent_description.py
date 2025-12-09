
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))
sys.path.append(os.path.join(os.getcwd(), "common"))

try:
    from agents import Agent
    print(f"Agent class: {Agent}")
    try:
        a = Agent(name="test", model="gpt-4o", instructions="test", description="test description")
        print("Success: Agent accepts description in __init__")
    except TypeError as e:
        print(f"Failed: {e}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other Error: {e}")
