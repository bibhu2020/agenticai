import pytest
from dotenv import load_dotenv
from agents import Runner, trace
from ..common.aagents.yf_agent import yf_agent

load_dotenv()

# @pytest.mark.asyncio
# async def test_yf_agent_basic_query():
#     """Test Yahoo Finance agent with a basic stock query."""
#     with trace("YF Agent Basic Query"):
#         response = await Runner.run(
#             yf_agent,
#             "What is the current price and market sentiment for AAPL stock?",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertion: ensure agent responded with text
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 10
    
#     # Check that the response mentions AAPL
#     assert "AAPL" in response.final_output or "Apple" in response.final_output


@pytest.mark.asyncio
async def test_yf_agent_multiple_stocks():
    """Test Yahoo Finance agent with multiple stock comparison."""
    with trace("YF Agent Multiple Stocks"):
        response = await Runner.run(
            yf_agent,
            "Compare the market sentiment for AAPL and MSFT over the last month.",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that both stocks are mentioned
    output_upper = response.final_output.upper()
    assert "AAPL" in output_upper or "APPLE" in output_upper
    assert "MSFT" in output_upper or "MICROSOFT" in output_upper


@pytest.mark.asyncio
async def test_yf_agent_historical_data():
    """Test Yahoo Finance agent with historical data request."""
    with trace("YF Agent Historical Data"):
        response = await Runner.run(
            yf_agent,
            "Show me the historical price data for TSLA over the last 5 days.",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 10
    
    # Check that TSLA is mentioned
    assert "TSLA" in response.final_output or "Tesla" in response.final_output


# @pytest.mark.asyncio
# async def test_yf_agent_with_time_context():
#     """Test Yahoo Finance agent uses current datetime for context."""
#     with trace("YF Agent Time Context"):
#         response = await Runner.run(
#             yf_agent,
#             "What is the current market sentiment for GOOGL? Include today's date in your analysis.",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertions
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 10
    
#     # Check that GOOGL is mentioned
#     assert "GOOGL" in response.final_output or "Google" in response.final_output or "Alphabet" in response.final_output
    
#     # Check that a date is mentioned (could be various formats)
#     import re
#     # Look for date patterns like "2025", "December", "Dec", etc.
#     has_date = bool(re.search(r'(202[0-9]|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', response.final_output))
#     assert has_date, "Response should include date context"


# @pytest.mark.asyncio
# async def test_yf_agent_invalid_symbol():
#     """Test Yahoo Finance agent handles invalid stock symbols gracefully."""
#     with trace("YF Agent Invalid Symbol"):
#         response = await Runner.run(
#             yf_agent,
#             "What is the price of INVALIDXYZ123 stock?",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertions
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 10
    
#     # Should mention that data is unavailable or invalid
#     output_lower = response.final_output.lower()
#     assert any(word in output_lower for word in ["unavailable", "invalid", "not found", "no data", "error"])
