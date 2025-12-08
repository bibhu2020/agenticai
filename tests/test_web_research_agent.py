# tests/test_web_research_agent.py
import pytest
from dotenv import load_dotenv
from agents import Runner, trace
from ..common.aagents.web_research_agent import web_research_agent

load_dotenv()


@pytest.mark.asyncio
async def test_web_research_agent_run():
    """Test web_research_agent for MLops tools in 2025."""
    with trace("Market Research Agent Run"):
        response = await Runner.run(
            web_research_agent,
            "Popular MLops tools in 2025."
        )

    # Print formatted output for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, (str, list, dict))
    assert len(str(response.final_output)) > 10
