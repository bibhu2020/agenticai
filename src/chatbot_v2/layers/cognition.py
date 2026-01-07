import json
import os
from typing import List, Dict, Optional
from common.utility.openai_model_factory import OpenAIModelFactory
from openai import OpenAI, AsyncOpenAI

class CognitiveOutput:
    def __init__(self, thought: str, action: Optional[str] = None, action_input: Optional[Dict] = None, final_answer: Optional[str] = None):
        self.thought = thought
        self.action = action
        self.action_input = action_input
        self.final_answer = final_answer

class CognitionLayer:
    """
    The 'Brain' of the agent.
    Uses OpenAI GPT-4o (via OpenAIModelFactory) to reason and decide which tools to use.
    """
    
    
    def __init__(self):
        # Direct OpenAI client usage for maximum compatibility
        # We circumvent the factory wrapper to access the raw client directly for JSON mode
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        
        # If we wanted to use the factory strictly, we'd need to know the exact internal attribute
        # self.model_wrapper = OpenAIModelFactory.get_model(...)
        # self.client = self.model_wrapper.client  # guessing 'client' vs 'openai_client'
        # But to be safe and fix the user's error immediately:
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)

        self.model_name = "gpt-4o"
        
        self.system_prompt = """
You are the **AI Chat Orchestrator**. 
Your goal is to provide a comprehensive, multi-perspective answer by synthesizing data from specialized sub-agents.

**Available Tools**:
1. `broadcast_research(query: str, include_finance: bool, include_news: bool, include_search: bool)`: 
   Broadcasts the query to specialized agents (Finance, News, Web Search). Use this for complex queries needing external info.
2. `web_search(query: str)`: Single web search.
3. `financial_data(query: str)`: Single financial check.
4. `news_search(query: str)`: Single news check.

**Workflow**:
1.  **Analyze Request**: Understand the user's question.
2.  **Determine Needs**: Decide calls are needed.
    *   **Finance**: For stock prices, market trends, company financials.
    *   **News**: For recent events, headlines.
    *   **Web Search**: For general knowledge, history.
3.  **Action**: 
    If you need external info, PREFER `broadcast_research` to query multiple sources in parallel.
    If it's a simple greeting or general chat not requiring data, just answer.
4.  **Synthesize Results**: 
    When you receive tool outputs ("Agent Reports"), combine them into a clear, professional summary.
    Do NOT simply paste the reports. Synthesize them.

**Output Format**:
You must output valid JSON only:
{
  "thought": "Reasoning...",
  "action": "tool_name_or_null",
  "action_input": { "arg": "value" } or null,
  "final_answer": "Final output to user" or null
}
"""

    async def decide(self, history: List[Dict[str, str]]) -> CognitiveOutput:
        # 1. Construct Messages
        messages = [{"role": "system", "content": self.system_prompt}]
        
        for entry in history:
            role = entry['role']
            content = entry['content']
            
            # Map roles. 'system' in our history layer usually means tool output.
            if role == 'user':
                messages.append({"role": "user", "content": content})
            elif role == 'assistant':
                messages.append({"role": "assistant", "content": content})
            elif role == 'system':
                messages.append({"role": "user", "content": f"Observation/Tool Output: {content}"})

        # 2. Call LLM (Async)
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            if response_text.startswith("```"):
                response_text = response_text.strip("`").replace("json", "").strip()

            data = json.loads(response_text)
            
            return CognitiveOutput(
                thought=data.get("thought", ""),
                action=data.get("action"),
                action_input=data.get("action_input"),
                final_answer=data.get("final_answer")
            )
            
        except Exception as e:
            return CognitiveOutput(
                thought=f"Error: {str(e)}",
                final_answer="I encountered an error processing your request."
            )
