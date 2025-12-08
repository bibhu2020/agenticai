import os
import asyncio
from datetime import datetime
from typing import TypedDict, Sequence, Optional, Annotated, List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT

from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import PlaceSearchTool
from tools.expense_calculator_tool import CalculatorTool
from tools.currency_conversion_tool import CurrencyConverterTool


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class GraphBuilder:
    def __init__(self, model_provider: str = "openai"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()

        self.tools = []

        # Load tools
        self.weather_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConverterTool()

        # Register tools
        self.tools.extend([
            *self.weather_tools.weather_tool_list,
            *self.place_search_tools.place_search_tool_list,
            *self.calculator_tools.calculator_tool_list,
            *self.currency_converter_tools.currency_converter_tool_list
        ])

        # Bind LLM with tools
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)

        self.graph = None
        self.system_prompt = SYSTEM_PROMPT

    async def async_agent_function(self, state: MessagesState):
        """
        Async agent function that streams the LLM response.
        """
        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question

        full_response = ""
        async for chunk in self.llm_with_tools.astream(input_question):
            if isinstance(chunk, AIMessageChunk):
                content = chunk.content or ""
                full_response += content
                print(f"[LLM] {content}", end="", flush=True)

        print()  # newline after full message
        return {"messages": [chunk]}

    def should_continue(self, state: AgentState) -> str:
        """
        Decide whether to continue to tools or end the graph.
        """
        messages = state['messages']
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"

    def build_graph(self):
        """
        Build the LangGraph state machine with streaming.
        """
        graph_builder = StateGraph(MessagesState)

        # Add nodes
        graph_builder.add_node("agent", self.async_agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        # Add transitions
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges(
            source="agent",
            path=self.should_continue,
            path_map={
                "end": END,
                "continue": "tools"
            }
        )
        graph_builder.add_edge("tools", "agent")

        self.graph = graph_builder.compile()
        return self.graph

    async def stream(self, user_input: str):
        """
        Stream the response end-to-end from graph.
        """
        if self.graph is None:
            self.build_graph()

        print(f"[User] {user_input}\n")
        async for event in self.graph.astream(
            {"messages": [HumanMessage(content=user_input)]},
            config=RunnableConfig()
        ):
            if 'messages' in event:
                for msg in event['messages']:
                    print(f"\n[Tool/Final] {msg.content}\n")


    async def __call__(self, user_input: str) -> str:
        if self.graph is None:
            self.build_graph()

        final_output = ""

        async for event in self.graph.astream(
            {"messages": [HumanMessage(content=user_input)]},
            config=RunnableConfig()
        ):
            if "messages" in event:
                for msg in event["messages"]:
                    final_output = msg.content  # only keep last
                    print(f"[Tool/LLM] {msg.content}")

        return final_output
