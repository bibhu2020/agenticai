
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
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .hero-container {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        text-align: center;
        padding: 3rem 1rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .stMetric {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🐙 GitHub Portal Agent</div>
    <div class="hero-subtitle">Real-world Agentic Intelligence for your Repositories</div>
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
    st.header("⚙️ Configuration")
    owner = st.text_input("Owner", value=os.environ.get("GITHUB_OWNER", "bibhu2020")).strip()
    repo = st.text_input("Repository", value=os.environ.get("GITHUB_REPO", "agenticai")).strip()
    
    st.markdown("---")
    st.subheader("🌐 Remote MCP Status")
    if st.button("Check Connection"):
        try:
            async def test_conn():
                await bridge.connect()
                return await bridge.session.list_tools()
            tools = asyncio.run(test_conn())
            st.success(f"Connected! {len(tools.tools)} tools found.")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.ai_session = SQLiteSession(f"github_portal_{st.session_state.session_id}.db")
        st.rerun()

# Layout
chat_col, dash_col = st.columns([2, 1])

with dash_col:
    st.subheader("📊 Key Metrics")
    # Quick health check
    if owner and repo:
        try:
            async def get_metrics():
                await bridge.connect()
                issues = await bridge.call_tool("list_issues", {"owner": owner, "repo_name": repo})
                sec = await bridge.call_tool("list_security_alerts", {"owner": owner, "repo_name": repo})
                pipes = await bridge.call_tool("list_workflow_runs", {"owner": owner, "repo_name": repo})
                return issues, sec, pipes
            
            with st.spinner("Analyzing repository..."):
                i, s, p = asyncio.run(get_metrics())
                st.metric("Open Issues", len(i) if isinstance(i, list) else 0)
                st.metric("Security Alerts", len(s) if isinstance(s, list) else 0)
                failed = len([r for r in p if r.get('conclusion') == 'failure']) if isinstance(p, list) else 0
                st.metric("Failed Pipelines", failed)
        except Exception as e:
            st.warning("Dashboard offline. Use the Agent for details.")

with chat_col:
    st.subheader("💬 GitHub Agent")
    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask the GitHub Agent anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent thinking..."):
                try:
                    # Provide context to the prompt
                    full_prompt = f"Using repository {owner}/{repo}: {prompt}"
                    
                    async def run_agent():
                        # We don't need to manually connect here as the tools do it, 
                        # but connecting once at start is better.
                        await bridge.connect()
                        result = await Runner.run(github_agent, full_prompt, session=st.session_state.ai_session)
                        return result.final_output
                    
                    response = asyncio.run(run_agent())
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Agent Error: {str(e)}")
