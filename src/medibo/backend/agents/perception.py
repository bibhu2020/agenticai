
try:
    from agents import Agent, function_tool, handoff
except ImportError:
    raise ImportError("OpenAI Agents SDK not found.")

from .cognitive import cognitive_agent

def transfer_to_cognitive(analysis: str):
    """
    Transfers the conversation to the Cognitive Agent for risk assessment.
    Args:
        analysis: A string summary of the identified symptoms and tone.
    """
    print(f"DEBUG: Transferring to Cognitive Agent. Analysis: {analysis}")
    return handoff(cognitive_agent)

# 1. Perception Agent
# Responsibilities: Extract symptoms, identify tone.
perception_agent = Agent(
    name="PerceptionAgent",
    model="gpt-4o-mini",
    instructions="""
    You are the Perception Module of the MediBo system.
    
    Your role is to strictly analyze the raw patient input.
    1. Extract ALL medical symptoms mentioned (e.g., "headache", "chest pain").
    2. Extract metadata if available: Duration, Severity description, Location.
    3. Analyze the patient's emotional tone (e.g., "Anxious", "Calm", "In Pain").
    
    Once analyzed, you MUST immediately call the 'transfer_to_cognitive' tool.
    Pass a structured summary of these findings as the 'analysis' argument.
    
    Do NOT ask for Patient ID (Security Agent handles this).
    Do NOT give medical advice (Action Agent handles this).
    
    Analyze the symptoms. Then you MUST call 'transfer_to_cognitive(analysis=...)'. Pass your findings in the 'analysis' argument. Do not output text to the user.
    """,
    tools=[function_tool(transfer_to_cognitive)]
)
