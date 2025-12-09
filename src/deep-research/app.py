import streamlit as st
import asyncio
import time
import html
from io import BytesIO
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from appagents.orchestrator import Orchestrator
from agents import SQLiteSession

load_dotenv(override=True)

# --------------------
# Page config
# --------------------
st.set_page_config(page_title="Deep Research AI", layout="wide", page_icon="🧠")

# --------------------
# Premium CSS
# --------------------
st.markdown("""
<style>
    /* Global Defaults */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Remove default Streamlit top padding but add space for Fixed Header - Revert: Just remove top padding */
    .block-container {
        padding-top: 1rem !important; /* Small buffer */
    }
    
    /* Sticky Header */
    header[data-testid="stHeader"] { display: none; } /* Hide default streamlit header */
    
    .header-container {
        position: sticky;
        top: 0;
        z-index: 999;
        
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #ffffff;
        padding: 3rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        
        margin-top: -4rem; /* Pull up aggressively to cover top gap */
        margin-left: -5rem;
        margin-right: -5rem;
        
        border-bottom: none;
        border-radius: 0 0 1rem 1rem;
    }
    
    .app-brand {
        font-family: 'Inter', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }

    /* Centered Search Area */
    .search-wrapper {
        max-width: 800px;
        margin: 4rem auto 2rem auto;
        text-align: center;
    }
    
    .search-headline {
        font-size: 2.5rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }
    
    .search-subtext {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2.5rem;
    }

    /* Input styling override */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 1rem !important;
        background: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        font-size: 1.1rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Custom Button */
    .stButton button {
        background: black !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 0.5rem 2rem !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        transition: transform 0.1s ease;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }

    /* Report Paper Style */
    .report-paper {
        max-width: 850px;
        margin: 2rem auto;
        background: white;
        padding: 4rem;
        min-height: 800px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 20px 40px rgba(0,0,0,0.05);
        color: #2c3e50;
        border: 1px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# --------------------
# Session State
# --------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(id(st))

if "final_report" not in st.session_state:
    st.session_state.final_report = ""

if "is_researching" not in st.session_state:
    st.session_state.is_researching = False

if "research_logs" not in st.session_state:
    st.session_state.research_logs = []

# --------------------
# Helpers
# --------------------
def make_pdf_bytes(text: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, topMargin=0.5*72, bottomMargin=0.5*72, leftMargin=0.75*72, rightMargin=0.75*72)
    styles = getSampleStyleSheet()
    story = []
    
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Paragraph(" ", styles["Normal"]))
            continue
        
        if stripped.startswith("# "):
            story.append(Paragraph(html.escape(stripped[2:]), styles["Heading1"]))
        elif stripped.startswith("## "):
            story.append(Paragraph(html.escape(stripped[3:]), styles["Heading2"]))
        elif stripped.startswith("- "):
            story.append(Paragraph("• " + html.escape(stripped[2:]), styles["Normal"]))
        else:
            story.append(Paragraph(html.escape(stripped), styles["Normal"]))
            
    doc.build(story)
    buf.seek(0)
    return buf.read()

# --------------------
# Logic
# --------------------
async def run_research(query: str):
    session_id = st.session_state.session_id
    session = SQLiteSession(f"session_{session_id}.db")
    orchestrator = Orchestrator(session=session)
    
    report_content = ""
    status_container = st.status("🔍 Researching...", expanded=True)
    
    try:
        async for chunk in orchestrator.run(query):
            # Filtering heuristic: Orchestrator yields status messages then the final report.
            # Status messages are short and specific.
            if (chunk.startswith("View trace") or 
                chunk.startswith("Searches") or 
                chunk.startswith("Report written") or
                chunk.startswith("Starting")):
                
                status_container.markdown(chunk)
            else:
                # Assume this is the report content (or the final error note)
                report_content = chunk
                status_container.markdown("Processing final output...")
        
        st.session_state.final_report = report_content
        st.session_state.is_researching = False
        status_container.update(label="✅ Research Complete", state="complete", expanded=False)
        st.rerun()
        
    except Exception as e:
        status_container.update(label="❌ Error", state="error")
        st.error(f"Error: {e}")
        st.session_state.is_researching = False

# --------------------
# Layout
# --------------------

# Custom Header
st.markdown("""
<div class="header-container">
    <div class="app-brand">
        <span>🧠</span> Deep Research <i>(OpenAI Agentic)</i>
    </div>
    <div>
        <!-- Could add profile or other links here -->
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    research_depth = st.select_slider("Research Depth", options=["Quick", "Standard", "Deep"], value="Standard")
    report_format = st.selectbox("Report Format", ["Academic", "Business", "Creative"])
    st.caption("Settings affect the tone and depth of the final report.")
    
    st.divider()
    if st.button("🗑️ Clear History"):
        st.session_state.final_report = ""
        st.rerun()

# Main Interface
if not st.session_state.final_report and not st.session_state.is_researching:
    # Centered Input View
    st.markdown("""
    <div class="search-wrapper">
        <div class="search-headline">What do you want to know?</div>
        <div class="search-subtext">Deep Research will browse the web, analyze sources, and write a comprehensive report for you.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        query = st.text_area("Research Topic", height=60, placeholder="e.g. The future of quantum computing in drug discovery...", label_visibility="collapsed")
        
        col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
        with col_b2:
            if st.button("Start Research", use_container_width=True):
                if query.strip():
                    st.session_state.is_researching = True
                    st.session_state.current_query = query
                    st.rerun()

elif st.session_state.is_researching:
    # Researching View
    st.markdown("""
    <div class="search-wrapper">
        <div class="search-headline">Compiling Report...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Trigger async run
    asyncio.run(run_research(st.session_state.current_query))

else:
    # Result View - Title removed to let Sticky Header be the main branding, 
    # and Report itself be the focus.
    
    # Action Toolbar
    col_a1, col_a2, col_a3, col_a4 = st.columns([2, 1, 1, 2])
    with col_a2:
        pdf_bytes = make_pdf_bytes(st.session_state.final_report)
        st.download_button("📄 Download PDF", pdf_bytes, "report.pdf", mime="application/pdf", use_container_width=True)
    with col_a3:
        if st.button("🔄 New Search", use_container_width=True):
             st.session_state.final_report = ""
             st.rerun()

    # Final Report Render
    # We use a container with a class to apply the 'sheet' look via global CSS if possible,
    # or just use standard Markdown rendering which looks best.
    
    with st.container():
        st.markdown(st.session_state.final_report)

