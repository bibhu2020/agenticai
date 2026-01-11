from fpdf import FPDF
import io

class InterviewGuidePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Interview Guide', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_interview_guide_pdf(candidate_name, questions):
    pdf = InterviewGuidePDF()
    pdf.add_page()
    
    # Candidate Info
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Candidate: {candidate_name}", 0, 1)
    pdf.ln(5)
    
    # Questions
    pdf.set_font('Arial', '', 11)
    
    for q in questions:
        # Avoid orphan lines/page breaks in weird spots
        if pdf.get_y() > 250:
            pdf.add_page()
            
        # Question Header
        q_id = q.get('u_id', '?')
        cat = q.get('category', 'General')
        comp = q.get('complexity', 'Medium')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.multi_cell(0, 7, f"Q{q_id} [{cat} - {comp}]")
        
        # Question Body
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 7, q.get('question', ''))
        pdf.ln(2)
        
        # Answer Key
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(100, 100, 100) # Gray for answers
        pdf.multi_cell(0, 7, f"Likely Answer: {q.get('likely_answer', '')}")
        pdf.set_text_color(0, 0, 0) # Reset to black
        
        pdf.ln(5) # Spacing between questions

    return pdf.output(dest='S').encode('latin-1', 'replace')
