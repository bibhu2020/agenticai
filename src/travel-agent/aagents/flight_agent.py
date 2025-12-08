from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts import UserContext
from tools import search_flights
from output_types import FlightRecommendation

flight_agent = Agent[UserContext](
    name="Flight Specialist",
    handoff_description="Specialist agent for finding and recommending flights",
    instructions="""
    You are a flight specialist who helps users find the best flights for their trips.
    
    Use the search_flights tool to find flight options, and then provide personalized recommendations
    based on the user's preferences (price, time, direct vs. connecting).
    
    The user's preferences are available in the context, including preferred airlines.
    
    Always explain the reasoning behind your recommendations.
    
    Format your response in a clear, organized way with flight details and prices.
    """,
    model="gpt-4o-mini",
    tools=[search_flights],
    output_type=FlightRecommendation
)