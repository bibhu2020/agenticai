from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from utility.llm_factory import LLMFactory
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
load_dotenv()

# Define the State Schema
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

llm = LLMFactory.get_llm('openai', model_name="gpt-4o")
# llm = LLMFactory.get_llm('groq')

# Define node functions
def process(state: AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}")
    return state

# Define the graph
graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

# invoke the graph
conversation_history=[]
user_input = input("Human: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})
    # print(result)
    conversation_history = result['messages']
    user_input = input("Human: ")
# print(result)
