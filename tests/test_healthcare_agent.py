"""Test file for Healthcare RAG Agent"""
import pytest
import sys
from pathlib import Path

# Add common to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from agents import Runner, trace
from aagents.healthcare_agent import healthcare_agent
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.asyncio
async def test_healthcare_agent_diabetes_query():
    """Test healthcare agent with diabetes-related query"""
    with trace("Healthcare Agent Diabetes Query"):
        response = await Runner.run(
            healthcare_agent,
            "I am having chest burning from 12 hours. what could be the reasons?"
            # "What is diabetes and how is it managed?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    assert len(response.final_output) > 50
    
    # # Check for diabetes-related content
    # output_lower = response.final_output.lower()
    # assert "diabetes" in output_lower, "Response should mention diabetes"
    
    print("\n✓ Test passed: Healthcare agent responded to diabetes query")


# @pytest.mark.asyncio
# async def test_healthcare_agent_heart_health():
#     """Test healthcare agent with heart health query"""
#     with trace("Healthcare Agent Heart Health"):
#         response = await Runner.run(
#             healthcare_agent,
#             "How can I prevent heart disease?",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertions
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 50
    
#     # Check for heart-related content
#     output_lower = response.final_output.lower()
#     assert any(term in output_lower for term in ["heart", "cardiovascular", "prevention"]), \
#         "Response should mention heart health topics"
    
#     print("\n✓ Test passed: Healthcare agent responded to heart health query")


# @pytest.mark.asyncio
# async def test_healthcare_agent_nutrition():
#     """Test healthcare agent with nutrition query"""
#     with trace("Healthcare Agent Nutrition"):
#         response = await Runner.run(
#             healthcare_agent,
#             "What are the key components of a balanced diet?",
#         )

#     # Print for debugging
#     print("\n[DEBUG] Agent Final Output:\n")
#     print(response.final_output)

#     # Basic assertions
#     assert response.final_output is not None
#     assert isinstance(response.final_output, str)
#     assert len(response.final_output) > 50
    
#     # Check for nutrition-related content
#     output_lower = response.final_output.lower()
#     assert any(term in output_lower for term in ["diet", "nutrition", "food", "protein", "vitamin"]), \
#         "Response should mention nutrition topics"
    
#     print("\n✓ Test passed: Healthcare agent responded to nutrition query")


@pytest.mark.asyncio
async def test_healthcare_agent_includes_disclaimer():
    """Test that healthcare agent includes medical disclaimer"""
    with trace("Healthcare Agent Disclaimer Check"):
        response = await Runner.run(
            healthcare_agent,
            "Should I take aspirin for my headache?",
        )

    # Print for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(response.final_output)

    # Basic assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, str)
    
    # Check for disclaimer
    output_lower = response.final_output.lower()
    assert any(term in output_lower for term in ["disclaimer", "consult", "healthcare provider", "medical advice"]), \
        "Response should include medical disclaimer"
    
    print("\n✓ Test passed: Healthcare agent includes appropriate disclaimer")


# Run tests with: pytest -s tests/test_healthcare_agent.py
