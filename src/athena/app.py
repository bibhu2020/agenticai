import asyncio
import html
import re
import uuid
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from agents import SQLiteSession
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from model_factory import MODEL_LABELS, OLLAMA_MODEL_OPTIONS, get_model_from_label, provider_ready
from orchestrator import Orchestrator
from tracing import setup_langfuse_tracing

setup_langfuse_tracing()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Athena", layout="wide", page_icon="🦉")

st.markdown("""
<style>
    * { box-sizing: border-box; }

    /* ── 1. Single vivid gradient — the only background on the page ── */
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 10% 10%, rgba(99,102,241,0.55) 0%, transparent 55%),
            radial-gradient(ellipse 70% 55% at 90% 85%, rgba(139,92,246,0.50) 0%, transparent 55%),
            radial-gradient(ellipse 60% 40% at 55% 45%, rgba(59,130,246,0.30) 0%, transparent 55%),
            linear-gradient(160deg, #1e1b4b 0%, #312e81 60%, #1e3a8a 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
    }

    /* ── 2. Clear every Streamlit wrapper so the gradient shows through ── */
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    .element-container,
    [data-testid="stMarkdownContainer"] {
        background: transparent !important;
    }

    header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
    div[data-testid="stDecoration"] { display: none; }

    /* ── 3. Main content — single glass layer ── */
    .block-container {
        background: rgba(255, 255, 255, 0.10) !important;
        backdrop-filter: blur(28px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(160%) !important;
        padding: 2.5rem 2.5rem 3rem !important;
        max-width: 100% !important;
    }
    @media (max-width: 768px) {
        .block-container { padding: 1.5rem 1rem 2rem !important; }
    }

    /* ── 4. Sidebar — same glass, seamlessly connected ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: rgba(255, 255, 255, 0.10) !important;
        backdrop-filter: blur(28px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(160%) !important;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.18) !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        overflow-y: hidden !important;
        padding-top: 1.25rem !important;
        padding-bottom: 1rem !important;
    }

    /* ── 5. Sidebar text & widget colours for dark glass base ── */
    [data-testid="stSidebar"] h3 {
        font-size: 0.72rem !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 0.08em !important;
        color: rgba(255,255,255,0.55) !important; margin: 0 0 0.4rem !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: rgba(255,255,255,0.85) !important; }
    [data-testid="stSidebar"] .stCaption p {
        color: rgba(255,255,255,0.50) !important;
        font-size: 0.70rem !important; margin-top: 0.1rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important; margin: 0.75rem 0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stButton { margin-bottom: 0.5rem !important; }

    /* Sidebar select + slider: glass chips */
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255,255,255,0.14) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 10px !important; color: rgba(255,255,255,0.90) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] svg { fill: rgba(255,255,255,0.60) !important; }
    [data-testid="stSidebar"] [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] [data-testid="stTickBarMax"] { color: rgba(255,255,255,0.45) !important; }

    /* Sidebar button */
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.14) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        color: rgba(255,255,255,0.85) !important;
        border-radius: 10px !important; min-height: 38px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.22) !important;
    }

    /* ── 6. Body headings & text ── */
    h3, h4 { color: rgba(255,255,255,0.95) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5 { color: rgba(255,255,255,0.95) !important; }
    .stMarkdown p, .stMarkdown li { color: rgba(255,255,255,0.85) !important; line-height: 1.75; }
    .stCaption p { color: rgba(255,255,255,0.50) !important; font-size: 0.78rem !important; }

    /* ── 7. Textarea — light box on dark glass for clear readability ── */
    .stTextArea textarea {
        background: rgba(255,255,255,0.92) !important;
        border: 1px solid rgba(255,255,255,0.60) !important;
        border-radius: 14px !important;
        padding: 1rem !important;
        color: #1a1a1a !important;
        font-size: 1rem !important;
        line-height: 1.65 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.20) !important;
        transition: border-color 0.2s, box-shadow 0.2s;
        caret-color: #6366f1;
    }
    .stTextArea textarea::placeholder { color: #9ca3af !important; }
    .stTextArea textarea:focus {
        border-color: rgba(99,102,241,0.70) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.20), 0 2px 12px rgba(0,0,0,0.20) !important;
        background: #ffffff !important;
        outline: none !important;
    }
    .stTextArea label { color: rgba(255,255,255,0.80) !important; font-weight: 500 !important; }

    /* ── 8. Primary button ── */
    .stButton button {
        background: rgba(99,102,241,0.75) !important;
        color: white !important;
        border: 1px solid rgba(165,180,252,0.40) !important;
        border-radius: 20px !important; min-height: 44px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.30) !important;
        transition: background 0.2s, box-shadow 0.2s !important;
    }
    .stButton button:hover {
        background: rgba(99,102,241,0.90) !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
    }
    .stDownloadButton button {
        background: rgba(255,255,255,0.14) !important;
        color: rgba(255,255,255,0.90) !important;
        border: 1px solid rgba(255,255,255,0.28) !important;
        border-radius: 20px !important; min-height: 44px !important;
        font-weight: 500 !important; backdrop-filter: blur(8px) !important;
    }
    .stDownloadButton button:hover { background: rgba(255,255,255,0.22) !important; }

    /* ── 9. Status widget ── */
    [data-testid="stStatusWidget"] {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px) !important;
    }
    [data-testid="stStatusWidget"] p { color: rgba(255,255,255,0.85) !important; }

    /* ── 10. Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.20); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "session_id"     not in st.session_state: st.session_state.session_id     = str(uuid.uuid4())
if "final_report"   not in st.session_state: st.session_state.final_report   = ""
if "is_researching" not in st.session_state: st.session_state.is_researching = False
if "current_query"  not in st.session_state: st.session_state.current_query  = ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_pdf(text: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=22*mm, bottomMargin=22*mm,
        leftMargin=25*mm, rightMargin=25*mm,
    )

    indigo  = colors.HexColor("#1e1b4b")
    ink     = colors.HexColor("#1a1a1a")
    muted   = colors.HexColor("#555555")
    rule_c  = colors.HexColor("#d1d5db")
    code_bg = colors.HexColor("#f3f4f6")
    code_fg = colors.HexColor("#be185d")

    S = {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold",   fontSize=22, leading=28,
                              textColor=indigo, spaceBefore=14, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold",   fontSize=17, leading=22,
                              textColor=indigo, spaceBefore=12, spaceAfter=5),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold",   fontSize=14, leading=18,
                              textColor=indigo, spaceBefore=10, spaceAfter=4),
        "h4": ParagraphStyle("h4", fontName="Helvetica-Bold",   fontSize=12, leading=16,
                              textColor=ink,   spaceBefore=8,  spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica",    fontSize=11, leading=17,
                                textColor=ink, spaceBefore=3, spaceAfter=3,
                                alignment=TA_JUSTIFY),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=11, leading=16,
                                  textColor=ink, spaceBefore=2, spaceAfter=2,
                                  leftIndent=18, firstLineIndent=0),
        "num":    ParagraphStyle("num",    fontName="Helvetica", fontSize=11, leading=16,
                                  textColor=ink, spaceBefore=2, spaceAfter=2,
                                  leftIndent=18, firstLineIndent=0),
        "bq":  ParagraphStyle("bq",  fontName="Helvetica-Oblique", fontSize=11, leading=17,
                               textColor=muted, spaceBefore=5, spaceAfter=5,
                               leftIndent=20),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=9, leading=13,
                                textColor=code_fg, backColor=code_bg,
                                spaceBefore=2, spaceAfter=2,
                                leftIndent=14, rightIndent=14),
    }

    def fmt(s: str) -> str:
        """Convert inline markdown to reportlab XML."""
        s = html.escape(s)
        s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', s)
        s = re.sub(r'\*\*(.+?)\*\*',     r'<b>\1</b>',         s)
        s = re.sub(r'\*(.+?)\*',          r'<i>\1</i>',          s)
        s = re.sub(r'`(.+?)`',
                   r'<font name="Courier" color="#be185d">\1</font>', s)
        s = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'<u>\1</u>', s)
        return s

    story: list = []
    for line in text.splitlines():
        s = line.rstrip()
        if not s:
            story.append(Spacer(1, 5))
        elif s.startswith("#### "):
            story.append(Paragraph(fmt(s[5:]), S["h4"]))
        elif s.startswith("### "):
            story.append(Paragraph(fmt(s[4:]), S["h3"]))
        elif s.startswith("## "):
            story.append(Paragraph(fmt(s[3:]), S["h2"]))
        elif s.startswith("# "):
            story.append(Paragraph(fmt(s[2:]), S["h1"]))
        elif s.startswith("> "):
            story.append(Paragraph(fmt(s[2:]), S["bq"]))
        elif re.match(r'^[-*] ', s):
            story.append(Paragraph("• " + fmt(s[2:]), S["bullet"]))
        elif re.match(r'^\d+\. ', s):
            m = re.match(r'^(\d+)\. (.*)', s)
            story.append(Paragraph(f"{m.group(1)}. {fmt(m.group(2))}", S["num"]))
        elif re.match(r'^[-*_]{3,}$', s):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=rule_c))
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(fmt(s), S["body"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()


@st.cache_resource
def _get_orchestrator(model_label: str, ollama_model: str) -> Orchestrator:
    model   = get_model_from_label(model_label, ollama_model=ollama_model)
    session = SQLiteSession(f"dr_{st.session_state.session_id}.db")
    return Orchestrator(model=model, session=session)


async def run_research(query: str, report_format: str, research_depth: str) -> None:
    model_label  = st.session_state.get("model_label",  "GPT-4o")
    ollama_model = st.session_state.get("ollama_model", "qwen3:8b")
    orchestrator = _get_orchestrator(model_label, ollama_model)

    status = st.status("🔍 Researching…", expanded=True)
    report = ""
    try:
        async for chunk in orchestrator.run(query, report_format=report_format, research_depth=research_depth):
            if chunk.startswith(("Planning", "Running", "Searches complete", "⚠️")):
                status.markdown(chunk)
            else:
                report = chunk
                status.markdown("Finalising report…")

        st.session_state.final_report   = report
        st.session_state.is_researching = False
        status.update(label="✅ Research Complete", state="complete", expanded=False)
        st.rerun()
    except Exception as exc:
        status.update(label="❌ Error", state="error")
        st.error(f"Error: {exc}")
        st.session_state.is_researching = False

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 Model")
    selected_label = st.selectbox(
        "Model", options=MODEL_LABELS,
        index=MODEL_LABELS.index(st.session_state.get("model_label", "GPT-4o")),
        key="model_label", label_visibility="collapsed",
    )
    if selected_label == "Ollama (local)":
        st.selectbox("Ollama model", options=OLLAMA_MODEL_OPTIONS, key="ollama_model", label_visibility="collapsed")
    else:
        st.session_state.setdefault("ollama_model", "qwen3:8b")

    _ollama = st.session_state.get("ollama_model", "qwen3:8b")
    ready, warn = provider_ready(selected_label, ollama_model=_ollama)
    st.session_state["_provider_ready"] = ready
    if not ready:
        st.warning(warn, icon="⚠️")
    else:
        st.caption("✅ Provider ready")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    research_depth = st.select_slider("Depth", options=["Quick", "Standard", "Deep"], value="Standard")
    report_format  = st.selectbox("Format", ["Academic", "Business", "Humorous"], index=0)
    st.caption("Quick = 5 searches · Standard = 10 · Deep = 15")

    st.markdown("---")
    if st.button("🗑️ Clear Report", use_container_width=True):
        st.session_state.final_report   = ""
        st.session_state.is_researching = False
        st.rerun()

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
_provider_ok = st.session_state.get("_provider_ready", True)

if not st.session_state.final_report and not st.session_state.is_researching:

    st.markdown("### 🦉 What do you want to research?")
    st.caption("Deep Research browses the web, analyses sources, and writes a comprehensive report.")
    query = st.text_area(
        "Research Topic", height=180,
        placeholder="e.g. The future of quantum computing in drug discovery…",
        label_visibility="collapsed",
        value="Impact of Quantum Computing on Drug Research.",
    )
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        disabled = not (_provider_ok and query.strip())
        if st.button("Start Research", use_container_width=True, disabled=disabled):
            st.session_state.is_researching = True
            st.session_state.current_query  = query
            st.rerun()
    if not _provider_ok:
        st.caption("⚠️ Select a ready provider in the sidebar first.")

elif st.session_state.is_researching:
    st.markdown("#### Compiling Report…")
    asyncio.run(run_research(st.session_state.current_query, report_format, research_depth))

else:
    col_dl, col_new, _ = st.columns([1, 1, 4])
    with col_dl:
        st.download_button(
            "📄 Download PDF",
            make_pdf(st.session_state.final_report),
            "report.pdf", mime="application/pdf",
            use_container_width=True,
        )
    with col_new:
        if st.button("🔄 New Research", use_container_width=True):
            st.session_state.final_report   = ""
            st.session_state.is_researching = False
            st.rerun()

    st.markdown(st.session_state.final_report)
