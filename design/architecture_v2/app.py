import streamlit as st
import os
import sys
import asyncio
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google.auth.transport.requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import Agent architecture components
from layers.action import ActionLayer
from patterns.react_agent import ReActAgent

# --- Configuration ---
# Calculate absolute path to client_secret.json ensuring it's found regardless of CWD.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

# Ensure HTTPS for local dev (required by OAuthlib)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- Google Auth Functions ---

def get_flow():
    """Builds and returns the OAuth flow."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501/"  # Streamlit default port
    )
    return flow

def authenticate_user():
    """Handles the authentication flow in Streamlit."""
    
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None

    # Check if we have valid credentials in session
    if st.session_state.credentials:
        creds = st.session_state.credentials
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                st.session_state.credentials = creds
            except Exception as e:
                st.session_state.credentials = None # Force re-login
                st.error(f"Error refreshing token: {e}")
        
    # If still no credentials, show login button
    if not st.session_state.credentials:
        # Check query params for auth code (returned from Google)
        # Streamlit 1.0+ uses st.query_params
        query_params = st.query_params
        code = query_params.get("code")

        if code:
            # Exchange code for token
            try:
                flow = get_flow()
                flow.fetch_token(code=code)
                creds = flow.credentials
                st.session_state.credentials = creds
                # Clear query params to prevent re-use
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
        else:
            # Display Login Button
            flow = get_flow()
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            st.markdown(f'''
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #4285F4; 
                        color: white; 
                        padding: 10px 20px; 
                        border: none; 
                        border-radius: 5px; 
                        cursor: pointer;
                        font-size: 16px;">
                        Login with Google
                    </button>
                </a>
                ''', unsafe_allow_html=True)
            st.stop() # Stop execution until logged in

    return st.session_state.credentials

# --- Agent Logic ---

def initialize_agents():
    """Initialize the multi-agent system."""
    if 'router_agent' not in st.session_state:
        actions = ActionLayer()
        
        finance_agent = ReActAgent(
            name="FinanceAgent", 
            tools=actions.get_finance_tools(),
            instructions="You are a finance specialist. Use 'mock_get_stock_price' for stock queries."
        )
        
        web_agent = ReActAgent(
            name="WebResearcher", 
            tools=actions.get_web_tools(),
            instructions="You are a web researcher. MUST use 'mock_search_web' tool for queries."
        )
        
        router_agent = ReActAgent(
            name="Router", 
            handoffs=[finance_agent.agent, web_agent.agent],
            instructions="You are a Router. Redirect to 'FinanceAgent' (stocks) or 'WebResearcher' (weather/news). Transfer immediately."
        )
        st.session_state.router_agent = router_agent

# --- Main App ---

def main():
    st.set_page_config(page_title="Agentic AI Chatbot", page_icon="🤖")
    
    st.title("🤖 Agentic AI Interface")
    
    # 1. Authentication
    creds = authenticate_user()
    
    # User Profile (Optional display)
    if creds:
        # We can fetch user info here if needed
        st.sidebar.success("Logged in successfully!")
        
        if st.sidebar.button("Reset Agents (Clear Memory)"):
            if 'router_agent' in st.session_state:
                del st.session_state.router_agent
            st.rerun()
            
        if st.sidebar.button("Logout"):
            st.session_state.credentials = None
            st.rerun()

    # 2. Agent Initialization
    initialize_agents()
    
    # 3. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Ask about stocks or weather..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Agent Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Run Agent Loop
            try:
                # We need to run async agent in Streamlit's sync environment
                response = asyncio.run(st.session_state.router_agent.run(prompt))
                full_response = response
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {str(e)}"
                message_placeholder.error(full_response)
        
        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
