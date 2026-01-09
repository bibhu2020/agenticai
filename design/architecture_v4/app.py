import streamlit as st
import os
import sys
import asyncio
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth.transport.requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import V4 components
from patterns.swarm import AutoGenSystem

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(BASE_DIR, "../architecture_v2/client_secret.json"))
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- Google Auth (Reused) ---
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

# --- AutoGen Initialization ---
def initialize_autogen():
    if 'autogen_system' not in st.session_state:
        st.session_state.autogen_system = AutoGenSystem(model_name="gpt-4o", provider="openai")

# --- Main App ---
def main():
    st.set_page_config(page_title="Agentic AI V4 (AutoGen)", page_icon="🤖")
    st.title("🤖 Agentic AI V4: AutoGen Swarm (New API)")
    
    creds = authenticate_user()
    if creds:
        st.sidebar.success("Logged in.")
        if st.sidebar.button("Logout"):
            st.session_state.credentials = None
            st.rerun()
            
    initialize_autogen()

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
            full_response = ""
            
            # Since AutoGen 0.4 API yields message objects we can handle them asynchronously
            # We don't need ContextManager redirect_stdout anymore!
            
            try:
                async def run_chat():
                    nonlocal full_response
                    # We pass a callback to append text
                    def stream_cb(text):
                         nonlocal full_response
                         full_response += text
                         placeholder.markdown(full_response)
                         
                    await st.session_state.autogen_system.run_query(prompt, stream_cb)
                
                asyncio.run(run_chat())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                placeholder.error(f"Error: {e}")

if __name__ == "__main__":
    main()
