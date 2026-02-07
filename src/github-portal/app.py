
import streamlit as st
import os
import sys
import uuid
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
env_path = project_root / ".env"

# Load env vars
load_dotenv(dotenv_path=env_path, override=True)

# Add src to path for mcp_telemetry and other shared modules
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Add project root for common and agents packages
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add current dir for agent and bridge
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from agent import github_agent
from agents import Runner, SQLiteSession
from mcp_bridge import bridge

st.set_page_config(page_title="GitHub Portal AGENT", page_icon="🐙", layout="wide")

# Theme & Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-color: #030712;
        --surface-color: #0f172a;
        --glass-bg: rgba(15, 23, 42, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    .stApp {
        background-color: var(--bg-color);
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 100% 100%, rgba(139, 92, 246, 0.12) 0%, transparent 40%);
        background-attachment: fixed;
        color: var(--text-primary);
    }

    [data-testid="stSidebar"] {
        background-color: rgba(3, 7, 18, 0.95) !important;
        border-right: 1px solid var(--glass-border);
    }

    .compact-header {
        display: flex;
        align-items: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid var(--glass-border);
        margin-bottom: 2rem;
        gap: 1rem;
    }

    .compact-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #fff;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .compact-status {
        margin-left: auto;
        font-size: 0.8rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: var(--success, #10b981);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--success, #10b981);
    }

    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 1.25rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .glass-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
    }

    h1, h2, h3, h4 { font-family: 'Outfit', sans-serif; font-weight: 700; color: #fff; }
    p, span, div { font-family: 'Inter', sans-serif; }

    /* Hide default Streamlit headers and footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        background-color: transparent;
        border-radius: 4px;
        color: var(--text-secondary);
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent-primary) !important;
        border-bottom-color: var(--accent-primary) !important;
    }

    /* Style inputs */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--glass-border) !important;
        color: #fff !important;
        border-radius: 8px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.5rem 1rem !important;
        width: 100%;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Compact Header
st.markdown(f"""
<div class="compact-header">
    <div class="compact-title">SENTINEL HUB</div>
    <div class="compact-status">
        <div class="status-dot"></div>
        <span>SENTINEL ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "ai_session" not in st.session_state:
    st.session_state.ai_session = SQLiteSession(f"github_portal_{st.session_state.session_id}.db")

# Sidebar
with st.sidebar:
    st.header("🏢 Organization")
    owner = st.text_input("Owner / Org", value=os.environ.get("GITHUB_OWNER", "bibhu2020")).strip()
    
    st.markdown("---")
    st.subheader("🌐 Global Connection")
    if st.button("Verify Remote MCP"):
        try:
            async def test_conn():
                await bridge.connect()
                return await bridge.session.list_tools()
            tools = asyncio.run(test_conn())
            st.success(f"Connected! {len(tools.tools)} tools online.")
        except Exception as e:
            st.error(f"Offline: {str(e)}")

    if st.button("🗑️ Reset Analysis"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.ai_session = SQLiteSession(f"github_portal_{st.session_state.session_id}.db")
        st.rerun()

# Main Tabs
tab_ov, tab_chat = st.tabs(["🏢 Org Overview", "💬 Agentic Analysis"])

with tab_ov:
    st.subheader(f"Repositories for {owner}")
    try:
        async def fetch_repos():
            await bridge.connect()
            import json
            # call_tool returns list of content objects
            content_list = await bridge.call_tool("list_repositories", {})
            if content_list and hasattr(content_list[0], 'text'):
                return json.loads(content_list[0].text)
            return content_list
            
        with st.spinner("Fetching organization data..."):
            repos_data = asyncio.run(fetch_repos())
            
            # Simple list display for overview
            if isinstance(repos_data, list):
                cols = st.columns(3)
                for idx, repo in enumerate(repos_data):
                    if not isinstance(repo, dict): continue
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="glass-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <h4 style="margin:0; color:var(--accent-primary);">{repo.get('name')}</h4>
                                <span style="background: rgba(59, 130, 246, 0.1); color: var(--accent-primary); padding: 2px 8px; border-radius: 6px; font-size: 0.7rem;">{repo.get('language') or 'Mixed'}</span>
                            </div>
                            <p style="font-size:0.85rem; color:var(--text-secondary); margin:1rem 0; min-height: 3em;">{repo.get('description') or 'No description provided for this repository.'}</p>
                            <div style="display: flex; gap: 1rem; border-top: 1px solid var(--glass-border); padding-top: 1rem; font-size: 0.8rem; color: var(--text-primary);">
                                <span>⭐ {repo.get('stars')}</span>
                                <span>🍴 {repo.get('forks')}</span>
                                <span style="margin-left: auto; color: var(--text-secondary);">{repo.get('updated_at')[:10]}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No repositories found or format unrecognized.")
    except Exception as e:
        st.warning(f"Could not load repository list: {str(e)}")
        st.info("💡 Ensure you have redeployed the remote 'mcp-github' server with the latest code including the 'list_repositories' tool.")

with tab_chat:
    st.subheader("Interactive Analysis")
    # Display Chat
    for msg in st.session_state.messages:
        role_label = "SENTINEL" if msg["role"] == "assistant" else "USER"
        border_color = "var(--accent-primary)" if msg["role"] == "assistant" else "var(--text-secondary)"
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid {border_color};">
            <div style="font-size: 0.7rem; color: {border_color}; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: 1px;">{role_label}</div>
            <div style="font-family: 'Inter', sans-serif;">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

    # Chat Input
    if prompt := st.chat_input("Ask about any repository or global health..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent analyzing..."):
                try:
                    # Provide global context
                    full_prompt = f"Owner: {owner}. Query: {prompt}"
                    
                    async def run_agent():
                        await bridge.connect()
                        result = await Runner.run(github_agent, full_prompt, session=st.session_state.ai_session)
                        return result.final_output
                    
                    response = asyncio.run(run_agent())
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid var(--accent-primary);">
                        <div style="font-size: 0.7rem; color: var(--accent-primary); font-weight: 800; margin-bottom: 0.5rem; letter-spacing: 1px;">SENTINEL</div>
                        <div style="font-family: 'Inter', sans-serif;">{response}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Analysis Error: {str(e)}")
