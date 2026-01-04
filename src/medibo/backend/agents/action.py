
try:
    from agents import Agent, function_tool
except ImportError:
    raise ImportError("OpenAI Agents SDK not found.")

from ..tools.definitions import alert_emergency_services, book_appointment

# 3. Action Agent
# Responsibilities: Execute decisions.
action_agent = Agent(
    name="ActionAgent",
    model="gpt-4o-mini",
    instructions="""
    You are the Action Module.
    Based on the Urgency determined by the Cognitive Agent:
    - If CRITICAL: Call 'alert_emergency_services'.
    - If MODERATE: Call 'book_appointment'.
    - If MILD/LOW: Provide self-care advice based on the symptom info.
    
    Finally, generate a compassionate response to the patient telling them what you did.
    """,
    tools=[function_tool(alert_emergency_services), function_tool(book_appointment)]
)
