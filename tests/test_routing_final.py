
import sys
import os
import asyncio

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))
sys.path.append(os.path.join(os.getcwd(), "common"))

async def test():
    print("--- Testing Agent Setup ---")
    try:
        from common.aagents.google_agent import google_agent
        print(f"✅ Google Agent Imported: {google_agent.name}")
        print(f"   Description: {getattr(google_agent, 'description', 'MISSING')}")
        print(f"   Tools count: {len(google_agent.tools)}")
        print(f"   Instructions length: {len(google_agent.instructions)}")

        from common.aagents.news_agent import news_agent
        print(f"✅ News Agent Imported: {news_agent.name}")
        print(f"   Description: {getattr(news_agent, 'description', 'MISSING')}")
        
        from src.chatbot.appagents.OrchestratorAgent import orchestrator_agent
        print("✅ OrchestratorAgent Imported form src.chatbot.appagents")
        
        # Test routing prompt construction logic manually
        handoffs = [google_agent, news_agent]
        agent_descriptions = "\n".join([f"- {a.name}: {a.description}" for a in handoffs])
        print("✅ Routing Prompt Description Block:")
        print(agent_descriptions)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
