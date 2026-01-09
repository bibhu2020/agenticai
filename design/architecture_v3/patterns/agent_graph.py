from typing import Literal, TypedDict, Annotated, List, Callable
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from layers.action import ActionLayer
from layers.cognition import CognitionLayer

# --- Handoff Helper ---
def create_handoff_tool(target_agent_name: str, description: str):
    """
    Creates a tool that signals a handoff to another agent.
    """
    @tool(f"transfer_to_{target_agent_name.lower()}")
    def handoff_tool() -> str:
        f"""
        Transfer control to the {target_agent_name}. {description}
        """
        # The content returned here is mostly for the LLM's history. 
        # The actual routing happens via Command in the graph.
        return f"Successfully transferred to {target_agent_name}."
    
    return handoff_tool

# --- Graph Builder ---

class MultiAgentSystem:
    def __init__(self, model_name="gpt-4o", provider="openai"):
        self.model = CognitionLayer.get_model(model_name, provider)
        self.actions = ActionLayer()
        
        # Define Tools
        self.finance_tools = self.actions.get_finance_tools()
        self.web_tools = self.actions.get_web_tools()
        
        # Define Handoffs (Router Only)
        self.t_finance = create_handoff_tool("FinanceAgent", "Use for stock price queries.")
        self.t_web = create_handoff_tool("WebAgent", "Use for weather, news, or general web search.")
        
        self.router_tools = [self.t_finance, self.t_web]

    def build_graph(self):
        """
        Builds the LangGraph StateGraph for the swarm.
        """
        
        # --- Node Definitions ---
        
        # 1. Router Node
        # We can use prebuilt_react_agent, but standard "call_model" is simpler primarily for routing.
        # But prebuilt handles tool calling logic (even for handoffs if we map them).
        
        # Actually, for Swarms in LangGraph 0.2+, best pattern is: 
        # Each agent is a node returns 'Command(goto="node_name")' if handoff called.
        
        def router_node(state: MessagesState) -> Command[Literal["finance_agent", "web_agent", "__end__"]]:
            msg = self.model.bind_tools(self.router_tools).invoke(state["messages"])
            
            # Check for tool calls
            if msg.tool_calls:
                call = msg.tool_calls[0]
                if call["name"] == "transfer_to_financeagent":
                    # Return Command to go to finance node
                    return Command(
                        update={"messages": [msg, ToolMessage(content="Transferred.", tool_call_id=call["id"])]},
                        goto="finance_agent"
                    )
                elif call["name"] == "transfer_to_webagent":
                    return Command(
                         update={"messages": [msg, ToolMessage(content="Transferred.", tool_call_id=call["id"])]},
                         goto="web_agent"
                    )
            
            # If no handoff, return final answer (END)
            return Command(update={"messages": [msg]}, goto=END)

        # 2. Finance Agent Node (ReAct)
        finance_agent = create_react_agent(self.model, self.finance_tools)
        
        def finance_node(state: MessagesState) -> Command[Literal["__end__"]]:
            # Run the agent (subgraph), usually we just invoke it
            result = finance_agent.invoke(state)
            # result["messages"] contains the new history
            # Return result and end
            return Command(update=result, goto=END)

        # 3. Web Agent Node (ReAct)
        web_agent = create_react_agent(self.model, self.web_tools)
        
        def web_node(state: MessagesState) -> Command[Literal["__end__"]]:
            result = web_agent.invoke(state)
            return Command(update=result, goto=END)

        # --- Graph Construction ---
        builder = StateGraph(MessagesState)
        
        builder.add_node("router", router_node)
        builder.add_node("finance_agent", finance_node)
        builder.add_node("web_agent", web_node)
        
        builder.add_edge(START, "router")
        
        return builder.compile()

