import asyncio
from typing import Any, Dict, List
from agents import Runner
from common.aagents.search_agent import search_agent
from common.aagents.news_agent import news_agent
from common.aagents.yf_agent import yf_agent

class ActionLayer:
    """
    The 'Hands' of the agent.
    Responsibility: Execute specific, well-defined tools or side-effects.
    Does NOT reason about 'why'.
    """
    
    def __init__(self):
        # Register available tools
        self.tools = {
            "web_search": self._tool_web_search,
            "financial_data": self._tool_financial_data,
            "news_search": self._tool_news_search,
            "broadcast_research": self._tool_broadcast_research
        }
    
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        
        print(f"[Action] Executing tool: {tool_name} with args: {args}")
        try:
            return await self.tools[tool_name](**args)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    async def _tool_web_search(self, query: str) -> str:
        result = await Runner.run(search_agent, query)
        return f"Web Search Result:\n{result.final_output}"

    async def _tool_financial_data(self, query: str) -> str:
        result = await Runner.run(yf_agent, query)
        return f"Financial Data:\n{result.final_output}"

    async def _tool_news_search(self, query: str) -> str:
        result = await Runner.run(news_agent, query)
        return f"News Result:\n{result.final_output}"

    async def _tool_broadcast_research(self, query: str, include_finance: bool = True, include_news: bool = True, include_search: bool = True) -> str:
        """
        Broadcasts the search query to selected specialized agents in parallel and aggregates their responses.
        """
        active_agents = []
        if include_finance: active_agents.append(("YahooFinanceAgent", Runner.run(yf_agent, query)))
        if include_news: active_agents.append(("NewsAgent", Runner.run(news_agent, query)))
        if include_search: active_agents.append(("WebSearchAgent", Runner.run(search_agent, query)))

        if not active_agents:
            return "No agents were selected for this query."

        # Run in parallel
        agent_names = [name for name, _ in active_agents]
        coroutines = [coro for _, coro in active_agents]
        
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        outputs = []
        for name, res in zip(agent_names, results):
            if isinstance(res, Exception):
                outputs.append(f"❌ {name} Error: {str(res)}")
            else:
                outputs.append(f"✅ {name} Report:\n{res.final_output}")
                
        return "\n--- START OF AGENT REPORTS ---\n\n" + "\n\n-----------------------------------\n\n".join(outputs) + "\n\n--- END OF AGENT REPORTS ---"
