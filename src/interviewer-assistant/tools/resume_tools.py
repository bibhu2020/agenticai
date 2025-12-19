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
    Fetches the content of a web page using r.jina.ai for better parsing and blocking avoidance.
    """
    print(f"DEBUG: scrape_web_page called with URL: {url}")
    
    # 1. URL Formatting & Validation
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    
    # Ensure www.linkedin.com if user just typed linkedin.com
    if "linkedin.com" in url and "www.linkedin.com" not in url:
        url = url.replace("://linkedin.com", "://www.linkedin.com")
        
    print(f"DEBUG: Normalized URL: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Attempt 1: Jina Reader (Preferred for Markdown)
    try:
        jina_url = f"https://r.jina.ai/{url}"
        print(f"DEBUG: Requesting Jina: {jina_url}")
        
        # Jina often works better without custom UA, or with specific ones. Let's try passing the browser UA.
        response = requests.get(jina_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if len(content) > 200: # Valid content
                print(f"DEBUG: Jina success. Length: {len(content)}")
                return content[:20000]
            else:
                 print(f"DEBUG: Jina content too short: {len(content)}")
        else:
             print(f"DEBUG: Jina failed with Status {response.status_code}")
             
    except Exception as e:
        print(f"DEBUG: Jina exception: {e}")

    # Attempt 2: Google Cache via Jina (Fallback for 403)
    try:
        print(f"DEBUG: Attempting Google Cache for {url}")
        cache_url = f"http://webcache.googleusercontent.com/search?q=cache:{url}"
        jina_cache_url = f"https://r.jina.ai/{cache_url}"
        
        print(f"DEBUG: Requesting Jina Cache: {jina_cache_url}")
        response = requests.get(jina_cache_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            # Check for Google 404 or captcha markers if possible, but length is a good proxy
            if len(content) > 500 and "404. That’s an error" not in content:
                print(f"DEBUG: Jina Cache success. Length: {len(content)}")
                return content[:20000]
            else:
                 print(f"DEBUG: Cache content invalid, short, or 404.")
    except Exception as e:
        print(f"DEBUG: Jina Cache exception: {e}")

    # Attempt 3: Direct Scrape (Fallback)
    try:
        print(f"DEBUG: Falling back to direct scrape of {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts
            for s in soup(["script", "style", "nav", "footer"]):
                s.decompose()
            
            text = soup.get_text(separator="\n")
            
            # Clean empty lines
            clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            
            if len(clean_text) > 200:
                print(f"DEBUG: Direct scrape success. Length: {len(clean_text)}")
                return clean_text[:20000]
        else:
             print(f"DEBUG: Direct scrape failed with {response.status_code}")
             
    except Exception as e:
         print(f"DEBUG: Direct scrape exception: {e}")

    # Final Failure Message
    return f"Error: Failed to access {url} (Status 403 Forbidden). LinkedIn security is blocking automated access. Please save the profile as a PDF and upload it instead."
