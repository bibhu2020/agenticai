import streamlit as st
import os
import sys
import sqlite3
import shutil
import pandas as pd
from dotenv import load_dotenv
import asyncio

# --- Imports ---
# Ensure local modules can be imported
# Use insert(0) to prioritize local 'agents' folder over installed 'agents' package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.ingest import process_uploaded_files
from rag.db import get_db
# from agents.manager import get_agent_manager # Deprecated
from teams.evaluation_team import run_evaluation_team
import json
import re

# Load environment variables
# Assuming app.py is in src/interview-assistant/, root is 2 levels up
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Set page config
st.set_page_config(page_title="Agentic Interview Assistant", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for improvements
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    .main-header {
        font-size: 2.0rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 0.5rem;
    }
    /* Compact the grid */
    div[data-testid="column"] {
        padding: 0 !important;
    }
    p {
        margin-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Define Base Directory for persistent storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure data directory exists
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, "interview_state.db")
RAG_DIR = os.path.join(DATA_DIR, "interview_rag_db")

# --- Database Helper Functions ---

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Init Tables
    c.execute('''CREATE TABLE IF NOT EXISTS job_context (
                    id INTEGER PRIMARY KEY, 
                    description TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    filename TEXT,
                    status TEXT,
                    score INTEGER,
                    strengths TEXT,
                    weaknesses TEXT,
                    questions TEXT
                 )''')
    
    # Safe migration for existing dbs
    try:
         c.execute("ALTER TABLE candidates ADD COLUMN questions TEXT")
    except sqlite3.OperationalError:
         pass

    conn.commit()
    conn.close()

def load_state():
    """Loads JD and Candidates from SQLite to Session State"""
    if not os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Load JD
    try:
        jd_df = pd.read_sql_query("SELECT description FROM job_context LIMIT 1", conn)
        if not jd_df.empty:
            st.session_state['jd'] = jd_df.iloc[0]['description']
        
        # Load Candidates
        cands_df = pd.read_sql_query("SELECT * FROM candidates", conn)
        if not cands_df.empty:
            st.session_state['candidates'] = cands_df.to_dict('records')
    except Exception as e:
        print(f"Error loading state: {e}")
    finally:
        conn.close()

def save_new_session(job_desc, processed_docs):
    """Saves initial session data to SQLite based on processed RAG docs"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Save JD
    c.execute("DELETE FROM job_context")
    c.execute("INSERT INTO job_context (description) VALUES (?)", (job_desc,))
    
    # Save Candidates (Deduplicate based on name)
    c.execute("DELETE FROM candidates")
    
    # Extract unique candidates from docs
    unique_candidates = {}
    for doc in processed_docs:
        meta = doc['metadata']
        name = meta['candidate_name']
        if name not in unique_candidates:
            unique_candidates[name] = {
                'name': name,
                'filename': meta['filename'],
                'status': 'Pending',
                'score': 0,
                'strengths': '-',
                'weaknesses': '-',
                'questions': None
            }
    
    candidates_list = []
    for cand in unique_candidates.values():
        c.execute("""INSERT INTO candidates (name, filename, status, score, strengths, weaknesses, questions) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                     (cand['name'], cand['filename'], cand['status'], cand['score'], cand['strengths'], cand['weaknesses'], cand['questions']))
        candidates_list.append(cand)
    
    conn.commit()
    conn.close()
    return candidates_list

def update_candidate_record(name, status, score, strengths, weaknesses):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE candidates 
                 SET status = ?, score = ?, strengths = ?, weaknesses = ? 
                 WHERE name = ?""", 
                 (status, score, strengths, weaknesses, name))
    conn.commit()
    conn.close()

def update_candidate_questions(name, questions_json_str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE candidates SET questions = ? WHERE name = ?", (questions_json_str, name))
    conn.commit()
    conn.close()

def update_job_description(new_jd):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Update JD
    c.execute("DELETE FROM job_context")
    c.execute("INSERT INTO job_context (description) VALUES (?)", (new_jd,))
    
    # Reset candidates
    c.execute("UPDATE candidates SET status = 'Pending', score = 0, strengths = '-', weaknesses = '-'")
    conn.commit()
    conn.close()
    
    # Update session state
    st.session_state['jd'] = new_jd
    for c in st.session_state['candidates']:
        c['status'] = 'Pending'
        c['score'] = 0
        c['strengths'] = '-'
        c['weaknesses'] = '-'

# Removed st.experimental_dialog to ensure compatibility
# JD Editor logic moved to render_dashboard

def reset_system():
    """Wipes SQLite and RAG DB"""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except:
            pass
    
    # Reset ChromaDB
    try:
        get_db().reset()
    except Exception as e:
        # If DB file doesn't exist yet, that's fine
        print(f"RAG Reset info: {e}")
    
    st.session_state.clear()
    st.rerun()

# --- App Logic ---

# Initialize
if 'init_done' not in st.session_state:
    init_db()
    st.session_state['init_done'] = True
    st.session_state['candidates'] = []
    st.session_state['jd'] = ""
    load_state() # Load from DB if exists

if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'
if 'selected_candidate_for_studio' not in st.session_state:
    st.session_state['selected_candidate_for_studio'] = None

def main():
    # Header
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown('<div class="main-header">🤖 Agentic Interview Assistant</div>', unsafe_allow_html=True)
        st.markdown("Your AI-powered partner for talent acquisition.")
    
    with c2:
        if st.button("🔄 New Interview", type="secondary", help="Reset all data and start over"):
            reset_system()

    st.markdown("---")

    # Check for persistence
    has_active_session = bool(st.session_state['candidates']) and bool(st.session_state['jd'])

    # --- Flow 1: Upload & Store (Top Section) ---
    if not has_active_session:
        with st.container():
            st.info("👋 Welcome! Please upload resumes and provide a Job Description to get started.")
            
            c1, c2 = st.columns([1, 1], gap="small")
            with c1:
                st.markdown("### 1. Candidate Resumes")
                uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
            
            with c2:
                st.markdown("### 2. Job Description")
                jd_input = st.text_area("Paste the JD here...", height=150, placeholder="We are looking for a Senior Python Engineer...")
            
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                if uploaded_files and jd_input:
                    with st.spinner("Ingesting resumes & building Knowledge Base..."):
                        try:
                            # 1. Process PDFs
                            processed_docs = process_uploaded_files(uploaded_files)
                            
                            if not processed_docs:
                                st.error("No text could be extracted from these PDFs.")
                                st.stop()

                            # 2. Add to RAG (Chroma)
                            get_db().add_documents(processed_docs)
                            
                            # 3. Save Session Metadata to SQLite
                            st.session_state['candidates'] = save_new_session(jd_input, processed_docs)
                            st.session_state['jd'] = jd_input
                            
                            st.success(f"Successfully processed {len(st.session_state['candidates'])} candidates.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please upload files and enter a job description.")
    else:
        # Show mini stats
        total = len(st.session_state['candidates'])
        evaluated = len([c for c in st.session_state['candidates'] if c['status'] == 'Evaluated'])
        avg_score = 0
        if evaluated > 0:
            scores = []
            for c in st.session_state['candidates']:
                if c['status'] == 'Evaluated':
                    try:
                        scores.append(float(c['score']))
                    except (ValueError, TypeError):
                        scores.append(0)
            
            avg_score = sum(scores) / len(scores) if scores else 0

        # Compact Summary Row
        col_metrics, col_edit = st.columns([6, 1])
        with col_metrics:
            st.markdown(f"""
            <div style="display: flex; gap: 24px; align-items: center; padding: 10px 15px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 5px; font-size: 0.9rem;">
                <div>📊 <strong>Candidates:</strong> {total}</div>
                <div style="border-left: 1px solid #eee; height: 18px;"></div>
                <div>✅ <strong>Evaluated:</strong> {evaluated}</div>
                <div style="border-left: 1px solid #eee; height: 18px;"></div>
                <div>⭐ <strong>Avg Score:</strong> {avg_score:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_edit:
             if st.button("📝 Edit JD", help="View or Update Job Description"):
                 st.session_state['show_jd_edit'] = not st.session_state.get('show_jd_edit', False)

        # Inline Editor for maximum compatibility
        if st.session_state.get('show_jd_edit', False):
            with st.container():
                st.markdown("### Update Job Description")
                st.warning("⚠️ Saving a new JD will reset all candidate evaluations.")
                
                new_jd = st.text_area("Job Description", value=st.session_state['jd'], height=200, key="jd_editor_area")
                
                ec1, ec2 = st.columns([1, 5])
                with ec1:
                    if st.button("💾 Save & Reset", type="primary"):
                        update_job_description(new_jd)
                        st.session_state['show_jd_edit'] = False
                        st.rerun()
                with ec2:
                    if st.button("Cancel"):
                        st.session_state['show_jd_edit'] = False
                        st.rerun()
                st.markdown("---")

    # st.markdown("---") # Removed large divider

    # --- Flow Switcher ---
    if has_active_session:
        if st.session_state['current_view'] == 'dashboard':
            render_dashboard()
        else:
            render_studio()

def render_dashboard():
    st.subheader("📊 Candidate Dashboard")
    
# ... (Previous code)

# Helper function for evaluation (to avoid code duplication)
async def perform_evaluation(candidate_index, candidate_name, jd_text):
    raw_result = await run_evaluation_team(candidate_name, jd_text)
    
    # Improved JSON Extraction
    json_match = re.search(r'\{.*\}', raw_result, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group(0))
        except json.JSONDecodeError:
             result = {}
    else:
        result = {}

    # Map new keys (key_matches/gaps) to DB schema (strengths/weaknesses)
    # Fallback to old keys if agent reverts
    score = result.get('score', 0)
    strengths = result.get('key_matches', result.get('strengths', []))
    weaknesses = result.get('gaps', result.get('weaknesses', []))
    
    # Ensure they are lists
    if isinstance(strengths, str): strengths = [strengths]
    if isinstance(weaknesses, str): weaknesses = [weaknesses]
    
    strengths_str = "\n".join([f"- {s}" for s in strengths]) if strengths else "- None identified"
    weaknesses_str = "\n".join([f"- {w}" for w in weaknesses]) if weaknesses else "- None identified"
    
    # Update DB
    update_candidate_record(
        candidate_name, 
        'Evaluated', 
        score, 
        strengths_str, 
        weaknesses_str
    )
    
    # Update Session
    st.session_state['candidates'][candidate_index]['status'] = 'Evaluated'
    st.session_state['candidates'][candidate_index]['score'] = score
    st.session_state['candidates'][candidate_index]['strengths'] = strengths_str
    st.session_state['candidates'][candidate_index]['weaknesses'] = weaknesses_str

def render_dashboard():
    st.subheader("📊 Candidate Dashboard")
    
    # Header Row
    st.markdown("""
    <div style="display: grid; grid-template-columns: 2fr 1fr 2fr 1fr 1fr; gap: 10px; font-weight: bold; margin-bottom: 10px;">
        <div>Candidate Name</div>
        <div>Status</div>
        <div>Fitness Score</div>
        <div>Analysis</div>
        <div>Interview</div>
    </div>
    """, unsafe_allow_html=True)

    # Report Popup (Simulated with a container at top if active)
    if st.session_state.get('view_report_id') is not None:
        idx = st.session_state['view_report_id']
        # Safety check
        if idx < len(st.session_state['candidates']):
            cand = st.session_state['candidates'][idx]
            
            with st.container():
                st.markdown(f"### 📑 Evaluation Report: {cand['name']}")
                rc1, rc2, rc3 = st.columns([1, 1, 1])
                rc1.metric("Score", f"{cand['score']}/10")
                
                with rc2:
                    st.markdown("**✅ Key Matches**")
                    st.markdown(cand.get('strengths', '-'))
                
                with rc3:
                    st.markdown("**⚠️ Gaps**")
                    st.markdown(cand.get('weaknesses', '-'))
                
                # Actions
                ac1, ac2 = st.columns([1, 5])
                with ac1:
                     if st.button("🔄 Re-evaluate", key=f"re_eval_{idx}"):
                        with st.spinner("Re-evaluating..."):
                            asyncio.run(perform_evaluation(idx, cand['name'], st.session_state['jd']))
                            st.rerun()
                with ac2:
                    if st.button("Close Report"):
                        st.session_state['view_report_id'] = None
                        st.rerun()
                st.divider()

    for i, candidate in enumerate(st.session_state['candidates']):
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 1, 1])
            
            # Name -> Button as Link
            if c1.button(f"📄 {candidate['name']}", key=f"view_{i}", help="Click to view full evaluation details"):
                st.session_state['view_report_id'] = i
                st.rerun()
            
            # Status
            status_color = "green" if candidate['status'] == 'Evaluated' else "gray"
            c2.markdown(f":{status_color}[{candidate['status']}]")
            
            # Score
            try:
                score_val = float(candidate['score'])
            except (ValueError, TypeError):
                score_val = 0
            
            if score_val > 0:
                c3.progress(score_val / 10, text=f"{score_val}/10")
            else:
                c3.markdown("Waiting...")

            # Evaluate Button (Initial)
            if c4.button("⚡ Evaluate", key=f"eval_{i}", disabled=candidate['status'] == 'Evaluated', use_container_width=True):
                with st.spinner(f"Evaluating {candidate['name']} with Multi-Agent Team..."):
                    try:
                         asyncio.run(perform_evaluation(i, candidate['name'], st.session_state['jd']))
                         st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

            # Design Button
            if c5.button("🎙️ Design", key=f"design_{i}", disabled=candidate['status'] != 'Evaluated', use_container_width=True):
                st.session_state['selected_candidate_for_studio'] = candidate
                st.session_state['current_view'] = 'studio'
                st.rerun()
            
            # Compact separator
            st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #e0e0e0;' />", unsafe_allow_html=True)
 
from teams.interview_team import run_interview_generation_team, run_interview_revision

def render_studio():
    candidate = st.session_state['selected_candidate_for_studio']
    if not candidate:
        st.session_state['current_view'] = 'dashboard'
        st.rerun()
    
from pdf_utils import create_interview_guide_pdf

def render_studio():
    candidate = st.session_state['selected_candidate_for_studio']
    if not candidate:
        st.session_state['current_view'] = 'dashboard'
        st.rerun()
    
    # Session Persistence & Loading
    cand_id = candidate['name'] 
    state_key = f"questions_{cand_id}"
    
    # Load from persistence if missing using helper
    if state_key not in st.session_state:
        stored_q = candidate.get('questions')
        if stored_q:
            try:
                st.session_state[state_key] = json.loads(stored_q)
            except:
                st.session_state[state_key] = None
        else:
             st.session_state[state_key] = None

    c_back, c_title = st.columns([1, 6])
    with c_back:
         if st.button("← Back"):
            st.session_state['current_view'] = 'dashboard'
            st.session_state['selected_candidate_for_studio'] = None
            st.rerun()
    with c_title:
        st.subheader(f"Interview Studio: {candidate['name']}")

    # Main Studio Layout
    if st.session_state[state_key] is None:
        # Pre-generation View
        st.info("Click below to generate a tailored interview guide based on the candidate's profile and the Job Description.")
        if st.button("🚀 Generate Interview Guide", type="primary"):
            with st.spinner("Team working: Strategist setting weights -> Generator creating questions -> Reviewer validating..."):
                try:
                    raw_result = asyncio.run(run_interview_generation_team(candidate['name'], st.session_state['jd']))
                    
                    # Extract JSON
                    json_match = re.search(r'\[.*\]', raw_result, re.DOTALL)
                    if json_match:
                         questions_json = json_match.group(0)
                         questions = json.loads(questions_json)
                         
                         # Save to Session
                         st.session_state[state_key] = questions
                         
                         # Save to DB
                         update_candidate_questions(candidate['name'], questions_json)
                         candidate['questions'] = questions_json
                         
                         st.success("Guide Generated & Saved!")
                         st.rerun()
                    else:
                        st.error("Failed to parse agent output. See logs.")
                        st.text(raw_result)
                except Exception as e:
                    st.error(f"Generation Failed: {e}")
    else:
        # Post-generation View
        questions = st.session_state[state_key]
        
        c_left, c_right = st.columns([2, 1])
        
        with c_left:
            st.markdown("### 📝 Interview Guide")
            
            # Markdown Display Construction
            md_content = ""
            for q in questions:
                uid = q.get('u_id', '?')
                cat = q.get('category', 'General')
                level = q.get('complexity', '')
                text = q.get('question', '')
                ans = q.get('likely_answer', '')
                
                md_content += f"#### Q{uid}. {text} \n"
                md_content += f"*Category: {cat} | Level: {level}*  \n"
                md_content += f"> **Likely Answer**: {ans}\n\n"
                md_content += "---\n"
            
            st.markdown(md_content)
            
            st.divider()
            st.markdown("### 💬 Revise Questions")
            
            # Revision Chat
            if prompt := st.chat_input("Ex: Make the technical questions harder..."):
                with st.spinner("Agents are revising the guide..."):
                    try:
                        current_json = json.dumps(questions)
                        raw_result = asyncio.run(run_interview_revision(current_json, prompt))
                        
                        json_match = re.search(r'\[.*\]', raw_result, re.DOTALL)
                        if json_match:
                             new_q_json = json_match.group(0)
                             new_questions = json.loads(new_q_json)
                             
                             # Update State & DB
                             st.session_state[state_key] = new_questions
                             update_candidate_questions(candidate['name'], new_q_json)
                             candidate['questions'] = new_q_json
                             
                             st.success("Questions Revised!")
                             st.rerun()
                        else:
                             st.error("Revision failed to output JSON.")
                    except Exception as e:
                        st.error(f"Revision Error: {e}")

        with c_right:
            st.markdown("### ⚙️ Actions")
            
            if st.button("🔄 Regenerate from Scratch"):
                 st.session_state[state_key] = None
                 st.rerun()
            
            # PDF Generation
            try:
                pdf_bytes = create_interview_guide_pdf(candidate['name'], questions)
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{candidate['name'].replace(' ', '_')}_Interview_Guide.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            except Exception as e:
                st.error(f"PDF Generation Error: {e}")
            
            # Keep JSON as backup/debug
            st.download_button(
                label="Download JSON Source",
                data=json.dumps(questions, indent=2),
                file_name=f"{candidate['name']}_guide.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
