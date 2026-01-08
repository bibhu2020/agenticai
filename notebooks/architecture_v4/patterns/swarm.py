from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from layers.config import get_model_client
from layers.tools import mock_search_web, mock_get_stock_price

class AutoGenSystem:
    def __init__(self, model_name="gpt-4o", provider="openai"):
        self.model_client = get_model_client(model_name, provider)
        
        # 1. Define Specialized Agents
        # Note: In new AutoGen, tools are passed directly to the Agent constructor
        
        self.finance_agent = AssistantAgent(
            name="FinanceAgent",
            system_message="You are a finance specialist. Use the 'mock_get_stock_price' tool to answer queries about stock prices.",
            model_client=self.model_client,
            tools=[mock_get_stock_price]
        )
        
        self.web_agent = AssistantAgent(
            name="WebAgent",
            system_message="You are a web researcher. Use the 'mock_search_web' tool to find weather, news, or general info.",
            model_client=self.model_client,
            tools=[mock_search_web]
        )
        
        # The User Proxy in legacy is often replaced by just the User or managed by the Team runner.
        # But here we just need a Team of agents.
        # We can implement a "Planner" or "Router" agent if needed, or rely on SelectorGroupChat to select.
        
        self.planning_agent = AssistantAgent(
            name="PlanningAgent",
            description="A planner that determines which agent should act.",
            system_message="You are a router. Route to FinanceAgent for stocks, WebAgent for others.",
            model_client=self.model_client,
        )

        # 2. Define the Team (SelectorGroupChat)
        # This uses an LLM to select the next speaker.
        
        self.termination = TextMentionTermination("TERMINATE")
        
        # We create a team.
        # Note: In 0.4, we define a list of participants.
        self.team = SelectorGroupChat(
            [self.planning_agent, self.finance_agent, self.web_agent],
            model_client=self.model_client,
            termination_condition=self.termination,
            selector_prompt="Select the next agent based on the conversation. 'FinanceAgent' for stocks, 'WebAgent' for search. Return only the agent name."
        )

    async def run_query(self, message: str, stream_callback=None):
        """
        Runs the team with the given message.
        Support streaming callback if provided.
        """
        # Run the team
        # The new API returns a stream of events usually.
        # run_stream() yields TaskResult or content updates.
        
        async for valid_chunk in self.team.run_stream(task=message):
             # In 0.4, chunks can be AgentResponse, TaskResult, etc.
             # We try to extract text delta if possible, or print full messages.
             
             # For simplicity in this demo, strict type checking might be tricky without inspection.
             # We just assume we can cast to string or get specific attributes.
             
             if hasattr(valid_chunk, "content"):
                 # It's likely a message
                 content = getattr(valid_chunk, "content", "")
                 source = getattr(valid_chunk, "source", "Unknown")
                 
                 output_text = f"\n[{source}]: {content}"
                 
                 if stream_callback:
                     stream_callback(output_text)
                 else:
                     print(output_text)
             
             # Check for final result
             # if isinstance(valid_chunk, TaskResult): ...
