import os
import glob
import uuid
import asyncio
import logging
import streamlit as st

# Import the new Orchestrator Pattern
from src.chatbot_v2.patterns.orchestrator import ChatbotOrchestrator

# -----------------------------
# Configuration & Utils
# -----------------------------
st.set_page_config(
    page_title="Layered AI Assistant",
    layout="wide",
    page_icon="🧠"
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

# Initialize the Agent
if "agent" not in st.session_state:
    st.session_state.agent = ChatbotOrchestrator()

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
            padding-bottom: 0rem !important;
        }
        
        .hero-container {
            margin-top: -2rem;
            margin-left: -1rem;
            margin-right: -1rem;
            /* Break out of the 1rem padding */
            padding: 2rem 1rem 1.5rem 1rem; /* Compact mobile padding */
            border-radius: 0 0 12px 12px;
        }
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
async def get_ai_response(prompt: str) -> str:
    try:
        agent: ChatbotOrchestrator = st.session_state.agent
        
        # We pass the *previous* history (messages excluding the latest one which we just appended)
        # Actually, st.session_state.messages ALREADY has the new user message appended below.
        # So we pass messages[:-1] as "history"
        history = st.session_state.messages[:-1]
        
        result = await agent.run(user_input=prompt, external_history=history)
        return result
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
            st.session_state.agent = ChatbotOrchestrator() # Reset agent memory too
            selected_prompt = prompt_text

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = ChatbotOrchestrator()
        st.rerun()

# -----------------------------
# Main Content
# -----------------------------

# Hero Banner (Always visible & Sticky)
st.markdown("""
    <div class="hero-container" role="banner">
        <div class="hero-title">🧠 Layered AI Agent</div>
        <div class="hero-subtitle">Architecture: Perception ➜ Cognition ➜ Action</div>
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
        with st.spinner("🧠 Thinking (Layers Active)..."):
            response_text = asyncio.run(get_ai_response(prompt))
            st.markdown(response_text, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    if selected_prompt:
        st.rerun()
