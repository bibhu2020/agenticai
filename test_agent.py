
import os
import agents
from agents import Agent, run

print("Imported successfully")

# Mock simple agent
agent = Agent(name="Test", instructions="You are a helpful bot.", model="gpt-4o-mini")
print("Agent created")

# We won't run it yet as we might need api key.
# accessing env to check key presence (not value)
if "OPENAI_API_KEY" in os.environ:
    print("Key present")
else:
    print("Key missing")
