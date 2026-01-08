import streamlit as st
import os
import sys
import asyncio
from typing import List
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth.transport.requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import V3 components
from patterns.agent_graph import MultiAgentSystem
from langchain_core.messages import HumanMessage, AIMessage

# --- Configuration ---
# Point to the existing client_seek inside architecture_v2 to avoid duplication
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(BASE_DIR, "../architecture_v2/client_secret.json"))
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- Google Auth Functions (Reused) ---
def get_flow():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        st.error(f"Client Secrets file not found at: {CLIENT_SECRETS_FILE}")
        st.stop()
        
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501/"
    )
    return flow

def authenticate_user():
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None

    if st.session_state.credentials:
        creds = st.session_state.credentials
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                st.session_state.credentials = creds
            except Exception as e:
                st.session_state.credentials = None
                st.error(f"Error refreshing token: {e}")
        
    if not st.session_state.credentials:
        query_params = st.query_params
        code = query_params.get("code")

        if code:
            try:
                flow = get_flow()
                flow.fetch_token(code=code)
                st.session_state.credentials = flow.credentials
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
        else:
            flow = get_flow()
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.markdown(f'<a href="{auth_url}" target="_self"><button>Login with Google</button></a>', unsafe_allow_html=True)
            st.stop()

    return st.session_state.credentials

# --- Graph Initialization ---
def initialize_graph():
    if 'graph' not in st.session_state:
        # We can allow model selection in sidebar later, for now defaults
        system = MultiAgentSystem(model_name="gpt-4o", provider="openai")
        st.session_state.graph = system.build_graph()

def convert_messages(messages: List[dict]):
    """Convert session state dict messages to LangChain BaseMessage objects."""
    langchain_msgs = []
    for m in messages:
        if m["role"] == "user":
            langchain_msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            langchain_msgs.append(AIMessage(content=m["content"]))
    return langchain_msgs

# --- Main App ---
def main():
    st.set_page_config(page_title="Agentic AI V3 (LangGraph)", page_icon="🕸️")
    st.title("🕸️ Agentic AI V3: LangGraph Swarm")
    
    creds = authenticate_user()
    if creds:
        st.sidebar.success("Logged in.")
        if st.sidebar.button("Logout"):
            st.session_state.credentials = None
            st.rerun()
            
    initialize_graph()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about stocks or weather..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            
            try:
                # Prepare state
                history = convert_messages(st.session_state.messages)
                
                # Execute Graph
                # invoke returns the final state
                result = asyncio.run(st.session_state.graph.ainvoke({"messages": history}))
                
                # Get the last message (which should be the final answer)
                last_msg = result["messages"][-1]
                response_text = last_msg.content
                
                placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                placeholder.error(f"Error: {e}")

if __name__ == "__main__":
    main()
