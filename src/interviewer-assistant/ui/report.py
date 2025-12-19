import streamlit as st
import re
import json
from fpdf import FPDF
from teams.team import extract_json

def generate_markdown_report(messages):
    """
    Compiles the final report from agent messages.
    """
    candidate_name = "Candidate"
    
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
                candidate_name = json_data.get("candidate_name", candidate_name)
                candidate_summary = f"### Candidate Profile\n**Name**: {candidate_name}\n\n**Summary**: {json_data.get('candidate_summary')}\n\n"
                if "key_skills" in json_data:
                    candidate_summary += f"**Key Skills**: {', '.join(json_data['key_skills'])}\n\n"
            
            elif "fitness_score" in json_data:
                score = json_data.get("fitness_score")
                fitness_score = f"### Fitness Assessment\n**Score**: {score}/10\n\n"
                justification = f"**Assessment**: {json_data.get('justification')}\n\n"
            
            elif "structured_interview" in json_data:
                interview_questions = "### Structured Interview Questions\n\n"
                q_count = 1
                for section in json_data.get("structured_interview", []):
                    label = section.get("skill", section.get("category", "General"))
                    interview_questions += f"#### {label}\n"
                    for q_data in section.get("questions", []):
                        if isinstance(q_data, str):
                            interview_questions += f"**{q_count}.** {q_data}\n\n"
                            q_count += 1
                        else:
                            q_text = q_data.get("q", "")
                            q_type = q_data.get("type", "General")
                            q_complex = q_data.get("complexity", "Norm")
                            q_answer = q_data.get("sample_answer", "")
                            
                            interview_questions += f"**{q_count}. Q ({q_type}, {q_complex})**: {q_text}\n"
                            if q_answer:
                                interview_questions += f"  - *Listen for*: {q_answer}\n"
                            interview_questions += "\n" # Extra spacing
                            q_count += 1
                    interview_questions += "\n"

    report_md = f"# Interview Guide: {candidate_name}\n\n"
    report_md += candidate_summary
    report_md += fitness_score
    report_md += justification
    report_md += interview_questions
    
    return report_md

def create_pdf(markdown_text):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Interview Guide', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)
    
    # Process text line by line to handle basic formatting
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.encode('latin-1', 'replace').decode('latin-1')
        
        if line.startswith('# '):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, line.replace('# ', ''), 0, 1)
            pdf.set_font("Arial", size=11)
        elif line.startswith('### '):
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(0, 8, line.replace('### ', ''), 0, 1)
            pdf.set_font("Arial", size=11)
        elif line.startswith('#### '):
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, line.replace('#### ', ''), 0, 1)
            pdf.set_font("Arial", size=11)
        elif line.strip().startswith('**') and '. Q (' in line: # Question detection
             # Highlight questions
             pdf.set_font("Arial", 'B', 11)
             clean = line.replace('**', '')
             pdf.multi_cell(0, 6, clean)
             pdf.set_font("Arial", size=11)
        else:
            clean = line.replace('**', '').replace('*', '')
            pdf.multi_cell(0, 6, clean)
            
    return pdf.output(dest='S').encode('latin-1')

def render_persistent_view():
    """Renders the generated report if it exists in session state."""
    # ------------------------------------------------------------------------------
    # REPORT DISPLAY (Persistent)
    # ------------------------------------------------------------------------------
    if st.session_state.get("generated_report"):
        st.markdown("---")
        st.header("📝 Interview Guide")
        
        # Render Markdown
        st.markdown(st.session_state.generated_report)
        
        # Render Download Button
        if st.session_state.get("generated_pdf"):
            st.download_button(
                label="📄 Download Interview Guide (PDF)",
                data=st.session_state.generated_pdf,
                file_name="interview_guide.pdf",
                mime="application/pdf"
            )
