"""Healthcare Chatbot - Streamlit UI for healthcare information retrieval."""
import streamlit as st
import sys
import os  # Added for OTEL setup
import html
from pathlib import Path
from chat import ChatManager
from healthcare_agent import healthcare_graph

# --------------------
# Page Configuration
# --------------------
st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------
# Custom CSS for Modern Chat UI
# --------------------
CUSTOM_CSS = """
<style>
    /* Main container */
    .block-container {
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #1E88E5;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Chat message containers */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .message-role {
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    .message-content {
        line-height: 1.6;
    }
    
    /* Tool call badges */
    .tool-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        margin: 0.25rem 0.25rem 0.5rem 0;
        font-weight: 500;
    }
    
    /* Disclaimer box */
    .disclaimer {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: #856404;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    /* specific sidebar button styling to prevent wrapping */
    section[data-testid="stSidebar"] .stButton > button {
        padding: 0.5rem 1rem;
        white-space: nowrap;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Chat container */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 0.7rem;
        color: #999;
        margin-top: 0.25rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --------------------
# Session State Initialization
# --------------------
if "chat_manager" not in st.session_state:
    st.session_state.chat_manager = ChatManager(healthcare_graph)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------
# Sidebar
# --------------------
with st.sidebar:
    st.header("⚙️ Assistant Controls")
    st.markdown("---")
    
    st.subheader("About")
    st.info(
        """
        This chatbot uses advanced RAG (Retrieval-Augmented Generation) 
        combined with web search to provide healthcare information.
        
        **Features:**
        - 📚 Knowledge base search
        - 🌐 Web search fallback
        - 💬 Conversation memory
        - 📝 Source citations
        """
    )
    
    st.markdown("---")
    
    # Conversation controls
    st.subheader("Controls")
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.chat_manager.clear_history()
        st.session_state.messages = []
        st.rerun()
    
    # Export conversation
    st.subheader("Export")
    export_format = st.selectbox(
        "Format",
        ["text", "markdown", "json"],
        label_visibility="collapsed"
    )
    
    if st.button("📥 Export Chat", use_container_width=True):
        if st.session_state.messages:
            exported = st.session_state.chat_manager.export_conversation(export_format)
            st.download_button(
                label="Download",
                data=exported,
                file_name=f"healthcare_chat_{st.session_state.chat_manager.session_id}.{export_format}",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.warning("No conversation to export")
    
    st.markdown("---")
    
    # Statistics
    st.subheader("Session Info")
    st.metric("Messages", len(st.session_state.messages))
    st.caption(f"Session ID: {st.session_state.chat_manager.session_id}")

# --------------------
# Main Chat Interface
# --------------------
st.title("🩺 Healthcare Assistant")
st.markdown('<p class="subtitle">Ask me anything about healthcare topics</p>', unsafe_allow_html=True)

# Display disclaimer at the top
st.markdown(
    """
    <div class="disclaimer">
        ⚠️ <strong>Medical Disclaimer:</strong> This chatbot provides information for educational purposes only. 
        Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat messages using Streamlit's chat_message component
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        # Use Streamlit's chat_message for better rendering
        with st.chat_message(role, avatar="👤" if role == "user" else "🏥"):
            # Show tool calls if available
            if role == "assistant" and "metadata" in message and message["metadata"]:
                if "tool_calls" in message["metadata"] and message["metadata"]["tool_calls"]:
                    tools = message["metadata"]["tool_calls"]
                    tool_names = ", ".join([f"`{tool['name']}`" for tool in tools])
                    st.caption(f"🔧 Tools used: {tool_names}")
            
            # Display the message content as markdown
            st.markdown(content)

# --------------------
# Input Area
# --------------------
st.markdown("---")

# Create columns for input and button
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Type your question here...",
        key="user_input",
        placeholder="e.g., What is diabetes?",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("Send 📤", use_container_width=True, type="primary")

# Handle message sending
if send_button and user_input:
    # Add user message to display
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Show loading spinner while getting response
    with st.spinner("🤔 Thinking..."):
        # Get response from chat manager
        # Get response from chat manager
        response = st.session_state.chat_manager.get_response(user_input)
        
        # Add assistant response to display
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["content"],
            "metadata": {
                "tool_calls": response.get("tool_calls", [])
            }
        })
    
    # Rerun to update the chat display
    st.rerun()

# --------------------
# Example Questions
# --------------------
if not st.session_state.messages:
    st.markdown("### 💡 Try asking:")
    
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("What is sunburn and its preventive care?", use_container_width=True, key="example1"):
            # Add the example question directly as a user message
            st.session_state.messages.append({
                "role": "user",
                "content": "What is sunburn and its preventive care?"
            })
            # Get response
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chat_manager.get_response("What is sunburn and its preventive care?")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["content"],
                    "metadata": {
                        "tool_calls": response.get("tool_calls", [])
                    }
                })
            st.rerun()
    
    with example_col2:
        if st.button("What could be the reason for chest burn?", use_container_width=True, key="example2"):
            # Add the example question directly as a user message
            st.session_state.messages.append({
                "role": "user",
                "content": "What could be the reason for chest burn?"
            })
            # Get response
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chat_manager.get_response("What could be the reason for chest burn?")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["content"],
                    "metadata": {
                        "tool_calls": response.get("tool_calls", [])
                    }
                })
            st.rerun()
    
    with example_col3:
        if st.button("What is the use of ICD-10 in Healthcare?", use_container_width=True, key="example3"):
            # Add the example question directly as a user message
            st.session_state.messages.append({
                "role": "user",
                "content": "What is the use of ICD-10 in Healthcare?"
            })
            # Get response
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chat_manager.get_response("What is the use of ICD-10 in Healthcare?")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["content"],
                    "metadata": {
                        "tool_calls": response.get("tool_calls", [])
                    }
                })
            st.rerun()


# --------------------
# Footer
# --------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #999; font-size: 0.85rem;">
        Powered by Healthcare RAG Agent | Using Gemini 2.0 Flash & DuckDuckGo Search
    </div>
    """,
    unsafe_allow_html=True
)
