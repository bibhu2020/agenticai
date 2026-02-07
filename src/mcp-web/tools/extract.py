
"""
Extract content from URL
"""
import requests
from bs4 import BeautifulSoup
import html2text

def extract_content(url: str) -> str:
    """
    Extracts text content from a given URL.
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        h = html2text.HTML2Text()
        h.ignore_links = True
        text = h.handle(str(soup))
        return text
    except Exception as e:
        return f"Error extracting content: {str(e)}"
