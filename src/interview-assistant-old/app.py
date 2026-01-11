import streamlit as st
import os
import sys
import tempfile
import asyncio
import traceback
import extra_streamlit_components as stx
from dotenv import load_dotenv

# Ensure we can import from local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from teams.team import get_interview_team
from ui.styles import apply_custom_styles
from ui.hero import render_hero
from ui.sidebar import render_sidebar
from ui.report import generate_markdown_report, create_pdf, render_persistent_view
from common.utility.autogen_model_factory import AutoGenModelFactory

# Load env variables
load_dotenv()

st.set_page_config(page_title="Interviewer Assistant", page_icon="👔", layout="wide")

# Cookie Manager (Must be initialized at top level)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# 1. Apply Styles
apply_custom_styles()

# 2. Render Sidebar
sidebar_data = render_sidebar(cookie_manager)
mode = sidebar_data["mode"]
job_description = sidebar_data["job_description"]
uploaded_resume = sidebar_data["uploaded_resume"]
linkedin_url = sidebar_data["linkedin_url"]

# 3. Render Hero
render_hero()

# ------------------------------------------------------------------------------
# LOGIC & ANALYSIS HELPERS
# ------------------------------------------------------------------------------

async def run_analysis_stream(model_client, task_msg):
    team = get_interview_team(model_client)
    # Return the stream generator
    stream = team.run_stream(task=task_msg)
    return stream

# ------------------------------------------------------------------------------
# MAIN CONTENT LOGIC
# ------------------------------------------------------------------------------

if mode == "Candidate":
    st.markdown("## 🎓 Candidate Prep Portal")
    st.info("This feature is under development. It will allow candidates to take mock interviews based on the generated guide.")
    st.image("https://cdn-icons-png.flaticon.com/512/3220/3220565.png", width=150)
    st.stop()

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
                         debug_print(f"Stream Msg {msg_count}: {source}") 
                         
                         if isinstance(content, list):
                             content = "[Multimodal Content]"
                         elif not content:
                             content = "[No Content]"
                             
                         # Evidence: Show Data (Source Content) in UI & Console
                         if isinstance(content, str) and len(content) > 500:
                             print(f"--- EVIDENCE ({source}) ---\n{content[:5000]}\n---------------------------")
                             with st.expander(f"📄 Data Source Evidence ({source})", expanded=False):
                                 st.text(content)
                         
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
        st.rerun() 
        
else:
    st.info("👈 Please fill in the details in the sidebar to get started.")

# 4. Render Persistent View (Report)
render_persistent_view()
