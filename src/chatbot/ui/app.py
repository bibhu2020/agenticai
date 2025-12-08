import streamlit as st
import os
import glob
import asyncio
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from appagents.OrchestratorAgent import OrchestratorAgent
from agents import Runner, trace, SQLiteSession
from agents.exceptions import InputGuardrailTripwireTriggered


# -----------------------------
# Load predefined prompts
# -----------------------------
def load_prompts(folder="prompts"):
    prompts = []
    prompt_labels = []
    for file_path in glob.glob(os.path.join(folder, "*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                prompts.append(content)
                prompt_labels.append(os.path.basename(file_path).replace("_", " ").replace(".txt", "").title())
    return prompts, prompt_labels

prompts, prompt_labels = load_prompts()

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="AI Chat", layout="wide")

# -----------------------------
# Custom CSS (chat, hero banner, input)
# -----------------------------
st.markdown("""
<style>
header[data-testid="stHeader"] {display: none !important;}
.block-container {padding-top: 0 !important; margin-top: -2rem !important;}

/* Hero banner */
.hero-banner {
    width: 100%;
    background: linear-gradient(90deg, #343541 0%, #444654 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 0 0 12px 12px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
.hero-text { font-size: 1.8rem; font-weight: 700; }
.hero-subtext { font-size: 1rem; opacity: 0.8; }

/* Sidebar */
section[data-testid="stSidebar"] {padding-top: 0.5rem !important;}

/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    height: 70vh;
    overflow-y: auto;
    border: 1px solid #ddd;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    margin-top: 1rem;
}

/* Chat bubbles */
.user-bubble, .ai-bubble {
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 75%;
    margin: 6px 0;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.4;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.user-bubble {
    background-color: #DCF8C6;
    color: #111;
    align-self: flex-end;
}
.ai-bubble {
    background-color: #f0f0f0;
    color: #111;
    align-self: flex-start;
}

/* Icons */
.icon {
    font-size: 28px;
    margin: 4px;
    opacity: 0.8;
}

/* Input area */
.stTextInput input {
    border-radius: 10px;
    border: 1px solid #ccc;
    padding: 12px;
    font-size: 15px;
}
.stForm button {
    border-radius: 10px;
    font-size: 15px;
    background-color: #10a37f !important;
    color: white !important;
    border: none !important;
}

/* Mobile-specific Quick Prompts at top */
@media (max-width: 768px) {
    .mobile-prompts { display: block; margin-bottom: 1rem; }
    .desktop-sidebar { display: none; }
    .chat-container { height: 60vh; background-color: #f5f5f5; }
    .user-bubble, .ai-bubble { font-size: 14px; }
}
@media (min-width: 769px) {
    .mobile-prompts { display: none; }
    .desktop-sidebar { display: block; }
}
            
.quick-prompts-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.quick-prompts-grid button {
    flex: 1 1 45%;  /* two buttons per row approx */
    min-width: 120px;
    max-width: 250px;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    border: 1px solid #ccc;
    background-color: #f5f5f5;
    cursor: pointer;
}


</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session state defaults
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # newest-first

if "input_value" not in st.session_state:
    st.session_state.input_value = ""

if "pending_response" not in st.session_state:
    st.session_state.pending_response = False

if "pending_message" not in st.session_state:
    st.session_state.pending_message = None

if "auto_send_prompt" not in st.session_state:
    st.session_state.auto_send_prompt = None

# Create (or reuse) a persistent SQLite session
import uuid

# Generate a unique session ID for this browser session
if "ai_session_id" not in st.session_state:
    st.session_state.ai_session_id = str(uuid.uuid4())

session_id = st.session_state.ai_session_id

# Create a unique SQLite session per user
if "ai_session" not in st.session_state:
    st.session_state.ai_session = SQLiteSession(f"conversation_{session_id}.db")

session = st.session_state.ai_session



# -----------------------------
# Async AI response
# -----------------------------
async def get_ai_response(prompt: str) -> str:
    try:
        agent = OrchestratorAgent.create()
        with trace("Chatbot Search Agent Run"):
            result = await Runner.run(agent, prompt, session=session)
            return result.final_output
    except InputGuardrailTripwireTriggered as e:
        reasoning = getattr(e, "reasoning", None) \
            or getattr(getattr(e, "output", None), "reasoning", None) \
            or getattr(getattr(e, "guardrail_output", None), "reasoning", None) \
            or "Guardrail triggered, but no reasoning provided."

        return f"⚠️ Guardrail Blocked Input:\n\n**Reason:** {reasoning}"


# -----------------------------
# Desktop Sidebar Quick Prompts
# -----------------------------
with st.sidebar.container() if st.config.get_option("server.headless") is False else st.container() as container:
    st.markdown('<div class="desktop-sidebar">', unsafe_allow_html=True)
    # Desktop Quick Prompts
    st.sidebar.title("💡 Quick Prompts")
    buttons_html = '<div class="quick-prompts-grid">'
    for idx, prompt_text in enumerate(prompts):
        label = prompt_labels[idx] if idx < len(prompt_labels) else f"Prompt {idx+1}"
        buttons_html += f'<button onclick="window.location.href=\'#\'" id="prompt_{idx}">{label}</button>'
    buttons_html += '</div>'
    st.sidebar.markdown(buttons_html, unsafe_allow_html=True)



# -----------------------------
# Mobile Quick Prompts
# -----------------------------
with st.container():
    st.markdown('<div class="mobile-prompts">', unsafe_allow_html=True)
    with st.expander("💡 Quick Prompts"):
        for idx, prompt_text in enumerate(prompts):
            label = prompt_labels[idx] if idx < len(prompt_labels) else f"Prompt {idx+1}"
            if st.button(label, key=f"mobile_prompt_{idx}"):
                st.session_state.auto_send_prompt = prompt_text
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Hero banner
# -----------------------------
st.markdown("""
<div class="hero-banner">
    <div>
        <div class="hero-text">🤖 AI Chatbot</div>
        <div class="hero-subtext">Your intelligent assistant for insights, trends, and strategy exploration.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Chat input area
# -----------------------------
with st.form(key="chat_form", clear_on_submit=False):
    user_input = st.text_input(
        "Type your message here:",
        value=st.session_state.input_value,
        placeholder="Send a message...",
        key="chat_input"
    )
    send_button = st.form_submit_button("Send")

# -----------------------------
# Helper to insert user message immediately
# -----------------------------
def send_user_message(msg):
    st.session_state.chat_history.insert(0, {"role": "user", "message": msg})
    st.session_state.pending_message = msg
    st.session_state.pending_response = True
    st.session_state.input_value = ""

# -----------------------------
# Handle normal send
# -----------------------------
if send_button and user_input.strip():
    send_user_message(user_input.strip())

# Handle sidebar/mobile prompt auto-send
if st.session_state.auto_send_prompt:
    send_user_message(st.session_state.auto_send_prompt)
    st.session_state.auto_send_prompt = None

# -----------------------------
# Handle AI response asynchronously
# -----------------------------
if st.session_state.pending_response and st.session_state.pending_message:
    with st.spinner("🤖 Thinking..."):
        try:
            ai_response = asyncio.run(get_ai_response(st.session_state.pending_message))
        except Exception as e:
            ai_response = f"[Error generating response: {e}]"
    st.session_state.chat_history.insert(0, {"role": "assistant", "message": ai_response})
    st.session_state.pending_response = False
    st.session_state.pending_message = None

# -----------------------------
# Display chat history with Markdown in AI bubbles
# -----------------------------
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        msg_html = chat["message"].replace("\n","<br>")
        st.markdown(
            f"<div style='display:flex; justify-content:flex-end; align-items:flex-start;'>"
            f"<div class='user-bubble'>{msg_html}</div>"
            f"<span class='icon'>👤</span>"
            f"</div>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
<div style='display:flex; justify-content:flex-start; align-items:flex-start;'>
  <span class='icon'>🤖</span>
  <div class='ai-bubble'>
    {chat['message']}
  </div>
</div>
""",
            unsafe_allow_html=True
        )
