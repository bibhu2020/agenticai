import os
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document

def read_local_file(file_path: str) -> str:
    """
    Reads a local file (PDF, DOCX, or TXT) and returns its text content.
    """
    print(f"DEBUG: read_local_file called with path: {file_path}")
    if not os.path.exists(file_path):
        print(f"DEBUG: File not found at {file_path}")
        return f"Error: File not found at {file_path}"
    
    ext = os.path.splitext(file_path)[1].lower()
    print(f"DEBUG: Detected extension: {ext}")
    
    try:
        if ext == '.pdf':
            print("DEBUG: Reading PDF...")
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            print(f"DEBUG: PDF read success. Length: {len(text)}")
            return text
            
        elif ext == '.docx':
            print("DEBUG: Reading DOCX...")
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            print(f"DEBUG: DOCX read success. Length: {len(text)}")
            return text
            
        elif ext == '.txt':
            print("DEBUG: Reading TXT...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"DEBUG: TXT read success. Length: {len(content)}")
            return content
                
        else:
            print(f"DEBUG: Unsupported format {ext}")
            return f"Error: Unsupported file format {ext}. Please provide .pdf, .docx, or .txt"
            
    except Exception as e:
        print(f"DEBUG: Exception in read_local_file: {e}")
        return f"Error reading file: {str(e)}"

def scrape_web_page(url: str) -> str:
    """
    Fetches the content of a web page (e.g., LinkedIn public profile) and returns the text.
    Naive implementation using requests and BeautifulSoup. 
    Note: Many sites like LinkedIn block simple scrapers.
    """
    print(f"DEBUG: scrape_web_page called with URL: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Collapse whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if len(clean_text) < 100:
            print(f"DEBUG: Scraped content significantly short ({len(clean_text)} chars). Likely blocked.")
            return f"Error: Could not extract meaningful content from {url}. The site might be blocking automated access (e.g., LinkedIn auth wall). Please rely on the provided Resume only."
            
        print(f"DEBUG: Scrape success. Length: {len(clean_text)}")
        return clean_text[:10000] # Limit content to avoid context overflow
        
    except Exception as e:
        print(f"DEBUG: Exception in scrape_web_page: {e}")
        return f"Error fetching URL {url}: {str(e)}"
