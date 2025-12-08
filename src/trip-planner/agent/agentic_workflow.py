
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.graph.message import add_messages # Is reducer function that just aggregrates the messages.
from langgraph.prebuilt import ToolNode, tools_condition
from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import PlaceSearchTool
from tools.expense_calculator_tool import CalculatorTool
from tools.currency_conversion_tool import CurrencyConverterTool
from typing import TypedDict, Sequence, Optional, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from datetime import datetime

class AgentState(TypedDict):
    # messages is a list (or other sequence) of BaseMessage objects, and it has extra metadata attached to it: add_messages
    ## Sequence is a type hint that represents any ordered, iterable collection of items — like lists, tuples, or strings 
    ## Annotated type lets you attach metadata to a type. It's not used by Python itself, but frameworks (like LangGraph, Pydantic, FastAPI) can use it.
    messages: Annotated[Sequence[BaseMessage], add_messages]

class GraphBuilder():
    def __init__(self,model_provider: str = "openai"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        self.tools = []
        
        self.weather_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConverterTool()
        
        self.tools.extend([* self.weather_tools.weather_tool_list, 
                           * self.place_search_tools.place_search_tool_list,
                           * self.calculator_tools.calculator_tool_list,
                           * self.currency_converter_tools.currency_converter_tool_list])
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        
        self.system_prompt = SYSTEM_PROMPT
    
    
    def agent_function(self,state: MessagesState):
        """Main agent function"""
        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question
        # with mlflow.start_run(run_name="genai-trip-planner-llm-call", nested=True):
        response = self.llm_with_tools.invoke(input_question)
        return {"messages": [response]}
    
    def should_continue(self, state: AgentState) -> AgentState:
        messages = state['messages']
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"
    
    def build_graph(self):
        
        graph_builder=StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START,"agent")
        # graph_builder.add_conditional_edges("agent",tools_condition)
        graph_builder.add_conditional_edges(
            source="agent",
            path=self.should_continue,
            path_map={
                # Edge: Node
                "end": END,
                "continue": "tools"
            }
        )
        graph_builder.add_edge("tools","agent")
        # graph_builder.add_edge("agent",END)
        self.graph = graph_builder.compile()
        return self.graph
        
    def __call__(self):
        return self.build_graph()