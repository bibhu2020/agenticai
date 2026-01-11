import io
import re
from pypdf import PdfReader

def extract_text_from_pdf(file_bytes):
    """
    Extracts text from a PDF file object (BytesIO).
    """
    try:
        reader = PdfReader(file_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def clean_text(text):
    """
    Simple text cleanup: remove excessive whitespace.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_uploaded_files(uploaded_files):
    """
    Processes a list of Streamlit UploadedFile objects.
    Returns a list of dicts: {'text': str, 'metadata': dict}
    """
    processed_docs = []
    
    for uploaded_file in uploaded_files:
        # Create a BytesIO object from the uploaded file
        # Streamlit UploadedFile is already file-like, but let's be safe
        text = extract_text_from_pdf(uploaded_file)
        if not text:
            continue
            
        cleaned_text = clean_text(text)
        
        # Heuristic: Name is often the first line, but filename is safer for unique ID
        candidate_name = uploaded_file.name.replace(".pdf", "").replace("_", " ").title()
        
        processed_docs.append({
            "text": cleaned_text,
            "metadata": {
                "filename": uploaded_file.name,
                "candidate_name": candidate_name
            }
        })
        
    return processed_docs
