
"""
Integration tests for MCP Web tools.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import paths logic
import sys
import os

# Add src and mcp-web to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, "../src")))
sys.path.append(os.path.abspath(os.path.join(current_dir, "../src/mcp-web")))

# Mock mcp_telemetry to avoid import errors
sys.modules["mcp_telemetry"] = MagicMock()

try:
    from tools.search import search_web
    from tools.extract import extract_content
    from tools.research import research_topic
    from tools.wikipedia import search_wikipedia, get_wikipedia_page
    from tools.arxiv import search_arxiv
except ImportError:
    # Handle direct runs
    sys.path.append(os.path.abspath(os.path.join(current_dir, "../src/mcp-web/tools")))
    from search import search_web
    from extract import extract_content
    from research import research_topic
    from wikipedia import search_wikipedia, get_wikipedia_page
    from arxiv import search_arxiv

def test_search_web():
    mock_results = [{"title": "Test", "href": "http://test.com", "body": "Snippet"}]
    # Mock DuckDuckGo
    with patch("tools.search.DDGS") as MockDDGS:
        instance = MockDDGS.return_value.__enter__.return_value
        instance.text.return_value = mock_results
        
        res = search_web("test query")
        assert len(res) == 1
        assert res[0]["title"] == "Test"

def test_extract_content():
    # Mock requests
    with patch("tools.extract.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b"<html><body><h1>Title</h1><p>Content</p></body></html>"
        mock_get.return_value = mock_resp
        
        content = extract_content("http://test.com")
        assert "Title" in content
        assert "Content" in content

def test_research_topic():
    # Mock search and extract
    mock_search_res = [{"title": "Article 1", "url": "http://1.com", "snippet": "S1"}]
    
    with patch("tools.research.search_web", return_value=mock_search_res) as mock_search:
        with patch("tools.research.extract_content", return_value="Full Content 1") as mock_extract:
            res = research_topic("topic")
            assert len(res) == 1
            assert res[0]["content"] == "Full Content 1"

def test_wikipedia_search():
    with patch("tools.wikipedia.wikipedia.search", return_value=["Page 1", "Page 2"]):
        res = search_wikipedia("query")
        assert "Page 1" in res

def test_wikipedia_page():
    with patch("tools.wikipedia.wikipedia.page") as mock_page:
        mock_p = MagicMock()
        mock_p.title = "Title"
        mock_p.content = "Content"
        mock_p.summary = "Summary"
        mock_p.url = "http://wiki"
        mock_page.return_value = mock_p
        
        res = get_wikipedia_page("Title")
        assert res["title"] == "Title"
        assert res["summary"] == "Summary"

def test_arxiv_search():
    with patch("tools.arxiv.arxiv.Search") as MockSearch:
        mock_result = MagicMock()
        mock_result.title = "Paper Title"
        mock_result.summary = "Abstract"
        class MockAuthor:
            def __init__(self, name):
                self.name = name
        mock_result.authors = [MockAuthor("Author 1")]
        mock_result.pdf_url = "http://pdf"
        mock_result.published = "2023-01-01"
        
        instance = MockSearch.return_value
        instance.results.return_value = [mock_result]
        
        res = search_arxiv("query")
        assert res[0]["title"] == "Paper Title"
        assert res[0]["authors"] == ["Author 1"]
