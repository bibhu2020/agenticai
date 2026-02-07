
"""
SEO & ADA Compliance MCP Server
"""
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Set
from mcp_telemetry import log_usage

# Initialize FastMCP Server
mcp = FastMCP("SEO & ADA Audit")

@mcp.tool()
def analyze_seo(url: str) -> Dict[str, Any]:
    """
    Perform a basic SEO audit of a webpage.
    Checks title, meta description, H1 tags, image alt attributes, and internal/external links.
    """
    log_usage("mcp-seo", "analyze_seo")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        result = {
            "url": url,
            "status_code": response.status_code,
            "title": soup.title.string if soup.title else None,
            "meta_description": None,
            "h1_count": len(soup.find_all('h1')),
            "images_missing_alt": 0,
            "internal_links": 0,
            "external_links": 0
        }
        
        # Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result["meta_description"] = meta_desc.get('content')
            
        # Images
        imgs = soup.find_all('img')
        for img in imgs:
            if not img.get('alt'):
                result["images_missing_alt"] += 1
                
        # Links
        links = soup.find_all('a', href=True)
        domain = urlparse(url).netloc
        for link in links:
            href = link['href']
            if href.startswith('/') or domain in href:
                result["internal_links"] += 1
            else:
                result["external_links"] += 1
                
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_ada(url: str) -> Dict[str, Any]:
    """
    Perform a basic ADA/WCAG accessibility check.
    Checks for missing alt text, form labels, lang attribute, and ARIA usage.
    """
    log_usage("mcp-seo", "analyze_ada")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        issues = []
        
        # 1. Images missing alt
        imgs = soup.find_all('img')
        missing_alt = [img.get('src', 'unknown') for img in imgs if not img.get('alt')]
        if missing_alt:
            issues.append(f"Found {len(missing_alt)} images missing alt text.")
            
        # 2. Html Lang attribute
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            issues.append("Missing 'lang' attribute on <html> tag.")
            
        # 3. Form input labels
        inputs = soup.find_all('input')
        for inp in inputs:
            # Check if input has id and a corresponding label
            inp_id = inp.get('id')
            label = soup.find('label', attrs={'for': inp_id}) if inp_id else None
            # Or parent is label
            parent_label = inp.find_parent('label')
            # Or aria-label
            aria_label = inp.get('aria-label')
            
            if not (label or parent_label or aria_label):
                issues.append(f"Input field (type={inp.get('type')}) missing label.")
                
        return {
            "url": url,
            "compliance_score": max(0, 100 - (len(issues) * 10)), # Rough score
            "issues": issues
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_sitemap(url: str, max_depth: int = 1) -> List[str]:
    """
    Crawl the website to generate a simple list of internal URLs (sitemap).
    """
    visited = set()
    to_visit = [(url, 0)]
    domain = urlparse(url).netloc
    
    try:
        while to_visit:
            current_url, depth = to_visit.pop(0)
            if current_url in visited or depth > max_depth:
                continue
                
            visited.add(current_url)
            
            try:
                response = requests.get(current_url, timeout=5)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    parsed = urlparse(full_url)
                    
                    if parsed.netloc == domain and full_url not in visited:
                        # Only add html pages usually, but for simplicity we add all internal
                        to_visit.append((full_url, depth + 1))
            except Exception:
                continue
                
        return sorted(list(visited))
    except Exception as e:
        return [f"Error: {str(e)}"]

if __name__ == "__main__":
    mcp.run()
