import pytest

from agents import Runner, trace
from ..common.aagents.news_agent import news_agent



@pytest.mark.asyncio
async def test_news_agent_top_headlines():
    """Test news agent fetching top headlines."""
    with trace("News Agent Top Headlines"):
        response = await Runner.run(
            news_agent,
            "What are the top news headlines today?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertion: ensure agent responded with text
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10


@pytest.mark.asyncio
async def test_news_agent_topic_search():
    """Test news agent searching for specific topic."""
    with trace("News Agent Topic Search"):
        response = await Runner.run(
            news_agent,
            "Find recent news about artificial intelligence",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that AI-related terms are mentioned
    output_lower = response.final_output.lower()
    assert any(term in output_lower for term in ["ai", "artificial intelligence", "machine learning"])


@pytest.mark.asyncio
async def test_news_agent_category():
    """Test news agent fetching category-specific news."""
    with trace("News Agent Category News"):
        response = await Runner.run(
            news_agent,
            "Show me the latest technology news",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that technology-related content is present
    output_lower = response.final_output.lower()
    assert any(term in output_lower for term in ["technology", "tech", "software", "hardware"])


@pytest.mark.asyncio
async def test_news_agent_business_news():
    """Test news agent fetching business news."""
    with trace("News Agent Business News"):
        response = await Runner.run(
            news_agent,
            "What are the latest business headlines?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
