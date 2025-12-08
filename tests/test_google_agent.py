import pytest
from dotenv import load_dotenv
from agents import Runner, trace
from ..common.aagents.google_agent import google_agent

load_dotenv()

# @pytest.mark.asyncio
# async def test_google_agent_general_search():
#     """Test Google agent with a general search query."""
#     with trace("Google Agent General Search"):
#         response = await Runner.run(
#             google_agent,
#             "What is quantum computing?",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertion: ensure agent responded with text
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 10
    
#     # Check that quantum computing is mentioned
#     output_lower = response.final_output.lower()
#     assert "quantum" in output_lower


@pytest.mark.asyncio
async def test_google_agent_recent_search():
    """Test Google agent with time-specific search."""
    with trace("Google Agent Recent Search"):
        response = await Runner.run(
            google_agent,
            "Find recent news about SpaceX from this week",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that SpaceX is mentioned
    output_lower = response.final_output.lower()
    assert "spacex" in output_lower or "space" in output_lower


@pytest.mark.asyncio
async def test_google_agent_factual_query():
    """Test Google agent with factual information query."""
    with trace("Google Agent Factual Query"):
        response = await Runner.run(
            google_agent,
            "Who is the CEO of Microsoft?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that Microsoft is mentioned
    output_lower = response.final_output.lower()
    assert "microsoft" in output_lower


@pytest.mark.asyncio
async def test_google_agent_research_query():
    """Test Google agent with research-style query."""
    with trace("Google Agent Research Query"):
        response = await Runner.run(
            google_agent,
            "What are the benefits of renewable energy?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that renewable energy terms are mentioned
    output_lower = response.final_output.lower()
    assert any(term in output_lower for term in ["renewable", "energy", "solar", "wind", "clean"])


# @pytest.mark.asyncio
# async def test_google_agent_current_events():
#     """Test Google agent with current events query."""
#     with trace("Google Agent Current Events"):
#         response = await Runner.run(
#             google_agent,
#             "What are the latest developments in AI technology?",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertions
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 10
    
#     # Check that AI-related terms are mentioned
#     output_lower = response.final_output.lower()
#     assert any(term in output_lower for term in ["ai", "artificial intelligence", "technology"])
