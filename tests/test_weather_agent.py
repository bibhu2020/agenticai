import pytest

from agents import Runner, trace
from ..common.aagents.weather_agent import weather_agent



@pytest.mark.asyncio
async def test_weather_agent_run():
    """Test weather agent end-to-end."""
    with trace("Weather Agent Run"):
        response = await Runner.run(
            weather_agent,
            "How is the weather in Melissa and bhubaneswar for next 2 days?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertion: ensure agent responded with text
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
