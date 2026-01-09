from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage # base message class
from langchain_core.messages import SystemMessage # provides instructions to LLM
from langchain_core.messages import HumanMessage 
from langchain_core.messages import ToolMessage # passes data back to LLM after it calls a tool
from langchain_core.tools import tool # a decorate that tells the function is a tool function.

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages # Is reducer function that just aggregrates the messages.
from langgraph.prebuilt import ToolNode

from utility.llm_factory import LLMFactory
import streamlit as st

# Create state schema
class AgentState(TypedDict):
    # messages is a list (or other sequence) of BaseMessage objects, and it has extra metadata attached to it: add_messages
    ## Sequence is a type hint that represents any ordered, iterable collection of items — like lists, tuples, or strings 
    ## Annotated type lets you attach metadata to a type. It's not used by Python itself, but frameworks (like LangGraph, Pydantic, FastAPI) can use it.
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Define tool functions
@tool
def add(a: int, b: int):
    """
    This is an addition function that adds 2 numbers together.
    """
    return a + b;

@tool
def substract(a: int, b: int):
    """
    This is a substract function that substract 2 numbers.
    """
    return a - b;

@tool
def multiply(a: int, b: int):
    """
    This is an addition function that adds 2 multiply together.
    """
    return a * b;

tools = [add, substract, multiply]

llm = LLMFactory.get_llm('groq')
llm = llm.bind_tools(tools)

# llm = ChatOpenAI(model="gpt-4o")
# llm = llm.bind_tools(tools)


# Define node functions
def model_call(state: AgentState) -> AgentState:
    # system_promt = SystemMessage(content="You are an assistant. Answer my query based to your ability.")
    system_promt = SystemMessage(
        content=(
            "You are an assistant. Answer my query based to your ability."
        )
    )
    response = llm.invoke([system_promt] + state['messages'])
    return {"messages": [response]} # add_message() takes care of appending the message

def should_continue(state: AgentState) -> AgentState:
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
# Define the graphs
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

graph.add_edge(START, "our_agent")

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.add_conditional_edges(
    source="our_agent",
    path=should_continue,
    path_map={
        # Edge: Node
        "end": END,
        "continue": "tools"
    }
)

graph.add_edge("tools", "our_agent")

app = graph.compile()

# Save the graph visualization to disk as an image (e.g., PNG)
# Assuming you have already created and compiled your graph as 'app'
png_graph = app.get_graph().draw_mermaid_png() 

# Save the PNG file
with open("my_graph.png", "wb") as f:
    f.write(png_graph)



def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# inputs = {"messages": [("user", "Add 40 + 12 and then multiply the result by 6. Also tell me a joke please.")]}
inputs = {"messages": HumanMessage(content="Add 40 + 12 and then mupltiply the result by 6. Also tell me a joke please.")}
print_stream(app.stream(inputs, stream_mode="values"))


