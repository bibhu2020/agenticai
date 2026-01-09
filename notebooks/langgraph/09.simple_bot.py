from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from utility.llm_factory import LLMFactory
from langgraph.graph import StateGraph, START, END
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
load_dotenv()

# Define the State Schema
class AgentState(TypedDict):
    messages: List[HumanMessage]

# llm = LLMFactory.get_llm('openai', model_name="gpt-4o")
llm = LLMFactory.get_llm('openai', model_name="gpt-4o")

# Define node functions
def process(state: AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    print(f"\n AI: {response.content}")
    return state

# Define the graph
graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

# invoke the graph
user_input = input("Query: ")
while user_input != "exit":
    result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")
# print(result)
