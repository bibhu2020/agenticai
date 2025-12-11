import asyncio
import os
from dotenv import load_dotenv
from stock_analyst.aagents.agents import get_news_agent
from autogen_agentchat.messages import TextMessage

# Load env vars (ensure GEMINI_API_KEY is available if needed by the agent's internal logic, 
# though agents.py loads it globally, we might need to be sure)
load_dotenv()

async def run_debug():
    print("Initializing News Agent...")
    try:
        agent = get_news_agent()
        print("Agent initialized.")
        
        message = TextMessage(content="Find the latest news about Tesla (TSLA) stock.", source="user")
        print(f"Sending message: {message.content}")
        
        response = await agent.on_messages(
            [message],
            cancellation_token=None
        )
        
        print("\nResponse received:")
        print(f"Type: {type(response)}")
        print(f"Content: {response.chat_message.content}")
        
        # Check for tool calls in the response (inner messages)
        # on_messages returns a Response object which has 'chat_message'
        # To see tool calls, we might need to inspect the inner steps if possible, 
        # or just rely on the fact that if it calls a tool, the final response should contain news.
        
        if "Tesla" in str(response.chat_message.content):
            print("✅ Seems to have found info (or at least hallucinated relevance).")
        else:
            print("❌ Response seems generic.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Add src to sys.path to find stock_analyst
    import sys
    sys.path.append(os.path.join(os.getcwd(), "src"))
    asyncio.run(run_debug())
