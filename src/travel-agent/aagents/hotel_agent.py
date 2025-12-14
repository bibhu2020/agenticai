from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts.user_context import UserContext
from tools.hotel import search_hotels
from output_types import HotelSearchResults

hotel_agent = Agent[UserContext](
    name="Hotel Specialist",
    handoff_description="Specialist agent for finding and recommending hotels and accommodations",
    instructions="""
    You are a hotel specialist who helps users find the best accommodations for their trips.
    
    Use the search_hotels tool to find hotel options.
    
    CRITICAL: You MUST provide at least 3 distinct hotel options if available.
    
    Format your response as a HotelSearchResults object containing a list of HotelRecommendation items.
    """,
    model="gpt-4-turbo",
    tools=[search_hotels],
    output_type=HotelSearchResults
)