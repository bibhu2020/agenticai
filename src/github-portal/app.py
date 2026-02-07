
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

# Theme & Styling - "Command Center" v2
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;700&family=Fira+Code:wght@400;500&display=swap');

    :root {
        --bg-main: #09090b;
        --bg-card: #18181b;
        --border-color: #27272a;
        --accent: #3b82f6;
        --accent-glow: rgba(59, 130, 246, 0.15);
        --text-color: #f4f4f5;
        --text-dim: #a1a1aa;
    }

    .stApp {
        background-color: var(--bg-main);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }

    /* Top Navigation Bar */
    .top-bar {
        display: flex;
        align-items: center;
        padding: 0.75rem 1.5rem;
        background: var(--bg-card);
        border-bottom: 1px solid var(--border-color);
        position: sticky;
        top: 0;
        z-index: 999;
        margin: -4rem -5rem 2rem -5rem;
    }

    .brand {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #fff;
        font-size: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .brand span {
        color: var(--accent);
    }

    .system-status {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-dim);
        letter-spacing: 0.5px;
    }

    .pulse-dot {
        width: 6px;
        height: 6px;
        background: var(--accent);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--accent);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.2); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        padding: 0.25rem;
        background: var(--bg-card);
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        color: var(--text-dim);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.05);
        color: #fff !important;
    }

    /* Grid Cards */
    .sentinel-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
        height: 100%;
        transition: all 0.2s ease;
    }

    .sentinel-card:hover {
        border-color: var(--accent);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px var(--accent-glow);
        transform: translateY(-2px);
    }

    .card-id {
        font-family: 'Fira Code', monospace;
        font-size: 0.7rem;
        color: var(--accent);
        margin-bottom: 0.5rem;
    }

    /* Chat Bubbles */
    .user-bubble {
        background: transparent;
        border: 1px solid var(--border-color);
        border-radius: 12px 12px 0 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        max-width: 85%;
        margin-left: auto;
    }

    .ai-bubble {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-left: 2px solid var(--accent);
        border-radius: 12px 12px 12px 0;
        padding: 1rem;
        margin-bottom: 1rem;
        max-width: 85%;
    }

    .bubble-meta {
        font-size: 0.65rem;
        color: var(--text-dim);
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Sidebar Fixes */
    [data-testid="stSidebar"] {
        background-color: #0c0c0e !important;
        border-right: 1px solid var(--border-color);
    }

    /* Hide default Streamlit bits */
    header, footer { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown("""
<div class="top-bar">
    <div class="brand">GITHUB<span>SENTINEL</span></div>
    <div class="system-status">
        <div class="pulse-dot"></div>
        NEURAL LINK ACTIVE
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
    st.markdown("### 🛠️ CORES")
    owner = st.text_input("ENTITY / OWNER", value=os.environ.get("GITHUB_OWNER", "bibhu2020")).strip()
    
    st.markdown("---")
    st.markdown("### ⚡ QUICK LINKS")
    if st.button("DIAGNOSE MCP"):
        try:
            async def test_conn():
                await bridge.connect()
                return await bridge.session.list_tools()
            tools = asyncio.run(test_conn())
            st.success(f"ONLINE: {len(tools.tools)} Toolmaps")
        except Exception as e:
            st.error(f"OFFLINE: {str(e)}")

    if st.button("PURGE SESSION"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.ai_session = SQLiteSession(f"github_portal_{st.session_state.session_id}.db")
        st.rerun()

# Layout
tab_ov, tab_sentinel = st.tabs(["📊 ASSET OVERVIEW", "�️ SENTINEL COMMAND"])

with tab_ov:
    st.markdown(f"#### Managed Assets: `{owner}`")
    try:
        async def fetch_repos():
            await bridge.connect()
            import json
            content_list = await bridge.call_tool("list_repositories", {})
            if content_list and hasattr(content_list[0], 'text'):
                return json.loads(content_list[0].text)
            return content_list
            
        with st.spinner("Decoding asset tree..."):
            repos_data = asyncio.run(fetch_repos())
            
            if isinstance(repos_data, list):
                cols = st.columns(3)
                for idx, repo in enumerate(repos_data):
                    if not isinstance(repo, dict): continue
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="sentinel-card">
                            <div class="card-id">ID: {repo.get('name').upper()[:12]}</div>
                            <h4 style="margin:0;">{repo.get('name')}</h4>
                            <p style="font-size:0.8rem; color:var(--text-dim); margin:0.75rem 0; min-height: 2.5em;">
                                {repo.get('description') or 'Data encryption standard. No description found.'}
                            </p>
                            <div style="font-size: 0.75rem; border-top: 1px solid var(--border-color); padding-top: 1rem; display: flex; gap: 0.75rem;">
                                <span style="color:var(--accent);">⭐ {repo.get('stars')}</span>
                                <span style="color:var(--text-dim);">🛠️ {repo.get('language') or 'MIXED'}</span>
                                <span style="margin-left:auto; opacity:0.5;">{repo.get('updated_at')[:10]}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("System Ready. Waiting for asset mapping.")
    except Exception as e:
        st.error(f"Link Desync: {str(e)}")

with tab_sentinel:
    # Chat display
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-bubble">
                <div class="bubble-meta">Operator</div>
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-bubble">
                <div class="bubble-meta">Sentinel Intelligence</div>
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # Input
    if prompt := st.chat_input("Input command for Sentinel..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# Handle new prompt
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    with st.spinner("Processing neural patterns..."):
        try:
            full_prompt = f"Owner: {owner}. Query: {last_prompt}"
            async def run_agent():
                await bridge.connect()
                result = await Runner.run(github_agent, full_prompt, session=st.session_state.ai_session)
                return result.final_output
            
            response = asyncio.run(run_agent())
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        except Exception as e:
            st.error(f"Neural Error: {str(e)}")
