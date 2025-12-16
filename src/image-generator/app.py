import streamlit as st
import asyncio
import os
import sys
import re

# Add root directory to sys.path to allow importing 'common'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from teams.image_team import get_image_team

# Page config
st.set_page_config(page_title="Agentic Image Generator", layout="wide", page_icon="🎨")

# Premium CSS & Layout Optimization
st.markdown("""
<style>
    /* ---------------------------------------------------------------------
       GLOBAL & RESET
       --------------------------------------------------------------------- */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ---------------------------------------------------------------------
       SIDEBAR
       --------------------------------------------------------------------- */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        min-width: 450px !important;
        max-width: 800px !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* ---------------------------------------------------------------------
       HERO BANNER & LAYOUT
       --------------------------------------------------------------------- */
    
    /* Desktop Layout */
    @media (min-width: 769px) {
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 2rem !important;
            padding-left: 3rem !important; /* Adjusted for sidebar */
            padding-right: 3rem !important;
            max-width: 100% !important;
        }
        
        .hero-container {
            margin-top: -3rem;
            margin-left: -3rem;
            margin-right: -3rem;
            padding: 2.5rem 1rem 2rem 1rem;
        }
    }
    
    /* Mobile Layout */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .hero-container {
            margin-top: -2rem;
            margin-left: -1rem;
            margin-right: -1rem;
            padding: 2rem 1rem 1.5rem 1rem;
            border-radius: 0 0 12px 12px;
        }
    }
    
    /* Hero Styling */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Purple/Blue gradient for creativity */
        color: white;
        text-align: center;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2rem;
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
    
    /* Remove default streamlit header decoration */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0 !important;
    }
    div[data-testid="stDecoration"] { display: none; }
    
</style>
""", unsafe_allow_html=True)

# Custom Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎨 Agentic Image Generator</div>
    <div class="hero-subtitle">Powered by AutoGen & FLUX.1</div>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_image_path" not in st.session_state:
    st.session_state.generated_image_path = None

async def run_agent_team(user_request):
    """
    Runs the AutoGen team with the user request.
    """
    team = get_image_team()
    
    # Construct history string to allow stateless agents to see previous context
    history_context = ""
    last_prompt = None
    
    if len(st.session_state.messages) > 1: 
        history_context = "PREVIOUS CONVERSATION HISTORY:\n"
        for msg in st.session_state.messages[:-1]: 
             content = msg['content']
             
             # Convert to string if it's a list (handle AutoGen multimodal messages)
             if isinstance(content, list):
                 content = str(content)
                 
             # Sanitize content to prevent early termination triggers from history
             clean_content = str(content).replace("Image generated successfully", "Image (previous run)")
             
             role = msg['role']
             history_context += f"{role}: {clean_content}\n"
             
             # Track the last seen prompt
             if "PROMPT:" in str(content):
                 # simplistic extraction: assuming the content STARTS with PROMPT: or contains it
                 # If the agent output multiple lines, we might need to be careful, 
                 # but usually it's "PROMPT: ..."
                 if "PROMPT: " in content:
                     parts = content.split("PROMPT: ")
                     if len(parts) > 1:
                         last_prompt = parts[1].strip()
                         
        history_context += "\nEND OF HISTORY.\n\n"
    
    # Explicitly inject the last prompt so the agent doesn't have to hunt for it
    prompt_context = ""
    if last_prompt:
        prompt_context = f"LAST GENERATED PROMPT: {last_prompt}\n\n"
        
    full_task = f"{history_context}{prompt_context}CURRENT REQUEST: {user_request}"
    
    stream = team.run_stream(task=full_task)
    
    async for message in stream:
        source = getattr(message, 'source', 'System')
        content = getattr(message, 'content', "")
        
        # Add to history
        st.session_state.messages.append({"role": source, "content": content})
        
        # Check for image path in content
        # Use regex to find the path reliably
        match = re.search(r"(src[\\/].*?\.png)", str(content))
        if match:
            path = match.group(1)
            # Cleanup any potential trailing quoting characters if regex grabbed too much (unlikely with .png ending but safe)
            st.session_state.generated_image_path = path

# Sidebar
with st.sidebar:
    st.header("Conversation")
    
    # Input Area (AT THE TOP)
    with st.form(key="chat_form", clear_on_submit=True):
        user_input_val = st.text_area("Describe the image you want...", height=100)
        submit_btn = st.form_submit_button("Generate")
        
    if submit_btn and user_input_val:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input_val})
        
        # We need to rerun or handle async immediately. 
        # But since we are in a form submit, we can just set a flag or run it.
        # However, async run needs to happen outside the form context usually for better UI updates,
        # but here we trigger it via session state or direct call.
        
        # Let's run it directly here.
        with st.spinner("Agents are collaborating..."):
            asyncio.run(run_agent_team(user_input_val))
            
    st.divider()
    
    # Display chat history (REVERSED: Newest on Top)
    for msg in reversed(st.session_state.messages):
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role):
            st.write(content)

# We remove the old user_input logic because it is now handled in the form above.
# The `run_agent_team` function remains the same.


# Main Area: Image Display
st.divider()
if st.session_state.generated_image_path and os.path.exists(st.session_state.generated_image_path):
    st.image(st.session_state.generated_image_path, caption="Generated by Agentic Workflow", use_container_width=True)
elif st.session_state.generated_image_path:
    st.error(f"Image file not found at: {st.session_state.generated_image_path}")
else:
    st.info("Start a conversation in the sidebar to generate an image.")
    st.markdown("""
    ### How it works:
    1. **Prompt Engineer**: Refines your simple request into a professional prompt.
    2. **Critic**: Validates the prompt for safety and alignment with your request.
    3. **Generator**: Creates the image using FLUX.1.
    """)
