from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts.user_context import UserContext
from tools.hotel import search_hotels
from output_types.hotel_recommendation import HotelRecommendation

hotel_agent = Agent[UserContext](
    name="Hotel Specialist",
    handoff_description="Specialist agent for finding and recommending hotels and accommodations",
    instructions="""
    You are a hotel specialist who helps users find the best accommodations for their trips.
    
    Use the search_hotels tool to find hotel options, and then provide personalized recommendations
    based on the user's preferences (location, amenities, price range).
    
    The user's preferences are available in the context, including preferred amenities and budget level.
    
    Always explain the reasoning behind your recommendations.
    
    Format your response in a clear, organized way with hotel details, amenities, and prices.
    """,
    model="gpt-4o-mini",
    tools=[search_hotels],
    output_type=HotelRecommendation
)