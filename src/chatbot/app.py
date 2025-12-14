import os
import glob
import uuid
import asyncio
# import trace_config
import logging
import streamlit as st
from aagents.orchestrator_agent import orchestrator_agent
from agents import Runner, trace, SQLiteSession
from agents.exceptions import InputGuardrailTripwireTriggered
# from langsmith import traceable

from traceloop.sdk import Traceloop
from opentelemetry.sdk.trace import Span

# --- Monkeypatch to fix "Invalid type Omit" errors ---
# This filters out 'NotGiven'/'Omit' values from OpenAI that crash the OTel exporter
_original_set_attribute = Span.set_attribute

def _safe_set_attribute(self, key, value):
    # Check string representation of type to avoid importing specific internal types
    type_str = str(type(value))
    if "Omit" in type_str or "NotGiven" in type_str:
        return self
    return _original_set_attribute(self, key, value)

Span.set_attribute = _safe_set_attribute
# -----------------------------------------------------

Traceloop.init(
  disable_batch=True,
  api_key="tl_1c19b8e8fcfd411fb9fcdb02d381faef"
)

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
    /* ---------------------------------------------------------------------
       1. GLOBAL & RESET
       --------------------------------------------------------------------- */
    * {
        box-sizing: border-box;
    }
    
    .stApp, [data-testid="stAppViewContainer"] {
        /* Standard Streamlit background */
        background-color: #f8f9fa;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';
    }
    
    html {
        -webkit-text-size-adjust: 100%; /* Prevent iOS font boosting */
    }
    
    /* ---------------------------------------------------------------------
       2. LAYOUT & HERO BANNER
       --------------------------------------------------------------------- */
    
    /* Mobile font optimization */
    @media (max-width: 768px) {
        /* Target all markdown text specifically */
        .stMarkdown p, .stMarkdown li, .stChatMessage p, .message-content, .stDataFrame, .stTable {
            font-size: 16px !important;
            line-height: 1.6 !important;
            color: #1a1a1a !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a !important;
        }
    }
    
    /* Desktop Layout */
    @media (min-width: 769px) {
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 2rem !important;
            padding-left: 5rem !important;
            padding-right: 5rem !important;
            max-width: 100% !important;
        }
        
        .hero-container {
            margin-top: -3rem;
            margin-left: -5rem;
            margin-right: -5rem;
            /* Simple negative margins to pull edge-to-edge */
            padding: 2.5rem 1rem 2rem 1rem; /* Compact desktop padding */
        }
    }
    
    /* Mobile Layout */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 0 !important;
        }
        
        .hero-container {
            margin-top: -2rem;
            margin-left: -1rem;
            margin-right: -1rem;
            /* Break out of the 1rem padding */
            padding: 2rem 1rem 1.5rem 1rem; /* Compact mobile padding */
            border-radius: 0 0 12px 12px;
        }
        
        /* Ensure font sizes are standard (Streamlit defaults is ~16px) */
        /* We DO NOT override them to 17px/fixed, allowing system zoom to work. */
    }

    /* Hero Styling */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2rem; /* Slightly smaller */
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: white !important;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 400;
        color: rgba(255,255,255,0.95) !important;
    }
    
    /* Remove Header Decoration */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0 !important;
        z-index: 100;
    }
    div[data-testid="stDecoration"] { display: none; }
    
    /* ---------------------------------------------------------------------
       3. COMPONENT STYLING (Healthcare-like)
       --------------------------------------------------------------------- */
    
    /* Chat Bubbles - Clean & Readable */
    .stChatMessage {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        padding: 1rem;
    }
    
    .stChatMessage[data-testid="stChatMessage"]:nth-of-type(odd) {
         background-color: #f8f9fa;
    }
    
    /* Input Fields */
    .stTextInput input {
        border-radius: 20px; /* Matching healthcare-assistant roundness */
        border: 1px solid #ddd;
        padding: 0.75rem 1rem;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 20px; /* Matching healthcare-assistant */
        min-height: 48px;
        font-weight: 500;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eaeaea;
    }
    
    /* Minimize Sidebar Top Padding */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Logic
# -----------------------------
# @traceable(name="chatbot")
async def get_ai_response(prompt: str) -> str:
    try:
        agent = orchestrator_agent
        # Ensure session is valid
        current_session = st.session_state.ai_session
        current_session = st.session_state.ai_session
        with trace("Chatbot Agent Run"): # Keep existing custom trace wrapper
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
        st.markdown(message["content"], unsafe_allow_html=True)

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
            st.markdown(response_text, unsafe_allow_html=True)


            
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # If it was a sidebar click, we need to rerun to clear the selection state potentially, 
    # but st.chat_input usually handles focus. With buttons, a rerun happens automatically 
    # but we want to make sure the input box is cleared (which 'selected_prompt' doesn't use).
    if selected_prompt:
        st.rerun()
