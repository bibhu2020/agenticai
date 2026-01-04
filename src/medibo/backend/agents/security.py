
try:
    from agents import Agent, function_tool, handoff
except ImportError:
    raise ImportError("OpenAI Agents SDK not found.")

from ..tools.definitions import lookup_patient_id
from .perception import perception_agent

def transfer_to_perception():
    """
    Transfers the conversation to the Perception Agent for symptom analysis.
    Call this immediately after patient verification.
    """
    print("DEBUG: Transferring to Perception Agent")
    return handoff(perception_agent)

# 4. Security Agent
# Responsibilities: Verify Identity.
security_agent = Agent(
    name="SecurityAgent",
    model="gpt-4o-mini",
    instructions="""
    You are the Security Module.
    Verify the patient ID using 'lookup_patient_id'.
    If valid, handoff to the PerceptionAgent.
    If invalid, deny access politely.
    
    If patient is verified, you MUST call 'transfer_to_perception'. Do not speak to the user. Just call the tool.
    """,
    tools=[function_tool(lookup_patient_id), function_tool(transfer_to_perception)]
)
