
try:
    from agents import Agent, function_tool, handoff
except ImportError:
    raise ImportError("OpenAI Agents SDK not found.")

from ..tools.definitions import check_symptom_severity
from .action import action_agent

def transfer_to_action(urgency: str, rationale: str):
    """
    Transfers the conversation to the Action Agent for executing medical decisions.
    Args:
        urgency: The determined urgency level (CRITICAL, MODERATE, MILD).
        rationale: The reasoning behind the urgency.
    """
    print(f"DEBUG: Transferring to Action Agent. Urgency: {urgency}")
    return handoff(action_agent)

# 2. Cognitive Agent
# Responsibilities: Assess risk using Tools.
cognitive_agent = Agent(
    name="CognitiveAgent",
    model="gpt-4o-mini",
    instructions="""
    You are the Cognitive Module.
    Take the symptoms identified by the Perception Agent.
    Use the 'check_symptom_severity' tool for EACH symptom to determine risk.
    Decide the overall Urgency: CRITICAL, MODERATE, or MILD.
    
    Assess the risk. Then you MUST call 'transfer_to_action(urgency=..., rationale=...)'. Pass your findings in the arguments. Do not output text to the user.
    """,
    tools=[function_tool(check_symptom_severity), function_tool(transfer_to_action)]
)
