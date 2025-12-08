import streamlit as st
import asyncio
import time
import html
from datetime import datetime, UTC
from io import BytesIO

from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from appagents.orchestrator import Orchestrator
from agents import SQLiteSession

load_dotenv(override=True)

# --------------------
# Page config
# --------------------
st.set_page_config(page_title="Deep Research AI", layout="wide")

# --------------------
# Session-state init
# --------------------
if "session_store" not in st.session_state:
    st.session_state.session_store = {}

if "session_id" not in st.session_state:
    st.session_state.session_id = str(id(st))

if "final_report" not in st.session_state:
    st.session_state.final_report = ""

if "button_disabled" not in st.session_state:
    st.session_state.button_disabled = False

# --------------------
# Updated CSS for better visibility across devices
# --------------------
UPDATED_CSS = """
<style>
.block-container { max-width: 90% !important; margin-left:5% !important; margin-right:5% !important; padding-top:1.5rem; padding-bottom:2rem; }
h1, h2, h3 { font-size:2.2rem !important; text-align:center; color: #F8F9FA !important; }
h2, h3 { color: #F8F9FA !important; }
.report-box { background:#212529; padding:24px; border-radius:12px; border:1px solid #343A40; box-shadow:0 6px 18px rgba(0, 0, 0, 0.4); font-size:1.05rem; line-height:1.65; white-space:pre-wrap; color: #E9ECEF; }
target.textarea, .stTextArea>div>div>textarea { background: #343A40 !important; color: #F8F9FA !important; font-size:1.05rem !important; }
.stButton>button { background-color: #495057 !important; color: #F8F9FA !important; }
.stButton>button:hover { background-color: #6C757D !important; }
.stButton>button:active { background-color: #ADB5BD !important; }
body { background-color: #121212; color: #F8F9FA; }
.small-muted { color:#CED4DA; font-size:0.9rem; }
</style>
"""
st.markdown(UPDATED_CSS, unsafe_allow_html=True)

# --------------------
# Helpers: orchestrator streaming
# --------------------
async def run_async_chunks(query: str, session_id: str):
    if session_id not in st.session_state.session_store:
        st.session_state.session_store[session_id] = SQLiteSession(f"session_{session_id}.db")
    session = st.session_state.session_store[session_id]
    orchestrator = Orchestrator(session=session)
    async for chunk in orchestrator.run(query):
        yield chunk

def safe_title_from_query(q: str):
    q = q.strip()
    if not q:
        return "Untitled Report"
    first_line = q.splitlines()[0]
    # limit length for title
    return (first_line[:80] + "...") if len(first_line) > 80 else first_line

# --------------------
# Export helpers
# --------------------
def make_pdf_bytes(text: str) -> bytes:
    """Convert markdown text to PDF with proper formatting."""
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, topMargin=0.5*72, bottomMargin=0.5*72, leftMargin=0.75*72, rightMargin=0.75*72)
    styles = getSampleStyleSheet()
    story = []
    
    # parse markdown: headings, lists, bold, italic
    lines = text.split("\n")
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            story.append(Paragraph(" ", styles["Normal"]))  # empty line
            continue
        
        # heading levels
        if stripped.startswith("# "):
            story.append(Paragraph(html.escape(stripped[2:]), styles["Heading1"]))
        elif stripped.startswith("## "):
            story.append(Paragraph(html.escape(stripped[3:]), styles["Heading2"]))
        elif stripped.startswith("### "):
            story.append(Paragraph(html.escape(stripped[4:]), styles["Heading3"]))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            # bullet list
            story.append(Paragraph("• " + html.escape(stripped[2:]), styles["Normal"]))
        elif stripped[0].isdigit() and ". " in stripped[:4]:
            # numbered list
            story.append(Paragraph(html.escape(stripped), styles["Normal"]))
        else:
            # regular paragraph with basic markdown formatting
            # escape first, then replace with safe formatting tags
            p_text = html.escape(stripped)
            
            # handle **bold** (convert escaped ** back and wrap in <b> tags)
            p_text = p_text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            # Simple approach: replace **text** with <b>text</b>
            import re
            p_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', p_text)
            p_text = re.sub(r'__(.+?)__', r'<b>\1</b>', p_text)
            # handle *italic* → <i>italic</i> carefully (avoid double replacement)
            p_text = re.sub(r'\*([^*]+?)\*', r'<i>\1</i>', p_text)
            p_text = re.sub(r'_([^_]+?)_', r'<i>\1</i>', p_text)
            
            story.append(Paragraph(p_text, styles["Normal"]))
    
    doc.build(story)
    buf.seek(0)
    return buf.read()

def make_md_bytes(text: str) -> bytes:
    return text.encode("utf-8")

def make_html_bytes(text: str, title="Deep Research Report") -> bytes:
    # simple HTML wrapper, escape content and preserve newlines
    body = "<br/>".join(html.escape(text).split("\n"))
    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset=\"utf-8\">
<title>{{html.escape(title)}}</title>
<style>body{{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:24px; max-width:900px; margin:auto; line-height:1.6; color: #F8F9FA; background: #121212; }}</style>
</head>
<body>
<h1>{{html.escape(title)}}</h1>
<div>{{body}}</div>
</body>
</html>"""
    return html_doc.encode("utf-8")

# --------------------
# Streaming runner (final output replaces trace)
# --------------------
def run_streaming(query: str, final_ph, status_ph):
    session_id = st.session_state.session_id

    # placeholders
    progress_ph = st.empty()

    # reset final_report
    st.session_state.final_report = ""
    # track only the last received chunk
    last_chunk = ""
    progress_val = 0
    progress_bar = progress_ph.progress(progress_val)

    # ensure any prior final output is cleared while streaming
    try:
        final_ph.empty()
    except Exception:
        pass

    async def _stream():
        nonlocal progress_val, last_chunk
        status_ph.info("Streaming... receiving data")
        bStartChunkCollected = False
        async for chunk in run_async_chunks(query, session_id):
            # start collecting chunks once we see one beginning with #
            if not bStartChunkCollected and chunk.strip().startswith("#"):
                bStartChunkCollected = True

            if bStartChunkCollected:
                last_chunk += chunk
                # render accumulated markdown in real-time so user sees content streaming
                status_ph.markdown(last_chunk)
            
            progress_val = min(progress_val + 2, 98)
            progress_bar.progress(progress_val)

    # run async generator (compatibility fallback)
    try:
        asyncio.run(_stream())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_stream())
        loop.close()
    except Exception as e:
        # on exception, re-enable button and show error
        st.session_state.button_disabled = False
        status_ph.error(f"❌ Error during research: {{str(e)}}")
        progress_ph.empty()
        return

    # finalize
    progress_bar.progress(100)
    status_ph.success("✅ Research complete!")

    # set final_report to only the last yield (trim surrounding whitespace)
    md_text = last_chunk.strip()
    st.session_state.final_report = md_text
    progress_ph.empty()

    # re-enable button after completion
    st.session_state.button_disabled = False

    # render final output as Markdown into the dedicated placeholder
    if st.session_state.final_report:
        final_ph.markdown(st.session_state.final_report)
    else:
        final_ph.empty()

    st.rerun()

# --------------------
# Main UI
# --------------------
st.title("🧠 Deep Research (Powered by Agentic AI)")
st.write("What topic would you like to research?")

query = st.text_area("Enter your research topic", value="The impact of AI on the Healthcare Industry.", height=50, label_visibility="collapsed")

# Action row with buttons
col1, col2, col3, col4 = st.columns([2.0, 2.0, 2.0, 2.0])

with col1:
    run_clicked = st.button("🚀 Run Deep Research", key="run", disabled=st.session_state.button_disabled)

# PDF and MD download buttons appear inline after a final_report exists
if st.session_state.final_report:
    with col2:
        # PDF generator stream - create bytes on demand
        pdf_bytes = make_pdf_bytes(st.session_state.final_report)
        st.download_button("📄 Download PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
    
    with col3:
        # Markdown
        md_bytes = make_md_bytes(st.session_state.final_report)
        st.download_button("📝 Download MD", data=md_bytes, file_name="report.md", mime="text/markdown")

# placeholder for final report (used so streaming traces can be cleared)
final_ph = st.empty()

# placeholder for streaming status and progress updates
status_ph = st.empty()

# Run research if requested; disable button on click and re-run
if run_clicked and query.strip():
    st.session_state.button_disabled = True
    st.rerun()

# Execute streaming if button was disabled (i.e., on the rerun after click)
if st.session_state.button_disabled and query.strip():
    run_streaming(query.strip(), final_ph, status_ph)
elif not st.session_state.button_disabled:
    # if final_report exists (e.g., from previous run), show it in the final placeholder
    if st.session_state.final_report:
        final_ph.markdown(st.session_state.final_report, unsafe_allow_html=True)
    else:
        st.info("Enter a topic and press Run. Final report will replace streaming traces.")

# small debug caption
st.caption(f"Session: {{st.session_state.session_id}}")
