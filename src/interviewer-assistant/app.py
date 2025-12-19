import streamlit as st
import os
import sys
import tempfile
import asyncio
import traceback
import pandas as pd
from fpdf import FPDF
from dotenv import load_dotenv
import extra_streamlit_components as stx

# Ensure we can import from local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from teams.team import get_interview_team, extract_json

# Load env variables
load_dotenv()

st.set_page_config(page_title="Interviewer Assistant", page_icon="👔", layout="wide")

# Cookie Manager Setup
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# Retrieve cookies (only LinkedIn)
cookie_linkedin = cookie_manager.get(cookie="linkedin_url")

# Custom CSS
st.markdown("""
<style>
    /* GLOBAL LAYOUT */
    div.block-container {
        padding-top: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stChatMessage { background-color: #262730; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .report-container { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    h1, h2, h3 { color: #f0f2f6; }
    
    /* HERO BANNER - CONTAINED */
    .hero-banner {
        width: 100%;
        height: 120px;
        background: transparent; 
        color: #333;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        z-index: 1;
        padding-top: 10px;
        border-bottom: 1px solid #eee;
    }
    
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        /* Black Gradient */
        background: -webkit-linear-gradient(#000000, #333333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #000;
    }
    
    /* MOVE SIDEBAR UP */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SIDEBAR: INPUTS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Interview Prep")
    st.info("Upload JD and Resume to generate a structured interview guide.")
    
    st.markdown("---")
    st.subheader("1. Job Description")
    job_description = st.text_area("Paste JD Text", height=200, placeholder="Paste the full Job Description here...")

    st.subheader("2. Candidate Resume")
    uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx", "txt"])
    
    st.subheader("3. LinkedIn (Optional)")
    default_linkedin = cookie_linkedin if cookie_linkedin else ""
    linkedin_url = st.text_input("LinkedIn Profile URL", value=default_linkedin, placeholder="https://www.linkedin.com/in/...")

    st.markdown("---")
    # State Initialization
    if "analyzing" not in st.session_state:
        st.session_state.analyzing = False
    if "generated_report" not in st.session_state:
        st.session_state.generated_report = None
    if "generated_pdf" not in st.session_state:
        st.session_state.generated_pdf = None

    def start_btn_click():
        st.session_state.analyzing = True
        st.session_state.generated_report = None # Clear previous
        st.session_state.generated_pdf = None
        # Save cookies when button is clicked
        if linkedin_url:
            cookie_manager.set("linkedin_url", linkedin_url, key="set_linkedin")

    if st.session_state.analyzing:
        # Disable button while running
        btn_disabled = True
    else:
        btn_disabled = False

    start_clicked = st.button("🚀 Generate Interview Guide", type="primary", use_container_width=True, on_click=start_btn_click, disabled=btn_disabled)

    # Note: cookie logic moved to on_click

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# LOGIC & ANALYSIS
# ------------------------------------------------------------------------------

async def run_analysis_stream(model_client, task_msg):
    team = get_interview_team(model_client)
    # Return the stream generator
    stream = team.run_stream(task=task_msg)
    return stream


def generate_markdown_report(messages):
    """
    Compiles the final report from agent messages.
    """
    report_md = "# Interviewer Assistant Report\n\n"
    
    # Extract key pieces
    candidate_summary = ""
    fitness_score = ""
    justification = ""
    interview_questions = ""
    
    # We iterate through messages to find the latest valid JSON outputs
    for msg in messages:
        # Handle AutoGen 0.4 Message Objects (TextMessage, MultiModalMessage, etc)
        content = ""
        source = ""
        
        if hasattr(msg, 'content'):
            content = msg.content
        if hasattr(msg, 'source'):
            source = msg.source
            
        # Skip if no content
        if not content or isinstance(content, list): # Basic handling for multimodal list content if needed
             continue
        
        json_data = extract_json(content)
        if json_data and isinstance(json_data, dict):
            
            if "candidate_summary" in json_data:
                candidate_summary = f"### Candidate Profile\n**Summary**: {json_data.get('candidate_summary')}\n\n"
                if "key_skills" in json_data:
                    candidate_summary += f"**Key Skills**: {', '.join(json_data['key_skills'])}\n\n"
            
            elif "fitness_score" in json_data:
                score = json_data.get("fitness_score")
                fitness_score = f"### Fitness Assessment\n**Score**: {score}/10\n\n"
                justification = f"**Assessment**: {json_data.get('justification')}\n\n"
            
            elif "structured_interview" in json_data:
                interview_questions = "### Structured Interview Questions\n\n"
                for section in json_data.get("structured_interview", []):
                    label = section.get("skill", section.get("category", "General"))
                    interview_questions += f"#### {label}\n"
                    for q_data in section.get("questions", []):
                        if isinstance(q_data, str):
                            interview_questions += f"- {q_data}\n"
                        else:
                            q_text = q_data.get("q", "")
                            q_type = q_data.get("type", "General")
                            q_complex = q_data.get("complexity", "Norm")
                            q_answer = q_data.get("sample_answer", "")
                            
                            interview_questions += f"- **Q ({q_type}, {q_complex})**: {q_text}\n"
                            if q_answer:
                                interview_questions += f"  - *Listen for*: {q_answer}\n"
                    interview_questions += "\n"

    report_md += candidate_summary
    report_md += fitness_score
    report_md += justification
    report_md += interview_questions
    
    return report_md

def create_pdf(markdown_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # Simple markdown-ish parsing for PDF (MultiCell handles newlines)
    # Removing markdown bold syntax for cleaner PDF
    clean_text = markdown_text.replace("**", "").replace("### ", "\n\n").replace("#### ", "\n")
    
    # Identify non-latin chars replacement (basic support)
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 7, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# ------------------------------------------------------------------------------
# HERO SECTION
# ------------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Interviewer Assistant</div>
    <div class="hero-subtitle">Automated Resume Analysis & Interview Prep • Powered by AutoGen</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MAIN PANEL
# ------------------------------------------------------------------------------

if st.session_state.analyzing:
    # Validation
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Missing OpenAI API Key. Please check your .env file or environment variables.")
        st.session_state.analyzing = False
        st.stop()
    if not job_description:
        st.error("Missing Job Description.")
        st.session_state.analyzing = False
        st.stop()
    if not uploaded_resume:
        st.error("Missing Resume File.")
        st.session_state.analyzing = False
        st.stop()

    try:
        # Process Input
        resume_path = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_resume.name.split('.')[-1]}") as tmp_file:
             tmp_file.write(uploaded_resume.getvalue())
             resume_path = tmp_file.name

        resume_content_msg = f"Candidate Resume File Path: {resume_path} (Please use `read_local_file` to read this)."
        if linkedin_url:
            resume_content_msg += f"\nAlso check LinkedIn: {linkedin_url} (use `scrape_web_page`)."

        # Execution
        prog_bar = st.progress(0)
        status_text = st.empty()
        
        # Create Model Client using Factory
        from common.utility.autogen_model_factory import AutoGenModelFactory
        model_client = AutoGenModelFactory.get_model(
            provider="openai", model_name="gpt-4-turbo", model_info={"vision": False, "function_calling": True, "json_output": False}
        )
        
        task_msg = f"""
        Here is the Job Description:
        {job_description}

        {resume_content_msg}

        The team must follow the strict workflow: 
        Profiler -> Job Analyst -> Reviewer -> Evaluator -> Designer.
        """

        status_text.text("Initializing Agents...")
        prog_bar.progress(10)
        
        # Create a placeholder for debug output to avoid context issues inside async
        debug_placeholder = st.empty()
        
        # Define debug print helper
        def debug_print(msg):
            print(f"DEBUG: {msg}")
            # Optional: toast for visibility
            # st.toast(msg)

        debug_print("Analysis Started. Loop initializing...")

        async def execute_analysis(placeholder):
            try:
                debug_print("Entering execute_analysis async function")
                with st.spinner("Analyzing candidate and designing interview..."):
                     # Get the stream
                     debug_print(f"Creating team and stream with task length {len(task_msg)}")
                     stream = await run_analysis_stream(model_client, task_msg)
                     
                     messages = []
                     msg_count = 0
                     debug_print("Stream created. Iterating...") 
                     
                     # Stream messages
                     async for message in stream:
                         msg_count += 1
                         messages.append(message)
                         
                         source = getattr(message, 'source', 'Unknown')
                         content = getattr(message, 'content', '')
                         print(f"Stream Msg {msg_count}: {source} - Content: {str(content)[:50]}...") 
                         
                         if isinstance(content, list):
                             content = "[Multimodal Content]"
                         elif not content:
                             content = "[No Content]"
                         
                         # Update Debug UI safely
                         placeholder.text(f"[{msg_count}] {source}: {str(content)[:150]}...")
                         
                         # Progress bar update
                         if source == "Candidate_Profiler": prog_bar.progress(20)
                         elif source == "Job_Analyst": prog_bar.progress(40)
                         elif source == "Job_Analyst_Reviewer": prog_bar.progress(60)
                         elif source == "Evaluator": prog_bar.progress(80)
                         elif source == "Interview_Designer": prog_bar.progress(95)
                     
                     if msg_count == 0:
                         st.error("No messages received. Check logs/console.")
                         debug_print("Stream finished with 0 messages.")
                     else:
                         debug_print(f"Stream finished with {msg_count} messages.")

                prog_bar.progress(100)
                status_text.text("Analysis Complete.")
                
                # Generation
                final_markdown = generate_markdown_report(messages)
                
                if not final_markdown.strip():
                     final_markdown = "## Report Generation Failed\nNo structured output was found from the agent team."
                
                # Save to State (Persistence)
                st.session_state.generated_report = final_markdown
                st.session_state.generated_pdf = create_pdf(final_markdown)
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
                import traceback
                st.text(traceback.format_exc())
                debug_print(f"Async Job Failed: {e}")

        # Run the async execution
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(execute_analysis(debug_placeholder))
            finally:
                # Cleanup pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
        except Exception as e:
            st.error(f"System Error: {e}")
            import traceback
            st.text(traceback.format_exc())
            
    finally:
        # Reset analysis state at the end so user can run again
        st.session_state.analyzing = False
        # Optional: st.rerun() if we want to reset UI immediately, but keeping visible results is better.
        # But if we don't rerun, the "Disabled" button stays disabled? 
        # Actually I used `if st.session_state.analyzing: disabled=True`. 
        # Since I set it to False here, the next rerun (triggered by download or interaction) will enable it.
        # To re-enable immediately: switch the disabled logic to check a different key or force rerun
        st.rerun() 
        
else:
    st.info("👈 Please fill in the details in the sidebar to get started.")

# ------------------------------------------------------------------------------
# REPORT DISPLAY (Persistent)
# ------------------------------------------------------------------------------
if st.session_state.generated_report:
    st.markdown("---")
    st.header("📝 Interview Guide")
    
    # Render Markdown
    st.markdown(st.session_state.generated_report)
    
    # Render Download Button
    if st.session_state.generated_pdf:
        st.download_button(
            label="📄 Download Interview Guide (PDF)",
            data=st.session_state.generated_pdf,
            file_name="interview_guide.pdf",
            mime="application/pdf"
        )
