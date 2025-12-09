import streamlit as st
import os
import glob
import asyncio
import sys
import uuid
from pathlib import Path
# Add project root
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
# Add common directory to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from aagents.orchestrator_agent import orchestrator_agent
from agents import Runner, trace, SQLiteSession
from agents.exceptions import InputGuardrailTripwireTriggered

# -----------------------------
# Configuration & Utils
# -----------------------------
st.set_page_config(
    page_title="AI Assistant",
    layout="wide",
    page_icon="🤖"
)

def load_prompts(folder="prompts"):
    prompts = []
    prompt_labels = []
    if os.path.exists(folder):
        for file_path in glob.glob(os.path.join(folder, "*.txt")):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    prompts.append(content)
                    prompt_labels.append(os.path.basename(file_path).replace("_", " ").replace(".txt", "").title())
    return prompts, prompt_labels

prompts, prompt_labels = load_prompts()

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ai_session_id" not in st.session_state:
    st.session_state.ai_session_id = str(uuid.uuid4())

# Persistent SQLite session
if "ai_session" not in st.session_state:
    st.session_state.ai_session = SQLiteSession(f"conversation_{st.session_state.ai_session_id}.db")

session = st.session_state.ai_session

# -----------------------------
# Premium Styling
# -----------------------------
st.markdown("""
<style>
    /* Global Cleanliness */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        overflow-x: hidden !important; /* Force hide horizontal scroll */
    }
    
    .block-container {
        max-width: 1200px;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Remove default header decoration */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 100 !important; /* Ensure it stays clickable but transparent */
    }
    
    div[data-testid="stDecoration"] {
        display: none;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    /* Hero Section */
    .hero-container {
        position: relative;
        width: 100vw;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        margin-top: -6rem; /* Pull up to cover top padding */
        padding: 4rem 1rem 2rem 1rem; /* Extra top padding for status bar area */
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .hero-title {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Accessibility: Focus Indicators */
    *:focus-visible {
        outline: 2px solid #764ba2 !important;
        outline-offset: 2px;
    }

    /* Chat Bubbles */
    .stChatMessage {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    .stChatMessage[data-testid="stChatMessage"]:nth-of-type(odd) {
         background-color: #f8f9fa; /* Slight contract for user/assistant if needed, but keeping white clean is fine */
    }
    
    /* Ensure text readability in chat */
    .stChatMessage p {
        color: #2c3e50;
        font-size: 1rem !important;
        line-height: 1.6;
    }

    div[data-testid="stChatMessageContent"] {
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eaeaea;
    }
    
    .suggestion-btn {
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        color: #495057;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        cursor: pointer;
        display: block;
        text-decoration: none;
    }
    .suggestion-btn:hover {
        background-color: #e2e6ea;
        border-color: #dae0e5;
        text-decoration: none;
        color: #212529;
    }
    
    /* Mobile Responsiveness Fixes */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .hero-title {
            font-size: 1.5rem;
        }
        .stChatMessage {
            padding: 0.75rem;
        }
    }
    
    /* Button accessibility */
    .stButton button {
        min-height: 44px; /* ADA Minimum Touch Target */
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Logic
# -----------------------------
async def get_ai_response(prompt: str) -> str:
    try:
        agent = orchestrator_agent
        # Ensure session is valid
        current_session = st.session_state.ai_session
        with trace("Chatbot Agent Run"):
            # Run agent
            result = await Runner.run(agent, prompt, session=current_session)
            return result.final_output
    except InputGuardrailTripwireTriggered as e:
        reasoning = getattr(e, "reasoning", None) \
            or getattr(getattr(e, "output", None), "reasoning", None) \
            or getattr(getattr(e, "guardrail_output", None), "reasoning", None) \
            or "Guardrail triggered, but no reasoning provided."
        return f"⚠️ **Guardrail Blocked Input**\n\n{reasoning}"
    except Exception as e:
        return f"❌ **Error**: {str(e)}"

# -----------------------------
# Sidebar - Quick Actions
# -----------------------------
with st.sidebar:
    st.markdown("### ⚡ Quick Starters")
    st.markdown("Select a prompt to start:")
    
    # We use a trick with st.button to act as input triggers
    # If a button is clicked, we'll handle it in the main loop logic
    selected_prompt = None
    for idx, prompt_text in enumerate(prompts):
        label = prompt_labels[idx] if idx < len(prompt_labels) else f"Prompt {idx+1}"
        if st.button(label, key=f"sidebar_btn_{idx}", use_container_width=True):
            # Reset conversation
            st.session_state.messages = []
            st.session_state.ai_session_id = str(uuid.uuid4())
            # Recreate session object with new ID
            st.session_state.ai_session = SQLiteSession(f"conversation_{st.session_state.ai_session_id}.db")
            selected_prompt = prompt_text

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# Main Content
# -----------------------------

# Hero Banner (Always visible & Sticky)
st.markdown("""
    <div class="hero-container" role="banner">
        <div class="hero-title">🤖 AI Companion</div>
        <div class="hero-subtitle">Your intelligent partner for research, analysis, and more.</div>
    </div>
""", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Handling
# We handle both the chat input widget and the sidebar selection here
if prompt := (st.chat_input("Type your message...") or selected_prompt):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = asyncio.run(get_ai_response(prompt))
            st.markdown(response_text)
            
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # If it was a sidebar click, we need to rerun to clear the selection state potentially, 
    # but st.chat_input usually handles focus. With buttons, a rerun happens automatically 
    # but we want to make sure the input box is cleared (which 'selected_prompt' doesn't use).
    if selected_prompt:
        st.rerun()
