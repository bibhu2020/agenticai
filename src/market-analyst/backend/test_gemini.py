import asyncio
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from common.utility.autogen_model_factory import AutoGenModelFactory
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

async def test_gemini_selection():
    model_client = AutoGenModelFactory.get_model(
        provider="google",
        model_name="gemini-2.0-flash",
        temperature=0
    )
    
    a = AssistantAgent("AgentA", model_client, system_message="User wants to say hi.")
    b = AssistantAgent("AgentB", model_client, system_message="You say hello back.")
    
    team = SelectorGroupChat(
        [a, b],
        model_client=model_client,
        termination_condition=MaxMessageTermination(2),
        selector_prompt="Select AgentA first, then AgentB."
    )
    
    print("Starting team run...")
    async for message in team.run_stream(task="Say hello"):
        print(f"[{getattr(message, 'source', 'System')}] {getattr(message, 'content', '')}")

if __name__ == "__main__":
    asyncio.run(test_gemini_selection())
