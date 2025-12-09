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
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
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
        z-index: 100 !important;
    }
    
    div[data-testid="stDecoration"] {
        display: none;
    }

    /* Hero Section (Matching Chatbot Style) */
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
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
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

    /* Centered Search Area */
    .search-wrapper {
        max-width: 800px;
        margin: 2rem auto;
        text-align: center;
        padding: 0 1rem;
    }
    
    .search-headline {
        font-size: 2rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 0.5rem;
    }
    
    .search-subtext {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Mobile font sizes */
    @media (max-width: 768px) {
        .search-headline {
            font-size: 1.75rem;
        }
    }

    /* Input styling override */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 1rem !important;
        background: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        font-size: 1rem !important; /* Proper reading size */
        color: #333 !important;
    }
    
    /* Custom Button */
    .stButton button {
        background: black !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 0.5rem 2rem !important;
        border: none !important;
        transition: transform 0.1s ease;
        min-height: 48px; /* Large touch target */
        white-space: nowrap !important; /* Prevent label wrapping */
    }
    .stButton button:hover {
        transform: scale(1.02);
    }

    /* Report Paper Style */
    .report-paper {
        max-width: 850px;
        margin: 2rem auto;
        background: white;
        padding: 2rem;
        min-height: 600px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #2c3e50;
        border-radius: 8px;
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
<div class="hero-container">
    <div class="hero-title">🧠 Deep Research</div>
    <div class="hero-subtitle">OpenAI Agentic Research Assistant</div>
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

