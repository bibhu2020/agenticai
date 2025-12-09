from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts import UserContext
from tools import search_flights
from output_types import FlightSearchResults

flight_agent = Agent[UserContext](
    name="Flight Specialist",
    handoff_description="Specialist agent for finding and recommending flights",
    instructions="""
    You are a flight specialist who helps users find the best flights for their trips.
    
    Use the search_flights tool to find flight options.
    
    CRITICAL: You MUST provide at least 3 distinct flight options if available.
    
    Format your response as a FlightSearchResults object containing a list of FlightRecommendation items.
    """,
    model="gpt-4o-mini",
    tools=[search_flights],
    output_type=FlightSearchResults
)