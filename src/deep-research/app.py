import streamlit as st
import asyncio
import time
import html
from io import BytesIO
import os
import sys
from pathlib import Path

# Add project root
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from appagents.orchestrator import Orchestrator
from agents import SQLiteSession

# ------------------------------------------------------------------------------
# OpenTelemetry Setup
# ------------------------------------------------------------------------------
from opentelemetry import trace as trace_api
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

if otel_endpoint:
    enable_otel = True
else:
    # Local development default
    otel_endpoint = "https://myotel.azurewebsites.net/v1/traces"
    enable_otel = True

if enable_otel:
    try:
        # Set up telemetry span exporter.
        # otel_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
        otel_exporter = OTLPSpanExporter(endpoint=otel_endpoint)
        span_processor = BatchSpanProcessor(otel_exporter)

        # Set up telemetry trace provider.
        tracer_provider = TracerProvider(resource=Resource({"service.name": "deep-research"}))
        tracer_provider.add_span_processor(span_processor)
        trace_api.set_tracer_provider(tracer_provider)

        # Custom hook to filter out Omit/NotGiven types from attributes
        def request_hook(span, kwargs):
            if span and span.is_recording():
                for key, value in kwargs.items():
                    # Check for "Omit" or "NotGiven" types which OTEL can't serialize
                    type_name = type(value).__name__
                    if type_name in ["Omit", "NotGiven"]:
                        # Setup correct attribute name expected by semantic conventions or just use key
                        # The instrumentation might use gen_ai.request.{key}
                        span.set_attribute(f"gen_ai.request.{key}", str(value))

        # Instrument the OpenAI Python library
        OpenAIInstrumentor().instrument(request_hook=request_hook)
        print(f"OpenTelemetry enabled with endpoint: {otel_endpoint}")
    except Exception as e:
        print(f"Failed to initialize OpenTelemetry: {e}")
else:
    print("OpenTelemetry disabled (Running in HF Space with no configured endpoint).")

# Get a tracer (works even if OTEL is disabled, returning a NoOp tracer)
tracer = trace_api.get_tracer("deep-research")

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
    /* ---------------------------------------------------------------------
       1. GLOBAL & RESET
       --------------------------------------------------------------------- */
    * {
        box-sizing: border-box;
    }
    
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';
    }
    
    html {
        -webkit-text-size-adjust: 100%;
    }
    
    /* ---------------------------------------------------------------------
       2. LAYOUT & HERO BANNER
       --------------------------------------------------------------------- */

    /* Mobile font optimization */
    @media (max-width: 768px) {
        .stMarkdown p, .stMarkdown li, .report-paper p, .report-paper li, .stDataFrame {
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
            margin-top: 0;
            margin-left: -5rem;
            margin-right: -5rem;
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
            margin-top: 0;
            margin-left: -1rem;
            margin-right: -1rem;
            padding: 2rem 1rem 1.5rem 1rem; /* Compact mobile padding */
            border-radius: 0 0 12px 12px;
        }
    }
    
    /* Hero Styling */
    .hero-container {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
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

    /* Centered Search Area */
    .search-wrapper {
        max-width: 800px;
        margin: 2rem auto;
        text-align: center;
        padding: 0 1rem;
    }
    
    .search-headline {
        font-size: 1.8rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 0.5rem;
    }
    
    .search-subtext {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Inputs */
    .stTextArea textarea {
        border-radius: 12px; /* Standard rounded */
        border: 1px solid #e0e0e0;
        padding: 1rem;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        color: #333;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 20px; /* Matching healthcare */
        min-height: 48px;
        font-weight: 500;
        background: black !important;
        color: white !important;
        white-space: nowrap !important;
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
        with tracer.start_as_current_span("run_research") as span:
            span.set_attribute("input.query", query)
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
        query = st.text_area("Research Topic", height=60, placeholder="e.g. The future of quantum computing in drug discovery...", label_visibility="collapsed", value="The future of quantum computing in drug discovery")
        
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

