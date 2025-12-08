from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts.user_context import UserContext

conversational_agent = Agent[UserContext](
    name="General Conversation Specialist",
    handoff_description="Specialist agent for giving basic responses to the user to carry out a normal conversation as opposed to structured output.",
    instructions="""
    You are a trip planning expert who answers basic user questions about their trip and offers any suggestions.
    Act as a helpful assistant and be helpful in any way you can be.
    """,
    model="gpt-4o-mini",
)