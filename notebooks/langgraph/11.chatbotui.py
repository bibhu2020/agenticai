from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from utility.llm_factory import LLMFactory
from langgraph.graph import StateGraph, START, END
import streamlit as st


# Initialize LLM
# llm = LLMFactory.get_llm('openai', model_name="gpt-4o")
llm = LLMFactory.get_llm('groq')

# Define the State Schema
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

# Define node functions
def process(state: AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=response.content))
    # print(f"\nAI: {response.content}")
    return state

# Define the graph
graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

# --- Streamlit UI ---
st.set_page_config(page_title="LangGraph Chatbot", page_icon="💬")
st.title("💬 Chatbot Interface")
st.write("Chat with your LangGraph-powered assistant!")

# --- Add session state for conversation ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# --- Display chat history from the session ---
for msg in st.session_state.conversation:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# --- Input box ---
if prompt := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to conversation
    st.session_state.conversation.append(HumanMessage(content=prompt))
    
    # Run the graph
    result = agent.invoke({"messages": st.session_state.conversation})
    st.session_state.conversation = result["messages"]

    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(result["messages"][-1].content)

#store the chat in a local text file
with open("chat.txt", "w") as file:
    file.write("Your conversation log: \n")

    for message in st.session_state.conversation:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n")

    file.write("End of coversation.")

# streamlit run 11.chatbotui.py